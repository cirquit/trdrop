## Qt Cross Platform Development

Short writeup of Windows / Linux (Ubuntu) cross platform development information with Qt

* Setup an initial repository
* Install Qt
* Install CMake (Linux)
* Install CMake (Windows)
* Install GStreamer (Linux)
* Install GStreamer (Windows)
* Install FFmpeg (Linux)
* Install FFmpeg (Windows)
* Install OpenCV 4.1 (Linux)
* Install OpenCV 4.1 (Windows)

## Setup an initial repository for Qt

## Install Qt

* Install [QtCreator](https://www.qt.io/download#)
    - I use the Qt version `5.12.2`, but I hope that any `5.*.*` version works
    - **Windows:** Check to install the correct compiler, I use `mingw_730`, the 32-bit version 
    - **Windows:** Install everything in the default installation directory -> `C:\Qt`
    -  **Windows:**Developer Options, check  `mingw730_32`
    - **Linux:** Check to install the correct compiler, I use `g++ 7.4.0`

## Install CMake (Linux)

Execute in the command line `sudo apt-get install cmake`

## Install CMake (Windows)

Use the `.msi` installer from [https://cmake.org/download/](https://cmake.org/download/). Pick the option to add CMake to the `PATH`.

## Install OpenCV (Linux)

Follow the instructions for `https://github.com/cirquit/opencv-template`. You can check if your installation works by running the examples in this template repository.

**Troubleshooting:** If the libraries are still not found after the installation, don't forget to run `sudo ldconfig -v`.

## Install OpenCV (Windows)

Install from [https://opencv.org/opencv-4-1-0.html](https://opencv.org/opencv-4-1-0.html), not the `Win Pack`, but the `Sources`. Extract the `opencv-4.1.0` directory to `C:`.

CMake Options:
```
Source code: C:/opencv-4.1.0
Where to build the binaries: C:/opencv-4.1.0/build
```

Follow the installation instructions of [https://wiki.qt.io/How_to_setup_Qt_and_openCV_on_Windows](https://wiki.qt.io/How_to_setup_Qt_and_openCV_on_Windows).

The only difference is that I created the build directory inside the opencv-dir `C:\opencv-4.1.0\build` instead a new one at `C:\opencv-build`.

My PATH environment variable for comparisson:

```
1) C:\Qt\Tools\mingw730_32\bin
2) C:\Qt\5.12.2\mingw73_32\bin
3) C:\opencv-4.1.0\build\install\x86\mingw\bin
```

> 1) is needed for CMake to get the correct compiler (gcc / g++)

> 2) is needed for the qt libraries on runtime (Qt5Gui.dll)

> 3) is possibly needed for some opencv specific stuff (TODO test this)

Pick the following flags configuration (deviating from the default configuration):

* [ ] Build_JAVA
* [ ] Build_opencv_java_bindings_generator
* [ ] Build_opencv_python_bindings_generator
* [Release] CMAKE_BUILD_TYPE
* [X] WITH_OPENGL
* [X] WITH_QT
* [ ] WITH_OPENCL_D3D11_NV

You may have to set the CMake settings multiple times, e.g. after the `WITH_QT` flag you have to set additional variables.

#### Current shortcomings

* Can't run the executable from QtCreator, need to manually locate it inside the build directory
