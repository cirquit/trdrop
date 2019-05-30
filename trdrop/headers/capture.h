#ifndef CAPTURE_H
#define CAPTURE_H

#include <QObject>
#include <QBasicTimer>
#include <QTimerEvent>
#include <QDebug>
#include "opencv2/opencv.hpp"

//! TODO
class Capture : public QObject {

    Q_OBJECT
    Q_PROPERTY(cv::Mat frame READ frame NOTIFY frameReady USER true)

//! constructors
public:
    //! TODO
    Capture(QObject *parent = nullptr)
        : QObject(parent)
        , _videocapture(new cv::VideoCapture("/home/asa/Videos/billie-eilish-bad-guy.mp4"))
    { }

//! methods
public:
//    //! TODO
//    Q_SIGNAL void started();
//    //! TODO
//    Q_SLOT void start()
//    {
//       if (_videocapture->isOpened()) {
//          _timer.start(0, this);
//          emit started();
//       }
//    }
//    //! TODO
//    Q_SLOT void stop() { _timer.stop(); }
//    //! TODO

    Q_SIGNAL void frameReady(const cv::Mat &);
    //! TODO
    cv::Mat frame() const { return _frame; }
    //! TODO
    Q_SLOT void getNextFrame()
    {
        _videocapture->read(_frame);
        qDebug() << "Reading frame!";
        emit frameReady(_frame);
    }
//! TODO
private:
    //! TODO
//    void timerEvent(QTimerEvent * ev)
//    {
//       if (ev->timerId() != _timer.timerId()) return;
//       if (!_videocapture->read(_frame)) { // Blocks until a new frame is ready
//          _timer.stop();
//          return;
//       }
//       emit frameReady(_frame);
//    }

// member
public:
    //! TODO
    cv::Mat _frame;
    //! TODO
    QBasicTimer _timer;
    //! TODO
    QScopedPointer<cv::VideoCapture> _videocapture;
};

#endif // CAPTURE_H
