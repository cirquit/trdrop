#ifndef VIDEOCAPTURELISTQML_H
#define VIDEOCAPTURELISTQML_H

#include <QObject>
#include <QDebug>
#include <vector>
#include "opencv2/opencv.hpp"

#include "headers/cpp_interface/videocapturelist.h"

//! A wrapper for videocaputrelist
class VideoCaptureListQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! initializes the videocapture list
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
        // read the frames if possible
        bool successful_reads = _videocapture_list.populate_next_frames();
        if (!successful_reads)
        {
            restartVideos();
            emit finishedProcessing();
            return;
        }
        qDebug() << "VideoCaptureListQML::readNextFrames()";
        emit framesReady(_videocapture_list.frame_list);
    }
    //! tries to open all videos
    Q_SLOT void openAllPaths(const QList<QVariant> & path_list)
    {
        qDebug() << "Opening" << path_list.size() << "videos";
        _videocapture_list.open_videos(path_list);
    }
    //! returns the progress of the video 0: start, 1: end of video
    Q_INVOKABLE QVariant getVideoProgress(const QVariant index) const
    {
        const int _index = index.toInt();
        const quint64 current_frame_count = _videocapture_list.get_frame_count_by_index(_index);
        const quint64 max_frame_count     = _videocapture_list.get_max_framecount_by_index(_index);
        return static_cast<double>(current_frame_count) / static_cast<double>(max_frame_count);
    }
    //! restarts the videocaptures with the previously opened videos
    Q_INVOKABLE void restartVideos()
    {
        _videocapture_list.restart_state();
    }

//! member
private:
    VideoCaptureList _videocapture_list;
};

#endif // VIDEOCAPTURELISTQML_H
