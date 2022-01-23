# Test Videos

All the test videos were converted from the GIF to their target codec/container via ffmpeg (4.4.1)
on Linux. 

Example command:

```bash
ffmpeg -i the-office-kevin-chili.gif -pix_fmt yuv420p -c:v mpeg2video kevin-chili-yuv420p-mpeg2video.mp4
```

The codec is always the last part of the name.

To test which codec / container is actually used, use `ffprobe`, which is also installed when
building ffmpeg.

Example:

```
> ffprobe kevin-chili-yuv420p-libvpx-vp8.mkv
ffprobe version N-105039-g12f21849e5 Copyright (c) 2007-2021 the FFmpeg developers
  built with gcc 7 (Ubuntu 7.5.0-3ubuntu1~18.04)
  configuration: --prefix=/home/asa/Documents/libs/ffmpeg/build --pkg-config-flags=--static --extra-cflags=-I/home/asa/home/asa/Documents/libs/ffmpeg/build/include --extra-ldflags=-L/home/asa/home/asa/Documents/libs/ffmpeg/build/lib --extra-libs='-lpthread -lm' --ld=g++ --bindir=/home/asa/Documents/libs/ffmpeg/bin --enable-gpl --enable-gnutls --enable-libass --enable-libfdk-aac --enable-libfreetype --enable-libmp3lame --enable-libopus --enable-libsvtav1 --enable-libdav1d --enable-libvorbis --enable-libvpx --enable-libx264 --enable-libx265 --enable-nonfree
  libavutil      57. 13.100 / 57. 13.100
  libavcodec     59. 15.102 / 59. 15.102
  libavformat    59. 10.100 / 59. 10.100
  libavdevice    59.  1.100 / 59.  1.100
  libavfilter     8. 21.100 /  8. 21.100
  libswscale      6.  1.102 /  6.  1.102
  libswresample   4.  0.100 /  4.  0.100
  libpostproc    56.  0.100 / 56.  0.100
Input #0, matroska,webm, from 'kevin-chili-yuv420p-libvpx-vp8.mkv':
  Metadata:
    ENCODER         : Lavf59.10.100
  Duration: 00:00:03.75, start: 0.000000, bitrate: 243 kb/s
  Stream #0:0: Video: vp8, yuv420p(tv, progressive), 500x282, 6.67 fps, 6.67 tbr, 1k tbn
    Metadata:
      ENCODER         : Lavc59.15.102 libvpx
      DURATION        : 00:00:03.750000000
```

