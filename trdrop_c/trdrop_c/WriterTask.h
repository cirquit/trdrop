#pragma once
#ifndef TRDROP_TASKS_POST_WRITER_H
#define TRDROP_TASKS_POST_WRITER_H

#include <functional>
#include <math.h>
#include <sstream>
#include <iomanip>
#include <opencv2\core\core.hpp>
#include <opencv2/highgui/highgui.hpp>  // VideoWriter

#include "Tasks.h"

namespace trdrop {
	namespace tasks {
		namespace post {

			using trdrop::tasks::posttask;

			class WriterTask : public posttask {

				// default member
			public:
				WriterTask() = delete;
				WriterTask(const WriterTask & other) = default;
				WriterTask & operator=(const WriterTask & other) = delete;
				WriterTask(WriterTask && other) = default;
				WriterTask & operator=(WriterTask && other) = delete;
				~WriterTask() = default;

				// specialized member
			public:
				WriterTask(std::string filename, int codec, double bakedFps, cv::Size frameSize, bool outputAsBmps)
					: output(filename, codec, bakedFps, frameSize)
					, outputAsBmps(outputAsBmps)
					, fileName(filename)
					, posttask(std::bind(&WriterTask::process
						, this
						, std::placeholders::_1
						, std::placeholders::_2))
				{	
					size_t dotIndex = filename.find_last_of('.');
					fileName = dotIndex == -1 ? filename : filename.substr(0, dotIndex);

#if _TR_DEBUG
					std::cout << "WriterTask - Output opened: " << (output.isOpened() ? "true" : "false") << '\n';
#endif
				}

				// interface methods
			public:
				void process(const cv::Mat & res, const size_t currentFrameIndex) {
					if (outputAsBmps) {
						char frameName[255];
						sprintf_s(frameName, "-%07zu.bmp", currentFrameIndex);
						cv::imwrite(fileName + frameName, res);
						cv::waitKey(100);
					}	else {
						output.write(res);
					}
				}

				// private methods
			private:

				// private member
			private:
				cv::VideoWriter output;
				const cv::Size frameSize;

				std::string fileName;
				bool outputAsBmps;
			};
		} // namespace post
	} // namespace tasks
} // namespace trdrop

#endif // !TDROP_TASKS_POST_WRITER_H
