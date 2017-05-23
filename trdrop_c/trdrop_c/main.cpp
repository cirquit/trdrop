#define _DEBUG 1
#define DEBUG(context, x) do { \
	if (_DEBUG) std::cerr << "DEBUG: " << context << " - " << #x << ":\n    " << x << std::endl; } \
 while (0)

#define DEBUGV(context, vector) do { \
	if (_DEBUG) { \
		int i = 0; \
		std::cerr << "DEBUG: " << context << " - " << #vector << ": \n"; \
		for (auto & v : vector) { std::cerr << "         " << std::string(" ", sizeof context) << #vector << '[' << i++ << "]: " << v << '\n'; } \
	} } while (0)

#define _DEBUGPATH 0

#include <iostream>
#include <string>
#include <algorithm>
#include <time.h>
#include <vector>
#include <functional>
#include <cstdlib>

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

#include "fpsdata.h"
#include "teardata.h"


int main(int argc, char **argv) {

	trdrop::config::Config config(argc, argv);

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
	trdrop::tasks::pre::FPSPreTask fpsPreT("FPS", config.inputs.size(), config.pixelDifference, config.refreshRate);

	// TearPreTask
	trdrop::tear_data tearTaskData(config.inputs.size());
	trdrop::tasks::pre::TearPreTask tearPreT("Tear", config.inputs.size(), config.pixelDifference, config.lineDifference);

	// FPSIntermediateTask
	trdrop::fps_data    fpsTaskData(config.inputs.size());
	trdrop::tasks::inter::FPSInterTask fpsInterT(
			fpsTaskData,
			tearTaskData,
			config.textLocations,
			config.refreshRate,
			config.colors,
			config.shadowColors,
			config.fpsText,
			config.fpsPrecision,
			config.shadows)
	;
	// ResizeTaks
	trdrop::tasks::post::ResizeTask resizeT(config.writerSize);

	// PlotTask
	trdrop::tasks::post::PlotTask plotT(fpsTaskData, tearTaskData, config.colors, config.writerSize);

	// ViewerTask
	trdrop::tasks::post::ViewerTask viewerT(config.viewerSize);
	if (config.viewerActive) viewerT.init();

	// WriterTask
	trdrop::tasks::post::WriterTask writerT(config.outputFile, config.codec, config.getBakedFPS(0), config.writerSize);

	// CMDProgressTask
	trdrop::tasks::post::CMDProgressTask cmdProgressT(config.getMinFrameIndex());

	// LoggerTask
	using tostring = trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFormatter>::tostring;
	std::vector<tostring> convertions;
	trdrop::tasks::inter::LoggerTask<trdrop::util::CSVFormatter> loggerT(
		convertions,
		{ "Frameindex", "   " + fpsPreT.id, "        " + tearPreT.id },
		config.inputNames,
		config.logName
	);
	convertions.push_back([&](int ix){
		return trdrop::util::string_format("%10i", scheduler.getCurrentFrameIndex());
	});
	convertions.push_back([&](int ix){
		return trdrop::util::string_format("%6." + std::to_string(config.fpsPrecision) + "f", fpsTaskData.fps[ix]);
    });
	convertions.push_back([&](int ix) {
		return tearTaskData.tears[ix] == 0 ? "       false" : "  " + std::to_string(static_cast<int>(tearTaskData.tears[ix] * 100)) + "%" + " - true";
	});

	// PreTasks - order does not matter
	scheduler.addPreTask(std::make_shared<trdrop::tasks::pre::FPSPreTask>(fpsPreT));
	scheduler.addPreTask(std::make_shared<trdrop::tasks::pre::TearPreTask>(tearPreT));

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

		// glue FPS source -> FPS consumer
		if (fpsPreT.result.successful()) {
			fpsTaskData = fpsPreT.result.getSuccess();
			DEBUG("Main loop: FpsTaskData", fpsTaskData.to_string());
		}

		if (tearPreT.result.successful()) {
			tearTaskData = tearPreT.result.getSuccess();
			DEBUGV("Main loop: Tears", tearTaskData.tears);
		}


	}
	return EXIT_SUCCESS;
} 