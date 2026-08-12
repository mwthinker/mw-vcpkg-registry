#! /usr/bin/env python3
"""Build and run the registry's isolated local port test projects."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


def run(command: List[str], cwd: Path, env: Dict[str, str]) -> None:
    print(f"\n> {' '.join(command)}")
    subprocess.run(command, cwd=cwd, env=env, check=True)


def find_vcpkg(root_argument: Optional[str]) -> Tuple[Path, Path]:
    root: Optional[Path]
    executable: Optional[Path]

    if root_argument:
        requested = Path(root_argument).expanduser().resolve()
        executable = requested if requested.is_file() else None
        root = requested.parent if executable else requested
    else:
        root_environment = os.environ.get("VCPKG_ROOT")
        root = Path(root_environment).expanduser().resolve() if root_environment else None
        executable = None

    if executable is None and root is not None:
        executable_name = "vcpkg.exe" if os.name == "nt" else "vcpkg"
        executable = root / executable_name

    if executable is None or not executable.exists():
        found_executable = shutil.which("vcpkg")
        if found_executable is not None:
            executable = Path(found_executable).resolve()
            if root is None:
                root = executable.parent

    if executable is None or root is None or not executable.exists():
        raise RuntimeError(
            "Could not find vcpkg. Set VCPKG_ROOT or pass --vcpkg-root."
        )

    return root, executable


def manifest_version(manifest: dict) -> Tuple[str, int]:
    version_keys = ("version", "version-semver", "version-date", "version-string")
    for key in version_keys:
        if key in manifest:
            return str(manifest[key]), int(manifest.get("port-version", 0))
    raise ValueError("manifest has no supported version field")


def validate_registry(root: Path) -> None:
    ports_dir = root / "ports"
    versions_dir = root / "versions"
    baseline_path = versions_dir / "baseline.json"

    with baseline_path.open(encoding="utf-8") as file:
        baseline = json.load(file)
    baseline_ports = baseline.get("default", {})

    errors: List[str] = []
    for port_dir in sorted(path for path in ports_dir.iterdir() if path.is_dir()):
        port_name = port_dir.name
        manifest_path = port_dir / "vcpkg.json"
        portfile_path = port_dir / "portfile.cmake"
        versions_path = versions_dir / f"{port_name[0]}-" / f"{port_name}.json"

        if not manifest_path.is_file():
            errors.append(f"{port_name}: missing ports/{port_name}/vcpkg.json")
            continue
        if not portfile_path.is_file():
            errors.append(f"{port_name}: missing ports/{port_name}/portfile.cmake")
            continue

        try:
            with manifest_path.open(encoding="utf-8") as file:
                manifest = json.load(file)
            if manifest.get("name") != port_name:
                errors.append(f"{port_name}: manifest name does not match directory")
            version, port_version = manifest_version(manifest)

            with versions_path.open(encoding="utf-8") as file:
                versions = json.load(file).get("versions", [])
            if not any(
                entry.get("version") == version
                and entry.get("port-version", 0) == port_version
                for entry in versions
            ):
                errors.append(f"{port_name}: current version is missing from {versions_path}")

            baseline_entry = baseline_ports.get(port_name)
            if baseline_entry is None:
                errors.append(f"{port_name}: missing from versions/baseline.json")
            elif (
                baseline_entry.get("baseline") != version
                or baseline_entry.get("port-version", 0) != port_version
            ):
                errors.append(f"{port_name}: baseline does not match vcpkg.json")
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
            errors.append(f"{port_name}: invalid registry metadata ({error})")

    if errors:
        raise RuntimeError("Registry validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    print("Registry metadata: OK")


def check_diff(root: Path, env: Dict[str, str]) -> None:
    run(["git", "diff", "HEAD", "--check"], root, env)
    print("Git whitespace check: OK")


def find_test_projects(test_dir: Path, port_name: Optional[str]) -> List[Path]:
    if port_name:
        project = test_dir / port_name
        if not project.is_dir() or not (project / "CMakeLists.txt").is_file():
            raise RuntimeError(f"No test project found for port '{port_name}'")
        return [project]

    projects = sorted(
        path
        for path in test_dir.iterdir()
        if path.is_dir()
        and path.name not in ("build_debug", "build_release")
        and (path / "CMakeLists.txt").is_file()
    )
    if not projects:
        raise RuntimeError(f"No test projects found in {test_dir}")
    return projects


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and run isolated registry port tests using local ports."
    )
    parser.add_argument(
        "--vcpkg-root",
        help="vcpkg installation directory, or path to the vcpkg executable",
    )
    parser.add_argument(
        "--preset",
        choices=("windows", "unix"),
        help="CMake preset; defaults to windows on Windows and unix elsewhere",
    )
    parser.add_argument(
        "--port",
        help="test only the named port; omit to test all ports",
    )
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="skip registry metadata validation",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="build but do not run the test executable",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    test_dir = root / "test"
    ports_dir = root / "ports"

    try:
        vcpkg_root, vcpkg = find_vcpkg(args.vcpkg_root)
        env = os.environ.copy()
        env["VCPKG_ROOT"] = str(vcpkg_root)
        env["VCPKG_OVERLAY_PORTS"] = str(ports_dir)
        preset = args.preset or ("windows" if os.name == "nt" else "unix")

        if not args.skip_metadata:
            validate_registry(root)

        for project_dir in find_test_projects(test_dir, args.port):
            project_name = project_dir.name
            print(f"\n=== Testing {project_name} ===")
            run(
                [
                    str(vcpkg),
                    "install",
                    "--overlay-ports",
                    str(ports_dir),
                    "--no-print-usage",
                ],
                project_dir,
                env,
            )

            for configuration in ("Debug", "Release"):
                build_directory = project_dir / f"build_{configuration.lower()}"
                run(
                    [
                        "cmake",
                        "--preset",
                        preset,
                        "-S",
                        str(project_dir),
                        "-B",
                        str(build_directory),
                        "-DCMAKE_VERBOSE_MAKEFILE=1",
                        f"-DCMAKE_BUILD_TYPE={configuration}",
                    ],
                    project_dir,
                    env,
                )
                run(
                    [
                        "cmake",
                        "--build",
                        str(build_directory),
                        "--config",
                        configuration,
                    ],
                    root,
                    env,
                )

                if not args.skip_run:
                    executable = build_directory / project_name
                    if os.name == "nt":
                        executable = build_directory / configuration / f"{project_name}.exe"
                    run([str(executable)], root, env)

        check_diff(root, env)
        print("\nAll port tests passed.")
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"\nTest failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
