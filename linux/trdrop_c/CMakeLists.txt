cmake_minimum_required(VERSION 2.8.7)
project(trdrop_c)

##################################
##          trdrop_c            ##
##################################

# set flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -lavtranscoder")
#set (CMAKE_CXX_COMPILER "/usr/bin/x86_64_w64-mingw32-g++")
#set (CMAKE_C_COMPILER "/usr/bin/x86_64_w64-mingw32-gcc")
# static library of trdrop
set (PROJECT_LINK_LIBS trdrop )
link_directories( ../trdrop_lib/build )
include_directories( ../trdrop_lib/include )


# include c++ wrapper for ffmpeg
# link_directories( ../ext/avTranscoder/build )
# include_directories( ../ext/avTranscoder/src/AvTranscoder )

# headers lie in the folder "include"
include_directories(include)

# set every src/*.cpp file as source
file(GLOB SOURCES "src/*.cpp")

add_executable(trdrop_c ${SOURCES})
target_link_libraries(trdrop_c ${PROJECT_LINK_LIBS})

##################################
##        trdrop_c_tests        ##
##################################

# create an interface for catch
add_library(Catch INTERFACE)

# tell cmake where the header of catch lies
target_include_directories(Catch INTERFACE ../ext/)

# tell cmake where the tests lie
file(GLOB TEST_SOURCES "tests/*.cpp")
add_executable(trdrop_c_tests ${TEST_SOURCES})

# create the test
enable_testing()
target_link_libraries(trdrop_c_tests Catch)
add_test(NAME Test COMMAND trdrop_c_tests)

