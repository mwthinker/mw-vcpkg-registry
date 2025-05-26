vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO mwthinker/Calculator
    REF 577c56fb4a996c30bd773ec988c63722760c68bf
    SHA512 24620d8b64210b8309d7ffc906a4ae252464132614110f28ffc46b7e24e7335593101085d69318756fb14f5d054e8d6b55d6d11e63ccfd2042ef76cd09de08ff
    HEAD_REF master
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)

vcpkg_check_linkage(ONLY_STATIC_LIBRARY) # No export symbols is available in the dll, maybe in the future?

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(PACKAGE_NAME Calculator CONFIG_PATH share/cmake/${PORT})

file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/include)
file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/share)

file(INSTALL ${CMAKE_CURRENT_LIST_DIR}/usage DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT})

vcpkg_install_copyright(FILE_LIST ${CURRENT_PACKAGES_DIR}/share/doc/${PORT}/LICENSE.txt)
