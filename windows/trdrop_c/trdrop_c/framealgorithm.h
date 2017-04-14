#pragma once
#ifndef TRDROP_FRAMEALGORITHM_H
#define TRDROP_FRAMEALGORITHM_H

#include <iostream>

#include<opencv2/core/core.hpp>

#include "util.h"

namespace trdrop {
	namespace algorithm {

		/*
		* Supports following types if the dim is fitting
		* http://docs.opencv.org/trunk/dc/dc2/mat_8hpp.html#Typedefs
		*/
		template <class T>
		bool are_equal(const cv::Mat & frameA, const cv::Mat & frameB) {
			return std::equal(frameA.begin<T>(), frameA.end<T>(), frameB.begin<T>());
		}

		/*
		 * Specialisation for short circuit compare
		 */
		template <>
		bool are_equal<uchar*>(const cv::Mat & frameA, const cv::Mat & frameB) {
			int rindex;
			for (int i = 0; i < frameA.rows; ++i) {
				rindex = i * frameA.rows;
				for (int j = 0; j < frameA.cols; ++j) {
					if (frameA.data[rindex + j] != frameB.data[rindex + j]) return false;
				}
			}
			return true;
		}

		/*
		* Specialisation for implemented difference map, works only on 3 dimensions
		*/
		template <>
		bool are_equal<int>(const cv::Mat & frameA, const cv::Mat & frameB) {
			cv::Mat res = frameA != frameB;
			return (cv::countNonZero(res) == 0);
			/*
			std::vector<cv::Mat> channels(3);
			cv::split(res, channels);
			return (cv::countNonZero(channels[0]) == 0)
				&& (cv::countNonZero(channels[1]) == 0)
				&& (cv::countNonZero(channels[2]) == 0); */
		}

	} // namespace algorithm
} // namespace trdrop

#endif // !TRDROP_FRAMEALGORITHM_H
