vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/CppSdl3
    REF 36ed10cb1318c0b9a3922c262bc750c23bbedba7
    SHA512 35ae22e4f8e32dc70029fdb8f6cb1b5ab23fe1ee0425b77be414f2d6e680a1ce3590f83cabb78e6d98669c9b1868ff209db7525fccfba34a7d23618c9177d783
    HEAD_REF master
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS_RELEASE -DFETCHCONTENT_FULLY_DISCONNECTED=OFF # ImGui is fetched, needs this to be OFF
    OPTIONS_DEBUG -DFETCHCONTENT_FULLY_DISCONNECTED=OFF # ImGui is fetched, needs this to be OFF
)

vcpkg_check_linkage(ONLY_STATIC_LIBRARY) # No export symbols is available in the dll, maybe in the future?

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME CppSdl3 CONFIG_PATH share/cmake/${PORT})

file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/include)
file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/share)

file(INSTALL ${CMAKE_CURRENT_LIST_DIR}/usage DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT})

vcpkg_install_copyright(FILE_LIST ${CURRENT_PACKAGES_DIR}/share/doc/${PORT}/LICENSE.txt)
