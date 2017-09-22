project(CAFReusePackage)
cmake_minimum_required(VERSION 3.5.1)

if(NOT APPLE AND NOT WIN32)
    set(EXTRA_FLAGS "-pthread")
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_FLAGS "-std=c++11 ${CMAKE_CXX_FLAGS} ${EXTRA_FLAGS}")

add_executable(caf-test
             tests/libcaf_io/test/basp.cpp
             tests/libcaf_test/src/caf-test.cpp)

target_include_directories(caf-test PUBLIC tests/libcaf_test)

target_link_libraries(caf-test CONAN_PKG::caf ${EXTRA_LIBS})
