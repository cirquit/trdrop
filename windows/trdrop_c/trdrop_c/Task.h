#pragma once

#include <opencv2/core.hpp>

namespace trdrop {
	namespace tasks {

		/*
		 * Interface to create tasks that process the frames with sliding window 2
		 * 
		 * 
		 */
		template <class T>
		class Task {
		public:

			Task(T result)
				: result(result) { }

			using value_t = T;
			virtual void process(cv::Mat & prev, cv::Mat & cur, int currentFrameIndex) = 0;

			T & getResult() const {
				return result;
			}

		protected:
			T result;
		};

	} // namespace tasks
} //namespace trdrop