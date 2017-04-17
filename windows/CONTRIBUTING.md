# Windows

#### Prerequesites

I'm using Visual Studio 2017 Enterprise Edition on Win8.1.

#### Libraries

* [OpenCV3 - pseudoofficial steps](https://github.com/MicrocontrollersAndMore/OpenCV_3_Windows_10_Installation_Tutorial/blob/master/Installation%20Cheat%20Sheet%201%20-%20OpenCV%203%20and%20C%2B%2B.pdf)
  * if you did everything, and it still doesn't compile, copy **all** `.dll` files to the directoy where the `.exe` is found. In my case `$HOME\Documents\github-repos\trdrop\windows\trdrop_c\x64\Debug`
  * [My steps, because the ones in the instruction are not enough](open-cv.md)

* [Yaml-CPP](https://github.com/jbeder/yaml-cpp)
  * installation since VS 2015 bugs out because of different stl types (**??**), so I had no other choice that copying the whole source as `.h` and `.cpp` files to the project. Hoping that [#451](https://github.com/jbeder/yaml-cpp/issues/461) will be fixed someday
  * currently at [#0fdb1b9](https://github.com/jbeder/yaml-cpp/commit/11607eb5bf1258641d80f7051e7cf09e317b4746)
