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
			TaskContainer(trdrop::config::Config & config)
				: config(config)
				, inputs(config.inputs) {

			}

			void addPreTask(trdrop::tasks::pretask task) {
				preTasks.push_back(task);
			}

			void addPostTask(trdrop::tasks::posttask task) {
				postTasks.push_back(task);
			}
			
			bool next() {
				static bool readSuccessful;
				
				if (currentFrameIndex == 0) {
					readSuccessful = inputs[0].read(prev);
					readSuccessful = inputs[0].read(cur);
				}
				else {
					cur.copyTo(prev);
					readSuccessful = inputs[0].read(cur);
				}

				if (readSuccessful) {

					if (currentFrameIndex == 0) {
						std::for_each(postTasks.begin(), postTasks.end(), [&](trdrop::tasks::posttask f) { f(prev, 0); });
					}

					currentFrameIndex += 1;

					// transform does not work for some reason
					std::for_each(preTasks.begin(), preTasks.end(), [&](trdrop::tasks::pretask f) {
							taskFinished.push_back(std::move(std::async(std::launch::async, f, prev, cur, currentFrameIndex, 0))); });

					std::for_each(taskFinished.begin(), taskFinished.end(), [](std::future<void> & future){
						future.wait();
					}); 
					taskFinished.clear();

					cur.copyTo(res);
					std::for_each(postTasks.begin(), postTasks.end(), [&](trdrop::tasks::posttask f) { f(res, 0); });
				}
				
				return readSuccessful;
			}

			size_t getCurrentFrameIndex() {
				return currentFrameIndex;
			}

			// public member
		public:
			const trdrop::config::Config & config;

			// private member
		private:
			std::vector<cv::VideoCapture> inputs;
			std::vector<trdrop::tasks::pretask> preTasks;
			std::vector<std::future<void>> taskFinished;
			std::vector<trdrop::tasks::posttask> postTasks;
			cv::Mat cur;
			cv::Mat prev;
			cv::Mat res;
			size_t currentFrameIndex = 0;
		};

	} // namespace tasks
} // namespace trdrop

#endif // !TRDROP_TASKS_TASKCONTAINER_H