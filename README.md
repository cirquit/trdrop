# T(ea)RDrop 
<img src="images/trdrop_logo_text.png" alt="Teardrop logo" width="200" height="330">

trdrop - a cross platform fps analyzer for raw video data

## Description

This software is used for analyzing raw video data, calculating framedrops and visualizing tears.
The result can be exported with an overlay displaying the information. For a more detailed description, look up the documentation in `docs/`.

The projects is split in 3 parts, the **trdrop\_lib**, **trdrop\_cbin** and the **trdrop\_vbin**.

##### Library
The library provides an extendable interface to design the overlay, save the processed data und peek into result.

##### Command Line Program
The command line program uses the library and/or a config file and/or command line flags to configure the overlay. The result should be streamable with vlc. Example usage:

```
$ trdrop_cbin video_01.raw video_02.raw > processed_video.mp4 | vlc
```  

##### GUI Program
The GUI program will be developed in `Qt` if there is time left. It may look like this.
![This is a the pitch screenshot](images/trdrop_pitch.png "Pitch Scetch")

#### Cross Platform

Because this project is being developed with C++, `ffmpeg` and CMake, it should be portable to Windows atleast, even if the development is being done on Linux.

#### Milestones

TODO Refactoring

| Milestone     | Feature         											  								  | Time  | Completed |
| ------------- |:----------------											  								  | -----:|----------:|
| **Nr.1**      | run `Qt` on Linux 											  							  |    2h |           |
| 			    | setup a build system, learn simple `cmake`, `qt-developer`, lookup conan 					  |    2d |			  |
| 			    | setup travis      										  								  |    2h |			  |
| 			    | 														      								  | 2d,4h |			  |
| 			    | 														      								  |       |			  |
| **Nr.2**      | create a simple gui with a viewport in 1080p which can load a `raw` video 				  |    3d |           |
| 			    | create a custom fps field which has a predefined settings and let is calculate the fps      |    3d |			  |
| 			    | create the run/stop buttons     				   			  				     			  |    2h |			  |
| 			    | run `Qt` on Windows and test the previous work     			  			     			  |    4h |			  |
| 			    | 														      								  | 6d,6h |			  |
| 			    | 														      								  |       |			  |
| **Nr.3:**	    | refactor the fps field as a tool and make it selectable     				     			  |    1d |			  |
| 			    | create the config bar with the settings of the currently selected element      			  |    1d |			  |
| 			    | make it *responsive*      	 						   									  |    4h |			  |
| 			    | make elements delete'able      						   									  |    2h |			  |
| 			    | create the "view"-tool, which adds another viewport      									  |    1d |			  |
| 			    | create the File-Menu (only Open + Exit)             		  								  |    2h |			  |
| 			    | 														      								  | 3d,8h |			  |
| 			    | 														      								  |       |			  |
| **Nr.4:**     | implement YT-friendly Export with fps overlay       		  								  |    2d |			  |
| 			    | implement frameskip +1 / -1     	 	   	    	  		  								  |    4h |			  |
| 			    | create keybindings for everything        	    	  		  								  |    1d |			  |
| 			    | implement drag'n'drop for viewports      	    	  		  								  |    5h |			  |
| 			    | create the analyze tool for tears        	    	  		  								  |       |			  |
| 			    | * save tear-time and allow jumps to tears     	  		  								  | 1d 18h|			  |
| 			    | * show the probably used time for the analysis      		  								  |    6h |			  |
| 			    | 														      								  | 5d,9h |			  |
| 			    | 														      								  |       |			  |
| **Nr.5:**     | allow serialization for configuration					      								  |       |			  |
| 			    | * save      								  												  |    2d |			  |
| 			    | * load      								  												  |    1d |			  |
| 			    | save configs and tears for videos based on filename	      								  |    2h |			  |
| 			    | 														      								  |  3d,2h|			  |
|**Summary**    | trdrop alpha v0.1										      								  | 20d,7h|			  |
**Features:**
* `.avi` container with raw *encoding* 
* 1080p export, with futureproof 2k and 4k extension
* centering videos and fit to height


**Extra goodies:**
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

