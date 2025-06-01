vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/Signal
    REF ec691ee062b79dd4ca084f821ce9500c14a897f9
    SHA512 7801d439157984a5ac6619e47fb548dd3b64d00e352eea7236ef59f4721526278bc5d6d3e841b2a37ed69c31a6f9a7da73c0b6af925ed580de78a4998eb89ea2
    HEAD_REF master
)
vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)
vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME "Signal" CONFIG_PATH share/cmake/${PORT})

file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/include)
file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/share)

file(INSTALL ${CMAKE_CURRENT_LIST_DIR}/usage DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT})

vcpkg_install_copyright(FILE_LIST ${CURRENT_PACKAGES_DIR}/share/doc/${PORT}/LICENSE.txt)
