#pragma once
#ifndef TRDROP_CONFIG_H
#define TRDROP_CONFIG_H

#include <string>
#include <iostream>
#include <vector>
#include <functional>
#include <experimental/filesystem>
#include <algorithm>
#include <numeric>

#include <yaml-cpp/yaml.h>
#include "Either.h"	



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
			
			// parsed config
			// not using the stream approach because of the custom error handling
			Config(int argc, char** argv)
			{
				std::string path = trdropYAMLConfig;
				if (argc >= 2) {
					std::string maybePath(argv[1]);
					if (doesFileExist(maybePath)) {
						path = maybePath;
						std::cout << "trdrop: Using config-path \"" << maybePath << "\"\n";
					}
				}
				else {
					std::cout << "trdrop: Using default config-path \"" << path << "\"\n";
				}
				YAML::Node yamlConfig = YAML::LoadFile(path);
				std::vector<std::string> errors;

				fromSequenceTag("input-files", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					inputs.push_back(cv::VideoCapture(it->as<std::string>()));
					inputNames.push_back(it->as<std::string>());
				});

				fromTag("codec", yamlConfig, errors, [&](std::string tag) {
					std::string cc = yamlConfig[tag].as<std::string>();
					if (cc.size() < 4 || cc == "0000") {
						codec = -1;
						std::cout << "error - parsed: " << cc << '\n';
					} else {
						codec = cv::VideoWriter::fourcc(cc[0], cc[1], cc[2], cc[3]);
					}
				});

				fromTag("output-file", yamlConfig, errors, [&](std::string tag) {
					outputFile = yamlConfig[tag].as<std::string>();
				});

				fromTag("log-file", yamlConfig, errors, [&](std::string tag) {
					logName = yamlConfig[tag].as<std::string>();
				});

				
				fromSequenceTag("colors", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					int r = it->second["r"].as<int>();
					int g = it->second["g"].as<int>();
					int b = it->second["b"].as<int>();
					colors.push_back(cv::Scalar(b, g, r));
				});

				fromTag("pixel-difference", yamlConfig, errors, [&](std::string tag) {
					pixelDifference = yamlConfig[tag].as<int>();
				});

				fromTag("line-difference", yamlConfig, errors, [&](std::string tag) {
					lineDifference = yamlConfig[tag].as<int>();
				});

				fromSequenceTag("fps-text-locations", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					textLocations.push_back(cv::Size(it -> second["x"].as<int>(), it -> second["y"].as<int>()));
				});

				fromSequenceTag("fps-text", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					fpsText.push_back(it->second["text"].as<std::string>());
#if _DEBUG
					std::cout << "DEBUG: Config - fps-text - got \"" << fpsText.back() << "\"\n";
#endif
				});

				fromTag("fps-precision", yamlConfig, errors, [&](std::string tag) {
					fpsPrecision = yamlConfig[tag].as<int>();
				});

				fromTag("fps-shadow", yamlConfig, errors, [&](std::string tag) {
					shadows = yamlConfig[tag].as<bool>();
				});
				
				fromSequenceTag("fps-shadow-colors", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					int r = it->second["r"].as<int>();
					int g = it->second["g"].as<int>();
					int b = it->second["b"].as<int>();
					shadowColors.push_back(cv::Scalar(b, g, r));
				});


				fromSequenceTag("fps-refresh-rate", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					refreshRate.push_back(it->second["rate"].as<int>());
				});

				fromTag("viewer-active", yamlConfig, errors, [&](std::string tag) {
					viewerActive = yamlConfig[tag].as<bool>();
				});


				if (viewerActive) {
					fromTag("viewer-size", yamlConfig, errors, [&](std::string tag) {
						fromTag("viewer-width", yamlConfig[tag], errors, [&](std::string tag_) {
							viewerSize.width = yamlConfig[tag][tag_].as<int>();
						});

						fromTag("viewer-height", yamlConfig[tag], errors, [&](std::string tag_) {
							viewerSize.height = yamlConfig[tag][tag_].as<int>();
						});
					});
				}
#if _DEBUG				
				std::cout << "DEBUG: Config - viewer-size: " << viewerSize << '\n';
#endif				
				fromTag("writer-size", yamlConfig, errors, [&](std::string tag) {
					fromTag("writer-width", yamlConfig[tag], errors, [&](std::string tag_) {
						writerSize.width = yamlConfig[tag][tag_].as<int>();
					});

					fromTag("writer-height", yamlConfig[tag], errors, [&](std::string tag_) {
						writerSize.height = yamlConfig[tag][tag_].as<int>();
					});
				});


				if (errors.empty()) { // somehow this does not work with inline-if in the Either constructor
					parsing = Either<std::vector<std::string>, std::string>(Right<std::string>("trdrop_c: No warnings, yet."));
				}
				else {
					parsing = Either<std::vector<std::string>, std::string>(Left<std::vector<std::string>>(errors));
				}

#if _DEBUG
				std::cout << "DEBUG: Config.successful(): " << parsing.successful() << '\n';
				util::enumerate(inputs.begin(), inputs.end(), 0, [&](size_t ix, cv::VideoCapture input) {
					std::cout << "DEBUG: Config - FrameCounts: input[" << ix << "]: " << util::getFrameCount(input) << '\n';
				});
#endif
			}
			

			cv::Size getVideoFrameSize(int index) {
				return trdrop::util::getSize(inputs[index]);
			}

			double getBakedFPS(int index) {
				return trdrop::util::getFrameRate(inputs[index]);
			}

			std::vector<double> getBakedFPS() {
				std::vector<double> bakedFps;
				std::transform(inputs.begin(), inputs.end(), std::back_inserter(bakedFps),
					[&](cv::VideoCapture input) {
					return trdrop::util::getFrameRate(input);
				});
				return bakedFps;
			}

			int getMinFrameIndex() {
				return std::accumulate(inputs.begin(), inputs.end(), static_cast<int>(trdrop::util::getFrameCount(inputs[0])), [&](int acc, cv::VideoCapture input){
					return std::min(acc, static_cast<int>(trdrop::util::getFrameCount(input)));
				});
			}

			// private methods
		private:

			bool doesFileExist(const std::string& name) {
				return std::experimental::filesystem::exists(name);
			}
			
			void error(std::vector<std::string> & vec, const std::string & msg) {
				vec.push_back( "Parsing error: " + msg);
			}

			void fromTag(const std::string & tag, YAML::Node & yamlNode, std::vector<std::string> & errors, std::function<void(std::string)> f) {
				if (yamlNode[tag]) {
					f(tag);
				}
				else {
					error(errors, "tag \"" + tag + "\" could not be found in " + trdropYAMLConfig + ", please check the syntax of the tag\n");
				}
			}

			void fromSequenceTag(const std::string & tag, YAML::Node & yamlNode, std::vector<std::string> & errors, std::function<void(YAML::const_iterator, std::string)> f) {
				if (yamlNode[tag]) {
					for (YAML::const_iterator it = yamlNode[tag].begin(); it != yamlNode[tag].end(); ++it) {
						f(it, tag);
					}
				}
				else {
					error(errors, "tag \"" + tag + "\" could not be found in " + trdropYAMLConfig + ", please check the syntax of the tag\n");
				}
				
				
			}

		// public member
		public:
			std::vector<cv::VideoCapture> inputs;
			std::vector<std::string>      inputNames;

			int		    codec;
			std::string outputFile;

			int			pixelDifference;
			int         lineDifference;

			std::vector<cv::Point>   textLocations;
			std::vector<std::string> fpsText;
			std::vector<cv::Scalar>  colors;
			std::vector<int>	     refreshRate;
			int				         fpsPrecision;
			bool				     shadows;
			std::vector<cv::Scalar>  shadowColors;

			cv::Size viewerSize;
			bool	 viewerActive;

			cv::Size writerSize;

			std::string								              logName;
			trdrop::Either<std::vector<std::string>, std::string> parsing;

		// private member
		private:
#if _DEBUGPATH
			std::string trdropYAMLConfig = "../../../configs/trdrop-config.yaml";
#else
			std::string trdropYAMLConfig = "trdrop-config.yaml"; 
#endif

		};
	} // namespace config
} // namespace trdrop

#endif // !TRDROP_CONFIG_H
