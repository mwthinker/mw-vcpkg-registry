vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/Signal
    REF b23addf5b3344e62a2067cbdced1a8d0fd35db9a
    SHA512 741471805ae796e2bef36eb4b230821e51b0f779a7914f36013ed56492b4b70d4801fad724dc6a489ea00997ff03c7d91f749ceb7d691ed507a8739ce11cf985
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
