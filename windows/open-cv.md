## How to use OpenCV on Windows in VS2017

Get precompiled opencv from [here](https://sourceforge.net/projects/opencvlibrary/files/opencv-win/)

Extract into your preferred directory. Mine is C:\Users\rewrite\Documents\cpp-libs. Change the following links accordignly.

Create a new VS Project and change the following in Project -> Properties:

VC++ -> Include: C:\Users\rewrite\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\include
VC++ -> Library Dir: C:\Users\rewrite\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\lib

Linker -> General -> Additional Library Dir: C:\Users\rewrite\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\bin
Linker -> General -> Use Library Dependency Inputs: Yes

Linker -> Input -> Additional Deps: opencv_world320.lib

Set the Project Configuration (second menu line) from `x86` to `x64`.

Add to custom made 'PATH' **AND** predefined for Win 'Path' variable:
  * C:\Users\rewrite\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\bin
  * C:\Users\rewrite\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\lib

Copy the `C:\Users\rewrite\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\libopencv_world320.lib` to `YOUR_PROJECT\x64\Debug\`.