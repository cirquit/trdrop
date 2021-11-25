
<p align="center">
    <img height="100" src="images/logos/trdrop_logo_alpha.png">
</p>

# trdrop - v1.1.1
###### ˈtɛr-dɹɑp - a raw video analysis program

## Examples

<p align="center">
    <img height="160" src="https://github.com/cirquit/trdrop/raw/ef4462994df90fdc3b2c961a76e874a4a964a12e/images/2019-07-28-tear-visualization.gif">
    <img height="160" src="https://github.com/cirquit/trdrop/raw/ef4462994df90fdc3b2c961a76e874a4a964a12e/images/2019-07-22-plots-options.gif">
    <img height="160" src="https://github.com/cirquit/trdrop/raw/ef4462994df90fdc3b2c961a76e874a4a964a12e/images/2019-07-13-full-showcase-delta-renderering.gif">
</p>

## Binaries

```diff
- Please create an issue if you encounter problems and search the closed issues for already solved ones.

- If you want to have a specific feature in mind, please attach as much exemplary information as possible (screenshots, mockups)
```

* [**Issues**](https://github.com/cirquit/trdrop/issues?q=is%3Aopen+is%3Aissue)
* [**Solved Issues**](https://github.com/cirquit/trdrop/issues?q=is%3Aissue+is%3Aclosed)

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
    - Customizable text overlay (`font` + `color` + `position`)
    - "Centered" plot also possible
* **Frametime** estimation
    - Customizable plot visualization (`color` + `time`)
* **Tear** detection
    - complementing tears don't change the framerate (configurable)
    - Visualization (`color`)
* CSV export
    - Framerate
    - Frametime
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

[MIT License](https://en.wikipedia.org/wiki/MIT_License). Commercial use is allowed.