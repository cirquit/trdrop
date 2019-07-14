#ifndef TEARPROCESSING_H
#define TEARPROCESSING_H

#include <QDebug>
#include <QList>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <memory>
#include "headers/cpp_interface/fpsoptions.h"
#include "headers/cpp_interface/teardata.h"

//! TODO
class TearProcessing
{

//! constructors
public:
    //! TODO
    TearProcessing()
        : _received_first_frames(false)
        , _max_video_count(3)
    {
        _init_member();
    }

//! methods
public:
    //! TODO
    QList<TearData> check_for_tears(const QList<cv::Mat> & cv_frame_list
                                  , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list)
    {
        //! TODO
        Q_UNUSED(shared_fps_options_list);
        //Q_UNUSED(shared_tear_options_list);

        QList<cv::Mat> difference_frames;
        QList<TearData> tear_data_list;

        // default init
        for (int i = 0; i < cv_frame_list.size(); ++i) {
            difference_frames.push_back(cv::Mat());
            const quint64 row_count = static_cast<quint64>(cv_frame_list[i].rows);
            tear_data_list.push_back(TearData(row_count));
        }

        if (!_received_first_frames)
        {
            _received_first_frames = true;
            // save the current frame list
            _cache_framelist(cv_frame_list);
            // return the normal frames as we can't calculate a difference
            return tear_data_list;
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
                    const quint32 pixel_difference = (*shared_fps_options_list)[i].pixel_difference.value();
                    difference_frames[i] = _get_difference(_cached_frames[i], cv_frame_list[i], pixel_difference).clone();
                    tear_data_list[i].set_tear_rows(_get_tear_rows(difference_frames[i]));
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

        return tear_data_list;
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
    void _are_equal_with_draw(const cv::Mat & frame_a, const cv::Mat & frame_b, const int pixel_difference, cv::Mat & output) const {
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
    //! TODO
    void _cache_framelist(const QList<cv::Mat> _other)
    {
        for (int i = 0; i < _other.size(); ++i)
        {
            _cached_frames[i] = _other[i].clone();
        }
    }
    //! get the rows where we detect a tear (may not be ordered from 0 to max_rows, e.g 0 3 2)
    std::vector<quint64> _get_tear_rows(const cv::Mat & difference) const
    {
        std::vector<quint64> tear_rows;
        #pragma omp parallel for
        for (int row = 0; row < difference.rows; ++row)
        {
            if (_is_row_a_tear(difference, row))
            {
                tear_rows.push_back(static_cast<quint64>(row));
            }
        }
        return tear_rows;
    }

    //! short circuits if any pixel in a row is found not to be full black (0,0,0)
    bool _is_row_a_tear(const cv::Mat & difference, const int row) const
    {
        for (int col = 0; col < difference.cols; ++col)
        {
            bool red_channel_is_not_black   = difference.at<cv::Vec3b>(row,col)[0] != 0;
            bool green_channel_is_not_black = difference.at<cv::Vec3b>(row,col)[1] != 0;
            bool blue_channel_is_not_black  = difference.at<cv::Vec3b>(row,col)[2] != 0;
            bool pixel_is_not_black = red_channel_is_not_black && green_channel_is_not_black && blue_channel_is_not_black;
            // if the difference frame is not black, we detected a change in the subsequent image
            if (pixel_is_not_black)
            {
                return false;
            }
        }
        return true;
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

#endif // TEARPROCESSING_H
