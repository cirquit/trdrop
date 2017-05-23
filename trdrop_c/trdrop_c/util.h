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

		void setFrameIndex(cv::VideoCapture & input, int frame) {
			input.set(CV_CAP_PROP_POS_FRAMES, frame);
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

		// safe snprintf
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
		
		// blatantly copied from http://stackoverflow.com/questions/3752019/how-to-get-the-index-of-a-value-in-a-vector-using-for-each
		template <typename InputT, typename Function>
		Function enumerate(InputT first,
			InputT last,
			typename std::iterator_traits<InputT>::difference_type initial,
			Function func)
		{
			for (; first != last; ++first, ++initial)
				func(initial, *first);
			return func;
		}

		// blatanlty copied from http://jepsonsblog.blogspot.de/2012/10/overlay-transparent-image-in-opencv.html
		// opencv still can't handle alpha...
		void overlayImage(const cv::Mat &background, const cv::Mat &foreground,
			cv::Mat &output, cv::Point2i location)
		{
			background.copyTo(output);


			// start at the row indicated by location, or at row 0 if location.y is negative.
			for (int y = std::max(location.y, 0); y < background.rows; ++y)
			{
				int fY = y - location.y; // because of the translation

										 // we are done of we have processed all rows of the foreground image.
				if (fY >= foreground.rows)
					break;

				// start at the column indicated by location, 

				// or at column 0 if location.x is negative.
				for (int x = std::max(location.x, 0); x < background.cols; ++x)
				{
					int fX = x - location.x; // because of the translation.

											 // we are done with this row if the column is outside of the foreground image.
					if (fX >= foreground.cols)
						break;

					// determine the opacity of the foregrond pixel, using its fourth (alpha) channel.
					double opacity =
						(static_cast<double>(foreground.data[fY * foreground.step + fX * foreground.channels() + 3]))

						/ 255.;


					// and now combine the background and foreground pixel, using the opacity, 

					// but only if opacity > 0.
					for (int c = 0; opacity > 0 && c < output.channels(); ++c)
					{
						unsigned char foregroundPx = static_cast<unsigned char>(
							foreground.data[fY * foreground.step + fX * foreground.channels() + c]);
						unsigned char backgroundPx = static_cast<unsigned char>(
							background.data[y * background.step + x * background.channels() + c]);
						output.data[y*output.step + output.channels()*x + c] = static_cast<unsigned char>(
							backgroundPx * (1. - opacity) + foregroundPx * opacity);
					}
				}
			}
		}

		// again, blatantly copied from https://stackoverflow.com/questions/18398468/c-stl-convert-string-with-rgb-color-to-3-int-values
		cv::Scalar hexToBGR(std::string & hex, cv::Scalar & default)
		{
			if (hex.size() < 6) return default;
			if (hex[0] == '#') hex = hex.erase(0, 1);

			int r, g, b;

			std::istringstream(hex.substr(0, 2)) >> std::hex >> r;
			std::istringstream(hex.substr(2, 2)) >> std::hex >> g;
			std::istringstream(hex.substr(4, 2)) >> std::hex >> b;

			if (r < 0 || r > 255 || g < 0 || g > 255 || b < 0 || b > 255) return default;

			return cv::Scalar(b, g, r);
		}

	} // namespace util
} // namespace trdrop

#endif // !TRDROP_UTIL_H