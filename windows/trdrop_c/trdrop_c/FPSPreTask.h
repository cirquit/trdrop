#pragma once
#ifndef TRDROP_TASKS_PRE_FSD_H
#define TRDROP_TASKS_PRE_FSD_H

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

			class FPSPreTask : public pretask {

				// types
			private:
				using EitherSD = Either<std::string, double>;
				using RightD = Right<double>;
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
				FPSPreTask(std::string id, std::vector<int> window, double bakedFps)
					: id(id)
					, window(window)       // window size to pool until fps calculation
					, bakedFps(bakedFps)   // baked fps which was provided by the video === sample rate
					, pretask(std::bind(&FPSPreTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3))
				{
					if (window[0] == -1) {
						this -> window[0] = static_cast<int>(std::floor(bakedFps));;
					}
				}

				// interface methods
			public:
				void process(const cv::Mat & prev, const cv::Mat & cur, const size_t currentFrameIndex) {
					static int differentFramesCount;
#if _DEBUG
					trdrop::util::timeit_([&] {
						differentFramesCount += trdrop::algorithm::are_equal<cv::Vec3b>(prev, cur) ? 0 : 1;
					});
#else
					differentFramesCount += trdrop::algorithm::are_equal<cv::Vec3b>(prev, cur) ? 0 : 1;
#endif
					if (currentFrameIndex % window[0] == 0) {
						realFps = bakedFps * differentFramesCount / window[0];
						differentFramesCount = 0;
						result = EitherSD(RightD(realFps));
					}
					else {
						result = EitherSD(LeftS("FPSPreTask: Not calculated yet, " + std::to_string(currentFrameIndex % window[0]) + " to go."));
					}
				}

				// public member
			public:
				EitherSD result;
				const std::string id;

				// private member
			private:
				std::vector<int>  window;
				const double      bakedFps;
				double            realFps = 0;

			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_PRE_FSD_H