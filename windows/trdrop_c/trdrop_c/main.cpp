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

#include "framealgorithm.h"
#include "util.h"
#include "utilvideo.h"
#include "Config.h"
#include "Either.h"
#include "CSVFile.h"

#include "TaskContainer.h"
#include "FPSPreTask.h"
#include "FPSInterTask.h"
#include "ViewerTask.h"
#include "WriterTask.h"
// #include "LoggerTask.h"

int main(int argc, char *argv) {

	trdrop::config::Config config(-1);  // opencv gives a popup for the installed codecs with configuration options
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
	trdrop::tasks::TaskContainer container(config.inputs);
	
	// FPSPreTask
	trdrop::tasks::pre::FPSPreTask fpsPreT("FPS", config.captureWindows, config.getBakedFPS());

	// FPSIntermediateTask
	std::vector<double> framerates(config.inputs.size());
	trdrop::tasks::inter::FPSInterTask fpsInterT(framerates, config.textLocations, config.fpsPrecision, config.shadows);

	// ViewerTask
	trdrop::tasks::post::ViewerTask viewerT(config.viewerSize);
	if (config.viewerActive) viewerT.init();

	// WriterTask
	trdrop::tasks::post::WriterTask writerT(config.outputFile, config.codec, config.getBakedFPS(0), config.getVideoFrameSize(0));

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
	container.addPreTask(fpsPreT);
	
	// IntermediateTasks - order does not matter
	container.addInterTask(fpsInterT);
	//container.addInterTask(loggerT);

	// PostTask - order matters
	if (config.viewerActive) container.addPostTask(viewerT);
	container.addPostTask(writerT);

	while (container.next()) {

		if (trdrop::util::video::pushedKey(27)) return 0; // ESC -> terminate

		// glue FPS source -> FPS consumer
		if (fpsPreT.result.successful()) {
			framerates = fpsPreT.result.getSuccess();
			//std::cout << "Main loop: framerates:" << framerates[0] << ", " << framerates[1] << '\n';
		}

	}

	return EXIT_SUCCESS;
} 