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
				using EitherSI = Either<std::string, int>;
				using RightI = Right<int>;
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
				TearPreTask(std::string id, int lineTolerance, int pixelTolerance)
					: id(id)
					, lineTolerance(lineTolerance)
					, pixelTolerance(pixelTolerance)
					, pretask(std::bind(&TearPreTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3
						, std::placeholders::_4))
				{ }

				// interface methods
			public:
				void process(const cv::Mat & prev, const cv::Mat & cur, const size_t currentFrameIndex, const size_t vix) {
					cv::Mat differenceMat;
					cv::absdiff(prev, cur, differenceMat);

					bool tear = false;
					int zeroRows = 0;
					for (int i = 0; i < differenceMat.rows; ++i) {
						if (differenceMat.at<uchar>(i, 0) <= pixelTolerance) {
							tear = true;
							for (int j = 0; j < differenceMat.cols; ++j) {
								if (differenceMat.at<uchar>(i, j) > pixelTolerance) {
									tear = false;
									break;
								}
							}
							if (tear) ++zeroRows;
							if (zeroRows == lineTolerance) {
								tearIndex = i;
								result = EitherSI(RightI(tearIndex));
								return;
							}
						}
					}
					result = EitherSI(LeftS("No tear found within the given tolerances."));
				}

				// public member
			public:
				EitherSI result;

				// private member
			private:
				const std::string id;
				int lineTolerance;
				int pixelTolerance;
				int tearIndex = -1;
			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_PRE_TEAR_H
