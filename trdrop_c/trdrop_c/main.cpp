#define _DEBUG 0

#include <iostream>
#include <string>
#include <algorithm>
#include <time.h>
#include <vector>
#include <functional>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/flann/logger.h>

#include "framealgorithm.h"
#include "util.h"
#include "utilvideo.h"
#include "Config.h"
#include "Either.h"
#include "CSVFile.h"

#include "TaskScheduler.h"
#include "FPSPreTask.h"
#include "TearPreTask.h"
#include "FPSInterTask.h"
#include "ViewerTask.h"
#include "WriterTask.h"
#include "CMDProgressTask.h"
// #include "LoggerTask.h"


int main(int argc, char **argv) {

	trdrop::config::Config config(-1, argc, argv);  // opencv gives a popup for the installed codecs with configuration options
										      // it's currently not possible to configure them from code, because of the missing interface

	if (!config.parsing.successful()) {
		std::cerr << "trdrop_c terminating!\n"
			<< "  Following errors occured:\n";
		std::vector<std::string> & errors = config.parsing.getError();
		std::for_each(errors.begin(), errors.end(), [&](std::string & err) {
			std::cerr << "  " << err;
		});
		return EXIT_FAILURE;
	}

	// create container
	trdrop::tasks::TaskScheduler scheduler(config.inputs);
	
	// FPSPreTask
	trdrop::tasks::pre::FPSPreTask fpsPreT("FPS", config.inputs.size(), config.pixelDifference);

	// TearPreTask - TODO think about configurability
	trdrop::tasks::pre::TearPreTask tearPreT("Tear", 20, 5);

	// FPSIntermediateTask
	std::vector<double> framerates(config.inputs.size());
	trdrop::tasks::inter::FPSInterTask fpsInterT(framerates, config.textLocations, config.refreshRate, config.fpsPrecision, config.shadows);

	// ViewerTask
	trdrop::tasks::post::ViewerTask viewerT(config.viewerSize);
	if (config.viewerActive) viewerT.init();

	// WriterTask
	trdrop::tasks::post::WriterTask writerT(config.outputFile, config.codec, config.getBakedFPS(0), config.getVideoFrameSize(0));

	// CMDProgressTask
	trdrop::tasks::post::CMDProgressTask cmdProgressT(config.getMinFrameIndex());

	// LoggerTask
	/*using tostring = trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFile>::tostring;
	std::vector<tostring> convertions;
	std::ofstream out;
	trdrop::util::CSVFile file(config.logFile, { "Frame", "   " + fpsPreT.id }, &out);
	trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFile> loggerT(config.logFile, 1, file, convertions);
	convertions.push_back([&]() { return trdrop::util::string_format("%5i", container.getCurrentFrameIndex()); });
	convertions.push_back([&]() { return trdrop::util::string_format("%6." + std::to_string(config.fpsPrecision) + "f", framerate); });
	*/

	// PreTasks - order does not matter
	scheduler.addPreTask(fpsPreT);
	//scheduler.addPreTask(tearPreT);

	// IntermediateTasks - order does not matter
	scheduler.addInterTask(fpsInterT);
	//container.addInterTask(loggerT);

	// PostTask - order matters
	if (config.viewerActive) scheduler.addPostTask(viewerT);
	scheduler.addPostTask(writerT);
	scheduler.addPostTask(cmdProgressT);

	while (scheduler.next()) {

		if (trdrop::util::video::pushedKey(27)) return 0; // ESC -> terminate

#if _DEBUG
		std::cout << "DEBUG: Main loop: fpsPreT.result.success(): " << fpsPreT.result.successful() << '\n';
#endif

		// glue FPS source -> FPS consumer
		if (fpsPreT.result.successful()) {
			framerates = fpsPreT.result.getSuccess();
#if _DEBUG
			std::cout << "DEBUG: Main loop: got framerates: ";
			std::for_each(framerates.begin(), framerates.end(), [&](int framerates) {
				std::cout << framerates << ", ";
			});
			std::cout << '\n';
#endif
		}

		if (tearPreT.result.successful()) {
#if _DEBUG
			std::cout << "TearTask: " << tearPreT.result.getSuccess() << '\n';
#endif
		}

	}

	return EXIT_SUCCESS;
} 