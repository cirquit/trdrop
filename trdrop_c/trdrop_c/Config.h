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
				YAML::Node yamlConfig = parseArgs(argc, argv);

				std::vector<std::string> errors;
				fromSequenceTag("input-files", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					inputs.push_back(cv::VideoCapture(it->as<std::string>()));
					inputNames.push_back(it->as<std::string>());
				});

				// trdrop::util::setFrameIndex(inputs[0], 1100);

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

				fromTag("output-as-bmps", yamlConfig, errors, [&](std::string tag) {
					outputAsBmps = yamlConfig[tag].as<bool>();
				});

				fromTag("log-file", yamlConfig, errors, [&](std::string tag) {
					logName = yamlConfig[tag].as<std::string>();
				});

				fromSequenceTag("colors", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					std::string hex = it->second["hex"].as<std::string>();
					colors.push_back(trdrop::util::hexToBGR(hex, cv::Scalar(0,0,0)));
				});
				fromTag("pixel-difference", yamlConfig, errors, [&](std::string tag) {
					pixelDifference = yamlConfig[tag].as<int>();
				});
				fromTag("line-difference", yamlConfig, errors, [&](std::string tag) {
					lineDifference = yamlConfig[tag].as<int>();
				});
				fromSequenceTag("tear-color", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					std::string hex = it->second["hex"].as<std::string>();
					tearColors.push_back(trdrop::util::hexToBGR(hex, cv::Scalar(220,0,0)));
				});

				fromSequenceTag("fps-text-locations", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					textLocations.push_back(cv::Size(it -> second["x"].as<int>(), it -> second["y"].as<int>()));
				});

				fromSequenceTag("fps-text", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					fpsText.push_back(it->second["text"].as<std::string>());
#if _TR_DEBUG
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
					std::string hex = it->second["hex"].as<std::string>();
					shadowColors.push_back(trdrop::util::hexToBGR(hex, cv::Scalar(230, 230, 230)));
				});


				fromSequenceTag("fps-refresh-rate", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					refreshRate.push_back(it->second["rate"].as<int>());
				});

				fromTag("plot-background-color", yamlConfig, errors, [&](std::string tag) {
					std::string hex = yamlConfig[tag].as<std::string>();
					plotBackgroundColor = (trdrop::util::hexToBGR(hex, cv::Scalar(230, 230, 230)));
				});

				fromTag("plot-lines-color", yamlConfig, errors, [&](std::string tag) {
					std::string hex = yamlConfig[tag].as<std::string>();
					plotLinesColor = (trdrop::util::hexToBGR(hex, cv::Scalar(230, 230, 230)));
				});

				fromTag("plot-axes-color", yamlConfig, errors, [&](std::string tag) {
					std::string hex = yamlConfig[tag].as<std::string>();
					plotAxesColor = (trdrop::util::hexToBGR(hex, cv::Scalar(230, 230, 230)));
				});

				fromTag("plot-background-alpha", yamlConfig, errors, [&](std::string tag) {
					plotAlpha = yamlConfig[tag].as<double>();
				});

				fromTag("viewer-active", yamlConfig, errors, [&](std::string tag) {
					viewerActive = yamlConfig[tag].as<bool>();
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
#if _TR_DEBUG				
				std::cout << "DEBUG: Config - viewer-size: " << viewerSize << '\n';
#endif				
				fromTag("writer-size", yamlConfig, errors, [&](std::string tag) {
					fromTag("writer-width", yamlConfig[tag], errors, [&](std::string tag_) {
						writerFrameSize.width = yamlConfig[tag][tag_].as<int>();
					});

					fromTag("writer-height", yamlConfig[tag], errors, [&](std::string tag_) {
						writerFrameSize.height = yamlConfig[tag][tag_].as<int>();
					});
				});


				if (errors.empty()) { // somehow this does not work with inline-if in the Either constructor
					parsing = Either<std::vector<std::string>, std::string>(Right<std::string>("trdrop_c: No warnings, yet."));
				}
				else {
					parsing = Either<std::vector<std::string>, std::string>(Left<std::vector<std::string>>(errors));
				}

#if _TR_DEBUG
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

			int getMinimumBakedFPS() {
				std::vector<double> & bakedFPS = getBakedFPS();
				return static_cast<int>(std::ceil(*std::min_element(bakedFPS.begin(), bakedFPS.end())));
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

			YAML::Node parseArgs(int argc, char** argv) {

				// yaml encapsulated with single quotes and using double quotes for strings
				if (argc >= 2 && (strcmp(argv[1], "--yaml") == 0)) {
						std::cout << "trdrop: Using the config from the command line:\n";
						std::cout << "    Got: " << argv[2] << '\n';
						return YAML::Load(argv[2]);
				}
				
				// custom config path
				if (argc >= 2 && doesFileExist(std::string(argv[1]))) {
					std::string maybePath(argv[1]);
					std::cout << "trdrop: Using config-path \"" << maybePath << "\"\n";
					return YAML::LoadFile(maybePath);
				}

				// default config path
				std::string defaultPath = trdropYAMLConfig;
				std::cout << "trdrop: Using default config-path \"" << defaultPath << "\"\n";
				return YAML::LoadFile(defaultPath);
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

			std::vector<cv::Scalar>  tearColors;
			cv::Scalar plotBackgroundColor;
			cv::Scalar plotLinesColor;
			cv::Scalar plotAxesColor;
			double     plotAlpha;

			cv::Size viewerSize;
			bool	 viewerActive;

			cv::Size writerFrameSize;
			bool outputAsBmps;

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
