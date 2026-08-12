cmake_minimum_required(VERSION 3.31)
project(SignalTest LANGUAGES CXX)

add_executable(signal main.cpp)

find_package(Signal CONFIG REQUIRED)
target_link_libraries(signal PRIVATE Signal::Signal)

set_target_properties(signal PROPERTIES
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
