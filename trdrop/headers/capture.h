#ifndef CAPTURE_H
#define CAPTURE_H

#include <QObject>
#include <QDebug>
#include <vector>
#include "opencv2/opencv.hpp"

//! TODO
class Capture : public QObject {

    Q_OBJECT
    //Q_PROPERTY(cv::Mat frame READ frame NOTIFY frameReady USER true)

    //"/home/asa/Videos/billie-eilish-bad-guy.mp4"

//! constructors
public:
    //! reserves the memory for prealloc_video_count amount of videos
    Capture(quint8 prealloc_video_count,
            QObject *parent = nullptr)
        : QObject(parent)
    {
        _frame_list.reserve(prealloc_video_count);
        _videocapture_list.reserve(prealloc_video_count);
    }

//! methods
public:
    //! signal to wait for on any successional converter
    Q_SIGNAL void framesReady(const QList<cv::Mat> & _frame_list);
    //! reallocates the framelist if need be, then reads one frame from each videocapture
    //! and emits the framesReady signal
    Q_SLOT void readNextFrames()
    {
        bool not_enough_frames_allocated = _videocapture_list.size() > static_cast<size_t>(_frame_list.size());
        if (not_enough_frames_allocated) _prepare_frame_list();

        for (size_t i = 0; i < _videocapture_list.size(); ++i) _videocapture_list[i].read(_frame_list[i]);

        emit framesReady(_frame_list);
    }
    //! try to open all paths with the cv::VideoCapture
    //! TODO: check for errors
    Q_INVOKABLE void openAllPaths(const QList<QVariant> & path_list)
    {
        _reset_state();
        for(int i = 0; i < path_list.size(); ++i)
        {
            const QString path  = path_list[i].toString();
            cv::VideoCapture vc(path.toStdString());
            _videocapture_list.push_back(vc);
        }
    }

//! methods
private:
    //! reset all state of the object
    void _reset_state()
    {
        _frame_list.clear();
        _videocapture_list.clear();
        _current_frame_count = 0;
    }
    //! resets the frame_list member and reads the current frame from each videocapture
    //! TODO: maybe set the videocaptures to 0'th frame
    void _prepare_frame_list()
    {
        _frame_list.clear();
        for (size_t i = 0; i < _videocapture_list.size(); ++i)
        {
            cv::Mat frame;
            _videocapture_list[i].read(frame);
            _frame_list.push_back(frame);
        }
    }

//! member
private:
    //! TODO
    QList<cv::Mat> _frame_list;
    //! TODO
    std::vector<cv::VideoCapture> _videocapture_list;
    //! TODO
    quint64 _current_frame_count;
};

#endif // CAPTURE_H
