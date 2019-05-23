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

Setup a `.gitignore` file

```bash
> cat .gitignore
qt-opencv.pro.user*
qt-opencv.pro.user
```

## Install Qt

Install the Qt Creator from ... Install the packages mingw32 (**32bit** and **64bit**) both in Tools and Qt 5.12.2 subdirectory

## Install CMake (Linux)

Execute in the command line `sudo apt-get install cmake`

## Install CMake (Windows)

Use the `.msi` installer from [https://cmake.org/download/](https://cmake.org/download/). Pick the option to add CMake to the `PATH`.

## Install GStreamer (Linux)

## Install GStreamer (Windows)

Install the 64 bit mingw `.msi` from [https://gstreamer.freedesktop.org/data/pkg/windows/1.15.2/](https://gstreamer.freedesktop.org/data/pkg/windows/1.15.2/), e.g `gstreamer-1.0-mingw-x86_64-1.15.2.msi` **and** the according `devel` package, e.g `gstreamer-1.0-devel-mingw-x86_64-1.15.2.msi`.

Use the `Typical` install option. This installs the binary, library and headers to `C:\gstreamer`

## Install FFmpeg (Linux)

## Install FFmpeg (Windows)

Download the installer from [here](https://ffmpeg.zeranoe.com/builds/). Pick the Version `4.1.1`, Windows 64-bit, static **and** dev, extract both in the same directory at `C:\ffmpeg`

## Install OpenCV (Linux)

Follow the instructions for `https://github.com/cirquit/opencv-template`. You can check if your installation works by running the examples in this template repository.

**Troubleshooting:** If the libraries are still not found after the installation, don't forget to run `sudo ldconfig -v`.

## Install OpenCV (Windows)

Install from [https://opencv.org/opencv-4-1-0.html](https://opencv.org/opencv-4-1-0.html), not the `Win Pack`, but the `Sources`. Extract the `opencv-4.1.0` directory to `C:`.

Follow the installation instructions of [https://wiki.qt.io/How_to_setup_Qt_and_openCV_on_Windows](https://wiki.qt.io/How_to_setup_Qt_and_openCV_on_Windows).

Don't forget the PATH variable, otherwise you will get a problem while generating the Makefile in CMake.

Pick the following flags configuration (deviating from the default configuration):

* [ ] Build_JAVA
* [ ] Build_opencv_java_bindings_generator
* [ ] Build_opencv_python_bindings_generator
* [X] Build_opencv_world
* [Release] CMAKE_BUILD_TYPE
* [X] WITH_OPENGL
* [X] WITH_QT
* Check if the gstreamer libraries got found -> should look like this


#### Problems

> CMake Error at modules/videoio/cmake/detect_ffmpeg.cmake:16 (include):
  include could not find load file:

