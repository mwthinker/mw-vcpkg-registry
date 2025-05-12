cmake_minimum_required(VERSION 3.31)
project(TestProject
	DESCRIPTION
		"Description"
	LANGUAGES
		CXX
)

add_executable(TestProject
	main.cpp

	CMakePresets.json
	vcpkg.json
	vcpkg-configuration.json
)

set_property(GLOBAL PROPERTY USE_FOLDERS On)
set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT TestProject)

# Add all ports to check that they compile
find_package(CppSdl2 CONFIG REQUIRED)
find_package(Signal CONFIG REQUIRED)
find_package(Calculator CONFIG REQUIRED)

target_link_libraries(TestProject
	PUBLIC
		CppSdl2::CppSdl2
		Signal::Signal
		Calculator::Calculator
)

set_target_properties(TestProject
	PROPERTIES
		CXX_STANDARD 23
		CXX_STANDARD_REQUIRED YES
		CXX_EXTENSIONS NO
)
