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
				FPSInterTask(std::vector<double> & framerates, std::vector<cv::Point> points, std::vector<int> refreshRate, int precision = 2, bool shadows = true)
					: framerates(framerates)
					, points(points)
					, precision(precision)
					, shadows(shadows)
					, refreshRate(refreshRate)
					, text(framerates.size())
					, intertask(std::bind(&FPSInterTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3))
				{
					tempFrameRates.assign(framerates.begin(), framerates.end());
				}

				// interface methods
			public:
				void process(cv::Mat & res, const size_t currentFrameIndex, const size_t vix) {
					if (currentFrameIndex % refreshRate[vix] == 0) {
						tempFrameRates.assign(framerates.begin(), framerates.end());
#if _DEBUG
						std::cout << "DEBUG - FPSInterTask - copied the framerates\n";
#endif
					}
		
					// stringstream + setprecision does not add zeros to e.g 0 /=> 0.00
					text[vix] = trdrop::util::string_format("FPS: %." + std::to_string(precision) + "f", tempFrameRates[vix]);

					if (shadows) cv::putText(res, text[vix], points[vix] + cv::Point(3, 3), CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 0, 0), 4, CV_AA);
					cv::putText(res, text[vix], points[vix], CV_FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(255, 255, 255), 2, CV_AA);
#if _DEBUG
					std::cout << "DEBUG: FPSInterTask[" << vix << "] - drawing \"" << text[vix] << "\"\n";
#endif
				}

				// private member
			private:
				std::vector<double> &  framerates;
				std::vector<double>    tempFrameRates;
				std::vector<cv::Point> points;
				std::vector<int>       refreshRate;
				std::vector<std::string> text;
				const int			   precision;
				const bool		       shadows;

			};
		} // namespace inter
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_INTER_FSD_H