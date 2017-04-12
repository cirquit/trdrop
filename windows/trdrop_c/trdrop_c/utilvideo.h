#pragma once
#ifndef TRDROP_UTIL_VIDEO_H
#define TRDROP_UTIL_VIDEO_H

#include <ctime>
#include <iostream>
#include <string>

#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>

namespace trdrop {
	namespace util {
		namespace video {

			const std::string videoFrameName("Trdrop - VideoFrame");

			void initVideoFrame() {
				cv::namedWindow(videoFrameName, CV_WINDOW_NORMAL);
			}

			void resize(cv::Size size) {
				cv::resizeWindow(videoFrameName, size.width, size.height);
			}

			void showFrame(const cv::Mat & frame, int delay = 0) {
				cv::imshow(videoFrameName, frame);
				if (delay > 0) {
					cv::waitKey(delay);
				}
				else {
					cv::waitKey();
				}
			}

		} // namespace video
	} // namespace util
} // namespace trdrop

#endif // !TRDROP_UTIL_VIDEO_H