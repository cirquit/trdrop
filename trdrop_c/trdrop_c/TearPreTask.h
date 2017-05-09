#pragma once
#ifndef TRDROP_TASKS_PRE_TEAR_H
#define TRDROP_TASKS_PRE_TEAR_H

#include <functional>
#include <math.h>

#include "Tasks.h"
#include "Either.h"

namespace trdrop {
	namespace tasks {
		namespace pre {

			using trdrop::tasks::pretask;
			using trdrop::Either;
			using trdrop::Right;
			using trdrop::Left;

			class TearPreTask : public pretask {

				// types
			private:
				using EitherSVI = Either<std::string, std::vector<double>>;
				using RightVI = Right<std::vector<double>>;
				using LeftS = Left<std::string>;

				// default member
			public:
				TearPreTask() = delete;
				TearPreTask(const TearPreTask & other) = default;
				TearPreTask & operator=(const TearPreTask & other) = delete;
				TearPreTask(TearPreTask && other) = default;
				TearPreTask & operator=(TearPreTask && other) = delete;
				~TearPreTask() = default;

				// specialized member
			public:
				TearPreTask(std::string id, size_t videoCount, int pixelTolerance)
					: id(id)
					, tears(videoCount)
					, pixelTolerance(pixelTolerance)
					, windowSize(windowSize)
					, pretask(std::bind(&TearPreTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3
						, std::placeholders::_4))
				{ 

				}

				// interface methods
			public:
				void process(const cv::Mat & prev, const cv::Mat & cur, const size_t currentFrameIndex, const size_t vix) {
					cv::Mat diffMat;
					cv::absdiff(prev, cur, diffMat);
					std::vector<int> badPixel = { 0, 0 };

					for (size_t i = 0; i < diffMat.rows; ++i)
					{
						for (size_t j = 0; j < diffMat.cols; ++j)
						{
							badPixel[vix] += diffMat.at<uchar>(i,j) <= 5 ? 0 : 1;
						}
					}

					static std::mutex mutex;
					std::lock_guard<std::mutex> lock(mutex);

					// count the bad pixels and if they consume more than 50% of the image -> tear (shown with a 1)
					tears[vix] = static_cast<double>(badPixel[vix]) / static_cast<double>(diffMat.rows * diffMat.cols);
					result = EitherSVI(RightVI(tears));
				}

				// public member
			public:
				EitherSVI result;
				const std::string id;

				// private member
			private:
				int pixelTolerance;
				const int windowSize = 60; // not clean
				std::vector<double> tears;

			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_PRE_TEAR_H
