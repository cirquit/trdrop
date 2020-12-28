# Deployment

## Windows

We currently support latest Win 10 (installed at 31.07.2019) as I build it manually in a virtual machine.

#### Manually

##### Create the executable

* Install Virtualbox
* Get Win10.iso (64-bit) from the [official Microsoft homepage](https://www.microsoft.com/en-us/software-download/windows10ISO)
* Install Windows, skip activation
* Install [QtCreator (open-source version)](https://www.qt.io/download) and the Qt Installer Framework 3.0 (included, have to check it)
* Build OpenCV and the application in Release mode, see detailed instructions in [DEVELOPMENT.md](DEVELOPMENT.md)
* Copy all the `.dll`'s from the following directories
    - `C:\opencv-4.5.1\build_64\install\x64\mingw\bin`
    - `C:\Qt\Tools\mingw810_64\bin`
* To the release directory of the application
* Go to the release directory of the application, in my case `C:\Users\asa\Documents\github-repos\trdrop\build-trdrop-Desktop_Qt_5_15_2_MinGW_64_bit-Release\release`
* Execute the following command `windeployqt.exe --qmldir C:\Users\asa\Documents\github-repos\trdrop\trdrop .`
* Now the executable has the correct dlls in the directory to run on a different system!

##### Create the installer

* Installer the [QtInstallerFramework](https://download.qt.io/official_releases/qt-installer-framework)
* Add the qt installer binaries to the PATH environment variable	
    - e.g `C:\Qt\Tools\QtInstallerFramework\3.0\bin` or if you installed seperately `C:\Qt\QtIFW-4.0.1\bin`
* Open QtCreator
    - Tools -> Options -> Help -> Documentation -> Add
        + `C:\Qt\Tools\QtInstallerFramework\3.0\doc\ifw.qch`
* Use the installer-template from the `template` directory
    - bump up the version number in the `config\config` file
    - copy the contents of the prepared directory into the `packages\org.cirquit.trdrop\data` directory
    - bump up the version in the `installer\packages\org.cirquit.trdrop\meta\package` file
* Open the **Qt 5.15.2 (MinGW 810 64-bit)** command line tool and `cd` into the template directory
    - run `binarycreator --offline-only -c config/config.xml -p packages TrdropInstaller`

#### Automated (TODO)



## Linux (TODO)

## Mac OS (TODO)