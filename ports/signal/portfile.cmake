vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/Signal
    REF 6c877fdc86219daf62faf7a51416b09a70bc4628
    SHA512 fe129facaa44940e2c028ca1d22db5e47e72531bd85b8fc967ef7eff2ea4dca571a13f87562acfaec49a185cff00de9ac9981cd066f16111079a80cf046a2b93
    HEAD_REF master
)
vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)
vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME "Signal" CONFIG_PATH share/cmake/${PORT})

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

file(INSTALL "${CMAKE_CURRENT_LIST_DIR}/usage" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}")

vcpkg_install_copyright(FILE_LIST "${CURRENT_PACKAGES_DIR}/share/doc/Signal/LICENSE.txt")
