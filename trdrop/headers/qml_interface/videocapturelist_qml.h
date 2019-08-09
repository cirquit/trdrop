#ifndef VIDEOCAPTURELISTQML_H
#define VIDEOCAPTURELISTQML_H

#include <QObject>
#include <QDebug>
#include <vector>
#include "opencv2/opencv.hpp"

#include "headers/cpp_interface/videocapturelist.h"

//! A wrapper for videocapturelist in qml
class VideoCaptureListQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    VideoCaptureListQML(quint8 prealloc_video_count,
            QObject *parent = nullptr)
          : QObject(parent)
          , _videocapture_list(VideoCaptureList(prealloc_video_count))
    { }

//! methods
public:
    //! signal to wait for to get the frames
    Q_SIGNAL void framesReady(const QList<cv::Mat> & frame_list);
    //! signal to wait for to finish the video analysis / export
    Q_SIGNAL void finishedProcessing();
    //! tries to read the next frames from all sources and emits framesReady or finishedProcessing signals
    Q_SLOT void readNextFrames()
    {
        // if no video was selected but the rendering could be started is a bug
        if (_videocapture_list.no_videos_opened())
        {
            qDebug() << "Capture.readNextFrames() got triggered with no videos opened, this should never happen";
            return;
        }
        // read the frames if possible, emit corresponding signals
        bool successful_reads = _videocapture_list.populate_next_frames();
        if (!successful_reads)
        {
            restartVideos();
            emit finishedProcessing();
            return;
        }
        emit framesReady(_videocapture_list.frame_list);
    }
    //! tries to open all videos
    Q_SLOT void openAllPaths(const QList<QVariant> & path_list)
    {
        _videocapture_list.open_videos(path_list);
    }
    //! returns the shortest progress of the video 0: start, 1: end of video, because we terminate the export
    Q_INVOKABLE QVariant getShortestVideoProgress() const
    {
        int video_count = static_cast<int>(_videocapture_list.get_open_videos_count());
        double shortest_progress = 0.0;
        for(int i = 0; i < video_count; ++i)
        {
            double current_progress = _get_video_progress(i);
            if (current_progress > shortest_progress)
            {
                shortest_progress = current_progress;
            }
        }
        return shortest_progress;
    }
    //! returns the progress of the video 0: start, 1: end of video
    Q_INVOKABLE QVariant getVideoProgress(const QVariant index) const
    {
        const int _index = index.toInt();
        return _get_video_progress(_index);
    }
    //! restarts the videocaptures with the previously opened videos
    Q_INVOKABLE void restartVideos()
    {
        _videocapture_list.restart_state();
    }
    //! returns the recorded framerates of all videos
    Q_INVOKABLE QList<double> getRecordedFramerates() const
    {
        return _get_recorded_framerates();
    }
    //! returns the recorded framerates of all videos in quint8
    Q_INVOKABLE QList<quint8> getUnsignedRecordedFramerates() const
    {
        QList<double> recorded_framerates = _get_recorded_framerates();
        QList<quint8> unsigned_recorded_framerates;
        for (int i = 0; i < recorded_framerates.size(); ++i)
        {
            unsigned_recorded_framerates.push_back(static_cast<quint8>(recorded_framerates[i]));
        }
        return unsigned_recorded_framerates;
    }
    //! returns the currently opened video count
    Q_INVOKABLE QVariant getOpenVideosCount() const { return static_cast<quint8>(_videocapture_list.get_open_videos_count()) ; }
//! methods
private:
    //! get the current video progress based on the video_index
    double _get_video_progress(const int video_index) const
    {
        const quint64 current_frame_count = _videocapture_list.get_frame_count_by_index(video_index);
        const quint64 max_frame_count     = _videocapture_list.get_max_framecount_by_index(video_index);
        return static_cast<double>(current_frame_count) / static_cast<double>(max_frame_count);
    }
    //! gets the framerates with which the videos were recorded
    QList<double> _get_recorded_framerates() const
    {
        return _videocapture_list.get_recorded_framerates();
    }

//! member
private:
    //! internal videocapture object
    VideoCaptureList _videocapture_list;
};

#endif // VIDEOCAPTURELISTQML_H
