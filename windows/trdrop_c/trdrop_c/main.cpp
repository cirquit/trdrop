#include <iostream>
#include <string>
#include <algorithm>
#include <time.h>
#include <vector>
#include <functional>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include "yaml-cpp\yaml-cpp-header\yaml.h"

#include "framealgorithm.h"
#include "util.h"
#include "utilvideo.h"
#include "Config.h"
#include "Either.h"
#include "CSVFile.h"

#include "TaskContainer.h"
#include "FPSPreTask.h"
#include "FPSPostTask.h"
#include "ViewerTask.h"
#include "WriterTask.h"
#include "LoggerTask.h"

int main(int argc, char *argv) {
	std::string video01("skyrim.avi");
	std::string video02("test-video-01.avi");
	std::string video03("20sec.avi");
	std::string outputVideo01("output.avi");


	YAML::Node yamlConfig = YAML::LoadFile("config.yaml");

	if (yamlConfig["input-file"]) {
		std::cout << "Got input-file: " << yamlConfig["input-file"].as<std::string>() << '\n';
	}

	return 0;

	// parse from somewhere
	trdrop::config::Config config(std::vector<std::string>{ video01 }           // inputNames
								, outputVideo01                                 // outputName
								, "log.csv"                                     // logName
								, -1 //cv::VideoWriter::fourcc('D', 'I', 'V', 'X')   // codec
								, false											// write delta
								, cv::Size(50,50)                               // text location
								, cv::Size(960, 540)                            // viewer size
								, 2                                             // fpsPrecision
									);

	// create container
	trdrop::tasks::TaskContainer container(config);
	
	// FPSPreTask
	trdrop::tasks::pre::FPSPreTask fpsPreT("FPS", static_cast<int>(std::floor(config.bakedFPS)), config.bakedFPS);

	// FPSPostTask
	double framerate = 0.0;
	trdrop::tasks::post::FPSPostTask fpsPostT(framerate, config.textLocation, config.fpsPrecision);

	// ViewerTask
	trdrop::tasks::post::ViewerTask viewerT(config.viewerSize);

	// WriterTask
	trdrop::tasks::post::WriterTask writerT(config.outputName, config.codec, config.bakedFPS, config.getVideoFrameSize(0));

	// LoggerTask
	using tostring = trdrop::tasks::post::LoggerTask<trdrop::util::CSVFile>::tostring;
	std::vector<tostring> convertions;
	std::ofstream out;
	trdrop::util::CSVFile file(config.logName, { "Frame", "   FPS" }, &out);
	trdrop::tasks::post::LoggerTask<trdrop::util::CSVFile> loggerT(config.logName, 1, file, convertions);

	// PreTasks - order does not matter
	container.addPreTask(fpsPreT);
	
	// PostTask - order matters
	container.addPostTask(fpsPostT);
	container.addPostTask(viewerT);
	container.addPostTask(loggerT);
	// container.addPostTask(writerT);

	convertions.push_back([&]() { return trdrop::util::string_format("%5i", container.getCurrentFrameIndex()); });
	convertions.push_back([&]() { return trdrop::util::string_format("%6." + std::to_string(config.fpsPrecision) + "f", framerate); });

	while (container.next()) {

		if (trdrop::util::video::pushedKey(27)) return 0; // ESC -> terminate

		// glue FPS source -> FPS consumer
		if (fpsPreT.result.successful()) {
			framerate = fpsPreT.result.getSuccess();
		}
		
		// Logger consumer
		
		//};

	}

	return EXIT_SUCCESS;
} 