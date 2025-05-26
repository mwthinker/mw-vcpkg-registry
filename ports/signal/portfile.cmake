vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/Signal
    REF 86e486fe480b1019a95942cb887e9ebecd62b09d
    SHA512 e3f8a33ab9445b8bf14d0219b5ea0074f9ffe9d654de70c4408d0d009f789f2fa5b2a09b4c2fdafa64c29fcf3fc20435c5b3489d8cabf67c941223ce07b3d646
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
