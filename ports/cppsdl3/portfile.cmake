vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/CppSdl3
    REF 7c09d0d77516445da3a5f2fcba07a4c0a4b187e7
    SHA512 8fe78040a0b726d154f6af9d7743451d43c5c2d40a71e8cf79307510c847e6cdef2779b301ee25ab3d0f9766c2111b39be9b4b1b91df033a5fdf5b105c020cba
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
