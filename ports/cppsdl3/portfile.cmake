vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/CppSdl3
    REF f4cf07857e0438893be13d11858c231270a3350e
    SHA512 d276a6b6354364c7cdf8e8d0c50f0f8a45b07baa0f4a2212d876b81927a21d47add3a9005036779438eb539881326d6329709fea2ca599ad325ffb11b3c2969d
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
