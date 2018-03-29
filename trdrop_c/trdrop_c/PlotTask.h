#pragma once
#ifndef TRDROP_TASKS_POST_PLOT_H
#define TRDROP_TASKS_POST_PLOT_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>
#include <deque>
#include <vector>

#include <opencv2\core\core.hpp>

#include "Tasks.h"
#include "util.h"
#include "teardata.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;

			class PlotTask : public posttask {

				// default member
			public:
				PlotTask() = delete;
				PlotTask(const PlotTask & other) = default;
				PlotTask & operator=(const PlotTask & other) = delete;
				PlotTask(PlotTask && other) = default;
				PlotTask & operator=(PlotTask && other) = delete;
				~PlotTask() = default;

				// specialized member
			public:
				PlotTask(trdrop::fps_data & fpsTaskData, trdrop::tear_data & tearTaskData, std::vector<cv::Scalar> colors, std::vector<cv::Scalar> tearColors, cv::Scalar plotBackgroundColor, cv::Scalar plotLinesColor, cv::Scalar plotAxesColor, double plotAlpha, cv::Size writerFrameSize)
					: fpsTaskData(fpsTaskData)
					, tearTaskData(tearTaskData)
					, colors(colors)
					, tearColors(tearColors)
					, plotBackgroundColor(plotBackgroundColor)
					, plotLinesColor(plotLinesColor)
					, plotAxesColor(plotAxesColor)
					, plotAlpha(plotAlpha)
					, fpsContainer(fpsTaskData.videoCount)
					, tearContainer(fpsTaskData.videoCount)
					, timeContainer(fpsTaskData.videoCount)
					, writerFrameSize(writerFrameSize)
					, posttask(std::bind(&PlotTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{	
					margin = writerFrameSize.width / marginScalingRatio;
					height = writerFrameSize.height / 4;
					width = writerFrameSize.width - 2 * margin;

					std::for_each(fpsContainer.begin(), fpsContainer.end(), [&](std::deque<double> & dd) {
						dd.insert(dd.end(), plotWindow(), 0.0);
					});

					std::for_each(tearContainer.begin(), tearContainer.end(), [&](std::deque<double> & dd) {
						dd.insert(dd.end(), plotWindow(), 0.0);
					});
				}

				// interface methods
			public:
				void process(cv::Mat & res, const size_t currentFrameCount) {
					int plotWindow_ = plotWindow();
					
					// remove oldest values
					util::enumerate(fpsContainer.begin(), fpsContainer.end(), 0, [&](size_t i, std::deque<double> & dd) {
						dd.push_back(getFps(i));
						dd.pop_front();
					});

					util::enumerate(tearContainer.begin(), tearContainer.end(), 0, [&](size_t i, std::deque<double> & dd) {
						double tear = fpsTaskData.duplicateFrame[i] ? 0 : tearTaskData.tears[i];
						dd.push_back(tear);
						dd.pop_front();
					});

					drawGrid(res);
					drawLines(res);
					drawTears(res);
				}

				// public member
			public:

				std::function<int()> plotWindow = [&]() { return (writerFrameSize.width - 2 * margin) / 10;  };

				std::function<void(cv::Mat & res)> drawGrid = [&](cv::Mat & res) {
					
					// graph starting points
					int x = margin;
					int y = writerFrameSize.height - margin - height;

					// extra space above 60fps line in px
					int overhead = 6; // 20; // writerFrameSize.width / 320;
					
					// graph background
					cv::Mat roi = res(cv::Rect(x, y - overhead, width, height+ overhead));
					cv::Mat color(roi.size(), CV_8UC3, plotBackgroundColor);
					cv::addWeighted(color, plotAlpha, roi, 1.0 - plotAlpha, 0.0, roi);
					
					// a little brighter than the background
					//cv::Scalar sepLineColor = cv::Scalar(plotBackgroundColor[0] + 40 % 255
					//							     , plotBackgroundColor[1] + 40 % 255
					//							     , plotBackgroundColor[2] + 40 % 255);


					int spriteWScale = writerFrameSize.width / spriteWidthScaleRatio;
					int spriteHScale = writerFrameSize.width / spriteHeightScaleRatio;

					int spriteXOffset = writerFrameSize.width / spriteXScaleRatio;
					int spriteYOffset = writerFrameSize.width / spriteYScaleRatio;

					int sepLineThickness = writerFrameSize.width / separationLineThicknessRatio;
					int lineYOffset = writerFrameSize.width / lineYOffsetRatio;

					// separation lines
					for (int i = 1; i < 6; ++i) {
						int lineY = (maxFps - 10 * i*height / maxFps) + writerFrameSize.height - maxFps - margin;
						cv::line(res, cv::Point(x, lineY- lineYOffset), cv::Point(x + width, lineY- lineYOffset), plotLinesColor, sepLineThickness, CV_AA);
						cv::resize(number_sprites[i-1], number_sprites[i-1], cv::Size(spriteWScale, spriteHScale));
						util::overlayImage(res, number_sprites[i-1], res, cv::Point2i(x - spriteXOffset, lineY - spriteYOffset));
					}
				
					int graphLineThickness = writerFrameSize.width / graphLineThicknessRatio;

					// y-line
					cv::line(res, cv::Point(x, y - overhead), cv::Point(x, y + height), plotAxesColor, graphLineThickness, CV_AA);

					// y-line text with shadows

					int fpsSpriteWScale = writerFrameSize.width / fpsSpriteWidthScaleRatio;
					int fpsSpriteHScale = writerFrameSize.width / fpsSpriteHeightScaleRatio;

					int fpsSpriteXOffset = writerFrameSize.width / fpsSpriteXScaleRatio;
					int fpsSpriteYOffset = writerFrameSize.width / fpsSpriteYScaleRatio;

					cv::resize(fps_sprite, fps_sprite, cv::Size(fpsSpriteWScale, fpsSpriteHScale));
					util::overlayImage(res, fps_sprite, res, cv::Point2i(x - fpsSpriteXOffset, y - fpsSpriteYOffset - overhead));


					// x-line
					cv::line(res, cv::Point(x, y + height), cv::Point(x + width, y + height), plotAxesColor, graphLineThickness, CV_AA);

				};

				std::function<void(cv::Mat & res)> drawLines = [&](cv::Mat & res) {

					int pointDistance = margin + writerFrameSize.width / pointDistanceRatio;
					int pointDistanceIncrement = width / plotWindow();

					cv::Point lastPoint(margin, writerFrameSize.height - margin - 4);
					std::vector<cv::Point> lastPoints(fpsTaskData.videoCount, lastPoint);

					int lineThickness = writerFrameSize.width / lineThicknessRatio;
					int lineYOffset	  = writerFrameSize.width / lineYOffsetRatio;
					int lastLineXOffSet = writerFrameSize.width / lastLineXOffSetRatio;

					util::enumerate(fpsContainer[0].begin(), fpsContainer[0].end(), 0, [&](size_t i, double fps) {
						util::enumerate(fpsContainer.begin(), fpsContainer.end(), 0, [&](size_t vix, std::deque<double> fpsDeque) {

							int currentFps = static_cast<int>(fpsDeque[i]);
							int y = (maxFps - currentFps*height / maxFps) + writerFrameSize.height - maxFps - margin - lineYOffset;
							cv::Point currentPoint(pointDistance, y);

							// set the first point to the start of the grid
							if (i == 0) lastPoints[vix] = currentPoint; 

							// set the last point to the end of the grid
							// custom offset...because we need to rewrite the whole orientation
							if (i == fpsContainer[0].size() - 1) currentPoint.x = width + margin - lastLineXOffSet;

							cv::line(res, lastPoints[vix], currentPoint, colors[vix], lineThickness, CV_AA);
							lastPoints[vix] = currentPoint;
						});
						pointDistance += pointDistanceIncrement;
					});
				};

				std::function<void(cv::Mat & res)> drawTears = [&](cv::Mat & res) {
					
					int pointDistance = margin + 6;
					int pointDistanceIncrement = width / plotWindow();
					int tearHeight = height / static_cast<int>(tearContainer.size()); // Fit all videos into the graph
					int baseHeight = writerFrameSize.height - margin - 4;
					
					int lineThickness = writerFrameSize.width / lineThicknessRatio;

					util::enumerate(tearContainer[0].begin(), tearContainer[0].end(), 0, [&](size_t i, double tear) {
						util::enumerate(tearContainer.begin(), tearContainer.end(), 0, [&](size_t vix, std::deque<double> tearDeque) {
							if (tearDeque[i] != 0) {
                                unsigned vix_int = (unsigned)vix;
								cv::Point basePoint(pointDistance, baseHeight - vix_int * tearHeight);
								cv::Point topPoint(pointDistance, baseHeight - tearHeight - vix_int * tearHeight);
								cv::Point midPoint(pointDistance, static_cast<int>(baseHeight - tearDeque[i] * tearHeight - vix_int * tearHeight));
								cv::line(res, basePoint, midPoint, tearColors[vix], lineThickness, CV_AA);
								cv::line(res, midPoint, topPoint, colors[vix], lineThickness, CV_AA);
							}
						});
						pointDistance += pointDistanceIncrement;
					});
				};

				std::function<double(size_t)> getFps = [&](size_t vix) {
					double fps = 0.0;
					if (fpsTaskData.fps_unprocessed.size() > 0) {
						trdrop::util::enumerate(fpsTaskData.fps_unprocessed[vix].begin(), fpsTaskData.fps_unprocessed[vix].end(), 0, [&](size_t i, double d) {
							if (d == 1.0 && tearTaskData.tear_unprocessed[vix][i] == 0) {
								fps += 1.0;
							}
						});
					}
					return fps;
				};


				/*
				std::function<void(cv::Mat & res)> drawFrametimes = [&](cv::Mat & res) {

					int pointDistance = margin + 6;
					int pointDistanceIncrement = width / plotWindow();
					int baseHeight = writerFrameSize.height - margin - 4;

					cv::Point lastPoint(pointDistance, baseHeight);
					std::vector<cv::Point> lastPoints(fpsTaskData.videoCount, lastPoint);

					util::enumerate(timeContainer[0].begin(), timeContainer[0].end(), 0, [&](unsigned i, double time) {
						util::enumerate(timeContainer.begin(), timeContainer.end(), 0, [&](unsigned vix, std::deque<double> timeDeque) {
							int currentTime = static_cast<int>(timeDeque[i]);
							int y = (60 - currentTime*height / 60) + baseHeight - 60;
							cv::Point currentPoint(pointDistance, y);
							if (i == 0) lastPoints[vix] = currentPoint;
							cv::line(res, lastPoints[vix], currentPoint, colors[vix], 2, CV_AA);
							lastPoints[vix] = currentPoint;
						});
						pointDistance += pointDistanceIncrement;
					});
				};
				*/

				// private member
			private:
				trdrop::fps_data    & fpsTaskData;
				trdrop::tear_data   & tearTaskData;
				std::vector<std::deque<double>> fpsContainer;
				std::vector<std::deque<double>> tearContainer;
				std::vector<std::deque<double>> timeContainer;

				std::vector<cv::Scalar> colors;
				std::vector<cv::Scalar> tearColors;
				const cv::Scalar graphColor = cv::Scalar(255, 255, 255);
				cv::Scalar plotBackgroundColor;
				cv::Scalar plotLinesColor;
				cv::Scalar plotAxesColor;

				double		   plotAlpha;
				int            margin;
				int			   height; 
				int			   width;
				const cv::Size writerFrameSize;

				const int	   maxFps = 60;


				const int marginScalingRatio      = 64;   // 1920 / 30, because 30 was our initial px setting for 1080p 

				const int spriteWidthScaleRatio   = 87;   // 1920 / 22, init px settings
				const int spriteHeightScaleRatio  = 83;   // 1920 / 23, init px settings
				const int spriteXScaleRatio	      = 69;   // 1920 / 28, init px settings
				const int spriteYScaleRatio		  = 213;  // 1920 / 9,  init px settings

				const int fpsSpriteWidthScaleRatio  = 51;  // 1920 / 37, init px settings
				const int fpsSpriteHeightScaleRatio = 76;  // 1920 / 25, init px settings
				const int fpsSpriteXScaleRatio		= 76;  // 1920 / 25, init px settings
				const int fpsSpriteYScaleRatio	    = 76;  // 1920 / 25,  init px settings

				const int lineThicknessRatio		   = 960;  // 1920 / 2, init px thickness
				const int separationLineThicknessRatio = 1920; // 1920 / 1, init px thickness
				const int graphLineThicknessRatio      = 384;  // 1920 / 5, init px thickness

				const int pointDistanceRatio		   = 320;  // 1920 / 6, init px offset
				const int lineYOffsetRatio			   = 480;  // 1920 / 4, init px offset
				const int lastLineXOffSetRatio		   = 960;  // 1920 / 2, init px offset 
				
#if _DEBUGPATH
				const std::string prep = "../../../images/";
#else 
				const std::string prep = ""; 
#endif
				cv::Mat fps_sprite    = cv::imread(prep + "trdrop_sprites/fps_sprite.png", -1);
				cv::Mat ten_sprite    = cv::imread(prep + "trdrop_sprites/10_sprite.png",  -1);
				cv::Mat twenty_sprite = cv::imread(prep + "trdrop_sprites/20_sprite.png",  -1);
				cv::Mat thirty_sprite = cv::imread(prep + "trdrop_sprites/30_sprite.png",  -1);
				cv::Mat fourty_sprite = cv::imread(prep + "trdrop_sprites/40_sprite.png",  -1);
				cv::Mat fifty_sprite  = cv::imread(prep + "trdrop_sprites/50_sprite.png",  -1);
				std::vector<cv::Mat> number_sprites = { ten_sprite, twenty_sprite, thirty_sprite, fourty_sprite, fifty_sprite };
			};
		}// namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_POST_PLOT_H