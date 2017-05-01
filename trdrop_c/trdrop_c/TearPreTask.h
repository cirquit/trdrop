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
				using EitherSVI = Either<std::string, std::vector<int>>;
				using RightVI = Right<std::vector<int>>;
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
				TearPreTask(std::string id, size_t videoCount, int lineTolerance, int pixelTolerance)
					: id(id)
					, tears(videoCount)
					, lineTolerance(lineTolerance)
					, pixelTolerance(pixelTolerance)
					, pretask(std::bind(&TearPreTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2
						, std::placeholders::_3
						, std::placeholders::_4))
				{ 
					tears.insert(tears.end(), videoCount, -1);

				}

				// interface methods
			public:
				void process(const cv::Mat & prev, const cv::Mat & cur, const size_t currentFrameIndex, const size_t vix) {
					cv::Mat differenceMat;
					cv::absdiff(prev, cur, differenceMat);

					// TODO refactor with STL (e.g find_if)
					bool tear = false;
					tears[vix] = -1;
					int zeroRows = 0;
					for (int i = 0; i < differenceMat.rows; ++i) {
						if (differenceMat.at<uchar>(i, 0) <= pixelTolerance) {
							tear = true;
							for (int j = 0; j < differenceMat.cols; ++j) {
								if (differenceMat.at<uchar>(i, j) > pixelTolerance) {
									tear = false;
									tears[vix] = -1;
									break;
								}
							}
							if (tear) ++zeroRows;
							if (zeroRows == lineTolerance) {
								tearIndex = i;
								tears[vix] = tearIndex;
								result = EitherSVI(RightVI(tears));
								return;
							}
						} 
					}
					result = EitherSVI(RightVI(tears));
				}

				// public member
			public:
				EitherSVI result;
				const std::string id;

				// private member
			private:
				int lineTolerance;
				int pixelTolerance;
				int tearIndex = -1;
				std::vector<int> tears;
			};
		} // namespace pre
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_PRE_TEAR_H
