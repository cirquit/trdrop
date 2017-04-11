#pragma once
#ifndef TRDROP_TASKS_FSDTASK_H
#define TRDROP_TASKS_FSDTASK_H

#include <math.h>

#include "Task.h"
#include "Either.h"

namespace trdrop {
	namespace tasks {

		using trdrop::Either;
		using trdrop::Right;
		using trdrop::Left;
		using EitherSD = Either<std::string, double>;
		using RightD = Right<double>;
		using LeftS  = Left<std::string>;

		class FPSTask : public Task<Either<std::string, double>> {

		// default member
		public:
			FPSTask() = delete;
			FPSTask(const FPSTask & other) = delete;
			FPSTask & operator=(const FPSTask & other) = delete;
			FPSTask(FPSTask && other) = delete;
			FPSTask & operator=(FPSTask && other) = delete;
			~FPSTask() = default;

		// specialized member
		public:
			FPSTask(EitherSD result, int window, int bakedFps, int precision = 2)
				: Task(result)		   
				, window(window)       // window size to pool until fps calculation
				, bakedFps(bakedFps)   // baked fps which was provided by the video === sample rate
				, precision(precision) // precision of the resulting fps
			{}

		// interface methods
		public:
			void process(cv::Mat & prev, cv::Mat & cur, int currentFrameIndex) {
				static int differentFramesCount;
				differentFramesCount += trdrop::algorithm::are_equal<uchar*>(prev, cur) ? 0 : 1;
				if (currentFrameIndex % window == 0) {
					realFps = toPrecision(bakedFps * differentFramesCount / window);
					differentFramesCount = 0;
					result = EitherSD(RightD(realFps));
				}
				result = EitherSD(LeftS("FPSTask: Not calculated yet, " + std::to_string(currentFrameIndex % window) + " to go."));
			}

		// private methods
		private:
			double toPrecision(double x) {
				int power = static_cast<int>(std::pow(10, precision));
				return std::round(power * x) / power;
			}

		// private member
		private:
			int window    = 0;
			int precision = 0;
			double realFps  = 0;
			double bakedFps = 0;

		};
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_FSDTASK_H