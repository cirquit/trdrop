#pragma once
#ifndef TRDROP_TASKS_POST_RESIZE_H
#define TRDROP_TASKS_POST_RESIZE_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>

#include <opencv2\core\core.hpp>

#include "Tasks.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;

			class ResizeTask : public posttask {

				// default member
			public:
				ResizeTask() = delete;
				ResizeTask(const ResizeTask & other) = default;
				ResizeTask & operator=(const ResizeTask & other) = delete;
				ResizeTask(ResizeTask && other) = default;
				ResizeTask & operator=(ResizeTask && other) = delete;
				~ResizeTask() = default;

				// specialized member
			public:
				ResizeTask(cv::Size frameSize)
					: frameSize(frameSize)
					, posttask(std::bind(&ResizeTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{}

				// interface methods
			public:
				void process(const cv::Mat & res, const size_t currentFrameIndex) {
					if (res.size() != frameSize) {
						cv::resize(res, res, frameSize);
					}
				}

				// private member
			private:
				const cv::Size frameSize;
			};
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_POST_RESIZE_H
