#ifndef DELTAPROCESSING_H
#define DELTAPROCESSING_H

#include <QDebug>
#include <QList>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <memory>
#include "headers/cpp_interface/fpsoptions.h"

//! TODO
class DeltaProcessing
{

//! constructors
public:
    //! TODO
    DeltaProcessing()
        : _received_first_frames(false)
        , _max_video_count(3)
    {
        _init_member();
    }

//! methods
public:
    //! TODO
    QList<cv::Mat> check_for_difference(const QList<cv::Mat> & cv_frame_list
                                      , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list)
    {
        //! TODO
        Q_UNUSED(shared_fps_options_list);

        QList<cv::Mat> difference_frames;

        for (int i = 0; i < cv_frame_list.size(); ++i) {
            difference_frames.push_back(cv::Mat());
        }

        if (!_received_first_frames)
        {
            _received_first_frames = true;
            // save the current frame list
            _cache_framelist(cv_frame_list);
            // return the normal frames as we can't calculate a difference
            return cv_frame_list;
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
                    difference_frames[i] = _get_difference(_cached_frames[i], cv_frame_list[i]).clone();
                }
            } else {
                // we could try to calculate the difference for each frame which we have a difference for
                // but it might be a hassle if the second video got deleted live, because the indices get moved
                // it's easier to simply wait until the new frames arrive at the correct index. I should probably
                // disable removing files while exporting
            }
        }
        // save the current frame list
        _cache_framelist(cv_frame_list);

        return difference_frames;
    }
    //! TODO
    void reset_state()
    {
        _cached_frames.clear();
        _init_member();
    }

//! methods
private:
    //! TODO
    void _init_member()
    {
        // prepare buffer for each video
        for (int i = 0; i < _max_video_count; ++i)
        {
            _cached_frames.push_back(cv::Mat());
        }
        // first frames can't be compared
        _received_first_frames = false;
    }
    //! TODO
    cv::Mat _get_difference(const cv::Mat & first_frame, const cv::Mat & second_frame) const
    {
        cv::Mat difference;
        cv::absdiff(first_frame, second_frame, difference);
        return difference;
    }

    //! TODO rethink this
    //! take a look at https://stackoverflow.com/questions/18464710/how-to-do-per-element-comparison-and-do-different-operation-according-to-result
//    bool _are_equal_with(const cv::Mat & frame_a, const cv::Mat & frame_b, const int pixelDifference) const {
//        cv::Mat black_white_frame_a;
//        cv::Mat black_white_frame_b;
//        cv::cvtColor(frame_a, black_white_frame_a, cv::COLOR_BGRA2GRAY);
//        cv::cvtColor(frame_b, black_white_frame_b, cv::COLOR_BGRA2GRAY);

//        //qDebug() << black_white_frame_a.at<uchar>(0, 0) << "," << black_white_frame_b.at<uchar>(0, 0);
//        for (int i = 0; i < black_white_frame_a.rows; i += 1) {
//            for (int j = 0; j < black_white_frame_a.cols; j += 1) {
//                int ac(std::max(black_white_frame_a.at<uchar>(i, j)
//                              , black_white_frame_b.at<uchar>(i, j)));
//                int bc(std::min(black_white_frame_a.at<uchar>(i, j)
//                              , black_white_frame_b.at<uchar>(i, j)));
//                if (ac - bc > pixelDifference) {
//                    return false;
//                }
//            }
//        }
//        return true;
//    }

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
    bool           _received_first_frames;
    //! TODO
    QList<cv::Mat> _cached_frames;
    //! TODO
    const quint8  _max_video_count;
};


#endif // DELTAPROCESSING_H
