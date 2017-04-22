#pragma once
#ifndef TRDROP_TASKS_INTER_FSD_H
#define TRDROP_TASKS_INTER_FSD_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>

#include "Tasks.h"

namespace trdrop {
	namespace tasks {
		namespace inter {

			using trdrop::tasks::intertask;
			
			class FPSInterTask : public intertask {

				// default member
			public:
				FPSInterTask() = delete;
				FPSInterTask(const FPSInterTask & other) = default;
				FPSInterTask & operator=(const FPSInterTask & other) = delete;
				FPSInterTask(FPSInterTask && other) = default;
				FPSInterTask & operator=(FPSInterTask && other) = delete;
				~FPSInterTask() = default;

				// specialized member
			public:
				FPSInterTask(std::vector<double> & framerates, std::vector<cv::Point> points, int precision = 2, bool shadows = true, bool colorshift = true)
					: framerates(framerates)
					, points(points)
					, precision(precision)
					, shadows(shadows)
					, colorshift(colorshift) // TODO
					, intertask(std::bind(&FPSInterTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{}

				// interface methods
			public:
				void process(cv::Mat & res, const size_t vix) {
					// stringstream + setprecision does not add zeros to e.g 0 /=> 0.00
					std::string text = trdrop::util::string_format("FPS: %." + std::to_string(precision) + "f", framerates[vix]);
					if (shadows) cv::putText(res, text, points[vix]+cv::Point(3,3), CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 0, 0), 4, CV_AA);
					cv::putText(res, text, points[vix], CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255, 255, 255), 2, CV_AA);

#if _DEBUG
					std::cout << "DEBUG: FPSInterTask[" << vix << "] - drawing \"" << text << "\"\n";
#endif
				}

				// private member
			private:
				std::vector<double> &  framerates;
				std::vector<cv::Point> points;
				const int			   precision;
				const bool		       shadows;
				const bool		       colorshift;
			};
		} // namespace inter
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_INTER_FSD_H