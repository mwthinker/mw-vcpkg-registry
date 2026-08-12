cmake_minimum_required(VERSION 3.31)
project(CppSdl2Test LANGUAGES CXX)

add_executable(cppsdl2 main.cpp)

find_package(CppSdl2 CONFIG REQUIRED)
target_link_libraries(cppsdl2 PRIVATE CppSdl2::CppSdl2)

set_target_properties(cppsdl2 PROPERTIES
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
