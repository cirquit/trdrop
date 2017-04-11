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

	} // namespace algorithm
} // namespace trdrop

#endif // !TRDROP_FRAMEALGORITHM_H
