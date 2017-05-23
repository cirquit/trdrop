#pragma once

#include <vector>
#include <sstream>
#include <string>
#include <algorithm>

namespace trdrop {

	// This class is the used as a source by Inter-/PostTasks and should be easily copied and moved
	// Every member should be a vector, because it holds the data for multiple videos at once
	class fps_data {

		// default member
	public:
		fps_data() = delete;
		fps_data(const fps_data & other) = default;
		fps_data & operator=(const fps_data & other) = default;
		fps_data(fps_data && other) = default;
		fps_data & operator=(fps_data && other) = default;
		~fps_data() = default;

		// custom member
	public:
		fps_data(size_t videoCount)
			: duplicateFrame(videoCount, false)
			, fps(videoCount, 0)
			, videoCount(videoCount)
		{ }

	public:
		// only for debugging purposes
		std::string to_string() const
		{
			std::stringstream result;
			result << "FPS: ";
			std::for_each(fps.begin(), fps.end(), [&](double d) { result << std::to_string(d) << ' '; });
			result << "Duplicate Frames: ";
			std::for_each(duplicateFrame.begin(), duplicateFrame.end(), [&](bool b) { result << std::to_string(b) << ' '; });
			return result.str();
		}

	public:
		std::vector<bool>	duplicateFrame;
		std::vector<double> fps;
		std::vector<std::vector<double>> fps_unprocessed;
		size_t              videoCount;

	};

} // namespace trdrop

