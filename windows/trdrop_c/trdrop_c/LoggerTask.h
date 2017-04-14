#pragma once
#ifndef TRDROP_TASKS_POST_LOGGER_H
#define TRDROP_TASKS_POST_LOGGER_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>

#include <opencv2\core\core.hpp>

#include "Tasks.h"
#include "utilvideo.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;


			template <class LoggerType>
			class LoggerTask : public posttask {

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
				LoggerTask(std::string filename, size_t sleepFrames, LoggerType & log, std::vector<tostring> & convertions)
					: filename(filename)
					, sleepFrames(sleepFrames)  // every sleepFrames-Frame log information
					, log(log)                 
					, convertions(convertions)
					, posttask(std::bind(&LoggerTask::process
						, this
						, std::placeholders::_1))
				{ }

				// interface methods
			public:
				void process(cv::Mat & res) {
					static size_t counter;
					if (counter % sleepFrames == 0) {
						std::cout << "Process tries to log something with these values - FPS: " << convertions[0]() << ", Framecount: " << convertions[1]() << '\n';
						std::vector<std::string> values = { "2.0", "60" };
						std::transform(convertions.begin(), convertions.end(), values.begin(), [&](tostring f) { return f(); });
						// std::for_each(values.begin(), values.end(), [&](std::string e) { std::cout << e; });
						log.log(values.begin(), values.end());
					}
					counter += 1;
				}

				// private member
			private:
				LoggerType & log;
				std::vector<tostring> & convertions;
				const std::string filename;
				const size_t sleepFrames;
			};	
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_POST_LOGGER
