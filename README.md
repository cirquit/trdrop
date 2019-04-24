# T(ea)RDrop 
<img src="images/trdrop_logo_text_wide.png" alt="Teardrop logo">

trdrop - a cross platform fps analyzer for raw video data 

## Update 24.04.2019

I'm currently working on a cross platform (Win/Linux) Qt based implementation. Currently testing some of the key functionalities in private repos. Stay tuned!

## Description

This software is used for analyzing raw video data, calculating framedrops and visualizing tears.
The result can be exported with an overlay displaying the information. For a more detailed description, look up the documentation in [docs](docs/documentation.pdf).

## Disclaimer

Trdrop is a free, open source project we develop in our spare time with some help of [kind strangers](https://github.com/cirquit/trdrop/graphs/contributors). While we do our best to make it as accurate as possible, we **cannot guarantee** that it is free of errors.

We don't take responsibility for any analysis errors or inaccuracies that might damage or improve the reputation of any brand or organization. Trdrop is not an accurate scientific tool, but merely a demonstration of an algorithm and should be used with that in mind.

To minimize errors, please make sure that you use **raw** videos from a capture card. This tool analyzes the **raw** pixel data and therefore any compressed encoding might falsify the output. If you notice some unexpected behaviour, please [make an issue](https://github.com/cirquit/trdrop/issues) with a short clip and a description of your testing setup (which capture card). This way we can try so keep a summary of supported devices.

## Software limits

You can use our software if:
* your video is not encoded at all, also known as `.raw` format. Some vendors have own implementations of their `.raw` format and might not be comparable. In summary, you need to have a **non-compressed** video
* your video does **not** exceed 60 frames per second, either in real-life or recording speed
     * The **recording FPS** are read from the header information and not counted from the frame-time ([#21](https://github.com/cirquit/trdrop/issues/21)), which might be done in the future. If this information is corrupted, we can't do a proper analysis.
     * The **real-life FPS** are a requirement because we don't have the best solution for the plotting library ([#21](https://github.com/cirquit/trdrop/issues/21)) and at the start of this project we wanted to cater to the people with high-end capture card users which record only console games in up to 4K. To my knowledge this is currenlty only possible at `60` fps

## Contributing

If you want to contribute, please follow [this guide](BUILDING.md) which was kindly created by [PathogenDavid](https://github.com/PathogenDavid).

## Releases

Current releases are found [here](https://github.com/cirquit/trdrop/releases). (watch out - still an alpha)

## Features

* fps feature extraction
* support for up to three videos
* csv logger
* plot visualization
* configuration via a `yaml` file
* support for comparison of different resolution videos
* configurable output resolutions

<img src="images/triple-screenshot.jpg" alt="Teardrop logo" width="960" height="480">

