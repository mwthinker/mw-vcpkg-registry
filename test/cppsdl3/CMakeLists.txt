cmake_minimum_required(VERSION 3.31)
project(CppSdl3Test LANGUAGES CXX)

add_executable(cppsdl3 main.cpp)

find_package(CppSdl3 CONFIG REQUIRED)
target_link_libraries(cppsdl3 PRIVATE CppSdl3::CppSdl3)

set_target_properties(cppsdl3 PROPERTIES
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
