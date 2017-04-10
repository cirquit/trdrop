#include <iostream>
#include <string>
#include <algorithm>
#include <time.h>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "framealgorithm.h"
#include "util.h"
#include "utilvideo.h"
#include "FPSTask.h"
#include "Config.h"

int main(int argc, char *argv) {

	std::string video01("skyrim.avi");
	std::string video02("20sec.avi");
	std::string outputVideo01("output.avi");

	trdrop::config::Config config(video01);



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
	
	return EXIT_SUCCESS;
} 