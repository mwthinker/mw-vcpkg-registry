import json
import subprocess
import os
import platform
import hashlib
import requests
from typing import Optional, List, Tuple, Dict

def get_vcpkg_executable() -> str:
    vcpkg_root = os.environ.get("VCPKG_ROOT")
    if not vcpkg_root:
        raise EnvironmentError("VCPKG_ROOT environment variable is not set.")
    
    vcpkg_executable = os.path.join(vcpkg_root, "vcpkg.exe" if platform.system() == "Windows" else "vcpkg")
    if not os.path.isfile(vcpkg_executable):
        raise FileNotFoundError(f"Vcpkg executable not found at {vcpkg_executable}.")
    return vcpkg_executable

def format_vcpkg_manifest(vcpkg_json_path: str) -> bool:
    try:
        vcpkg_executable = get_vcpkg_executable()

        # Run the vcpkg command
        subprocess.run([vcpkg_executable, "format-manifest", vcpkg_json_path], check=True)
        print(f"Formatted manifest: {vcpkg_json_path}")
        return True
    except FileNotFoundError:
        print("Error: 'vcpkg' executable not found. Ensure VCPKG_ROOT is set correctly.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error formatting manifest {vcpkg_json_path}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while formatting manifest {vcpkg_json_path}: {e}")
        return False

def get_sha512_from_github(repo_name: str, git_hash: str) -> str:
    url = f"https://github.com/{repo_name}/archive/{git_hash}.tar.gz"
    print(f"Constructed URL: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        sha512_hash = hashlib.sha512()
        for chunk in response.iter_content(chunk_size=8192):
            sha512_hash.update(chunk)
        return sha512_hash.hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""

def run_vcpkg_add_new_ports() -> None:
    try:
        vcpkg_executable = get_vcpkg_executable()

        subprocess.run(
            [vcpkg_executable, "--x-builtin-ports-root=./ports", "--x-builtin-registry-versions-dir=./versions", "x-add-version", "--all", "--verbose"],
            check=True
        )
        print("vcpkg command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running vcpkg command: {e}")

def load_and_validate_vcpkg_json(vcpkg_json_path: str) -> dict:
    """
    Validate that a vcpkg.json file exists and contains a valid version.
    """
    if not os.path.isfile(vcpkg_json_path):
        raise FileNotFoundError(f"Error: Missing 'vcpkg.json' at {vcpkg_json_path}.")

    with open(vcpkg_json_path, "r") as f:
        vcpkg_data = json.load(f)

    if "version" not in vcpkg_data or not isinstance(vcpkg_data["version"], str) or not vcpkg_data["version"].strip():
        raise ValueError(
            f"Error: 'vcpkg.json' is missing the 'version' field, it is not a string, or it is empty at {vcpkg_json_path}."
        )

    return vcpkg_data

def get_or_create_baseline() -> Tuple[str, Dict]:
    """Get or create baseline.json file."""
    versions_dir = "versions"
    if not os.path.isdir(versions_dir):
        os.makedirs(versions_dir)
    
    baseline_file = os.path.join(versions_dir, "baseline.json")
    if not os.path.isfile(baseline_file):
        print(f"Creating new 'baseline.json' file in '{versions_dir}' directory.")
        with open(baseline_file, "w", newline='\n') as f:
            json.dump({"default": {}}, f, indent=2)
    with open(baseline_file, "r") as f:
        return baseline_file, json.load(f)
    
def get_git_tree_hash(port_path: str, commit_hash: str) -> Optional[str]:
    """Get the git-tree hash for a specific commit in the local repository for a specific port folder."""
    try:
        # Convert backslashes to forward slashes for Git compatibility
        git_friendly_port_path = port_path.replace('\\', '/')
        
        result = subprocess.run(
            ["git", "rev-parse", f"{commit_hash}:{git_friendly_port_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting git-tree hash for commit {commit_hash} in {port_path}: {e}")
        return None