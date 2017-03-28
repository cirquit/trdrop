### Prerequesites

I use `clang-3.9`, `cmake-3.5.2` for local development. Travis runs tests with `cmake-2.8.7`, `clang-3.9` and `gcc-4.6.3` (even if I specifiy `gcc-5`). Documentation for `trdrop_lib` is generated with [`doxygen-1.8.14`](http://www.stack.nl/~dimitri/doxygen/download.html).

Using `ffmpeg-libs`. Install with:

```bash
sudo apt-get install libavdevice-dev libavformat-dev libavfilter-dev libavcodec-dev libswscale-dev libavutil-dev yasm libtheora-dev libvorbis-dev libvpx-dev libx264-dev
```

After this, build ffmpeg from source:

```bash
$ cd ext/ffmpeg
$ ./configure --enable-shared --enable-swscale --enable-gpl  --enable-libx264 --enable-libvpx --enable-libtheora --enable-libvorbis
$ make -j4 
```


Using `https://github.com/avTranscoder/avTranscoder` as C++ wrapper for `ffmpeg`. Install with:

```bash
$ cd ext/avTranscoder 
$ mkdir build && cd build
$ cmake ..
$ make
$ sudo make install
```

Create docs for `avtranscoder`:

```bash
$ cd ext/avTranscoder
$ cd build/src

Modify the Doxyfile so OUTPUT_DIRECTORY points to .

$ doxygen Doxyfile
$ firefox html/index.html
```

### Build process for Linux

Clone or fork the repo. (cloning in the example)
```bash
$ git clone https://github.com/cirquit/trdrop
$ cd trdrop
```

Build the library:
```bash
$ cd trdrop_lib && mkdir build
$ cd build && cmake .. && make
```

Or if you want to install the library globally:
```bash
$ cd trdrop_lib && mkdir build
$ cd build && cmake .. && sudo make install
```

Build your executable (analogue for `trdrop_v`)
```bash
$ cd trdrop_c && mkdir build
$ cd build && cmake .. && make
$ ./trdrop_c
```

To generate the documentation for `trdrop_lib`
```bash
$ cd trdrop_lib
$ doxygen Doxyfile
$ cd apidocs/html && firefox index.html
```

### Code style

I use `clang-format` with the WebKit style. 

For use in SublimeText:

```bash
sudo apt-get install clang-format
```
Install Clang-Format Package in Sublime Text. `Preferences -> Package Settings -> Clang Format -> Settings (User)`. Copy the following snippet.
```json
{
    "binary": "/usr/bin/clang-format",
    "style": "WebKit",
    "format_on_save": true
}
```

### Code completion

I use the sublime package [C++ Completions](https://github.com/tushortz/CPP-Completions). 