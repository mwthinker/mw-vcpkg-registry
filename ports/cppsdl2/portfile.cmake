vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/CppSdl2
    REF 36f4795fa348e7349bae2eb6e339b0dddd17be02
    SHA512 ceab2b34b9e0598be422dbba53ee085095fe5fed10546509d32d9f5599d9703ee23a489205de278021e5ae86abd5762e0cc166371a511a517798b8f96a72b913
    HEAD_REF master
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS_RELEASE -DFETCHCONTENT_FULLY_DISCONNECTED=OFF # ImGui is fetched, needs this to be OFF
    OPTIONS_DEBUG -DFETCHCONTENT_FULLY_DISCONNECTED=OFF # ImGui is fetched, needs this to be OFF
)

vcpkg_check_linkage(ONLY_STATIC_LIBRARY) # No export symbols is available in the dll, maybe in the future?

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME CppSdl2 CONFIG_PATH share/cmake/${PORT})

file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/include)
file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/share)

file(INSTALL ${CMAKE_CURRENT_LIST_DIR}/usage DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT})

vcpkg_install_copyright(FILE_LIST ${CURRENT_PACKAGES_DIR}/share/doc/${PORT}/LICENSE.txt)
