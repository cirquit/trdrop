#pragma once
#ifndef TRDROP_UTIL_CSVFILE_H
#define TRDROP_UTIL_CSVFILE_H

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <iterator>
#include "util.h"

namespace trdrop {
	namespace util {

		class CSVFile {

			// default member
		public:
			
			CSVFile() = default;
			CSVFile(const CSVFile & other) = default;
			CSVFile & operator=(const CSVFile & other) = delete;
			CSVFile(CSVFile && other) = default;
			CSVFile & operator=(CSVFile && other) = delete;
			// ~CSVFile() = delete;
			
			// custom member
		public:
			CSVFile(std::string filename, std::vector<std::string> columns, std::ofstream * out)
			{
				csvFile = out;
				(*csvFile).open(filename);

#if _DEBUG
					std::cout << "CSVFile - Output opened: " << ((*csvFile).is_open() ? "true" : "false") << '\n';
#endif
				log(columns.begin(), columns.end());
			}
		
			~CSVFile()
			{
				(*csvFile).close();
#if _DEBUG
				std::cout << "CSVFile - Output closed: " << ((*csvFile).is_open() ? "false" : "true") << '\n';
#endif
			}
			
			// public methods
		public:


			// restricting the log to <std::string> container
			template<class Iterator>
			typename std::enable_if<
				std::is_same<typename std::iterator_traits<Iterator>::value_type, std::string>::value
			>::type log(Iterator begin, Iterator end) 
			{
				std::vector<std::string> commaSeparated(std::distance(begin, end));
				std::vector<std::string> commas(std::distance(begin, end));
				std::fill(commas.begin(), commas.end() - 1, separator);
				commas.push_back(" ");
				
				zipWith([&](typename std::iterator_traits<Iterator>::value_type value, std::string comma) {
					return value + comma;
				}, begin, end, commaSeparated.begin(), commas.begin());
				
				write(csvFile, commaSeparated.begin(), commaSeparated.end());
#if _DEBUG
				std::cout << "Log() was called with: ";
				std::for_each(commaSeparated.begin(), commaSeparated.end(), [&](Iterator::value_type e) {std::cout << e; });
				std::cout << '\n';
#endif
			}

			// private methods
		private:
			
			template <class Iterator, typename Value = typename Iterator::value_type>
			void write(std::ofstream * out, Iterator begin, Iterator end) {
				std::copy(begin, end, std::ostream_iterator<Value>(*out));
				*out << '\n';
			}

			// private member
		private:
			const std::string separator = ",";
			std::ofstream * csvFile;
		};

	} // namespace util
} // namespace trdrop

#endif // ! TRDROP_UTIL_CSVFILE_H
