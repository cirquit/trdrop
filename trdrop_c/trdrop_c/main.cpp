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
#include "CSVFormatter.h"

#include "TaskScheduler.h"
#include "FPSPreTask.h"
#include "TearPreTask.h"
#include "FPSInterTask.h"
#include "ViewerTask.h"
#include "WriterTask.h"
#include "CMDProgressTask.h"
#include "LoggerTask.h"
#include "PlotTask.h"
#include "ResizeTask.h"


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
	std::vector<int> tears(config.inputs.size());
	trdrop::tasks::pre::TearPreTask tearPreT("Tear", config.inputs.size(), 20, 5);

	// FPSIntermediateTask
	std::vector<double> framerates(config.inputs.size());
	trdrop::tasks::inter::FPSInterTask fpsInterT(
			framerates,
			config.textLocations,
			config.refreshRate,
			config.colors,
			config.fpsText,
			config.fpsPrecision,
			config.shadows)
	;

	// ResizeTaks
	trdrop::tasks::post::ResizeTask resizeT(config.writerSize);

	// PlotTask
	trdrop::tasks::post::PlotTask plotT(framerates, config.colors, config.writerSize);

	// ViewerTask
	trdrop::tasks::post::ViewerTask viewerT(config.viewerSize);
	if (config.viewerActive) viewerT.init();

	// WriterTask
	trdrop::tasks::post::WriterTask writerT(config.outputFile, cv::VideoWriter::fourcc('X','2','6','4'), config.getBakedFPS(0), config.writerSize);

	// CMDProgressTask
	trdrop::tasks::post::CMDProgressTask cmdProgressT(config.getMinFrameIndex());

	// LoggerTask
	using tostring = trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFormatter>::tostring;
	std::vector<tostring> convertions;
	trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFormatter> loggerT(
		convertions,
		{ "Frameindex", "   " + fpsPreT.id }, // "      " + tearPreT.id
		config.inputNames,
		config.logName
	);
	convertions.push_back([&](int ix){
		return trdrop::util::string_format("%10i", scheduler.getCurrentFrameIndex());
	});
	convertions.push_back([&](int ix){
		return trdrop::util::string_format("%6." + std::to_string(config.fpsPrecision) + "f", framerates[ix]);
    });
	/*convertions.push_back([&](int ix) {
		std::string res = tears[ix] == -1 ? " false" : ("  true - " + std::to_string(tears[ix]));
		return res;
	});*/


	// PreTasks - order does not matter
	scheduler.addPreTask(std::make_shared<trdrop::tasks::pre::FPSPreTask>(fpsPreT));
	//scheduler.addPreTask(std::make_shared<trdrop::tasks::pre::TearPreTask>(tearPreT));

	// IntermediateTasks - order does not matter
	scheduler.addInterTask(std::make_shared<trdrop::tasks::inter::FPSInterTask>(fpsInterT));
	scheduler.addInterTask(std::make_shared<trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFormatter>>(loggerT));

	// PostTask - order matters
	scheduler.addPostTask(std::make_shared<trdrop::tasks::post::ResizeTask>(resizeT));
	scheduler.addPostTask(std::make_shared<trdrop::tasks::post::PlotTask>(plotT));
	if (config.viewerActive) scheduler.addPostTask(std::make_shared<trdrop::tasks::post::ViewerTask>(viewerT));
	scheduler.addPostTask(std::make_shared<trdrop::tasks::post::WriterTask>(writerT));

#if !_DEBUG
	scheduler.addPostTask(std::make_shared<trdrop::tasks::post::CMDProgressTask>(cmdProgressT));
#endif

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
			std::for_each(framerates.begin(), framerates.end(), [&](double framerates) {
				std::cout << framerates << ", ";
			});
			std::cout << '\n';
#endif
		}

		if (tearPreT.result.successful()) {
			// tears = tearPreT.result.getSuccess();
#if _DEBUG
			std::cout << "DEBUG: Main loop: got tears: ";
			std::for_each(tears.begin(), tears.end(), [&](int tear) {
				std::cout << tear << ", ";
			});
			std::cout << '\n';
#endif
		}

	}

	return EXIT_SUCCESS;
} 