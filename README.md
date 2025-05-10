# mw-vcpkg-registry
A vcpkg repository containing some of mwthinker's C++ repositories.

## How to use this vcpkg registry
For a vcpkg project, use it by having a `vcpkg-configuration.json` file in the root of the project, alongside the `vcpkg.json` file. The `vcpkg-configuration.json` file should look something like this:
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

### How to add a new port
1. Create a new directory in the `ports` directory with the name of the port. The name must be lowercase and contain no spaces.
2. Add a `portfile.cmake` file. The REF and SHA256 hash can be set to `-`.
3. Add a `vcpkg.json` file.
4. Add a `usage` file.
5. Commit the changes to the repository.
6. Run the `update_ports.py` script; it will fill out any missing REF and SHA256 hash with the latest version of the repository. A baseline will be created.
7. Make sure it works before pushing the commits made by you and the script.

### How to update the ports
1. Run the `update_ports.py` script; it will update the REF and SHA256 hash to the latest version of the repository, and the baseline will be updated. Only ports that have a newer commit hash or a newer version/port-version in the remote repository will be updated.
2. Make sure the ports work before pushing the commits made by the script.

## Python
This repository contains a Python script to automate the process of creating a vcpkg registry. The script is located in the `scripts` directory and can be run with the following command:

### update_registry
Updates the vcpkg registry by checking for new commits for all added ports.
```bash
python update_registry.py
```
```ps
py update_registry.py
```

### get_sha256
The script takes a URL as an argument and returns the SHA256 hash of the github repository that is used in the `portfile.cmake` file.
```bash
./get_sha512.py mwthinker/CppSdl2 7e517673cfd8021ae67962f35d4267aa74a0bac5
Constructed URL: https://github.com/mwthinker/CppSdl2/archive/7e517673cfd8021ae67962f35d4267aa74a0bac5.tar.gz
SHA512: 3c32eabe8f9e5103d167863f0ed7079f238a9676572456c575ce6434239b52eb40561cd124c69ba4680c14ed152def80118c8d77174510027b4dba890fd9cb54
```
```ps
py get_sha512.py mwthinker/CppSdl2 7e517673cfd8021ae67962f35d4267aa74a0bac5
Constructed URL: https://github.com/mwthinker/CppSdl2/archive/7e517673cfd8021ae67962f35d4267aa74a0bac5.tar.gz
SHA512: 3c32eabe8f9e5103d167863f0ed7079f238a9676572456c575ce6434239b52eb40561cd124c69ba4680c14ed152def80118c8d77174510027b4dba890fd9cb54
```
