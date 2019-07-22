#ifndef FRAMERATEPROCESSING_H
#define FRAMERATEPROCESSING_H

#include <QDebug>
#include <QList>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <memory>
#include "headers/cpp_interface/fpsoptions.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! TODO
class FramerateProcessing
{

//! constructors
public:
    //! TODO
    FramerateProcessing()
        : _received_first_frames(false)
        , _max_video_count(3)
    {
        QList<quint8> _default_recorded_framerates = { 0, 0, 0 };
        _init_member(_default_recorded_framerates);
    }

//! methods
public:
    //! TODO
    void check_for_difference(const QList<cv::Mat> & cv_frame_list
                            , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list)
    {
        if (!_received_first_frames)
        {
            _received_first_frames = true;
            _cache_framelist(cv_frame_list);
        } else
        {
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
                    // if multiple videos are loaded, the cache list has not all frames loaded, wait for next iteration
                    //if (_cached_frames[i].empty()) break;
                    // get the pixel difference from the settings
                    int current_pixel_difference = static_cast<int>((*shared_fps_options_list)[i].pixel_difference.value());
                    // check if the previous frame and current frame are equal
                    bool are_equal = _are_equal_with(_cached_frames[i]
                                                   , cv_frame_list[i]
                                                   , current_pixel_difference);
                    // if the frame is equal, don't increment the whole frame count -> 0
                    const quint8 diff_frame = are_equal ? 0 : 1;
                    // explicit convertion for linter
                    const size_t _i           = static_cast<size_t>(i);
                    const size_t _frame_count = _current_framecount_list[_i];
                    // set the diff_frame for the video (_i) for the current count (_frame_count)
                    _frame_diff_lists[_i][_frame_count] = diff_frame;
                }
            }
            // increments the framecounter for each video and loops automatically
            _increment_current_framecount();
        }
        // save the current frame list
        _cache_framelist(cv_frame_list);
    }
    //! calculates the current framerate for each video
    const QList<double> get_framerates()
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

    //! resets the state of the object, but to ensure that the class is in a well defined state and nobody misuses it
    //! we need to know the recorded framerates (with no videos loaded this list will be empty)
    void reset_state(const QList<quint8> recorded_framerate_list)
    {
        _frame_diff_lists.clear();
        _current_framecount_list.clear();
        _cached_frames.clear();
        _init_member(recorded_framerate_list);
    }

//! methods
private:
    //! sums up the vector with (0's and 1's) to get the resulting framerate
    double _calculate_framerate(size_t video_index)
    {
        double framecount = std::accumulate(_frame_diff_lists[video_index].begin()
                                          , _frame_diff_lists[video_index].end()
                                          , 0.0);
        return framecount;
    }
    //! frametime for the last visible frame in milliseconds
    double _calculate_frametime(size_t video_index)
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
        // if the current frame is a duplicate, we have to wait until we got a new frame to estimate the time of the previous frame
        // if (_frame_diff_lists[video_index][current_framerate_count] == 0) { return 0; }
        // counter of how long the frame is show per 1 / recorded_framerate in seconds
        double frame_time_counter = 0.0;
        // start looping backwards for the frame_diff_list until we reach a new frame
        bool iterating_over_same_frame = true;
        bool found_last_diff = false;
        while (iterating_over_same_frame)
        {
            const quint8 diff = _frame_diff_lists[video_index][current_framerate_count];
            if (found_last_diff)
            {
                if (diff == 0) frame_time_counter += 1.0;
                if (diff == 1) { frame_time_counter += 1.0; iterating_over_same_frame = false; }
            } else {
                if (diff == 1) found_last_diff = true;
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
            _frame_diff_lists.push_back(std::vector<quint8>(recorded_framerate, 0));
            _cached_frames.push_back(cv::Mat());
            _current_framecount_list.push_back(0);
        }
        // without a seconds frame frames can't be compared
        _received_first_frames = false;
    }
    //! take a look at https://stackoverflow.com/questions/18464710/how-to-do-per-element-comparison-and-do-different-operation-according-to-result
    bool _are_equal_with(const cv::Mat & frame_a, const cv::Mat & frame_b, const int pixelDifference) const {
        cv::Mat black_white_frame_a;
        cv::Mat black_white_frame_b;
        cv::cvtColor(frame_a, black_white_frame_a, cv::COLOR_BGRA2GRAY);
        cv::cvtColor(frame_b, black_white_frame_b, cv::COLOR_BGRA2GRAY);

        //qDebug() << black_white_frame_a.at<uchar>(0, 0) << "," << black_white_frame_b.at<uchar>(0, 0);
        for (int i = 0; i < black_white_frame_a.rows; i += 1) {
            for (int j = 0; j < black_white_frame_a.cols; j += 1) {
                int ac(std::max(black_white_frame_a.at<uchar>(i, j)
                              , black_white_frame_b.at<uchar>(i, j)));
                int bc(std::min(black_white_frame_a.at<uchar>(i, j)
                              , black_white_frame_b.at<uchar>(i, j)));
                if (ac - bc > pixelDifference) {
                    return false;
                }
            }
        }
        return true;
    }
    //! TODO rethink this
    bool _are_equal(const cv::Mat & frame_a, const cv::Mat & frame_b) const {
        int rindex;
        for (int i = 0; i < frame_a.rows; ++i) {
            rindex = i * frame_a.rows;
            for (int j = 0; j < frame_a.cols; ++j) {
                if (frame_a.data[rindex + j] != frame_b.data[rindex + j]) return false;
            }
        }
        return true;
    }
    //! copies the framelist as cv::Mat is a smart pointer and need to be copied manually
    void _cache_framelist(const QList<cv::Mat> _other)
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
    size_t _decrement_modulo(size_t value, size_t max_value)
    {
        if (value == 0) return max_value;
        else return value - 1;
    }
//! member
private:

    //! holds the current framecount of each video (used to access the inner lists of _frame_diff_lists)
    std::vector<size_t>              _current_framecount_list;
    //! TODO
    bool                             _received_first_frames;
    //! TODO
    QList<cv::Mat>                   _cached_frames;
    //! the list which has a list for each video consisting of 0's or 1's, counting the differing frames
    std::vector<std::vector<quint8>> _frame_diff_lists;
    //! TODO
    const quint8                     _max_video_count;
};

#endif // FRAMERATEPROCESSING_H
