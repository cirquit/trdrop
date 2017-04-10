#pragma once
#include <functional>
#include <ctime>
#include <iostream>
#include <string>

namespace trdrop {

	namespace util {

		double getCurrentFrameIndex(cv::VideoCapture & input) {
			return input.get(CV_CAP_PROP_POS_FRAMES);
		}

		double getWidth(cv::VideoCapture & input) {
			return input.get(CV_CAP_PROP_FRAME_WIDTH);
		}

		double getHeight(cv::VideoCapture & input) {
			return input.get(CV_CAP_PROP_FRAME_HEIGHT);
		}

		cv::Size getSize(cv::VideoCapture & input) {
			return cv::Size(static_cast<int>(getWidth(input)), static_cast<int>(getHeight(input)));
		}

		double getFrameCount(cv::VideoCapture & input) {
			return input.get(CV_CAP_PROP_FRAME_COUNT);
		}

		size_t getPixelCount(cv::VideoCapture & input) {
			return static_cast<size_t>(getWidth(input) * getHeight(input));
		}

		double getFrameRate(cv::VideoCapture & input) {
			return input.get(CV_CAP_PROP_FPS);
		}

		double getVideoLengthInSec(cv::VideoCapture & input) {
			double frameRate(getFrameRate(input));
			if (frameRate > 0) {
				return getFrameCount(input) / frameRate;
			}
			else { // framerate leq zero
				return 0;
			}

		}

		template<class T>
		T timeit(std::function<T> f) {
			std::clock_t start = std::clock();
			T res = f();
			std::cout << "Elapsed time: " << (std::clock() - start) / static_cast<double>(CLOCKS_PER_SEC / 1000) << "ms\n";
			return res;
		}

		
		void timeit_(std::function<void()> f) {
			std::clock_t start = std::clock();
			f();
			std::cout << "Elapsed time: " << (std::clock() - start) / static_cast<double>(CLOCKS_PER_SEC / 1000) << "ms\n";
		}

	} // namespace util
} // namespace trdrop