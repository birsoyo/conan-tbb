project(test_package)
cmake_minimum_required(VERSION 3.11)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

file(GLOB SOURCE_FILES *.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} CONAN_PKG::tbb)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
