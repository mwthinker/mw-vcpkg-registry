vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/Calculator
    REF 6c81805bf1ed8d6be48acc21d27e78b203102bc4
    SHA512 f07f200f77014fab8d5cceaafd7762365b0dc23ae32e890626bf58d46e62122e9d522d41f9bdaa0a1da102623549d1e39234968b6e8ab9f3affb2c84bcf033ef
    HEAD_REF master
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)

vcpkg_check_linkage(ONLY_STATIC_LIBRARY) # No export symbols is available in the dll, maybe in the future?

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME "Calculator" CONFIG_PATH share/cmake/${PORT})

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

file(INSTALL "${CMAKE_CURRENT_LIST_DIR}/usage" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")

vcpkg_install_copyright(FILE_LIST "${CURRENT_PACKAGES_DIR}/share/doc/Calculator/LICENSE.txt")
