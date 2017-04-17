## How to use OpenCV on Windows in VS2017

1. Get precompiled opencv from [here](https://sourceforge.net/projects/opencvlibrary/files/opencv-win/)

2. Extract into your preferred directory. Mine is `$HOME\Documents\cpp-libs`. Change the following links accordignly.

3. Create a new VS Project and change the following in Project -> Properties:

4. VC++ -> Include: `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\include`
5. VC++ -> Library Dir: `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\lib`

6. Linker -> General -> Additional Library Dir: `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\bin`
7. Linker -> General -> Use Library Dependency Inputs: `Yes`

8. Linker -> Input -> Additional Deps: `opencv_world320.lib`

9. Set the Project Configuration (second menu line) from `x86` to `x64`.

10. Add to the predefined Win 'Path' variable:
  * `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\bin`
  * `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\lib`

If it still doesn't compile:

11. Copy from `$HOME\Documents\cpp-libs\OpenCV-3.2.0\opencv\build\x64\vc14\bin\` 
* `opencv_ffmpeg320_64.dll`
* `opencv_world320d.dll` 

to `YOUR_PROJECT\x64\Debug\`.

