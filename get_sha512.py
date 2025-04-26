#!/usr/bin/env python3
import argparse
from util.util import get_sha512_from_github

def main():
    parser = argparse.ArgumentParser(description="Retrieve SHA512 hash from a GitHub repository and commit hash.")
    parser.add_argument("repo_name", help="The GitHub repository name (e.g., owner/repo).")
    parser.add_argument("git_hash", help="The Git commit hash.")

    args = parser.parse_args()

    sha512 = get_sha512_from_github(args.repo_name, args.git_hash)
    if sha512:
        print(f"SHA512: {sha512}")
    else:
        print("Failed to retrieve SHA512 hash.")

if __name__ == "__main__":
    main()