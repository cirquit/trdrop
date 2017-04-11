#pragma once
#ifndef TRDROP_UTIL_VIDEO_H
#define TRDROP_UTIL_VIDEO_H

#include <ctime>
#include <iostream>
#include <string>

#include <opencv2/core.hpp>
#include <opencv2/highgui/highgui.hpp>


namespace util {
	
	namespace video {

		const std::string videoFrameName("Trdrop - VideoFrame");

		void initVideoFrame() {
			cv::namedWindow(videoFrameName, CV_WINDOW_NORMAL);
		}

		void showFrame(cv::Mat & frame, int delay = 0) {
			cv::imshow(videoFrameName, frame);
			if (delay > 0) cv::waitKey(delay);
		}

	} // namespace video
} // namespace util

#endif // !TRDROP_UTIL_VIDEO_H