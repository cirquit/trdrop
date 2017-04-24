#pragma once
#ifndef TRDROP_TASKS_PRE_FSD_H
#define TRDROP_TASKS_PRE_FSD_H

#include <functional>
#include <numeric>
#include <math.h>
#include <mutex>

#include "Tasks.h"
#include "Either.h"

namespace trdrop {
	namespace tasks {
		namespace pre {

			using trdrop::tasks::pretask;
			using trdrop::Either;
			using trdrop::Right;
			using trdrop::Left;

			class FPSPreTask : public pretask {

				// types
			private:
				using EitherSD = Either<std::string, std::vector<double>>;
				using RightD = Right<std::vector<double>>;
				using LeftS = Left<std::string>;

				// default member
			public:
				FPSPreTask() = delete;
				FPSPreTask(const FPSPreTask & other) = default;
				FPSPreTask & operator=(const FPSPreTask & other) = delete;
				FPSPreTask(FPSPreTask && other) = default;
				FPSPreTask & operator=(FPSPreTask && other) = delete;
				~FPSPreTask() = default;

				// specialized member
			public:
				FPSPreTask(std::string id, size_t videoCount, int pixelDifference)
					: id(id)							// id used for the csv header
					, fps(videoCount)					// allocate enough memory for all videos
					, isDifferentFrame(videoCount)		// allocate enough memory for all videos
					, pixelDifference(pixelDifference)  
					, pretask(std::bind(&FPSPreTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3
						, std::placeholders::_4))
				{
					util::enumerate(isDifferentFrame.begin(), isDifferentFrame.end(), 0, [&](unsigned ix, std::vector<double> &v) {
						v.insert(v.end(), windowSize, 0.0);
					});
				}

				// interface methods
			public:
				void process(const cv::Mat & prev, const cv::Mat & cur, const size_t currentFrameIndex, const size_t vix) {

					if (pixelDifference > 0){
						equal = trdrop::algorithm::are_equal_with<int>(prev, cur, pixelDifference);
					}
					else {
						equal = trdrop::algorithm::are_equal<uchar*>(prev, cur);
					}
					static std::mutex mutex;
					std::lock_guard<std::mutex> lock(mutex);

					size_t localIndex = currentFrameIndex % windowSize;
					isDifferentFrame[vix][localIndex] = equal ? 0.0 : 1.0;
					fps[vix] = std::accumulate(isDifferentFrame[vix].begin(), isDifferentFrame[vix].end(), 0.0);
					result = EitherSD(RightD(fps));
				}

				// public member
			public:
				EitherSD result;
				const std::string id;

				// private member
			private:
				std::vector<std::vector<double>>   isDifferentFrame;
				std::vector<double> fps;
				std::vector<int>    window;
				size_t			    resultIndex;
				double              realFps = 0;
				bool                equal = false;
				const int           windowSize = 60;
				int                 pixelDifference;
			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_PRE_FSD_H