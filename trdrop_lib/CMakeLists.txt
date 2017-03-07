cmake_minimum_required(VERSION 2.8.7)
project(trdrop_lib)
set(CMAKE_BUILD_TYPE Release)

# set flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")

# headers lie in the folder "include"
include_directories(include)

# set every src/*.cpp file as source
file(GLOB SOURCES "src/*.cpp")

# generate shared library from sources
# add_library(trdrop SHARED ${SOURCES})

# generate static library from sources
add_library(trdrop STATIC ${SOURCES})

# use "sudo make install" to install the library to location "/usr/lib"
install(TARGETS trdrop DESTINATION /usr/lib)
