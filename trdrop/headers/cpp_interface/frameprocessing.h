#ifndef FRAMEPROCESSING_H
#define FRAMEPROCESSING_H

#include <QDebug>
#include <QList>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <memory>

#include "headers/cpp_interface/framerateoptions.h"
#include "headers/cpp_interface/teardata.h"
#include "headers/qml_models/tearoptionsmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! TODO
class FrameProcessing
{

//! constructors
public:
    //! TODO
    FrameProcessing()
        : _received_first_frames(false)
        , _max_video_count(3)
    {
        QList<quint8> _default_recorded_framerates = { 0, 0, 0 };
        _init_member(_default_recorded_framerates);
    }

//! methods
public:
    //! returns the difference frames
    QList<cv::Mat> check_for_difference(const QList<cv::Mat> & cv_frame_list
                            , std::shared_ptr<QList<FramerateOptions>> shared_fps_options_list
                            , std::shared_ptr<QList<TearOptions>> shared_tear_options_list)
    {
        // we can only calculate the difference if we have at least two sets of frames
        if (!_received_first_frames)
        {
            _received_first_frames = true;
            _cache_framelist(cv_frame_list);
            return cv_frame_list;
        } else
        {
            // default init TODO refactor
            _tear_rows.clear();
            _difference_frames.clear();
            for (int i = 0; i < cv_frame_list.size(); ++i)
            {
                _difference_frames.push_back(cv::Mat());
            }
            // if multiple videos are loaded, the cache list has not all frames loaded, wait for next iteration
            // refactored this from the loop to allow omp
            bool all_cached_frames_filled = true;
            for (int i = 0; i < cv_frame_list.size(); ++i)
            {
                all_cached_frames_filled = all_cached_frames_filled && !_cached_frames[i].empty();
            }
            // TODO test this for performance
            if (all_cached_frames_filled) {
                #pragma omp parallel for
                for (int i = 0; i < cv_frame_list.size(); ++i)
                {
                    const quint32 pixel_difference = (*shared_fps_options_list)[i].pixel_difference.value();
                    _difference_frames[i] = _get_difference(_cached_frames[i], cv_frame_list[i], pixel_difference).clone();

                    // explicit convertion for linter
                    const size_t _i           = static_cast<size_t>(i);
                    const size_t _frame_count = _current_framecount_list[_i];
                    // calculate a diff frame based on the amount of "same" rows in the compared frames
                    double dismiss_tear_percentage = (*shared_tear_options_list)[i].dismiss_tear_percentage.value() / 100;
                    // fill the frame difference, the diff counter and tears
                    _frame_diff_lists[_i][_frame_count] = _get_frame_difference(_difference_frames[i], dismiss_tear_percentage, i, cv_frame_list.size());
                }
            }
            // increments the framecounter for each video and loops automatically
            _increment_current_framecount();
        }
        // save the current frame list
        _cache_framelist(cv_frame_list);
        return _difference_frames;
    }
    //! calculates the current framerate for each video
    QList<double> get_framerates() const
    {
        QList<double> framerates;
        for (size_t i = 0; i < _frame_diff_lists.size(); ++i)
        {
            framerates.push_back(_calculate_framerate(i));
        }
        return framerates;
    }
    //! calculates the current frametimes for each video for the last frames
    const QList<double> get_frametimes()
    {
        QList<double> frametimes;
        for (size_t i = 0; i < _frame_diff_lists.size(); ++i)
        {
            frametimes.push_back(_calculate_frametime(i));
        }
        return frametimes;
    }
    //! returns the tear indices from the last calculation
    std::vector<TearData> get_tear_indices() const
    {
        return _tear_rows;
    }
    //! resets the state of the object, but to ensure that the class is in a well defined state and nobody misuses it
    //! we need to know the recorded framerates (with no videos loaded this list will be empty)
    void reset_state(const QList<quint8> recorded_framerate_list)
    {
        _frame_diff_lists.clear();
        _current_framecount_list.clear();
        _cached_frames.clear();
        _difference_frames.clear();
        _init_member(recorded_framerate_list);
    }

//! methods
private:
    //! sums up the vector with (0's and 1's) to get the resulting framerate
    double _calculate_framerate(size_t video_index) const
    {
        double framecount = std::accumulate(_frame_diff_lists[video_index].begin()
                                          , _frame_diff_lists[video_index].end()
                                          , 0.0);
        return framecount;
    }
    //! frametime for the last visible frame in milliseconds
    double _calculate_frametime(size_t video_index) const
    {
        //! yes this the is the recorded framerate, TODO refactor this into a method with comments
        const size_t recorded_framerate = _frame_diff_lists[video_index].size();
        size_t current_framerate_count  = _current_framecount_list[video_index];

        // we always look at the previous frame first
        current_framerate_count = _decrement_modulo(current_framerate_count, _frame_diff_lists[video_index].size() - 1);
        // if the recorded framerate is zero, there is no video loaded for that index
        if (recorded_framerate == 0) { return 0; }
        // if no frames were analyzed, we can't analyze the frametime, we need a [1, ..., 1] diff window
        if (_calculate_framerate(video_index) < 2.0) { return 0; }
        // counter of how long the frame is show per 1 / recorded_framerate in seconds
        double frame_time_counter = 0.0;
        // start looping backwards for the frame_diff_list until we reach a new frame
        bool iterating_over_same_frame = true;
        bool found_last_diff = false;
        while (iterating_over_same_frame)
        {
            const double diff = _frame_diff_lists[video_index][current_framerate_count];
            if (found_last_diff)
            {
                if (diff == 0.0) frame_time_counter += 1.0;
                if (diff > 0) { frame_time_counter += 1.0; iterating_over_same_frame = false; }
            } else {
                if (diff > 0) found_last_diff = true;
            }
            current_framerate_count = _decrement_modulo(current_framerate_count, _frame_diff_lists[video_index].size() - 1);
        }
        double frametime_in_s = frame_time_counter / static_cast<double>(recorded_framerate);
        return frametime_in_s * 1000;
    }
    //! the inner lists of _frame_diff_lists are initialized to be the size of the framerate of each recorded video
    //! as we can not recognize a higher framerate than the one it was recorded with
    void _init_member(const QList<quint8> recorded_framerate_list)
    {
        for (int i = 0; i < _max_video_count; ++i)
        {
            quint8 recorded_framerate = 0;
            const bool has_recorded_framerate = i < recorded_framerate_list.size();
            if (has_recorded_framerate)
            {
                recorded_framerate = recorded_framerate_list[i];
            }
            _frame_diff_lists.push_back(std::vector<double>(recorded_framerate, 0.0));
            _cached_frames.push_back(cv::Mat());
            _difference_frames.push_back(cv::Mat());
            _current_framecount_list.push_back(0);
        }
        // without a seconds frame frames can't be compared
        _received_first_frames = false;
    }
    //! copies the framelist as cv::Mat is a smart pointer and need to be copied manually
    void _cache_framelist(const QList<cv::Mat> & _other)
    {
        for (int i = 0; i < _other.size(); ++i)
        {
            _cached_frames[i] = _other[i].clone();
        }
    }
    //! increases the framecount for each video and cuts it by the recorded_framerate (see _init_member())
    //! mod 0 is invalid, so we have to catch that
    void _increment_current_framecount()
    {
        for (size_t i = 0; i < _current_framecount_list.size(); ++i)
        {
            quint8 recorded_framerate = static_cast<quint8>(_frame_diff_lists[i].size());
            _current_framecount_list[i] += 1;
            if (recorded_framerate != 0) _current_framecount_list[i] %= recorded_framerate;
        }
    }
    //! TODO refactor this?
    size_t _decrement_modulo(size_t value, size_t max_value) const
    {
        if (value == 0) return max_value;
        else return value - 1;
    }
    //! make this chooseable?
    cv::Mat _get_difference(const cv::Mat & first_frame, const cv::Mat & second_frame, const quint32 pixel_difference) const
    {
        cv::Mat difference;
        //cv::absdiff(first_frame, second_frame, difference);
        _are_equal_with_draw(first_frame, second_frame, static_cast<int>(pixel_difference), difference);
        return difference;
    }
    //! TODO rethink this
    //! take a look at https://stackoverflow.com/questions/18464710/how-to-do-per-element-comparison-and-do-different-operation-according-to-result
    void _are_equal_with_draw(const cv::Mat & frame_a, const cv::Mat & frame_b, const int pixel_difference, cv::Mat & output) const
    {
        cv::Mat black_white_frame_a;
        cv::Mat black_white_frame_b;
        cv::cvtColor(frame_a, black_white_frame_a, cv::COLOR_BGRA2GRAY);
        cv::cvtColor(frame_b, black_white_frame_b, cv::COLOR_BGRA2GRAY);

        output = frame_a.clone();
        for (int i = 0; i < black_white_frame_a.rows; i += 1) {
            for (int j = 0; j < black_white_frame_a.cols; j += 1) {
                int ac(std::max(black_white_frame_a.at<uchar>(i, j)
                              , black_white_frame_b.at<uchar>(i, j)));
                int bc(std::min(black_white_frame_a.at<uchar>(i, j)
                              , black_white_frame_b.at<uchar>(i, j)));
                if (ac - bc > pixel_difference) {
                    // on difference, set to white
                    output.at<cv::Vec3b>(i,j)[0] = 255;
                    output.at<cv::Vec3b>(i,j)[1] = 255;
                    output.at<cv::Vec3b>(i,j)[2] = 255;
                } else {
                    // on "same" pixel, set to black
                    output.at<cv::Vec3b>(i,j)[0] = 0;
                    output.at<cv::Vec3b>(i,j)[1] = 0;
                    output.at<cv::Vec3b>(i,j)[2] = 0;
                }
            }
        }
    }
    //! returns 0 if the compared frames were identical
    //! returns 1 if the frames were at least in 1 pixel different
    //! if we detect a tear, we check how big it is (height) and see if its above the dismiss_tear_percentage
    //!     if it is, we return the percentage of the frame which was not a tear (e.g 1 - tear_percentage)
    //!     if it is NOT, we return 1 e.g we think of them as completely different
    double _get_frame_difference(const cv::Mat & difference, const double dismiss_tear_percentage, int video_index, int video_count)
    {
        // how much of a row has to be different to see it as a "tear cut"
        const double tear_row_completness = 0.1;
        // normalized row differences
        const std::vector<double> row_differences = _get_row_differences(difference);
        // if we found a different pixel and no tears, we have to return 1 (as in increment the framerate by 1)
        bool found_different_pixel = false;
        //
        bool tear_found = false;
        // saving the indices where tears were found. order: (lower, higher) indices
        //std::vector<std::tuple<size_t, size_t>> tear_rows;
        for (size_t row = 1; row < row_differences.size(); ++row)
        {
            const size_t index_A = row - 1;
            const size_t index_B = row;
            const double row_diff_A = row_differences[index_A];
            const double row_diff_B = row_differences[index_B];
            // save tear indices if we found them
            if (_are_tear_rows(row_diff_A, row_diff_B, tear_row_completness))
            {
                tear_found = true;
                _tear_rows.push_back(TearData(index_A, index_B, static_cast<size_t>(video_index), static_cast<size_t>(video_count), difference.rows));
            }
            // if a difference is found set it, otherwise use the accumulated result
            found_different_pixel = row_diff_A > 0.0 || found_different_pixel;
        }
        // if a tear was found, we return the remaining part of the frame
        if (tear_found)
        {
            const double max_tear_percentage = _get_max_tear_percentage(row_differences, _tear_rows);
            // if the tear is not big enough, we dismiss it
            if (max_tear_percentage < dismiss_tear_percentage)
            {
                // if we found a different pixel, we round to a full difference -> 100% -> 1.0, otherwise
                if (found_different_pixel) return 1.0;
                else return 0.0;
                // if the tear is big enough, we return the remaining frame
            } else return 1 - max_tear_percentage;
        }
        // if no tear was found but a different pixel was found, we "round" to a full difference -> 100% -> 1.0
        const bool tear_not_found = !tear_found;
        if (found_different_pixel && tear_not_found) return 1.0;
        // if no different pixel was found, it has to be a duplicate frame, e.g (0% difference -> 0.0)
        return 0.0;
    }
    //! returns the percentage of the biggest tear found
    double _get_max_tear_percentage(const std::vector<double> & row_differences
                                  , const std::vector<TearData> & tear_rows) const
    {
        double max_tear_percentage = 0.0;
        for (size_t i = 0; i < tear_rows.size(); ++i)
        {
            const std::tuple<size_t, size_t> tear = tear_rows[i].get_indices();
            const size_t index_A = std::get<0>(tear);
            const size_t index_B = std::get<1>(tear);
            if (row_differences[index_A] == 0.0)
            {
                // go in the direction of index_B + 1
                size_t index = index_B;
                size_t counter = 0;
                while (row_differences[index] > 0.0)
                {
                    counter += 1;
                    if (index == row_differences.size() - 1) break;
                    index   += 1;
                }
                const double tear_percentage = static_cast<double>(counter) / static_cast<double>(row_differences.size());
                if (tear_percentage > max_tear_percentage) max_tear_percentage = tear_percentage;
            }
            if (row_differences[index_B] == 0.0)
            {
                // go in the direction of index_A - 1
                size_t index = index_A;
                size_t counter = 0;
                while (row_differences[index] > 0.0)
                {
                    counter += 1;
                    if (index == 0) break;
                    index   -= 1;
                }
                const double tear_percentage = static_cast<double>(counter) / static_cast<double>(row_differences.size());
                if (tear_percentage > max_tear_percentage) max_tear_percentage = tear_percentage;
            }
        }
        return max_tear_percentage;
    }
    //! checks if the two normalized row differences count as a tear
    bool _are_tear_rows(const double row_diff_A, const double row_diff_B, const double tear_row_completness) const
    {
        // the tear happened with the old frame in row_diff_A and new frame in row_diff_B
        // duplicate row (e.g black)
        if (row_diff_A == 0.0)
        {
            // new row within bounds
            if (row_diff_B >= tear_row_completness)
            {
                return true;
            }
        }
        // the tear happened with the new frame in row_diff_A and old frame in row_diff_B
        // new row within bounds
        if (row_diff_A >= tear_row_completness)
        {
            // duplicate row (e.g black)
            if (row_diff_B == 0.0)
            {
                return true;
            }
        }
        // otherwise no tear is detected
        return false;
    }
    //! returns a summary for each row how many differences were found (normalized to 0.0 ~ 0% - 1.0 ~ 100%)
    //! see also _get_row_difference
    std::vector<double> _get_row_differences(const cv::Mat & difference) const
    {
        std::vector<double> row_differences(static_cast<size_t>(difference.rows), 0.0);
        #pragma omp parallel for
        for (int row = 0; row < difference.rows; ++row)
        {
            row_differences[static_cast<size_t>(row)] = _get_row_difference(difference, row);
        }
        return row_differences;
    }
    //! return the percentage of the row (0.0 - 1.0) for how many pixel are different (e.g not black)
    //! if 3 pixel were not black from a 10 pixel row we would return 0.3, e.g 30%
    double _get_row_difference(const cv::Mat & difference, const int row) const
    {
        double difference_counter = 0;
        #pragma omp parallel for reduction(+:difference_counter)
        for (int col = 0; col < difference.cols; ++col)
        {
            bool red_channel_is_not_black   = difference.at<cv::Vec3b>(row,col)[0] != 0;
            bool green_channel_is_not_black = difference.at<cv::Vec3b>(row,col)[1] != 0;
            bool blue_channel_is_not_black  = difference.at<cv::Vec3b>(row,col)[2] != 0;
            bool pixel_is_not_black = red_channel_is_not_black && green_channel_is_not_black && blue_channel_is_not_black;
            if (pixel_is_not_black) difference_counter += 1.0;
        }
        return difference_counter / static_cast<double>(difference.cols);
    }
//! member
private:

    //! holds the current framecount of each video (used to access the inner lists of _frame_diff_lists)
    std::vector<size_t>              _current_framecount_list;
    //! checks if we already received the first frames (only important on startup)
    bool                             _received_first_frames;
    //! saves the t-1 frames
    QList<cv::Mat>                   _cached_frames;
    //! the list which has a list for each video consisting of 0's or 1's, counting the differing frames
    std::vector<std::vector<double>> _frame_diff_lists;
    //! maximum video count (TODO maybe refactor this in the future)
    const quint8                     _max_video_count;
    //! if tears were found, they are saved for a frame here
    std::vector<TearData>            _tear_rows;
    //! caches the frame differences which may be rendered if need be
    QList<cv::Mat>                   _difference_frames;

};

#endif // FRAMEPROCESSING_H
