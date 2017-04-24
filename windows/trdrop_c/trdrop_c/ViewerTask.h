#pragma once
#ifndef TRDROP_TASKS_POST_VIEWER_H
#define TRDROP_TASKS_POST_VIEWER_H

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

			class ViewerTask : public posttask {

				// default member
			public:
				ViewerTask() = delete;
				ViewerTask(const ViewerTask & other) = default;
				ViewerTask & operator=(const ViewerTask & other) = delete;
				ViewerTask(ViewerTask && other) = default;
				ViewerTask & operator=(ViewerTask && other) = delete;
				~ViewerTask() = default;

				// specialized member
			public:
				ViewerTask(int delay, cv::Size size)
					: delay(delay)
					, posttask(std::bind(&ViewerTask::process
						, this
						, std::placeholders::_1))
				{
					std::cout << "Config - setting size to " << size << '\n';
					trdrop::util::video::resize(size);
				}

				ViewerTask(cv::Size size)
					: ViewerTask(1, size) {}

				// interface methods
			public:
				void process(cv::Mat & res) {
					trdrop::util::video::showFrame(res, delay);
				}

				// public member
			public:
				std::function<void()> init = [&]() { trdrop::util::video::initVideoFrame(); };

				// private member
			private:
				const int delay;
			};
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_POST_VIEWER
