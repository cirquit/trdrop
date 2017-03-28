#ifndef TRDROP_HPP
#define TRDROP_HPP

/** \file trdrop.hpp
 *  A brief description of this header.
 *
 */
#include <algorithm>
#include <iostream>

#include <AvTranscoder/file/InputFile.hpp>
#include <AvTranscoder/progress/NoDisplayProgress.hpp>
#include <AvTranscoder/properties/VideoProperties.hpp>
#include <AvTranscoder/util.hpp> // PropertyVector

/**
 * Example description of the trdrop.hpp
 */

namespace trdrop {

//! Run a silent analysis of the input file. This is the precondition for any property-based function
/*!
 */
void populate_properties(avtranscoder::InputFile& file)
{
    avtranscoder::NoDisplayProgress progress;
    file.analyse(progress, avtranscoder::eAnalyseLevelHeader);
}

//! Returns a vector of fps values for every stream
/*!
 */
const std::vector<float> get_fps_from_properties(avtranscoder::InputFile& file)
{
    // run silent analysis of metadata
    populate_properties(file);

    // get video properties for every stream
    const std::vector<avtranscoder::VideoProperties>& video_prop_vector(file.getProperties().getVideoProperties());

    std::vector<float> fps_vector(video_prop_vector.size());
    std::transform(video_prop_vector.begin(), video_prop_vector.end(), fps_vector.begin(),
        [](const avtranscoder::VideoProperties& video_prop) {
            return video_prop.getFps();
        });

    return fps_vector;
}

//! Prints each property separated by a cons on a single line
/*! util function, TODO move to a different header
 */
void print_properties(const avtranscoder::PropertyVector& properties)
{
    for_each(properties.begin(), properties.end(),
        [](const std::pair<std::string, std::string>& pair) {
            std::cout << std::get<0>(pair) << ": " << std::get<1>(pair) << '\n';
        });
}

//! Example description for the method `print_hello_from_lib` which prints a string to std::cout.
/*!
    Details to this function with **markdown** _test_
*/
void print_hello_from_lib();

} // namespace trdrop

#endif