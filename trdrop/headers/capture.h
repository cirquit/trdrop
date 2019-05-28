#ifndef CAPUTRE_H
#define CAPUTRE_H

#include <QObject>
#include <QBasicTimer>
#include <QTimerEvent>
#include <QDebug>
#include "opencv2/opencv.hpp"

//! TODO
class Capture : public QObject {

    Q_OBJECT
    Q_PROPERTY(cv::Mat frame READ frame NOTIFY frameReady USER true)

//! TODO
public:
    //! TODO
    Capture(QObject *parent = {}) : QObject(parent) { }
    //! TODO
    Q_SIGNAL void started();
    //! TODO
    Q_SLOT void start()
    {
       if (!m_videoCapture)
          m_videoCapture.reset(new cv::VideoCapture("/home/asa/Videos/billie-eilish-bad-guy.mp4"));
       if (m_videoCapture->isOpened()) {
          m_timer.start(0, this);
          emit started();
       }
    }
    //! TODO
    Q_SLOT void stop() { m_timer.stop(); }
    //! TODObillie-eilish-bad-guy.mp4

    Q_SIGNAL void frameReady(const cv::Mat &);
    //! TODO
    cv::Mat frame() const { return m_frame; }

//! TODO
private:
    //! TODO
    void timerEvent(QTimerEvent * ev)
    {
       if (ev->timerId() != m_timer.timerId()) return;
       if (!m_videoCapture->read(m_frame)) { // Blocks until a new frame is ready
          m_timer.stop();
          return;
       }
       emit frameReady(m_frame);
    }

// member
public:
    //! TODO
    cv::Mat m_frame;
    //! TODO
    QBasicTimer m_timer;
    //! TODO
    QScopedPointer<cv::VideoCapture> m_videoCapture;
};

#endif // CAPUTRE_H
