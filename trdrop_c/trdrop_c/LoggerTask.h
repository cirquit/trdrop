#pragma once
#ifndef TRDROP_TASKS_INTER_LOGGER_H
#define TRDROP_TASKS_INTER_LOGGER_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>

#include <opencv2\core\core.hpp>

#include "Tasks.h"
#include "utilvideo.h"

namespace trdrop {
	namespace tasks {
		namespace inter {

			using trdrop::tasks::intertask;

			template <class LoggerType>
			class LoggerTask : public intertask {

			// types
			public:
				using tostring = std::function<std::string()>;

				// default member
			public:
				LoggerTask() = default;
				LoggerTask(const LoggerTask & other) = default;
				LoggerTask & operator=(const LoggerTask & other) = delete;
				LoggerTask(LoggerTask && other) = default;
				LoggerTask & operator=(LoggerTask && other) = delete;
				~LoggerTask() = default;

				// specialized member
			public:
				LoggerTask(size_t sleepFrames, std::vector<tostring> & conversions
											 , std::vector<string> ids
											 , std::vector<string> logFileNames)
					: sleepFrames(sleepFrames)  // dump information every sleep frames
					, conversions(conversions)
					, ids(ids)
					, intertask(std::bind(&LoggerTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{
					std::transform(logFileNames.begin(), logFileNames.end(),std::back_inserter(loggers),
						[&](std::string logName) {
						return CSVFile(logName, ids, nullptr);
					};
				}

				// interface methods
			public:
				void process(cv::Mat & res, const size_t vix) {
					static std::vector<size_t> counter;
					if (counter[vix] % sleepFrames == 0) {
						std::vector<std::string> values(2);
						std::transform(conversions.begin(), conversions.end(), values.begin(), [&](tostring f) { return f(); });
						loggers[vix].log(values.begin(), values.end());
					}
					counter[vix] += 1;
				}

				// private member
			private:
				std::vector<LoggerType> loggers;
				std::vector<tostring> & conversions;
				const std::string filename;
				const size_t sleepFrames;
			};	
		} // namespace inter
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_INTER_LOGGER
