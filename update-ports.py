#!/usr/bin/env python3
"""
update-ports.py - Update vcpkg ports and baseline files automatically.

This script scans all subdirectories in the 'ports' folder, checks for updates in the corresponding GitHub repositories,
and updates the port's vcpkg.json, portfile.cmake, and the registry's versions and baseline files as needed.

Usage:
    python update-ports.py

Requirements:
    - Python 3.7+
    - 'requests' and 'packaging' modules (install with pip if missing)
    - Requires git in PATH

All changes are committed to git automatically.
"""

import os
import json
import subprocess
from typing import Optional
try:
    import requests
except ImportError:
    print("Error: The 'requests' module is required. Install it with 'pip install requests'.")
    exit(1)
try:
    from packaging.version import Version, InvalidVersion
except ImportError:
    print("Error: The 'packaging' module is required. Install it with 'pip install packaging'.")
    exit(1)

from util.util import format_vcpkg_manifest, get_sha512_from_github, load_and_validate_vcpkg_json, get_or_create_baseline, get_git_tree_hash

def get_latest_commit_hash(repo_name: str, branch: str) -> Optional[str]:
    url = f"https://api.github.com/repos/{repo_name}/git/refs/heads/{branch}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if "object" in data and "sha" in data["object"]:
            return data["object"]["sha"]
        else:
            print(f"Error: Unexpected response structure from GitHub API for {repo_name} branch {branch}.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching latest commit hash for {repo_name} branch {branch}: {e}")
        return None

def bump_version(version: str) -> str:
    """Bump the patch version of a semantic version string."""
    parts = version.split(".")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        parts[2] = str(int(parts[2]) + 1)  # Increment the patch version
        return ".".join(parts)
    else:
        raise ValueError(f"Invalid version format: {version}")

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

def update_port(portname: str) -> list[str]:
    """Update the port with the latest commit hash and version (or bump port-version)."""
    portfile_path = os.path.join("ports", portname, "portfile.cmake")
    vcpkg_json_path = os.path.join("ports", portname, "vcpkg.json")

    if not os.path.isfile(portfile_path):
        print(f"Error: Missing 'portfile.cmake' in '{portname}' directory.")
        return []

    try:
        vcpkg_data = load_and_validate_vcpkg_json(vcpkg_json_path)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        return []

    # Format the vcpkg.json file before proceeding
    if not format_vcpkg_manifest(vcpkg_json_path):
        print(f"Error formatting vcpkg.json for {portname}.")
        return []

    # Extract REPO and REF from portfile.cmake
    repo_name, current_ref, head_ref = None, None, None
    with open(portfile_path, "r") as f:
        for line in f:
            if line.strip().startswith("REPO "): # Match only lines starting with "REPO "
                repo_name = line.split()[1]
            elif line.strip().startswith("REF "): # Match only lines starting with "REF "
                current_ref = line.split()[1]
            elif line.strip().startswith("HEAD_REF "): # Match only lines starting with "HEAD_REF "
                head_ref = line.split()[1]

    if not repo_name or not current_ref or not head_ref:
        print(f"Error: Missing REPO, REF or HEAD_REF in '{portfile_path}'.")
        return []

    latest_commit_hash = get_latest_commit_hash(repo_name, head_ref)
    if not latest_commit_hash:
        return []
    
    if latest_commit_hash == current_ref:
        print(f"Port '{portname}' is already up to date commit hash '{current_ref}', skip")
        return []

    # Get latest SHA512 and version from GitHub
    new_sha512 = get_sha512_from_github(repo_name, latest_commit_hash)
    if not new_sha512:
        return []

    # Read version from GitHub vcpkg.json
    github_vcpkg_url = f"https://raw.githubusercontent.com/{repo_name}/{latest_commit_hash}/vcpkg.json"
    try:
        response = requests.get(github_vcpkg_url)
        response.raise_for_status()
        github_vcpkg_data = response.json()
        new_version: str = github_vcpkg_data.get("version", "").strip()
        new_port_version: int = github_vcpkg_data.get("port-version", 0)
        if not new_version:
            raise ValueError(f"Error: GitHub 'vcpkg.json' for {portname} is missing a valid 'version' field.")
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching or validating vcpkg.json from GitHub: {e}")
        return []

    current_version = vcpkg_data["version"]
    current_port_version = vcpkg_data.get("port-version", 0)
    # Check if the version has changed
    try:
        if new_version == current_version and new_port_version == current_port_version:
            print(f"Port '{portname}' has not changed version '{current_version}', or port-version '{current_port_version}', skip") 
            return []
        elif Version(new_version) < Version(current_version):
            print(f"Error: New version '{new_version}' is less than the current version '{current_version}' for {portname}.")
            return []
        elif Version(new_version) == Version(current_version) and new_port_version < current_port_version:
            print(f"Error: New port-version '{new_port_version}' is less than the current port-version '{current_port_version}' for {portname}.")
            return []
    except InvalidVersion as e:
        print(f"Error: Invalid version format for '{portname}': {e}")
        return []

    # Update portfile.cmake
    with open(portfile_path, "r") as f:
        lines = f.readlines()

    with open(portfile_path, "w", newline='\n') as f:
        for line in lines:
            if line.strip().startswith("REF"):
                line = f"    REF {latest_commit_hash}\n"
            elif line.strip().startswith("SHA512"):
                line = f"    SHA512 {new_sha512}\n"
            f.write(line)

    # Update vcpkg.json
    vcpkg_data["version"] = new_version
    vcpkg_data["port-version"] = new_port_version
    # Also update description, homepage, and license from remote vcpkg.json if present
    for field in ["description", "homepage", "license"]:
        if field in github_vcpkg_data and github_vcpkg_data[field]:
            vcpkg_data[field] = github_vcpkg_data[field]

    with open(vcpkg_json_path, "w") as f:
        json.dump(vcpkg_data, f, indent=2)
    
    if not format_vcpkg_manifest(vcpkg_json_path):
        print(f"Error formatting vcpkg.json for {portname}.")
        return []

    # Commit changes
    try:
        subprocess.run(["git", "add", portfile_path, vcpkg_json_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Updated {portname} to version {new_version}"], check=True)
        print(f"Committed updates for {portname}.")
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes for {portname}: {e}")
        return []

    # Get the local commit hash for the git-tree
    local_commit_hash = get_local_commit_hash()
    if not local_commit_hash:
        print("Error: Failed to get the local commit hash.")
        return []

    # Get the git-tree hash for the specific port folder
    port_path = os.path.join("ports", portname)
    git_tree = get_git_tree_hash(port_path, local_commit_hash)
    if not git_tree:
        print(f"Error: Failed to get git-tree hash for port '{portname}' at commit {local_commit_hash}.")
        return []

    # Update versions file and baseline.json
    return add_or_update_versions_file(portname, new_version, git_tree)
    
def get_or_create_versions_file(portname: str) -> tuple[str, dict]:
    versions_dir = "versions"
    if not os.path.isdir(versions_dir):
        os.makedirs(versions_dir)

    json_file = os.path.join(versions_dir, f"{portname[0]}-", f"{portname}.json")
    if not os.path.isfile(json_file):
        print(f"Creating new version file '{json_file}' for port '{portname}'.")
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        with open(json_file, "w", newline='\n') as f:
            json.dump({"versions": []}, f, indent=2)
    with open(json_file, "r") as f:
        return json_file, json.load(f)

def add_or_update_versions_file(portname: str, new_version: str, git_tree: str) -> list[str]:
    version_port_file, version_port_data = get_or_create_versions_file(portname)
    if "versions" not in version_port_data or not isinstance(version_port_data["versions"], list):
        print(f"Error: Invalid JSON structure in '{version_port_file}'.")
        return []

    # Check if the version already exists and bump port-version if necessary
    port_version = 0
    for version_entry in version_port_data["versions"]:
        if version_entry["version"] == new_version:
            if port_version <= version_entry["port-version"]:
                port_version = version_entry["port-version"] + 1
    # Add a new version entry
    version_port_data["versions"].insert(0, {
        "git-tree": git_tree,
        "version": new_version,
        "port-version": port_version
    })

    # Save the updated JSON file
    with open(version_port_file, "w", newline='\n') as f:
        json.dump(version_port_data, f, indent=2)
    print(f"Updated '{version_port_file}' with new version: {new_version}.")

    baseline_file, baseline_data = get_or_create_baseline()
    baseline_data["default"][portname] = {
        "baseline": new_version,
        "port-version": port_version
    }
    
    # Save the updated baseline.json
    with open(baseline_file, "w", newline='\n') as f:
        json.dump(baseline_data, f, indent=2)

    print(f"Updated 'baseline.json' for port '{portname}' with new version: {new_version}.")
    return [version_port_file, baseline_file]

def main() -> None:
    ports_dir = "ports"
    if not os.path.isdir(ports_dir):
        print(f"Error: '{ports_dir}' directory does not exist.")
        return

    updated_ports = []
    updated_files = []

    for portname in os.listdir(ports_dir):
        port_path = os.path.join(ports_dir, portname)
        if os.path.isdir(port_path):
            print(f"Processing port: {portname}")
            files = update_port(portname)
            if files:  # Only if something was updated
                updated_files.extend(files)
                updated_ports.append(portname)

    if updated_ports:
        print(f"Successfully updated ports: {', '.join(updated_ports)}")
        try:
            for file in updated_files:
                subprocess.run([
                    "git", "add",
                    file
                ], check=True)
            subprocess.run([
                "git", "commit",
                "-m", f"Updated baseline for {len(updated_ports)} port{'s' if len(updated_ports) > 1 else ''}",
                "-m", "\n".join(updated_ports)
            ], check=True)
            print("Committed version files.")
        except subprocess.CalledProcessError as commit_error:
            print(f"Error committing version files: {commit_error}")
    else:
        print("No ports were updated.")

if __name__ == "__main__":
    main()