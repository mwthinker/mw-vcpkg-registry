#!/usr/bin/env python3
import argparse
import os
import json
import subprocess
from typing import Optional

from util.util import get_sha512_from_github, format_vcpkg_manifest, run_vcpkg_add_new_ports

def replace_hash_in_portfile(portname: str, new_ref: str, new_sha512: str) -> None:
    portfile_path = os.path.join("ports", portname, "portfile.cmake")
    vcpkg_json_path = os.path.join("ports", portname, "vcpkg.json")

    if not os.path.isfile(portfile_path):
        print(f"Error: 'portfile.cmake' not found in the '{portname}' directory.")
        return

    with open(portfile_path, "r") as f:
        lines = f.readlines()

    with open(portfile_path, "w") as f:
        for line in lines:
            if line.strip().startswith("REF"):
                line = f"    REF {new_ref}\n"
            elif line.strip().startswith("SHA512"):
                line = f"    SHA512 {new_sha512}\n"
            f.write(line)

    print(f"Updated 'portfile.cmake' with REF: {new_ref} and SHA512: {new_sha512}.")

    # Format the vcpkg.json file after any modifications
    if not format_vcpkg_manifest(vcpkg_json_path):
        print(f"Warning: Failed to format 'vcpkg.json' for port '{portname}'. Please check the file manually.")

def check_staged_files() -> None:
    try:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        if result.stdout.strip():
            raise Exception("Error: There are already staged files. Aborting git commit.")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error checking staged files: {e}")

def commit_changes(portname: str, version: str, json_file: str) -> None:
    versions_dir = "versions"
    try:
        # Check if there are already staged files
        check_staged_files()

        subprocess.run(
            ["git", "add", json_file, 
             os.path.join("ports", portname, "portfile.cmake"), 
             os.path.join(versions_dir, "baseline.json")],
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"Replaced port {portname} {version}"],
            check=True
        )
        print("Git commit created successfully.")
    except Exception as e:
        print(e)

def commit_additional_files(portname: str, json_file: str) -> None:
    versions_dir = "versions"
    commit = input(f"Do you want to commit the updated {portname}.json and baseline.json files? (yes/no): ").strip().lower()
    if commit == "yes":
        try:
            # Check if there are already staged files
            check_staged_files()

            subprocess.run(
                ["git", "add", json_file, os.path.join(versions_dir, "baseline.json")],
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Updated version files for port {portname}"],
                check=True
            )
            print("Git commit for version files created successfully.")
        except Exception as e:
            print(e)

def remove_highest_version(portname: str) -> None:
    versions_dir = "versions"
    json_file: Optional[str] = None

    # Search for the <portname>.json file
    for root, _, files in os.walk(versions_dir):
        for file in files:
            if file == f"{portname}.json":
                json_file = os.path.join(root, file)
                break
        if json_file:
            break

    if not json_file:
        print(f"Error: '{portname}.json' not found in the '{versions_dir}' directory.")
        return

    # Load the JSON file
    with open(json_file, "r") as f:
        data = json.load(f)

    if "versions" not in data or not isinstance(data["versions"], list):
        print(f"Error: Invalid JSON structure in '{json_file}'.")
        return

    # Find and remove the block with the highest version number
    highest_version = max(data["versions"], key=lambda x: x["version"])
    data["versions"].remove(highest_version)

    # Save the updated JSON file
    with open(json_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Removed the block with the highest version: {highest_version['version']} from '{json_file}'.")

    # Update baseline.json
    baseline_file = os.path.join(versions_dir, "baseline.json")
    if not os.path.isfile(baseline_file):
        print(f"Error: 'baseline.json' not found in the '{versions_dir}' directory.")
        return

    with open(baseline_file, "r") as f:
        baseline_data = json.load(f)

    if "default" in baseline_data and portname in baseline_data["default"]:
        baseline_entry = baseline_data["default"][portname]
        if baseline_entry["baseline"] == highest_version["version"]:
            del baseline_data["default"][portname]

            # Save the updated baseline.json
            with open(baseline_file, "w") as f:
                json.dump(baseline_data, f, indent=2)

            print(f"Removed the block for '{portname}' with baseline '{highest_version['version']}' from 'baseline.json'.")
        else:
            print(f"No matching baseline found for '{portname}' in 'baseline.json'.")
    else:
        print(f"'{portname}' not found in 'baseline.json'.")

    commit = input("Do you want to do a git commit of the changes? (yes/no): ").strip().lower()
    if commit == "yes":
        commit_changes(portname, highest_version["version"], json_file)

    run_vcpkg_add_new_ports()

    commit_additional_files(portname, json_file)

def run(args: argparse.Namespace) -> None:
    ports_dir = "ports"
    if not os.path.isdir(ports_dir):
        print(f"Error: '{ports_dir}' directory does not exist.")
        return

    if args.portname not in os.listdir(ports_dir):
        print(f"Error: Port '{args.portname}' does not exist in the '{ports_dir}' directory.")
        return

    portfile_path = os.path.join(ports_dir, args.portname, "portfile.cmake")
    if not os.path.isfile(portfile_path):
        print(f"Error: 'portfile.cmake' not found in the '{args.portname}' directory.")
        return

    repo_name: Optional[str] = None
    with open(portfile_path, "r") as portfile:
        for line in portfile:
            if "REPO" in line:
                repo_name = line.split()[1]
                print(f"Found REPO: {repo_name}")
                break
        else:
            print("Error: REPO not found in 'portfile.cmake'.")
            return

    hash_value = get_sha512_from_github(repo_name, args.git_hash)
    if not hash_value:
        print("Error: Failed to fetch SHA512 hash from GitHub.")
        return

    proceed = input("Do you want to update the port? (yes/no): ").strip().lower()
    if proceed == "yes":
        replace_hash_in_portfile(args.portname, args.git_hash, hash_value)
        remove_highest_version(args.portname)
        print("SUCCESS")
    else:
        print("Aborted. No changes made.")

    print(f"Running with portname: {args.portname}")
    if args.replace:
        print("Replace flag is set.")
    print(f"Using git hash: {args.git_hash}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Vcpkg registry helper script")
    parser.add_argument("portname", help="Name of the vcpkg port (folder name in the ports directory)")
    parser.add_argument("-r", "--replace", action="store_true", help="replacing the port")
    parser.add_argument("-g", "--git-hash", required=True, help="Git hash of the repository")
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
