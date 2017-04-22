#pragma once
#ifndef TRDROP_CONFIG_H
#define TRDROP_CONFIG_H

#include <string>
#include <iostream>
#include <vector>
#include <functional>

#include "yaml-cpp/yaml-cpp-header/yaml.h"
#include "Either.h"	

// file exists
#ifdef _WIN32
#include <io.h> 
#define access    _access_s
#else
#include <unistd.h>
#endif

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
			Config(int codec)
				: codec(codec)
			{
				YAML::Node yamlConfig = YAML::LoadFile(trdropYAMLConfig);
				std::vector<std::string> errors;
				
				fromSequenceTag("input-files", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					inputs.push_back(cv::VideoCapture(it->as<std::string>()));
				});

				fromTag("output-file", yamlConfig, errors, [&](std::string tag) {
					outputFile = yamlConfig[tag].as<std::string>();
				});

				fromTag("log-file", yamlConfig, errors, [&](std::string tag) {
					logFile = yamlConfig[tag].as<std::string>();
				});

				
				fromSequenceTag("fps-text-locations", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					textLocations.push_back(cv::Size(it -> second["x"].as<int>(), it -> second["y"].as<int>()));
				});

				fromTag("fps-precision", yamlConfig, errors, [&](std::string tag) {
					fpsPrecision = yamlConfig[tag].as<int>();
				});

				fromTag("fps-shadow", yamlConfig, errors, [&](std::string tag) {
					shadows = yamlConfig[tag].as<bool>();
				});
				
				fromSequenceTag("fps-capture-windows", yamlConfig, errors, [&](YAML::const_iterator it, std::string tag) {
					captureWindows.push_back(it->second["window"].as<int>());
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

			// private methods
		private:

			bool doesFileExist(const std::string & filepath) {
				return access(filepath.c_str(), 0) == 0;
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

			std::vector<cv::Point> textLocations;
			std::vector<int>	   captureWindows;
			int				       fpsPrecision;
			bool				   shadows;

			cv::Size viewerSize;
			bool	 viewerActive;

			cv::Size writerSize;

			std::string								              logFile;
			trdrop::Either<std::vector<std::string>, std::string> parsing;

		// private member
		private:
			const std::string trdropYAMLConfig = "trdrop_c-config.yaml";

		};
	} // namespace config
} // namespace trdrop

#endif // !TRDROP_CONFIG_H
