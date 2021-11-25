# Deployment

## Windows

#### Manual

##### Create the executable

* Install [QtCreator (open-source version)](https://www.qt.io/download) and the Qt Installer Framework 3.0 (included, have to check it)
* Build OpenCV and the application in Release mode, see detailed instructions in [Compile OpenCV (Windows) (DEVELOPMENT.md)](DEVELOPMENT.md#compile-opencv-windows)
* Follow Running Trdrop with Qt Creator in [Running Trdrop with Qt Creator (Windows) (DEVELOPMENT.md)](DEVELOPMENT.md#running-trdrop-with-qt-creator-windows)
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

## MacOS (TODO)
