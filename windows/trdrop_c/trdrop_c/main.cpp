#include <iostream>
#include <string>
#include <algorithm>
#include <time.h>

#include<opencv2/core/core.hpp>
#include<opencv2/highgui/highgui.hpp>
#include<opencv2/imgproc/imgproc.hpp>

#include "framealgorithm.h"
#include "util.h"

int main(int argc, char *argv) {
	
	std::string video01("skyrim.avi");
	std::string video02("20sec.avi");
	std::string outputVideo01("output.avi");

	cv::VideoCapture input(video01);
	double bakedFPS(trdrop::util::getFrameRate(input));
	cv::Size bakedSize(trdrop::util::getSize(input));

	cv::VideoWriter  output;
	output.open(outputVideo01, cv::VideoWriter::fourcc('D', 'I', 'V', 'X'), bakedFPS, bakedSize);

	
	std::cout << "Baked Fps: " << bakedFPS << '\n';
	std::cout << "Baked Framecount: " << trdrop::util::getFrameCount(input) << '\n';
	std::cout << "Videolength in seconds: " << trdrop::util::getVideoLengthInSec(input) << '\n';
	std::cout << "Current Frameindex: " << trdrop::util::getCurrentFrameIndex(input) << '\n';
		
	cv::Mat a;
	cv::Mat b;

	input.read(a);
	input.read(b);

	trdrop::util::timeit_([&]() {
		std::cout << "Equal? " << (trdrop::algorithm::are_equal<uchar*>(a, b) ? "true" : "false") << '\n';
	});

	trdrop::util::timeit_([&]() {
		std::cout << "Equal? " << (trdrop::algorithm::are_equal<cv::Vec3b>(a, b) ? "true" : "false") << '\n';
	});
	return 0;
} 

/*
	double framerate_window = 60;
	double different_frames = 0;
	double current_window_count = 0;
	double real_fps = 0;

	if (!cap.read(current_frame)) {
		std::cout << "Can't read frame" << '\n';
		return -1;
	}

	// writer.open(filename, codec, baked_fps, current_frame.size());
	
	if (!writer.isOpened()) {
		std::cout << "Could not open the output video file for write\n";
		return -1;
	} 


	while (count > 1)
	{
		current_frame.copyTo(previous_frame);
		if (!cap.read(current_frame)) {
			std::cout << "Can't read frame!" << '\n';
			break;
		}

		//Resize for speed and smaller preview
		//cv::resize(current_frame, current_frame, current_frame.size()/2, 0.5, 0.5);
		
		bool mats_equal = are_equal(current_frame, previous_frame);
		if (!mats_equal) ++different_frames;

		if (current_window_count == framerate_window) {
			real_fps = std::round(10 * (baked_fps * different_frames / framerate_window)) / 10;
			current_window_count = 0;
			different_frames = 0;
			std::cout << real_fps << '\n';
		}
		
		// ++current_window_count;

		cv::Mat display(current_frame != previous_frame);

		//cv::putText(display, "FPS: " + std::to_string(real_fps).substr(0, 5), cv::Point(50, 50), 0, 1, cv::Scalar(255, 255, 255), 2);

		*/