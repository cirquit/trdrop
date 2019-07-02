#ifndef FRAMERATEPROCESSING_H
#define FRAMERATEPROCESSING_H

#include <QDebug>
#include <QList>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <memory>
#include "headers/cpp_interface/fpsoptions.h"

//! TODO
class FramerateProcessing
{

//! constructors
public:
    //! TODO
    FramerateProcessing()
        : _shared_frame_diff_count(0)
        , _received_first_frames(false)
        , _max_video_count(3)
        , _cached_framedifferences_count(60)
    {
        _init_member();
    }

//! methods
public:
    //! TODO
    void check_for_difference(const QList<cv::Mat> & cv_frame_list
                            , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list)
    {
        if (!_received_first_frames)
        {
            qDebug() << "check_for_difference():received_frames = false";
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
                    quint8 diff_frame = are_equal ? 0 : 1;
                    // explicit convertion for linter
                    size_t _i = static_cast<size_t>(i);
                    _frame_diff_lists[_i][_shared_frame_diff_count] = diff_frame;
                }
            }
            // frame count is incremented in between frames (difference only)
            _shared_frame_diff_count += 1;
            // reset every X frames
            _shared_frame_diff_count %= _cached_framedifferences_count;
        }
        // save the current frame list
        _cache_framelist(cv_frame_list);
    }
    //! TODO
    const QList<double> get_framerates()
    {
        QList<double> framerates;
        for (size_t i = 0; i < _frame_diff_lists.size(); ++i)
        {
            framerates.push_back(_calculate_framerate(i));
        }
        return framerates;
    }
    //! TODO
    void reset_state()
    {
        _frame_diff_lists.clear();
        _cached_frames.clear();
        _init_member();
    }

//! methods
private:
    //! TODO adapt this to any amount of recorded framerates (currenlty this is set by _cached_framedifferences_count)
    //! I have to make a counting window for the rec_framerate, then average the windows for each video independently
    //! then it should be possible to compare videos with an initial 30Hz and 60Hz recording
    double _calculate_framerate(size_t video_index)
    {
        double framecount = std::accumulate(_frame_diff_lists[video_index].begin()
                                          , _frame_diff_lists[video_index].end()
                                          , 0.0);
        return framecount;
    }
    //! TODO
    void _init_member()
    {
        // prepare buffer for each video
        for (int i = 0; i < _max_video_count; ++i)
        {
            _frame_diff_lists.push_back(std::vector<quint8>(_cached_framedifferences_count, 0));
            _cached_frames.push_back(cv::Mat());
        }
        // first frames can't be compared
        _received_first_frames = false;
        _shared_frame_diff_count = 0;
    }
    //! TODO rethink this
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
    //! TODO
    void _cache_framelist(const QList<cv::Mat> _other)
    {
        for (int i = 0; i < _other.size(); ++i)
        {
            _cached_frames[i] = _other[i].clone();
        }
    }

//! member
private:
    //! TODO
    quint64        _shared_frame_diff_count;
    //! TODO
    bool           _received_first_frames;
    //! TODO
    QList<cv::Mat> _cached_frames;
    //! TODO
    std::vector<std::vector<quint8>> _frame_diff_lists;
    //! TODO
    const quint8  _max_video_count;
    //! TODO
    const quint16 _cached_framedifferences_count;
};

#endif // FRAMERATEPROCESSING_H
