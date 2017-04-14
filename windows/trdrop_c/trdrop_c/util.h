#pragma once
#ifndef TRDROP_UTIL_H
#define TRDROP_UTIL_H

#include <functional>
#include <iterator>
#include <ctime>
#include <iostream>
#include <string>
#include <memory>
#include <cstdio>

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

		template<typename ... Args>
		std::string string_format(const std::string& format, Args ... args)
		{
			size_t size = std::snprintf(nullptr, 0, format.c_str(), args ...) + 1; // Extra space for '\0'
			std::unique_ptr<char[]> buf(new char[size]);
			std::snprintf(buf.get(), size, format.c_str(), args ...);
			return std::string(buf.get(), buf.get() + size - 1); // We don't want the '\0' inside
		}

		template <typename Iterator>
		void advance_all(Iterator & iterator) {
			++iterator;
		}
		template <typename Iterator, typename ... Iterators>
		void advance_all(Iterator & iterator, Iterators& ... iterators) {
			++iterator;
			advance_all(iterators...);
		}
		template <typename Function, typename InputIt, typename OutputIt, typename ... Iterators>
		OutputIt zipWith(Function func,
			InputIt first,
			InputIt last,
			OutputIt d_first,
			Iterators ... iterators)
		{
			for (; first != last; ++first, advance_all(iterators...))
				*d_first++ = func(*first, *(iterators)...);
			return d_first;
		}



	} // namespace util
} // namespace trdrop

#endif // !TRDROP_UTIL_H