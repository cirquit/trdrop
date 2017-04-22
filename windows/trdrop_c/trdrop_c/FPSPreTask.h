#pragma once
#ifndef TRDROP_TASKS_PRE_FSD_H
#define TRDROP_TASKS_PRE_FSD_H

#include <functional>
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
				FPSPreTask(std::string id, std::vector<int> window, std::vector<double> bakedFps)
					: id(id)			   // id used for the csv header
					, window(window)       // window size to pool until fps calculation
					, bakedFps(bakedFps)   // baked fps which was provided by the video === sample rate
					, fps(window.size())   // allocate enough memory for all videos
					, differentFramesCount(window.size()) // allocate enough memory for all videos
					, pretask(std::bind(&FPSPreTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3
						, std::placeholders::_4))
				{
					trdrop::util::zipWith([&](int w, double bFps) {
						if (w == -1) {
							return static_cast<int>(std::floor(bFps));
						}
						else {
							return w;
						}
					}, window.begin(), window.end(), this -> window.begin(), bakedFps.begin());
				}

				// interface methods
			public:
				void process(const cv::Mat & prev, const cv::Mat & cur, const size_t currentFrameIndex, const size_t vix) {
					//std::cout << "FPSPre - curFrameIndex: " << currentFrameIndex << ", vix: " << vix << '\n';
//#if _DEBUG
//					trdrop::util::timeit_([&] {
//						differentFramesCount[vix] += trdrop::algorithm::are_equal<cv::Vec3b>(prev, cur) ? 0 : 1;
//					});
//#else
					differentFramesCount[vix] += trdrop::algorithm::are_equal<cv::Vec3b>(prev, cur) ? 0 : 1;
//#endif
					if (currentFrameIndex % window[vix] == 0) {
						realFps = bakedFps[vix] * differentFramesCount[vix] / window[vix];
						fps[vix] = realFps;
						differentFramesCount[vix] = 0;
#if _DEBUG
						std::cout << "DEBUG: FPSPreTask - vix: " << vix << ", returning fps[0]: " << fps[0] << ", fps[1]: " << fps[1] << std::endl;
#endif					
						static std::mutex mutex;
						std::lock_guard<std::mutex> lock(mutex);

						resultIndex = currentFrameIndex;
						result = EitherSD(RightD(fps));
					}
					else {
						if (currentFrameIndex != resultIndex) {
							result = EitherSD(LeftS("FPSPreTask: Not calculated yet, " + std::to_string(currentFrameIndex % window[vix]) + " to go."));
						}
					}
				}

				// public member
			public:
				EitherSD result;
				const std::string id;

				// private member
			private:
				std::vector<int>    differentFramesCount;
				std::vector<double> fps;
				std::vector<int>    window;
				std::vector<double> bakedFps;
				size_t			    resultIndex;
				double              realFps = 0;

			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_PRE_FSD_H