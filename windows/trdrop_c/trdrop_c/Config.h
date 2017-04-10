#pragma once

#include <string>
#include <iostream>

namespace trdrop {

	class Config {
	public:

		Config() = default;
		Config(const Config & other) = default;
		Config & operator=(const Config & other) = default;
		Config(Config && other) = default;
		Config & operator=(Config && other) = default;
		~Config() = default;

	private:


};

} // namespace trdrop