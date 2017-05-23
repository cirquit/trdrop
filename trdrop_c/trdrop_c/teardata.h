#pragma once

#include <vector>
#include <sstream>
#include <string>
#include <algorithm>

namespace trdrop {

	// This class is the used as a source by Inter-/PostTasks and should be easily copied and moved
	// Every member should be a vector, because it holds the data for multiple videos at once
	class tear_data {

		// default member
	public:
		tear_data() = delete;
		tear_data(const tear_data & other) = default;
		tear_data & operator=(const tear_data & other) = default;
		tear_data(tear_data && other) = default;
		tear_data & operator=(tear_data && other) = default;
		~tear_data() = default;

		// custom member
	public:
		tear_data(size_t videoCount)
			: videoCount(videoCount)
			, tears(videoCount, 0)
			, tear_unprocessed(videoCount)
		{ }

	public:
		// only for debugging purposes
		std::string to_string() const
		{
			std::stringstream result;
			result << "Tears: ";
			std::for_each(tears.begin(), tears.end(), [&](double d) { result << std::to_string(d) << ' '; });
			return result.str();
		}

	public:
		std::vector<std::vector<double>> tear_unprocessed;
		std::vector<double> tears;
		size_t              videoCount;

	};

} // namespace trdrop

