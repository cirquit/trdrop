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
			Config(std::vector<std::string> inputNames, std::string outputName, bool writeDelta)
				: inputNames(inputNames)
				, outputName(outputName)
				, writeDelta(writeDelta)
				, inputVideoCount(inputNames.size())
			{}

			// single video file
			Config(std::string inputName, std::string outputName = "output.avi", bool writeDelta = false)
				: Config(std::vector<std::string>{inputName}, outputName, writeDelta) 
			{}

			
		// public member
		public:
			const std::vector<std::string> inputNames;
			const std::string outputName;
			const std::size_t inputVideoCount;

		// private member
		private:
			bool writeDelta = false;

		};
	} // namespace config
} // namespace trdrop

#endif // !TRDROP_CONFIG_H
