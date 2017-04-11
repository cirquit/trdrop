#pragma once
#ifndef TRDROP_TASKS_TASKCONTAINER_H
#define TRDROP_TASKS_TASKCONTAINER_H

#include <functional>

#include <opencv2/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

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
			TaskContainer(cv::VideoCapture & input, cv::VideoWriter & output, trdrop::config::Config & config)
				: input(input)
				, output(output)
				, config(config) {

			}

			TaskContainer(trdrop::config::Config & config)
				: TaskContainer(cv::VideoCapture(), cv::VideoWriter(), config) {}

			template<class T>
			int add(Task<T> task) {
				tasks.push_back([&] {
					task.process(prev, cur, currentFrameIndex);
				});
				return tasks.size() - 1;

			}
			
			bool next() {
				std::for_each(tasks.begin(), tasks.end(), [](std::function<void()> f) { f(); });
			}

			// public member
		public:
			const trdrop::config::Config config;

			// private member
		private:
			cv::VideoCapture input;
			cv::VideoWriter output;
			std::vector<std::function<void()>> tasks;
			cv::Mat cur;
			cv::Mat prev;
			size_t currentFrameIndex;
		};

	} // namespace tasks
} // namespace trdrop

#endif // !TRDROP_TASKS_TASKCONTAINER_H