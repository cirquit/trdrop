#pragma once
#ifndef TRDROP_TASKS_INTER_FSD_H
#define TRDROP_TASKS_INTER_FSD_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>
#include <numeric>

#include "Tasks.h"
#include "fpsdata.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;
			
			class FPSTextTask : public posttask {

				// default member
			public:
				FPSTextTask() = delete;
				FPSTextTask(const FPSTextTask & other) = default;
				FPSTextTask & operator=(const FPSTextTask & other) = default;
				FPSTextTask(FPSTextTask && other) = default;
				FPSTextTask & operator=(FPSTextTask && other) = default;
				~FPSTextTask() = default;

				// specialized member
			public:
				FPSTextTask(trdrop::fps_data & fpsTaskData
						  , trdrop::tear_data & tearTaskData
						  , std::vector<cv::Point> points
					      , std::vector<int> refreshRate
					      , std::vector<cv::Scalar> colors
						  , std::vector<cv::Scalar> shadowColors
						  , std::vector<std::string> fpsText
						  , cv::Size writerFrameSize
						  , int precision = 2, bool shadows = true)
					: fpsTaskData(fpsTaskData)
					, tearTaskData(tearTaskData)
					, points(points)
					, precision(precision)
					, shadows(shadows)
					, refreshRate(refreshRate)
					, text(fpsTaskData.fps.size())
					, colors(colors)
					, shadowColors(shadowColors)
					, fpsText(fpsText)
					, writerFrameSize(writerFrameSize)
					, videoIxs(fpsTaskData.videoCount)
					, posttask(std::bind(&FPSTextTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{
					std::iota(videoIxs.begin(), videoIxs.end(), 0);
					tempFrameRates.assign(fpsTaskData.fps.begin(), fpsTaskData.fps.end());
				}

				// interface methods
			public:
				void process(cv::Mat & res, const size_t currentFrameIndex) {
					std::for_each(videoIxs.begin(), videoIxs.end(), [&](int vix) {
						drawText(res, currentFrameIndex, vix);
					});
				}

				// private functions
			private:

				std::function<void(cv::Mat &, const size_t, int)> drawText = [&](cv::Mat & res, const size_t currentFrameIndex, int vix) {

					if (currentFrameIndex % refreshRate[vix] == 0) {
						tempFrameRates[vix] = getFps(vix);
						/*
						trdrop::util::enumerate(fpsTaskData.fps_unprocessed[vix].begin(), fpsTaskData.fps_unprocessed[vix].end(), 0, [&](unsigned i, double d) {
							if (d == 1.0 && tearTaskData.tear_unprocessed[vix][i] == 0) {
								tempFrameRates[vix] += 1;
							}
						}); */
						fpsTaskData.fps[vix] = tempFrameRates[vix];
#if _TR_DEBUG
						std::cout << "DEBUG - FPSTextTask - copied the framerates\n";
#endif
					}

					text[vix] = trdrop::util::string_format("%." + std::to_string(precision) + "f", tempFrameRates[vix]);

					int textThickness = std::max(writerFrameSize.width / textThicknessRatio,1);
					double textSize = writerFrameSize.width / textSizeRatio;

					if (shadows) cv::putText(res, fpsText[vix] + text[vix], points[vix] + cv::Point(2, 2), CV_FONT_HERSHEY_SIMPLEX, textSize, shadowColors[vix], textThickness * 2, CV_AA);
					cv::putText(res, fpsText[vix] + text[vix], points[vix], CV_FONT_HERSHEY_SIMPLEX, textSize, colors[vix], textThickness, CV_AA);
#if _TR_DEBUG
					std::cout << "DEBUG: FPSTextTask[" << vix << "] - drawing \"" << text[vix] << "\"\n";
#endif
				};

				std::function<double(int)> getFps = [&](int vix) {
					double fps = 0.0;
					if (fpsTaskData.fps_unprocessed.size() > 0) {
						trdrop::util::enumerate(fpsTaskData.fps_unprocessed[vix].begin(), fpsTaskData.fps_unprocessed[vix].end(), 0, [&](unsigned i, double d) {
							if (d == 1.0 && tearTaskData.tear_unprocessed[vix][i] == 0) {
								fps += 1.0;
							}
						});
					}
					return fps;
				};

				// private member
			private:
				trdrop::fps_data &       fpsTaskData;
				trdrop::tear_data &      tearTaskData;
				std::vector<double>      tempFrameRates;
				std::vector<std::string> fpsText;
				std::vector<cv::Point>   points;
				std::vector<int>         refreshRate;
				std::vector<cv::Scalar>  colors;
				std::vector<cv::Scalar>  shadowColors;
				std::vector<std::string> text;
				const int			     precision;
				const bool		         shadows;

				const cv::Size			 writerFrameSize;
				const int				 textThicknessRatio = 580;   // 1920 / 4 - initial thickness
				const double             textSizeRatio = 1920;  // 1920 / 1 - initial size

				std::vector<int>         videoIxs;


			};
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_INTER_FSD_H