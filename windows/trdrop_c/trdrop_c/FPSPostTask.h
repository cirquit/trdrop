#pragma once
#ifndef TRDROP_TASKS_POST_FSD_H
#define TRDROP_TASKS_POST_FSD_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>

#include "Tasks.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;
			
			class FPSPostTask : public posttask {

				// default member
			public:
				FPSPostTask() = delete;
				FPSPostTask(const FPSPostTask & other) = default;
				FPSPostTask & operator=(const FPSPostTask & other) = delete;
				FPSPostTask(FPSPostTask && other) = default;
				FPSPostTask & operator=(FPSPostTask && other) = delete;
				~FPSPostTask() = default;

				// specialized member
			public:
				FPSPostTask(double & framerate, cv::Point point, int precision = 2,  bool shadows = true, bool colorshift = true)
					: framerate(framerate)
					, point(point)
					, precision(precision)
					, shadows(shadows)
					, colorshift(colorshift)
					, posttask(std::bind(&FPSPostTask::process
						, this
						, std::placeholders::_1)) {}

				// interface methods
			public:
				void process(cv::Mat & res) {
					std::stringstream text;
					text << std::setprecision(precision) << "FPS: " << framerate << '\n';
					cv::putText(res, text.str(), point+cv::Point(3,3), CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 0, 0), 1+2, CV_AA);
					cv::putText(res, text.str(), point, CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255, 255, 255), 1, CV_AA);
				}

				// private methods
			private:
				// private member
			private:
				double & framerate;
				const cv::Point point;
				const int precision;
				const bool shadows;
				const bool colorshift;

			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_FSD_H