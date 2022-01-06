## Qt Cross Platform Development

Short writeup of Windows / Linux (Ubuntu) cross platform development information with Qt

* Setup an initial repository
* Install Qt 5.15.2
* Install CMake (Linux)
* Install CMake (Windows)
* Compile OpenCV 4.5.1 (Linux)
* Compile OpenCV 4.5.1 (Windows)
<!-- we're only using qimage save, comment these for now
* Install FFmpeg (Linux)
* Install FFmpeg (Windows)
-->
## Setup an initial repository

**Linux:**

**Windows:**

1. Install [Git](https://git-scm.com/download/win)

2. With your terminal of chioce and working directory, run `git clone https://github.com/cirquit/trdrop.git`

## Install Qt

* Install [QtCreator](https://www.qt.io/download#)
 - Qt version `5.15.2`
 - **Windows:**
 - Check to install the correct compiler, I use `mingw_810`, the 64-bit version 
 - Developer Options, check `mingw810_64`
 - Create an Environment Variable `Qt_Install` pointing to your downloaded Qt directory. i.e `C:\Qt`
 - **Linux:**
 - Check to install the correct compiler, I use `g++ 7.4.0`

## Install CMake (Linux)

Execute in the command line `sudo apt-get install cmake`

## Install CMake (Windows)

Use the `.msi` installer from https://cmake.org/download/. Pick the option to add CMake to the `PATH`.

## Compile OpenCV (Linux)

Follow the instructions for `https://github.com/cirquit/opencv-template`. You can check if your installation works by running the examples in this template repository.

**Troubleshooting:** If the libraries are still not found after the installation, don't forget to run `sudo ldconfig -v`.

## Compile OpenCV (Windows)

1. Download OpenCV version 4.5.1 from https://opencv.org/releases/, not the `Win Pack`, but the `Sources`. Extract the `opencv-4.5.1` directory to somewhere on your computer.

2. Create an Environment Variable `OpenCV_DIR` pointing to your extracted OpenCV source code. i.e `Z:\3rdparty\opencv-4.5.1`

2.1. Add the following folders to your path

```
%Qt_Install%\Tools\mingw810_64\bin
%Qt_Install%\5.15.2\mingw81_64\bin
```

3. CMake Options:

```
Source code: (your opencv directory)
Where to build the binaries: (your opencv directory)/build_64
```

Then click Configure, choose the following settings:

```
Specify the generator for this project: MinGW Makefiles
Specify native compilers, next
Compilers C:   (your Qt installation)\Tools\mingw810_64\bin\gcc.exe
Compilers C++: (your Qt installation)\Tools\mingw810_64\bin\g++.exe
```

Click Finish.

4. Pick the following flags configuration (deviating from the default configuration):

```
[ ] Build_JAVA
[ ] Build_opencv_java_bindings_generator
[ ] Build_opencv_python_bindings_generator
CMAKE_BUILD_TYPE: Release
[X] WITH_OPENGL
[X] WITH_QT
[ ] WITH_OPENCL_D3D11_NV
```

5. Click Generate

6. Once finished, with your terminal of choice, cd into `%OpenCV_DIR%/build_64`

7. Run the following commands:

```
mingw32-make -j 8
mingw32-make install
```

## Running Trdrop with Qt Creator (Windows)

1. Open `trdrop.pro` set config to MinGW 8.1.0 64 Bit, Build Config to Release.

2. With your terminal of chioce, go to the release directory of the application in my case `C:\git\trdrop\build-trdrop-Desktop_Qt_5_15_2_MinGW_64_bit-Release\release`

2. Execute the following commands:

```
copy %OpenCV_Dir%\build_64\install\x64\mingw\bin\*.dll .
copy %Qt_Install%\Tools\mingw810_64\bin\*.dll .
windeployqt.exe --qmldir ..\..\trdrop .
```

3. Running after compiling from Qt Creator should work. You can find the built binaries in `trdrop_root\build-trdrop-Desktop_Qt_5_15_2_MinGW_64_bit-Release\release`
