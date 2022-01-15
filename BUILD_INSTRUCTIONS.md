# Build Instructions

How to build trdrop locally on Debian Linux and Windows. We will:

* Install the Qt Creator Framework and Qt `5.15.2`
* Install Git
* Install CMake
* Install/Build `ffmpeg`
* Clone the repository
* Setup Qt Creator to build correctly
* (Optional) Package it as `.AppImage` for Linux or `.zip` for Windows

### General

1. [Download Qt Creator](https://www.qt.io/download-qt-installer)
    * When prompted for build kits, pick Qt 5.12.2 and the following compiler
    * **Linux**: `g++ 7.4.0`
    * **Windows**: `mingw810_64`
        - Create an environment variable `Qt_Install` with the path of your Qt directory, e.g., `C:\Qt`
2. Download Git
    * **Linux**: `sudo apt install git`
    * **Windows**: [Download here](https://git-scm.com/download/win)
3. Download CMake
    * **Linux**: `sudo apt install cmake` 
    * **Windows**: [Download here](https://cmake.org/download/), pick the option to add the executable to the PATH environment variable
    
### FFMPEG

**Windows**

There are prebuild libraries by GyanD to be downloaded into your preferred location [from here](https://github.com/GyanD/codexffmpeg/releases/download/4.4.1/ffmpeg-4.4.1-full_build-shared.7z). We use the 4.4.1 build.

Download them anywhere, extract them and create a new environment variable `FFMPEG_SOURCE` which points to the actual directory with the `include` and `lib` folders.
Example:
```
C:\ffmpeg-4.4.1-full_build-shared.7z
# extract it to the `ffmpeg` directory
C:\ffmpeg\ffmpeg-4.4.1-full_build-shared\
```

If extracting with WinRAR, there is a second directory created, so `FFMPEG_SOURCE` should point to `C:\ffmpeg\ffmpeg-4.4.1-full_build-shared`.

---

**Linux**

We will have to compile ffmpeg manually, but luckily the process is mostly copying commands for your particular distribution.

Please follow [the official guidelines carefully](https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu).

Our current compilation flags are described in the [github actions script for linux](.github/workflows/ci-linux64.yml).

After installing ffmpeg, please set the `FFMPEG_SOURCE` environment variable to point to the `include` and `lib` folders, e.g., `$HOME/Documents/libs/ffmpeg/build`

### Set up the repository

1. Open up your command line/git bash:

```
> git clone https://github.com/cirquit/trdrop
```

2. Open up Qt Creator and open up the `trdrop/trdrop/trdrop.pro` project file.
3. Navigate to `Projects -> Desktop Qt 5.15.2 -> Build`
 3.1 Enable shadow build
 3.2 Build directory `<your-trdrop-directory>/shadow-build`, e.g., `$HOME/Documents/github-repos/trdrop/shadow-build`
4. Go back to `Edit`
 4.1 Click on the top-level `trdrop` project and select `Run qmake`
 4.2 Now you should see a message in the `General Messages` tab on the bottom with the `Destination Path`, e.g. `Project MESSAGE: Destination path: linux/gcc/x64/debug`
 4.3 Now you can build both the `trdrop-tests` and `trdrop-ui` project in Debug or Profile mode

Note that you can only run the programs via the Qt Creator GUI and not when navigating to the command line.

This is because we build our library locally (`trdrop-lib`) and the system does not add it to the general linker path.
To run the program on linux without actually installing it globally, you need to updated the `LD_LIBRARY_PATH`:

```bash
~/Documents/github-repos/trdrop/build/linux/gcc/x64/debug> LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH ./trdrop-ui
```

**Build from the command line - Linux** 

```bash
trdrop> mkdir shadow-build
trdrop> cd shadow-build
trdrop/shadow-build> qmake ../trdrop/trdrop.pro -config release
trdrop/shadow-build> make
```

Now the build directory should have been created in `trdrop/build/linux/...` similar to the Qt Creator compilation process.

**Build from the command line - Windows**

We use Poweshell, please replace you own paths for the qmake.exe / mingw32-make.exe binaries and set the FFMPEG_SOURCE environment variable if you didn't set it for Windows globally.

```powershell
trdrop> mkdir shadow-build
trdrop> cd shadow-build
trdrop/shadow-build> C:\Qt\5.15.2\mingw81_64\bin\qmake.exe C:\Users\asa\Documents\github-repos\trdrop\trdrop\trdrop.pro -spec win32-g++ "CONFIG+=qtquickcompiler" 
(...)
trdrop/shadow-build> $Env:FFMPEG_SOURCE = "C:\Users\asa\Documents\libs\ffmpeg-4.4.1-full_build-shared"
trdrop/shadow-build> C:/Qt/Tools/mingw810_64/bin/mingw32-make.exe
(...)
```

Now the build directory should have been created in `trdrop/build/windows/...` similar to the Qt Creator compilation process.


### Build AppImage (Linux)

0. Build as release in Qt Creator
1. Prepare the linuxdeploy executable

```bash
> sudo add-apt-repository --remove ppa:savoury1/multimedia
> sudo apt update
> sudo apt install libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-bad
> wget https://github.com/probonopd/linuxdeployqt/releases/download/continuous/linuxdeployqt-continuous-x86_64.AppImage
> chmod a+x linuxdeployqt-continuous-x86_64.AppImage
```

2. Prepare the executable and library

```bash
> cp build/linux/gcc/x64/release/trdrop-ui linuxdeployqt-template/usr/bin
> cp build/linux/gcc/x64/release/lib* linuxdeployqt-template/usr/lib
```

3. Build the AppImage

We moved the linuxdeployqt binary to our PATH beforehand, but you can also call it from wherever you downloaded it.

We added the Qt binary path to our PATH variable so linuxdeployqt uses the correct `qmake` version. Same goes for the QML libraries.

```bash
> PATH=/opt/Qt/5.15.2/gcc_64/bin/:$PATH linuxdeployqt-continuous-x86_64.AppImage usr/share/applications/trdrop.desktop -verbose=1 -appimage -qmldir=/opt/Qt/5.15.2/gcc_64/qml/
```


