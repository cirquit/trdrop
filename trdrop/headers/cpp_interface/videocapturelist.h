#ifndef VIDEOCAPTURELIST_H
#define VIDEOCAPTURELIST_H

#include <QDebug>
#include <QList>
#include "opencv2/opencv.hpp"

//! TODO
class VideoCaptureList
{

// constructors
public:
    //! preallocates every container
    VideoCaptureList(quint8 prealloc_video_count)
    {
        frame_list.reserve(prealloc_video_count);
        frame_count_list.reserve(prealloc_video_count);
        _videocapture_list.reserve(prealloc_video_count);
    }

//methods
public:
    //! fills the next frames, if possible, returns if the reads for all videocaptures were successful
    bool populate_next_frames()
    {
        if (_container_sizes_not_matched()) _prepare_frame_lists();
        bool successful_frame_read = _videocapture_list.size() > 0;
        for (size_t i = 0; i < _videocapture_list.size(); ++i)
        {
            const int  _index = static_cast<int>(i);
            const bool successful_frame_read = _videocapture_list[i].read(frame_list[_index]);
            // if we have an insuccessful read, we terminate
            if (!successful_frame_read)
            {
                qDebug() << "VideoCaptureList::populate_next_frames(): terminated at index " << i << " at frame " << frame_count_list[i];
                return false;
            }
            frame_count_list[i] += 1;
        }
        return successful_frame_read;
    }
    //! simple getter
    bool no_videos_opened() const { return _videocapture_list.empty(); }
    //! simple getter
    cv::Mat get_frame_by_index(const int index) const
    {
        return frame_list[index];
    }
    //! simple getter (adapted for qt index type)
    quint64 get_frame_count_by_index(const int index) const
    {
        const size_t _index = static_cast<size_t>(index);
        return frame_count_list[_index];
    }
    //! simple getter (adapted for qt index type)
    cv::VideoCapture get_videocapture_by_index(const int index) const
    {
        const size_t _index = static_cast<size_t>(index);
        return _videocapture_list[_index];
    }
    //! simple getter
    quint64 get_max_framecount_by_index(const int index) const
    {
        const double max_frame_count = get_videocapture_by_index(index).get(cv::CAP_PROP_FRAME_COUNT);
        return static_cast<quint64>(max_frame_count);
    }
    //! opens the videocaptures based on the path, TODO check for validity
    void open_videos(const QList<QVariant> & path_list)
    {
        _reset_state();
        for(int i = 0; i < path_list.size(); ++i)
        {
            const QString path = path_list[i].toString();
            cv::VideoCapture vc(path.toStdString());
            _videocapture_list.push_back(vc);
        }
        _prepare_frame_lists();
    }
    //! restarts the videocaptures and resets the accompanying frame lists
    void restart_state()
    {
        for (size_t i = 0; i < _videocapture_list.size(); ++i)
        {
            _videocapture_list[i].set(cv::CAP_PROP_POS_FRAMES, 0);
        }
        _prepare_frame_lists();
    }
    //! TODO
    size_t get_open_videos_count() const
    {
        return _videocapture_list.size();
    }
    //! get the maxmimum captured framerate as we need to know this for the framerate counting
    double get_maximum_captured_framerate(const double default_value) const
    {
        double highest_framerate = default_value;
        for (size_t i = 0; i < _videocapture_list.size(); ++i)
        {
            const double framerate = get_captured_framerate(static_cast<int>(i));
            if (highest_framerate < framerate) { highest_framerate = framerate; }
        }
        return highest_framerate;
    }
    //! returns the raw framerate of the clip with which it was recorded
    double get_captured_framerate(const int index) const
    {
        return get_videocapture_by_index(index).get(cv::CAP_PROP_FPS);
    }

// methods
private:

    //! reset all state of the object
    void _reset_state()
    {
        frame_list.clear();
        frame_count_list.clear();
        _videocapture_list.clear();
    }
    //! sets the size of the frame_list to the size of the videocapture_list (similar to frame_count_list)
    void _prepare_frame_lists()
    {
        frame_list.clear();
        frame_count_list.clear();
        for (size_t i = 0; i < _videocapture_list.size(); ++i)
        {
            frame_list.push_back(cv::Mat());
            frame_count_list.push_back(0);
        }
    }
    //! checks if the container sizes in this class are not matched
    bool _container_sizes_not_matched() const
    {
        return static_cast<size_t>(frame_list.size()) != _videocapture_list.size();
    }

// member
public:
    // holds the frames that will be send via SIGNAL
    QList<cv::Mat>       frame_list;
    // should at all times have the same size as frame_list
    std::vector<quint64> frame_count_list;

private:
    // holds the videocaputers which are qued for frames
    std::vector<cv::VideoCapture> _videocapture_list;
};

#endif // VIDEOCAPTURELIST_H
