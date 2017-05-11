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
				PlotTask(trdrop::fps_data & fpsTaskData, std::vector<double> & tears, std::vector<cv::Scalar> colors, cv::Size frameSize)
					: fpsTaskData(fpsTaskData)
					, tears(tears)
					, colors(colors)
					, fpsContainer(fpsTaskData.videoCount)
					, tearContainer(tears.size())
					, frameSize(frameSize)
					, height(frameSize.height / 4)
					, width(frameSize.width - 2 * margin)
					, posttask(std::bind(&PlotTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{
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
					util::enumerate(fpsContainer.begin(), fpsContainer.end(), 0, [&](unsigned i, std::deque<double> & dd) {
						dd.push_back(fpsTaskData.fps[i]);
						dd.pop_front();
					});

					util::enumerate(tearContainer.begin(), tearContainer.end(), 0, [&](unsigned i, std::deque<double> & dd) {
						double tear = fpsTaskData.duplicateFrame[i] ? 0 : tears[i];
						dd.push_back(tear);
						dd.pop_front();
					});

					drawGrid(res);
					drawLines(res);
					drawTears(res);
				}

				// public member
			public:

				std::function<int()> plotWindow = [&]() { return (frameSize.width - 2 * margin) / 10;  };
				std::function<void(cv::Mat & res)> drawGrid = [&](cv::Mat & res) {
					
					// graph starting points
					int x = margin;
					int y = frameSize.height - margin - height;
					
					// graph background
					cv::Mat roi = res(cv::Rect(x, y, width, height));
					cv::Mat color(roi.size(), CV_8UC3, graphColor);
					double alpha = 0.4;
					cv::addWeighted(color, alpha, roi, 1.0 - alpha, 0.0, roi);
					
					// y-line
					cv::line(res, cv::Point(x, y), cv::Point(x, y + height), graphColor, 3, 10);

					// y-line text with shadows
					util::overlayImage(res, fps_sprite, res, cv::Point2i(x - 18, y - 28));

					// x-line
					cv::line(res, cv::Point(x, y + height), cv::Point(x + width, y + height), graphColor, 3, 10);
					
					// separation lines
					for (int i = 1; i < 6; ++i) {
						int lineY = (60 - 10 * i*height / 60) + frameSize.height - 60 - margin;
						cv::line(res, cv::Point(x, lineY-4), cv::Point(x + width, lineY-4), graphColor);
						cv::resize(number_sprites[i-1], number_sprites[i-1], cv::Size(22, 23));
						util::overlayImage(res, number_sprites[i-1], res, cv::Point2i(x - 28, lineY-9));
					}
				
				};

				std::function<void(cv::Mat & res)> drawLines = [&](cv::Mat & res) {

					int pointDistance = margin;
					int pointDistanceIncrement = width / plotWindow();

					cv::Point lastPoint(margin + 6, frameSize.height - margin - 4);
					std::vector<cv::Point> lastPoints(fpsTaskData.videoCount, lastPoint);


					util::enumerate(fpsContainer[0].begin(), fpsContainer[0].end(), 0, [&](unsigned i, double fps) {
						util::enumerate(fpsContainer.begin(), fpsContainer.end(), 0, [&](unsigned vix, std::deque<double> fpsDeque) {
							int currentFps = static_cast<int>(fpsDeque[i]);
							int y = (60 - currentFps*height / 60) + frameSize.height - 60 - margin - 4;
							cv::Point currentPoint(pointDistance + 6, y);
							if (i == 0) lastPoints[vix] = currentPoint;
							cv::line(res, lastPoints[vix], currentPoint, colors[vix], 2, CV_AA);
							lastPoints[vix] = currentPoint;
						});
						pointDistance += pointDistanceIncrement;
					});
				};

				std::function<void(cv::Mat & res)> drawTears = [&](cv::Mat & res) {

					cv::Scalar tearColor(0,0,200);
					int pointDistance = margin;
					int pointDistanceIncrement = width / plotWindow();
					int tearHeight = height / tearContainer.size(); // Fit all all videos into the graph

					util::enumerate(tearContainer[0].begin(), tearContainer[0].end(), 0, [&](unsigned i, double tear) {
						util::enumerate(tearContainer.begin(), tearContainer.end(), 0, [&](unsigned vix, std::deque<double> tearDeque) {
							if (tearDeque[i] != 0) {
								cv::Point basePoint(pointDistance + 6, frameSize.height - margin - 4);
								cv::Point topPoint(pointDistance + 6, frameSize.height - margin - tearHeight + vix * tearHeight);
								cv::Point midPoint(pointDistance + 6, frameSize.height - margin - tearDeque[i] * tearHeight);
								cv::line(res, basePoint, midPoint, tearColor, 2, CV_AA);
								cv::line(res, midPoint, topPoint, colors[vix], 2, CV_AA);
							}
						});
						pointDistance += pointDistanceIncrement;
					});
				};
					

				// private member
			private:
				trdrop::fps_data    & fpsTaskData;
				std::vector<double> & tears;
				std::vector<std::deque<double>> fpsContainer;
				std::vector<std::deque<double>> tearContainer;

				std::vector<cv::Scalar> colors;
				const cv::Scalar graphColor = cv::Scalar(255, 255, 255);
				const int margin = 30; // px
				const cv::Size frameSize;
				const int height; 
				const int width;
				
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