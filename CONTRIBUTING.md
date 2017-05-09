# Windows

#### Prerequesites

I'm using Visual Studio 2017 Enterprise Edition on Win8.1.

#### Libraries

* [OpenCV3 - download precompiled sources](https://sourceforge.net/projects/opencvlibrary/files/opencv-win/)
  * Extract into your preferred directory. Mine is `$HOME\Documents\cpp-libs`
  * Create an environment variable `OPEN_CV_PATH` and set it to `$HOME\Documents\cpp-libs\OpenCV-3.2.0` (adapt to your extracted path)
  * This setup should compile, but if it asks for the `opencv_world320.dll` or `opencv_ffmpeg320_64.dll` copy them from `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\bin\` next to your `.exe`


* [Yaml-CPP](https://github.com/jbeder/yaml-cpp)
  * `git clone https://github.com/jbeder/yaml-cpp`
  * `cd yaml-cpp`
  * `mkdir build`
  * `cd build`
  * `cmake -G "Visual Studio 15 2017 Win64" -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release ..`
  * Open the `YAML_CPP.sln` file located in the build folder with VS2017
  * Build the project `ALL_BUILD`

  * if you want to link against this library, go to your project:
    * Create an environment variable named `YAML_CPP_PATH` and with the path to the repository, e.g `$(HOME)\Documents\github-repos\yaml-cpp`
    * `Properties -> VC++ Directories -> Include Directories -> $(YAML_CPP_PATH)\include`
    * `Properties -> VC++ Directories -> Library Directories -> $(YAML_CPP_PATH)\yaml-cpp\build\Debug`
    * `Properties -> Linker -> Input -> Additional Dependencies -> Add libyaml-cppmdd.lib`
    * use header `<yaml-cpp/yaml.h>`

#### Custom steps
* You have to manually copy [the configuration files](config) (the `yaml` files) and [sprites](images/trdrop_sprites) (the whole folder) into the folder with the executable 