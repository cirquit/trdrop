#pragma once
#ifndef TRDROP_TASKS_TASKCONTAINER_H
#define TRDROP_TASKS_TASKCONTAINER_H

#include <functional>
#include <future>

#include <opencv2/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>


#include "Tasks.h"
#include "Config.h"

namespace trdrop {

	namespace tasks {

		class TaskContainer {

			// default member
		public:
			TaskContainer() = delete;
			TaskContainer(const TaskContainer & other) = delete;
			TaskContainer & operator=(const TaskContainer & other) = delete;
			TaskContainer(TaskContainer && other) = delete;
			TaskContainer & operator=(TaskContainer && other) = delete;
			~TaskContainer() = default;

			// specialized member
		public:
			TaskContainer(std::vector<cv::VideoCapture> & inputs)
				: inputs(inputs)
				, prev(inputs.size())
				, cur(inputs.size())
			{ }

			void addPreTask(trdrop::tasks::pretask task) {
				preTasks.push_back(task);
			}

			void addInterTask(trdrop::tasks::intertask task) {
				interTasks.push_back(task);
			}

			void addPostTask(trdrop::tasks::posttask task) {
				postTasks.push_back(task);
			}
			
			void merge(std::vector<cv::Mat> & frames, cv::Mat & result) {
				// resize based on config
				// merge and return

				int x = /*frames[0].size().width */  1920 / 4; // TODO only works for max 2 videos
				int y = 0;
				int width = /*frames[0].size().width */ 1920 / 2; // static_cast<int>(frames.size());
				int height = 1080; // frames[0].size().height;

				cv::Rect box(x, y, width, height);
				cv::Rect left(0, 0, width, height);
				cv::Rect right(x*2, 0, width, height);
				std::cout << "started merging\n";

				if (frames.size() == 1) {
					result = cv::Mat(frames[0].size(), true);
					frames[0].copyTo(result);
				} else if (frames.size() == 2) {
					frames[0].copyTo(result);
					// std::cout << "result is resized: " << result.size() << '\n';
//					std::cout << "result is resized to left: " << result(left).size() << '\n';
//					std::cout << "result is resized to right: " << result(right).size() << '\n';
					cv::Mat cropped0 = frames[0](box);
					cv::Mat cropped1 = frames[1](box);
					cropped0.copyTo(result(left));
					cropped1.copyTo(result(right));
				} 
			}

			bool next() {
				std::cout << "next()\n";
				std::cout << "input size: " << inputs.size() << '\n';
				if (currentFrameIndex == 0) {
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						readSuccessful &= input.read(prev[vix]);
						readSuccessful &= input.read(cur[vix]);
					});

					if (readSuccessful) {
						merged = cv::Mat(prev[0].size().height, prev[0].size().width, prev[0].depth());
					}
				} else {
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						cur[vix].copyTo(prev[vix]);  // TODO swap pointers
						readSuccessful &= input.read(cur[vix]);
					});
				}

				if (readSuccessful) {
					// if this is the first frame, we load two frames
					currentFrameIndex += currentFrameIndex == 0 ? 2 : 1;
					std::cout << "readSuccesful, frame: " << currentFrameIndex << '\n';

					// pretasks - parallel
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						std::for_each(preTasks.begin(), preTasks.end(), [&](trdrop::tasks::pretask f) {
							//f(prev[vix], cur[vix], currentFrameIndex, vix);
							preTasksFinished.push_back(std::move(std::async(std::launch::async, f, prev[vix], cur[vix], currentFrameIndex, vix)));
						});
					});

					std::cout << "launched pretasks\n";

					// pretasks - waiting
					std::for_each(preTasksFinished.begin(), preTasksFinished.end(), [](std::future<void> & future){
						future.wait();
					}); 
					preTasksFinished.clear();

					std::cout << "finished pretasks\n";

					// intermediate tasks - not parallel yet
					trdrop::util::enumerate(inputs.begin(), inputs.end(), 0, [&](unsigned vix, cv::VideoCapture input) {
						std::for_each(interTasks.begin(), interTasks.end(), [&](trdrop::tasks::intertask f) {
							// interTasksFinished.push_back(std::move(std::async(std::launch::async, f, prev[vix], vix)));
							f(prev[vix], vix);
						});
					});

					std::cout << "finished intermediate tasks\n";

					// merging
					merge(prev, merged);
					
					std::cout << "merged is done\n";

					// post tasks - sequential
					std::for_each(postTasks.begin(), postTasks.end(), [&](trdrop::tasks::posttask f) { f(merged); });

					std::cout << "finished posttasks\n";
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

			std::vector<trdrop::tasks::pretask> preTasks;
			std::vector<std::future<void>>		preTasksFinished;
			
			std::vector<trdrop::tasks::intertask> interTasks;
			std::vector<std::future<void>>		  interTasksFinished;
			
			std::vector<trdrop::tasks::posttask> postTasks;
			
			std::vector<cv::Mat> cur;
			std::vector<cv::Mat> prev;
			cv::Mat				 merged;
			size_t currentFrameIndex = 0;
		};

	} // namespace tasks
} // namespace trdrop

#endif // !TRDROP_TASKS_TASKCONTAINER_H