#pragma once
#ifndef TRDROP_TASKS_TASKCONTAINER_H
#define TRDROP_TASKS_TASKCONTAINER_H

#include <functional>
#include <algorithm>
#include <future>
#include <memory>

#include <opencv2/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "Tasks.h"
#include "Config.h"

namespace trdrop {

	namespace tasks {

		class TaskScheduler {

			// default member
		public:
			TaskScheduler() = delete;
			TaskScheduler(const TaskScheduler & other) = delete;
			TaskScheduler & operator=(const TaskScheduler & other) = delete;
			TaskScheduler(TaskScheduler && other) = delete;
			TaskScheduler & operator=(TaskScheduler && other) = delete;
			~TaskScheduler() = default;

			// specialized member
		public:
			TaskScheduler(std::vector<cv::VideoCapture> & inputs, const cv::Size writerFrameSize)
				: inputs(inputs)
				, writerFrameSize(writerFrameSize)
				, prev(inputs.size())
				, cur(inputs.size())
			{ }

			void addPreTask(std::shared_ptr<trdrop::tasks::pretask> taskptr) {
				preTasks.push_back(taskptr);
			}

			void addInterTask(std::shared_ptr<trdrop::tasks::intertask> taskptr) {
				interTasks.push_back(taskptr);
			}

			void addPostTask(std::shared_ptr<trdrop::tasks::posttask> taskptr) {
				postTasks.push_back(taskptr);
			}
			
			/* 
			 * Resizes every video to the desired writerFrameSize and crops accordingly.
			 * Currently supports up to 2 videos.
			 */
			void merge(std::vector<cv::Mat> & frames, cv::Mat & result) {

				std::vector<cv::Mat> resizedFrames;

				std::for_each(frames.begin(), frames.end(), [&](cv::Mat & a) {
					cv::Mat resized(writerFrameSize, frames[0].depth());
					cv::resize(a, resized, writerFrameSize);
					resizedFrames.push_back(resized);
				});

				if (frames.size() == 1) {
					resizedFrames[0].copyTo(result);
				} else if (frames.size() == 2) {

					int x = resizedFrames[0].size().width / 4;
					int y = 0;
					int width = resizedFrames[0].size().width / 2;
					int height = resizedFrames[0].size().height;

					cv::Rect box(x, y, width, height);
					cv::Rect left(0, 0, width, height);
					cv::Rect right(x * 2, 0, width, height);

					resizedFrames[0].copyTo(result); // somehow needed, even if we already allocated 'result'
					cv::Mat cropped0 = resizedFrames[0](box);
					cv::Mat cropped1 = resizedFrames[1](box);
					cropped0.copyTo(result(left));
					cropped1.copyTo(result(right));
				} else {
					std::cout << "\nError: merging for more than two videos is not defined...yet\n";
				}
			}

			bool next() {
#if _TR_DEBUG
				std::cout << "\nDEBUG: TaskScheduler.next() - currentFrameIndex\n";
#endif
				// first read reads two frames
				if (currentFrameIndex == 0) {
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						readSuccessful &= input.read(prev[vix]);
						readSuccessful &= input.read(cur[vix]);
					});

					if (readSuccessful) {
						merged = cv::Mat(writerFrameSize, prev[0].depth());
					}
				} else {
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						cur[vix].copyTo(prev[vix]);
						readSuccessful &= input.read(cur[vix]);
					});
				}

				if (readSuccessful) {
					// if this is the first frame, we load two frames
					currentFrameIndex += currentFrameIndex == 0 ? 2 : 1;
#if _TR_DEBUG
					std::cout << "DEBUG: TaskScheduler.readSuccesful, currentFrameIndex: " << currentFrameIndex << '\n';
#endif
					
					// pretasks - parallel
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						std::for_each(preTasks.begin(), preTasks.end(), [&](std::shared_ptr<trdrop::tasks::pretask> f) {
							preTasksFinished.push_back(std::move(std::async(std::launch::async, *f, prev[vix], cur[vix], currentFrameIndex, vix)));
						});
					}); 

					// pretasks - waiting
					std::for_each(preTasksFinished.begin(), preTasksFinished.end(), [](std::future<void> & future){
						future.wait();
					}); 		
#if _TR_DEBUG
					std::cout << "DEBUG: TaskScheduler - finished all pretasks - size: " << preTasksFinished.size() << "\n";
#endif
					preTasksFinished.clear();

					// intermediate tasks - parallel
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						std::for_each(interTasks.begin(), interTasks.end(), [&](std::shared_ptr<trdrop::tasks::intertask> f) {
							interTasksFinished.push_back(std::move(std::async(std::launch::async, *f, prev[vix], currentFrameIndex, vix)));
						}); 
					});

					// intermediate tasks - waiting
					std::for_each(interTasksFinished.begin(), interTasksFinished.end(), [](std::future<void> & future) {
						future.wait();
					});


#if _TR_DEBUG
					std::cout << "DEBUG: TaskScheduler - finished all intermediate tasks - size: " << interTasksFinished.size() << "\n";
#endif
					interTasksFinished.clear();
					merge(prev, merged);
#if _TR_DEBUG
					std::cout << "DEBUG: TaskScheduler - merged frames\n";
#endif
					// post tasks - sequential
					std::for_each(postTasks.begin(), postTasks.end(), [&](std::shared_ptr<trdrop::tasks::posttask> f) { (*f)(merged, currentFrameIndex); });
#if _TR_DEBUG
					std::cout << "DEBUG: TaskScheduler - finished all posttasks\n";
#endif
				}
				
				return readSuccessful;
			}

			size_t getCurrentFrameIndex() {
				return currentFrameIndex;
			}

			// private member
		private:
			std::vector<cv::VideoCapture> & inputs;
			bool readSuccessful = true;

			std::vector<std::shared_ptr<trdrop::tasks::pretask>> preTasks;
			std::vector<std::future<void>>		preTasksFinished;
			
			std::vector<std::shared_ptr<trdrop::tasks::intertask>> interTasks;
			std::vector<std::future<void>>		interTasksFinished;
			
			std::vector<std::shared_ptr<trdrop::tasks::posttask>> postTasks;
			
			std::vector<cv::Mat> cur;
			std::vector<cv::Mat> prev;
			cv::Mat				 merged;
			const cv::Size       writerFrameSize;
			size_t			     currentFrameIndex = 0;
		};

	} // namespace tasks
} // namespace trdrop

#endif // !TRDROP_TASKS_TASKCONTAINER_H
