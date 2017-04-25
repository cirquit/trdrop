#pragma once
#ifndef TRDROP_TASKS_POST_CMDPROGRESS_H
#define TRDROP_TASKS_POST_CMDPROGRESS_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>
#include <string>

#include <opencv2\core\core.hpp>

#include "Tasks.h"
#include "util.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;

			class CMDProgressTask : public posttask {

				// default member
			public:
				CMDProgressTask() = delete;
				CMDProgressTask(const CMDProgressTask & other) = default;
				CMDProgressTask & operator=(const CMDProgressTask & other) = delete;
				CMDProgressTask(CMDProgressTask && other) = default;
				CMDProgressTask & operator=(CMDProgressTask && other) = delete;
				~CMDProgressTask() = default;

				// specialized member
			public:
				CMDProgressTask(int maxIndex)
					: maxIndex(maxIndex)
					, posttask(std::bind(&CMDProgressTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{}

				// interface methods
			public:
				void process(cv::Mat & res, size_t currentFrameIndex) {
					double progress = static_cast<double>(currentFrameIndex) / static_cast<double>(maxIndex);
					int width = 50;
					int chars = static_cast<int>(progress * width);
					int spaces = width - chars;

					std::cout << "Progress: ["
						<< std::string(chars, '#')
						<< std::string(spaces, ' ')
						<< "] "
						<< trdrop::util::string_format("%3.2f", progress * 100)
						<< "%\r"
						<< std::flush;
				}

				// private member
			private:
				const int maxIndex;
			};
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_POST_CMDPROGRESS_H
