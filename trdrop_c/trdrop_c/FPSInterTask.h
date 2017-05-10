#pragma once
#ifndef TRDROP_TASKS_INTER_FSD_H
#define TRDROP_TASKS_INTER_FSD_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>

#include "Tasks.h"
#include "fpsdata.h"

namespace trdrop {
	namespace tasks {
		namespace inter {

			using trdrop::tasks::intertask;
			
			class FPSInterTask : public intertask {

				// default member
			public:
				FPSInterTask() = delete;
				FPSInterTask(const FPSInterTask & other) = default;
				FPSInterTask & operator=(const FPSInterTask & other) = default;
				FPSInterTask(FPSInterTask && other) = default;
				FPSInterTask & operator=(FPSInterTask && other) = default;
				~FPSInterTask() = default;

				// specialized member
			public:
				FPSInterTask(trdrop::fps_data & fpsTaskData
						  , std::vector<cv::Point> points
					      , std::vector<int> refreshRate
					      , std::vector<cv::Scalar> colors
						  , std::vector<cv::Scalar> shadowColors
						  , std::vector<std::string> fpsText
						  , int precision = 2, bool shadows = true)
					: fpsTaskData(fpsTaskData)
					, points(points)
					, precision(precision)
					, shadows(shadows)
					, refreshRate(refreshRate)
					, text(fpsTaskData.fps.size())
					, colors(colors)
					, shadowColors(shadowColors)
					, fpsText(fpsText)
					, intertask(std::bind(&FPSInterTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3))
				{
					tempFrameRates.assign(fpsTaskData.fps.begin(), fpsTaskData.fps.end());
				}

				// interface methods
			public:
				void process(cv::Mat & res, const size_t currentFrameIndex, const size_t vix) {
					if (currentFrameIndex % refreshRate[vix] == 0) {
						tempFrameRates.assign(fpsTaskData.fps.begin(), fpsTaskData.fps.end());
#if _DEBUG
						std::cout << "DEBUG - FPSInterTask - copied the framerates\n";
#endif
					}
		
					// stringstream + setprecision does not add zeros to e.g 0 /=> 0.00
					text[vix] = trdrop::util::string_format("%." + std::to_string(precision) + "f", tempFrameRates[vix]);

					if (shadows) cv::putText(res, fpsText[vix] + text[vix], points[vix] + cv::Point(2, 2), CV_FONT_HERSHEY_SIMPLEX, 1, shadowColors[vix], 4, CV_AA);
					cv::putText(res, fpsText[vix] + text[vix], points[vix], CV_FONT_HERSHEY_SIMPLEX, 1, colors[vix], 2, CV_AA);
#if _DEBUG
					std::cout << "DEBUG: FPSInterTask[" << vix << "] - drawing \"" << text[vix] << "\"\n";
#endif
				}

				// private member
			private:
				trdrop::fps_data &       fpsTaskData;
				std::vector<double>      tempFrameRates;
				std::vector<std::string> fpsText;
				std::vector<cv::Point>   points;
				std::vector<int>         refreshRate;
				std::vector<cv::Scalar>  colors;
				std::vector<cv::Scalar>  shadowColors;
				std::vector<std::string> text;
				const int			     precision;
				const bool		         shadows;

			};
		} // namespace inter
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_INTER_FSD_H