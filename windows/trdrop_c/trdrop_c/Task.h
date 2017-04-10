#pragma once

#include <opencv2\core.hpp>

namespace trdrop {
	namespace tasks {

		/*
		 * Interface to create tasks that process the frames with sliding window 2
		 */
		template <class T>
		class Task {
		public:
			virtual T process(cv::Mat & prev, cv::Mat & cur) = 0;
		private:

		};
	} // namespace tasks
} //namespace trdrop