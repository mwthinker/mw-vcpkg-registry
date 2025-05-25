#!/usr/bin/env python3
"""
bump-port-version.py - Bump the port-version for a specific vcpkg port.

This script takes a port name as input, checks if the port exists, and if the git-tree
is different from the current one while the version (not port-version) is the same.
It will then bump the port-version by one in the versions file and the baseline.json file.
No uncommitted changes are allowed in the port folder, if so the script will abort.

Usage:
    python bump-port-version.py --port <portname>

Requirements:
    - Python 3.7+
    - 'requests' and 'packaging' modules (install with pip if missing)
    - Requires git in PATH
"""

import argparse
import os
import json
import subprocess
from typing import Optional, List, Tuple, Dict

try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    print("Error: The 'packaging' module is required. Install it with 'pip install packaging'.")
    exit(1)

# Import utility functions
from util.util import format_vcpkg_manifest, get_or_create_baseline, get_git_tree_hash, load_and_validate_vcpkg_json

def get_local_commit_hash() -> Optional[str]:
    """Get the latest commit hash from the local repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting local commit hash: {e}")
        return None
    
def get_versions_file(portname: str) -> Tuple[str, Dict]:
    """Get versions file for a port."""
    versions_dir = "versions"
    json_file = os.path.join(versions_dir, f"{portname[0]}-", f"{portname}.json")
    
    if not os.path.isfile(json_file):
        raise FileNotFoundError(f"Error: Versions file for port '{portname}' does not exist at '{json_file}'.")
    
    with open(json_file, "r") as f:
        return json_file, json.load(f)

def check_uncommitted_changes(port_path: str) -> bool:
    """Check if there are uncommitted changes in the port folder."""
    try:
        git_friendly_port_path = port_path.replace('\\', '/')
        result = subprocess.run(
            ["git", "status", "--porcelain", git_friendly_port_path],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            print(f"Error: There are uncommitted changes in '{port_path}':")
            print(result.stdout)
            return True
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking git status for '{port_path}': {e}")
        return True  # Assume there are changes if we can't check

def bump_port_version(portname: str) -> List[str]:
    """
    Bump the port-version for a specific port.
    Returns a list of files that were updated.
    """
    # Check if the port exists
    port_path = os.path.join("ports", portname)
    if not os.path.isdir(port_path):
        print(f"Error: Port '{portname}' does not exist in 'ports' directory.")
        return []    # Check for uncommitted changes
    if check_uncommitted_changes(port_path):
        return []
        
    # Get the vcpkg.json path for later updating
    vcpkg_json_path = os.path.join(port_path, "vcpkg.json")
    
    # Verify that vcpkg.json exists
    if not os.path.isfile(vcpkg_json_path):
        print(f"Error: Missing 'vcpkg.json' at {vcpkg_json_path}.")
        return []

    # Get the local commit hash for the git-tree
    local_commit_hash = get_local_commit_hash()
    if not local_commit_hash:
        print("Error: Failed to get the local commit hash.")
        return []

    # Get the git-tree hash for the specific port folder
    git_tree = get_git_tree_hash(port_path, local_commit_hash)
    if not git_tree:
        print(f"Error: Failed to get git-tree hash for port '{portname}' at commit {local_commit_hash}.")
        return []

    # Get the versions file
    try:
        version_port_file, version_port_data = get_versions_file(portname)
    except FileNotFoundError as e:
        print(e)
        return []

    # Check if the version data is valid
    if "versions" not in version_port_data or not isinstance(version_port_data["versions"], list):
        print(f"Error: Invalid JSON structure in '{version_port_file}'.")
        return []

    # Get the latest version entry
    if not version_port_data["versions"]:
        print(f"Error: No version entries found in '{version_port_file}'.")
        return []

    latest_entry = version_port_data["versions"][0]
    latest_version = latest_entry["version"]
    latest_port_version = latest_entry.get("port-version", 0)
    latest_git_tree = latest_entry.get("git-tree", "")    # Check if the git-tree is different
    if latest_git_tree == git_tree:
        print(f"Error: Git-tree hash hasn't changed for port '{portname}'. No need to bump port-version.")
        return []

    new_port_version = latest_port_version + 1
    print(f"Bumping port-version for '{portname}' from {latest_port_version} to {new_port_version}...")
    
    try:
        vcpkg_data = load_and_validate_vcpkg_json(vcpkg_json_path)
        vcpkg_data["port-version"] = new_port_version
        with open(vcpkg_json_path, "w") as f:
            json.dump(vcpkg_data, f, indent=2)
    except Exception as e:
        print(f"Error updating vcpkg.json with new port-version: {e}")
        return []

    # Format the vcpkg.json file
    if not format_vcpkg_manifest(vcpkg_json_path):
        print(f"Error formatting vcpkg.json for {portname}.")
        return []
    version_port_data["versions"].insert(0, {
        "git-tree": git_tree,
        "version": latest_version,
        "port-version": new_port_version
    })

    # Save the updated JSON file
    with open(version_port_file, "w") as f:
        json.dump(version_port_data, f, indent=2)
    print(f"Updated '{version_port_file}' with new port-version: {new_port_version}.")    # Update baseline.json
    baseline_file, baseline_data = get_or_create_baseline()
    baseline_data["default"][portname] = {
        "baseline": latest_version,
        "port-version": new_port_version
    }
    
    # Save the updated baseline.json
    with open(baseline_file, "w") as f:
        json.dump(baseline_data, f, indent=2)

    print(f"Updated 'baseline.json' for port '{portname}' with new port-version: {new_port_version}.")
    
    # Commit changes
    try:
        subprocess.run(["git", "add", vcpkg_json_path, version_port_file, baseline_file], check=True)
        subprocess.run(["git", "commit", "-m", f"Bumped port-version for {portname} to {new_port_version}"], check=True)
        print(f"Committed updates for {portname}.")
        return [vcpkg_json_path, version_port_file, baseline_file]
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes for {portname}: {e}")
        return []

def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Bump port-version for a specific vcpkg port')
    parser.add_argument('--port', required=True, help='Name of the port to bump the port-version for')
    args = parser.parse_args()
    
    # Get the port name from command line arguments
    portname = args.port
    
    # Bump the port-version
    updated_files = bump_port_version(portname)
    
    if updated_files:
        print(f"Successfully bumped port-version for port: {portname}")
    else:
        print(f"Failed to bump port-version for port: {portname}")

if __name__ == "__main__":
    main()
