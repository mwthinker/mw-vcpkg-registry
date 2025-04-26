import subprocess
import os
import platform
import hashlib
import requests

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