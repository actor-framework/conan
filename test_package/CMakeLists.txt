project(CAFReusePackage)
cmake_minimum_required(VERSION 3.5.1)

if(NOT APPLE AND NOT WIN32)
  set(EXTRA_FLAGS "-pthread")
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_FLAGS "-fPIC -std=c++11 ${EXTRA_FLAGS}")

add_executable(caf-test
             tests/libcaf_io/test/basp.cpp
             tests/libcaf_test/src/caf-test.cpp)

target_include_directories(caf-test PUBLIC tests/libcaf_test ${CONAN_INCLUDE_DIRS})

target_link_libraries(caf-test ${CONAN_LIBS})
