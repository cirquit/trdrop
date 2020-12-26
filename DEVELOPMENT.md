## Qt Cross Platform Development

Short writeup of Windows / Linux (Ubuntu) cross platform development information with Qt

* Setup an initial repository
* Install Qt
* Install CMake (Linux)
* Install CMake (Windows)
* Install FFmpeg (Linux)
* Install FFmpeg (Windows)
* Compile OpenCV 4.1 (Linux)
* Compile OpenCV 4.1 (Windows)

## Setup an initial repository for Qt

## Install Qt

* Install [QtCreator](https://www.qt.io/download#)
    - I use the Qt version `5.12.2`, but I hope that any `5.*.*` version works
    - **Windows:** Check to install the correct compiler, I use `mingw_810`, the 64-bit version 
    - **Windows:** Install everything in the default installation directory -> `C:\Qt`
    - **Windows:** Developer Options, check `mingw810_64`
    - **Linux:** Check to install the correct compiler, I use `g++ 7.4.0`

## Install CMake (Linux)

Execute in the command line `sudo apt-get install cmake`

## Install CMake (Windows)

Use the `.msi` installer from [https://cmake.org/download/](https://cmake.org/download/). Pick the option to add CMake to the `PATH`.

## Install OpenCV (Linux)

Follow the instructions for `https://github.com/cirquit/opencv-template`. You can check if your installation works by running the examples in this template repository.

**Troubleshooting:** If the libraries are still not found after the installation, don't forget to run `sudo ldconfig -v`.

## Install OpenCV (Windows)

Install from [https://opencv.org/releases/](https://opencv.org/releases/), not the `Win Pack`, but the `Sources`. Extract the `opencv-4.5.1` directory to `C:`.

CMake Options:
```
Source code: C:/opencv-4.5.1
Where to build the binaries: C:/opencv-4.5.1/build_64
```

Follow the installation instructions of [https://wiki.qt.io/How_to_setup_Qt_and_openCV_on_Windows]().

The differences to that tutorial:
* I created the build directory inside the opencv-dir `C:\opencv-4.1.0\build_64` instead a new one at `C:\opencv-build`
* Using the 64 bit compilation because of the RAM restriction with 32 bit. 32 bit compilation works out of the box if the PATH variable is set accordingly + 64 is replaced with 86 or 32 in the paths

My PATH environment variable for comparisson:

```
1) C:\Qt\Tools\mingw810_64\bin
2) C:\Qt\5.12.2\mingw810_64\bin
3) C:\opencv-4.5.1\build\install\x64\mingw\bin
```

> 1) is needed for CMake to get the correct compiler (gcc / g++)

> 2) is needed for the qt libraries on runtime (Qt5Gui.dll)

> 3) is possibly needed for some opencv specific stuff (with 32bit program runs from QtCreator with this, 64 doesn't seem to work)

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

* Can't run the executable from QtCreator, need to manually locate it inside the build directory if compiled with 64-bit
