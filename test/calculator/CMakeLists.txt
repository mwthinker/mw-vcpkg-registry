cmake_minimum_required(VERSION 3.31)
project(CalculatorTest LANGUAGES CXX)

add_executable(calculator main.cpp)

find_package(Calculator CONFIG REQUIRED)
target_link_libraries(calculator PRIVATE Calculator::Calculator)

set_target_properties(calculator PROPERTIES
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
