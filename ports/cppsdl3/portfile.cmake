vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/CppSdl3
    REF b6f5f033701872a6354e19048b3cea2f095ceaa3
    SHA512 aeceaa19b3d6adcd84f8e6510ba05d681e3fbd176eca4c96dd44580ea80bcce759c0ad7c286f2afaefd3fc1a0a88d50b2de9c3297e14d44ed13648e978c284ec
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
