cmake_minimum_required(VERSION 2.8.7)
project(trdrop_c)

# set flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")

# static library of trdrop
set (PROJECT_LINK_LIBS libtrdrop.a )
link_directories( ../trdrop_lib/build )
include_directories( ../trdrop_lib/include )

# headers lie in the folder "include"
include_directories(include)

# set every src/*.cpp file as source
file(GLOB SOURCES "src/*.cpp")

add_executable(trdrop_c ${SOURCES})
target_link_libraries(trdrop_c ${PROJECT_LINK_LIBS})