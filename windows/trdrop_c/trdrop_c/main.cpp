#include <iostream>
#include <string>
#include <algorithm>
#include <time.h>
#include <vector>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "framealgorithm.h"
#include "util.h"
#include "utilvideo.h"
#include "FPSPreTask.h"
#include "FPSPostTask.h"
#include "Config.h"
#include "TaskContainer.h"
#include "Either.h"
#include "ViewerTask.h"

int main(int argc, char *argv) {

	std::string video01("skyrim.avi");
	std::string video02("20sec.avi");
	std::string outputVideo01("output.avi");

	trdrop::config::Config config(std::vector<std::string>{ video01 }, outputVideo01, cv::VideoWriter::fourcc('D', 'I', 'V', 'X'), false);

	// create captures...TODO move away
	std::vector<cv::VideoCapture> inputs;
	std::for_each(config.inputNames.begin(), config.inputNames.end(),
		[&](std::string name) { inputs.push_back(cv::VideoCapture(name)); });

	// create container
	trdrop::tasks::TaskContainer container(config, inputs);
	
	// Task information
	double bakedFPS(trdrop::util::getFrameRate(inputs[0]));
	
	// FPSPreTask
	trdrop::Either<std::string, double> fpsSource;
	trdrop::Either<std::string, double> & tmpFPSSource = fpsSource;
	trdrop::tasks::pre::FPSPreTask fpsPreT(tmpFPSSource, 60, bakedFPS);
	
	// FPSPostTask
	double framerate = 0.00;
	double & tmp = framerate;
	trdrop::tasks::post::FPSPostTask fpsPostT(tmp, cv::Point(50, 50));

	// ViewerTask
	trdrop::tasks::post::ViewerTask viewer(1, cv::Size(800, 600));

	//container.addPreTask(fpsPreT);
	container.addPostTask(fpsPostT);
	container.addPostTask(viewer);

	while (container.next()) {
		/*if (fpsSource.successful()) {
			tmp = fpsSource.getSuccess().get();
			std::cout << "Next frame - FPS: " << std::to_string(tmp) << '\n';

		}*/
	}

	/*

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
	*/
	return EXIT_SUCCESS;
} 