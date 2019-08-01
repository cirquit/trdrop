
<p align="center">
    <img height="100" src="images/logos/trdrop_logo_alpha.png">
</p>

# trdrop
###### ˈtɛr-dɹɑp - a raw video analysis program

## Examples

<p align="center">
    <img height="160" src="images/2019-07-28-tear-visualization.gif">
    <img height="160" src="images/2019-07-22-plots-options.gif">
    <img height="160" src="images/2019-07-13-full-showcase-delta-renderering.gif">
</p>

## Binaries

```diff
- This is highly volatile as I'm not sure if the installer works for everybody yet
- Please create an issue if you encounter problems
```

See the [**release page**](https://github.com/cirquit/trdrop/releases) for the Windows installer. Other distributions are on the roadmap (Linux, MacOS).

## Description

The main use of this software is to estimate the *"real"* framerate of **an uncompressed video**.

Usually, a dedicated [capture card](https://en.wikipedia.org/wiki/Video_capture) is employed to capture the video stream with a fixed framerate of a console. To estimate the real framerate of the console, we check for differences on a frame-by-frame basis and count the different frames. This results in the *"real"* **framerate**.

The same is done with the **frametime**, as we count the amount of time a single frame is shown.

We also try to detect [**frametears**](https://en.wikipedia.org/wiki/Screen_tearing) and incorporate them into the framerate and frametime calculation.

Hence the name **tr** (short for tear) and a framerate **drop**.

## Features

* Comparisson of up to 3 videos in parallel
    - any resolution
    - any raw and *"real"* framerate
* Export as imagesequence in `.png` or `.jpg`
    - Supporting 16:9 export resolution
* **Framerate** estimation
    - Customizable plot visualization (`color` + `time`)
    - Customizable text overlay (`font` + `color`)
* **Frametime** estimation
    - Customizable plot visualization (`color` + `time`)
* **Tear** detection
    - complementing tears don't change the framerate
    - Visualization (`color`)
* CSV export
    - Framerate
* Visual overlay export
* Difference frame export

See the [DEVELOPMENT_HISTORY.md](DEVELOPMENT_HISTORY.md) for gifs I made while developing the application.

We will provide a detailed explanation and showcase in the future.

## Disclaimer

trdrop is a free, open-source project we develop in our spare time. While we do our best to make it as accurate as possible, we cannot guarantee that it is free of errors.

We **do not take responsibility** for analysis errors or inaccuracies that might damage or improve the reputation of any brand or organization. trdrop is not an accurate scientific tool, but merely a demonstration of different algorithms.

## Contributing

trdrop is created with the [Qt framework](https://www.qt.io/) and [OpenCV](https://opencv.org/). Please follow the [DEVELOPMENT.md](DEVELOPMENT.md) guidelines to get started.

## License

We have to run with the LGPLv3 license as Qt forces us to. As far as I understand it (**not a lawyer**), you can use the software commercially. [This seems like a good summary](https://www.embeddeduse.com/2016/04/10/using-qt-5-6-and-later-under-lgpl/) of the restrictions which should be only of interest to the embedded crowd.