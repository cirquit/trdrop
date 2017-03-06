cmake_minimum_required(VERSION 3.5.2)
project(trdrop_v)

# static library of trdrop
set (PROJECT_LINK_LIBS libtrdrop.a )
link_directories( ../trdrop_lib/build )
include_directories( ../trdrop_lib/include )

# headers lie in the folder "include"
include_directories(include)

# set every src/*.cpp file as source
file(GLOB SOURCES "src/*.cpp")

add_executable(trdrop_v ${SOURCES})
target_link_libraries(trdrop_v ${PROJECT_LINK_LIBS})