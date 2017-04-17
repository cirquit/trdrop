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
					, colorshift(colorshift) // TODO
					, posttask(std::bind(&FPSPostTask::process
						, this
						, std::placeholders::_1)) {}

				// interface methods
			public:
				void process(cv::Mat & res) {
					// stringstream + setprecision does not add zeros to e.g 0 /=> 0.00
					std::string text = trdrop::util::string_format("FPS: %." + std::to_string(precision) + "f", framerate);
					if (shadows) cv::putText(res, text, point+cv::Point(3,3), CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 0, 0), 4, CV_AA);
					cv::putText(res, text, point, CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255, 255, 255), 2, CV_AA);

					
					cv::Size frameSize(res.size());
					cv::Scalar graphColor(200, 200, 200);
					
					int x = frameSize.width / 5;
					int y = frameSize.height / 3; //  *2;
					int height = frameSize.height / 3;
					int width = frameSize.width / 5 * 3;
					//y-line
					cv::line(res, cv::Point(x, y), cv::Point(x, y+height), graphColor, 3, 10);
					//x-line
					cv::line(res, cv::Point(x, y+height), cv::Point(x + width, y+height), graphColor, 3, 10);

				}

				// private member
			private:
				double & framerate;
				const cv::Point point;
				const int precision;
				const bool shadows;
				const bool colorshift;
			};
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_FSD_H