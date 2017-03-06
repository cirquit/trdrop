### Prerequesites

I use clang-3.9, cmake-3.5.2.

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