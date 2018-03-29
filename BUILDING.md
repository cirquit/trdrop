These instructions are written a little overly verbose for the sake of clarity. My fork diverges from the original in how it is built, these instructions will not work with it.

# Build Environment Setup

* I am going to be placing everything in one folder on my computer. Before you open Trdrop in Visual Studio, you should have a directory structure that looks like the following. I've included a few "key files" from each project so you know things are in the right place relative to one another. The absolute location does not matter, but I'll be using it for clarity purposes.
  * `C:\Projects\ThirdParty\trdrop\`
    * `trdrop` (This is the source of trdrop from GitHub.)
      * `trdrop_c`
        * `trdrop_c.sln`
        * (Etc...)
      * (Etc...)
    * `opencv`
      * `build`
      * `sources`
    * `openh264-1.7.0-win64.dll`  
    * `yaml-cpp` (This is the source release of yaml-cpp from GitHub.)
      * `include`
* I will be using Visual Studio 2017, the [Community Edition](https://www.visualstudio.com/downloads/) is free to download.
  * The current version at the time of writing is 15.6.4.
  * You should only need "Desktop development with C++" installed to build Trdrop.
    * You might also need to add "Windows 10 SDK (10.0.16299.0) for Desktop C++ [x86 and x64]" under "Individual Components". If it's not there, you can download it [here](https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk)
  * If for some reason you're running into issues and think you're missing something, [here's the full list of what I have installed](https://i.imgur.com/xhfAIJR.png). (Be forewarned: I use Visual Studio *a lot* so I have a ton of its components installed.)
* Download and install [CMake](https://cmake.org/download/) (I am using 3.11.0 x64.)
* Download and extract [OpenCV 3](https://github.com/opencv/opencv/releases/tag/3.4.1) (I'm using 3.4.1, you want the exe.)
  * OpenCV is a distributed as a self-extracting zip.
* Download and extract [OpenH264](https://github.com/cisco/openh264/releases/tag/v1.7.0) (You want `openh264-1.7.0-win64.dll.bz2`)
  * This is a single file, so just put it in the root of your build environment.
* Download and extract [yaml-cpp](https://github.com/jbeder/yaml-cpp/releases/tag/yaml-cpp-0.6.2)

# Build yaml-cpp

* Generate Visual Studio solution
  * Open the CMake GUI
  * Select the `C:\Projects\ThirdParty\trdrop\yaml-cpp\` folder for "Where is the soure code"
  * Select (and create) `C:\Projects\ThirdParty\trdrop\yaml-cpp\build\` folder for "Where to build the binaries"
  * Press "Configure"
    * Select "Visual Studio 15 2017 Win64" as the generator.
    * Leave everything else default (no optional toolset, "Use default native compilers"
    * Press "Finish"
  * Press "Generate"
* Open `C:\Projects\ThirdParty\trdrop\yaml-cpp\build\YAML_CPP.sln`
* Switch to release mode
  * Go to "Build > Configuration Manager"
  * Change "Active solution configuration" to "Release"
* Build yaml-cpp
  * Open the Solution Explorer if it is not already visible (View > Solution Explorer)
  * Right-click on `yaml-cpp static md` and click "Build"
  * Wait for Visual Studio to finish thinking...
  * You should now have a file `C:\Projects\ThirdParty\trdrop\yaml-cpp\build\Release\libyaml-cppmd.lib`

# Build Trdrop

* Open the Visual Studio solution (`C:\Projects\ThirdParty\trdrop\trdrop\trdrop_c\trdrop_c.sln`)
* Switch to release mode
  * Go to "Build > Configuration Manager"
  * Change "Active solution configuration" to "Release"
* Build yaml-cpp
  * Open the Solution Explorer if it is not already visible (View > Solution Explorer)
  * Right-click on `trdrop_c` and click "Build"
  * Wait for Visual Studio to finish thinking...
  * You should now have a file `C:\Projects\ThirdParty\trdrop\trdrop\trdrop_c\x64\Release\trdrop_c.exe`
