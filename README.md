mw-vcpkg-registry [![CI build](https://github.com/mwthinker/mw-vcpkg-registry/actions/workflows/ci.yml/badge.svg)](https://github.com/mwthinker/mw-vcpkg-registry/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
======
A vcpkg registry containing some of mwthinker's C++ repositories.

## Usage

Add a `vcpkg-configuration.json` file next to your `vcpkg.json`:
```json
{
  "default-registry": {
    "kind": "git",
    "baseline": "d8ad13c401b30c2836d00b8923c9127f05f591c7",
    "repository": "https://github.com/microsoft/vcpkg"
  },
  "registries": [
    {
      "kind": "git",
      "baseline": "a5390764a8ebc4b9a1b50000ae844bf456126124",
      "repository": "https://github.com/mwthinker/mw-vcpkg-registry.git",
      "packages": [
        "cppsdl2", "signal", "calculator"
      ]
    }
  ]
}
```

---

## Adding or Updating Ports

**Add a new port:**
1. Create a lowercase, space-free directory in `ports`.
2. Add `portfile.cmake` (REF and SHA256 can be `-`), `vcpkg.json`, and `usage`.
3. Commit your changes.
4. Run `update_ports.py` to fill in missing info and create a baseline.
5. Test before pushing.

**Update ports:**
1. Run `update_ports.py` to update REF, SHA256, and the baseline for changed ports.
2. Test before pushing.

---

## Testing Ports

- Update `CMakeLists.txt`, `vcpkg-configuration.txt`, and `vcpkg.json` with the new/updated port.
- GitHub Actions will build and run the binary.

---

## Python Scripts

- **update_registry:** Checks for new commits in all ports and updates the registry.
  - Bash: `./update_registry.py`
  - PowerShell: `py update_registry.py`
- **get_sha256:** Returns the SHA256 hash for a given GitHub repo/version.
  - Bash: `./get_sha512.py mwthinker/CppSdl2 <commit>`
  - PowerShell: `py get_sha512.py mwthinker/CppSdl2 <commit>`
- **bump-port-version:** Increments the version of a port and updates the SHA256 hash.
  - Bash: `./bump_port_version.py --port cppsdl2`
  - PowerShell: `py bump_port_version.py --port cppsdl2`

---

## License

MIT License - see the [LICENSE](LICENSE) file for details.