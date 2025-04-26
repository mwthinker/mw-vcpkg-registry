# mw-vcpkg-registry
A vcpkg repository containing mwthinkers C++ repos.

## Python
This repository contains a Python script to automate the process of creating a vcpkg registry. The script is located in the `scripts` directory and can be run with the following command:

### update_registry
```bash
python update_registry.py
```
```ps
py update_registry.py
```
The script reads the the `ports` directory and if any githup repository has a newer hash then current REF hash in `portfile.cmake` it will update the file and the corresponding `vcpkg.json` file. If github repository version in it's vcpkg.json is the same only the port version will be bumped. A commit will all ports changes will be made.

The next step is to update the baseline with the newer versions of the ports. A commit will then be made.

If manually adding a new port just att the folder under ports with correct files and then run the script.

### get_sha256
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
The script takes a URL as an argument and returns the SHA256 hash of the file at that URL. This can be useful for verifying the integrity of files downloaded from the internet.
