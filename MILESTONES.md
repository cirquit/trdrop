## Milestones

| Milestone     | Feature                                                                                     | Time  | Completed |
| ------------- |:----------------                                                                            | -----:|----------:|
| **Nr.1**      | setup a build system with cmake and project directories                                     |    3h |         ✓ |
|               | setup test environment & possibly travis/circleci                                           |    3h |           |
|               |                                                                                             |       |           |
| **Nr.2**      | create a dummy command line interface                                                       |    3h |           |
|               | read a raw video file and encode it so it's viewable                                        |    1d |           |
|               | encode it into YT-Format                                                                    |    1d |           |
|               | calculate fps and dump it into a csv-file                                                   |    2d |           |
|               | calculate tears and dump it into a csv-file                                                 |    1d |           |
|               | show the results in the video                                                               |    2d |           |
|               | follow the possibility to show the results as a stream in vls                               |    1d |           |
|               |                                                                                             |       |           |
| **Nr.3:**     | read from two videos simultaneously and write to one with overlay                           |    2d |           |
|               | think of an interface to make the overlay configurable                                      |    3d |           |
|               |                                                                                             |       |           |
| **Nr.4**      | command line interface should be reworked                                                   |    4d |           |
|               | ...                                                                                         |       |           |
|               |                                                                                             |       |           |
| **Nr.5**      | From here on we have time to do any of the possible features                                |       |           |
|               |                                                                                             |       |           |
|**Summary**    | trdrop alpha v0.1                                                                           | > 18d |           |


**Possible features:**
* mouse based translation for elements
* video time, current time for the selected viewport
    * possibility to jump to frame through click
* text field
    * font
    * size
    * color
* fps field
    * add color
* safe config and tears for videos based on some specially picked frames and hash + compare
* multi select for elements
    * translation with mouse
    * translation with keyboard
    * change same properties in config bar
* allow alignment via mouse based on every center/edge of elements for every element
    * show it interactivly like on `slides.com`
* viewports are moveable via mouse and can be moved interactivly
* multiple export settings, not only for `yt`
* possibility to open multiple files, not only `raw`
* port to Mac
* allow the viewport to show the analysis of the frames, or other graphs
* 1080p support and 2k,4k extension possibility
* centering videos and fit to height
