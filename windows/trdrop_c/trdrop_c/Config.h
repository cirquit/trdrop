#pragma once
#ifndef TRDROP_CONFIG_H
#define TRDROP_CONFIG_H

#include <string>
#include <iostream>
#include <vector>

namespace trdrop {

	namespace config {
		/*
		 * This Config class will be used to ask the user for custom configuration, like
		 *	- fps text position
		 *  - fps text color / pick automatic adaptability
		 *  - create a delta-frame video
		 *  - ...
		 */

		class Config {

		// default member
		public:
			Config() = delete;
			Config(const Config & other) = default;
			Config & operator=(const Config & other) = delete;
			Config(Config && other) = delete;
			Config & operator=(Config && other) = delete;
			~Config() = default;

		// specialized member
		public:

			// multiple video files
			Config(std::vector<std::string> inputNames, std::string outputName, std::string logName, int codec, bool writeDelta, cv::Size textLocation, cv::Size viewerSize, int fpsPrecision)
				: inputNames(inputNames)
				, outputName(outputName)
				, logName(logName)
				, codec(codec)
				, writeDelta(writeDelta)
				, inputVideoCount(inputNames.size())
				, textLocation(textLocation)
				, viewerSize(viewerSize)
				, fpsPrecision(fpsPrecision)
			{
				// TODO Error checking, get a parse method that tests for validity and returns an Either<string, int> (msg, errlvl)
				std::for_each(inputNames.begin(), inputNames.end(),
					[&](std::string name) { inputs.push_back(cv::VideoCapture(name)); });

				bakedFPS = trdrop::util::getFrameRate(inputs[0]);
			}


			cv::Size getVideoFrameSize(int index) {
				return trdrop::util::getSize(inputs[index]);
			}
			/*
			// single video file
			Config(std::string inputName, std::string outputName = "output.avi", int codec, bool writeDelta = false)
				: Config(std::vector<std::string>{inputName}, outputName, codec, writeDelta) 
			{} */

			
		// public member
		public:
			std::vector<cv::VideoCapture> inputs;
			double bakedFPS;
			const std::vector<std::string> inputNames;
			const std::string outputName;
			const std::string logName;
			const std::size_t inputVideoCount;
			const int codec;
			const cv::Size textLocation;
			const cv::Size viewerSize;
			const int fpsPrecision;

		// private member
		private:
			bool writeDelta = false;


		};
	} // namespace config
} // namespace trdrop

#endif // !TRDROP_CONFIG_H
