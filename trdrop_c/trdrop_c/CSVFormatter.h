#pragma once
#ifndef TRDROP_UTIL_CSVFORMAT_H
#define TRDROP_UTIL_CSVFORMAT_H

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <iterator>
#include "util.h"

namespace trdrop {
	namespace util {

		class CSVFormatter {

			// default member
		public:
			
			CSVFormatter() = default;
			CSVFormatter(const CSVFormatter & other) = default;
			CSVFormatter & operator=(const CSVFormatter & other) = default;
			CSVFormatter(CSVFormatter && other) = default;
			CSVFormatter & operator=(CSVFormatter && other) = default;
			~CSVFormatter() = default;

			// public methods
		public:

			// restricting the log to <std::string> container
			template<class Iterator>
			typename std::enable_if<
				std::is_same<typename std::iterator_traits<Iterator>::value_type, std::string>::value, std::string
			>::type format(Iterator begin, Iterator end)
			{
				std::vector<std::string> commaSeparated(std::distance(begin, end));
				std::vector<std::string> commas(std::distance(begin, end));
				std::fill(commas.begin(), commas.end() - 1, separator);
				commas.push_back(" ");

				zipWith([&](typename std::iterator_traits<Iterator>::value_type value, std::string comma) {
					return value + comma;
				}, begin, end, commaSeparated.begin(), commas.begin());

				commaSeparated.push_back("\n");

				return accumulate(commaSeparated.begin(), commaSeparated.end(), std::string(""));
			}
		
			// private member
		private:
			const std::string separator = ",";
		};

	} // namespace util
} // namespace trdrop

#endif // ! TRDROP_UTIL_CSVFILE_H
