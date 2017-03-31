# T(ea)RDrop 
<img src="images/trdrop_logo_text.png" alt="Teardrop logo" width="200" height="330">

trdrop - a cross platform fps analyzer for raw video data 

## Description

This software is used for analyzing raw video data, calculating framedrops and visualizing tears.
The result can be exported with an overlay displaying the information. For a more detailed description, look up the documentation in [docs](docs/documentation.pdf).

The projects is split in 3 parts, the **trdrop\_lib**, **trdrop\_c** and the **trdrop\_v**.

##### Library
The library provides an extendable interface to design the overlay, save the processed data und peek into result.

##### Command Line Program
The command line program uses the library and/or a config file and/or command line flags to configure the overlay. The result should be streamable with vlc. Example usage:

```bash
$ trdrop_cbin video_01.raw video_02.raw > processed_video.mp4 | vlc
```  

##### GUI Program
The GUI program will be developed in `Qt` if there is time left. [It may look like this](images/trdrop_pitch.png "Pitch Scetch")

#### Cross Platform

Because of dependecy hell, there are now two different projects, a `windows/` one, and a `linux/` one.

##### Linux

Development is done with `avTranscoder`, `ffmpeg` and `CMake`.

##### Windows

Development is done with `avTranscoder`, `ffmpeg` and whatever compiler Visual Studio 2017 is using.