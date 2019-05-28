#ifndef CONVERTER_H
#define CONVERTER_H

#include <QObject>
#include <QImage>
#include <QBasicTimer>
#include <QTimerEvent>
#include <QDebug>
#include "opencv2/opencv.hpp"

//! TODO
class Converter : public QObject {

    Q_OBJECT
    Q_PROPERTY(QImage image      READ image      NOTIFY imageReady USER true)
    Q_PROPERTY(bool   processAll READ processAll WRITE setProcessAll)

//! TODO
public:
    //! TODO
    void queue(const cv::Mat &frame)
    {
        if (!m_frame.empty()) qDebug() << "Converter dropped frame!";
        m_frame = frame;
        if (! m_timer.isActive()) m_timer.start(0, this);
    }
    //! TODO
    void process(const cv::Mat &frame)
    {
        Q_ASSERT(frame.type() == CV_8UC3);
        int width = static_cast<int>(frame.cols / 3.0);
        int height = static_cast<int>(frame.rows / 3.0);
        if (m_image.size() != QSize{width,height})
            m_image = QImage(width, height, QImage::Format_RGB888);
        cv::Mat mat(height
                  , width
                  , CV_8UC3
                  , m_image.bits()
                  , static_cast<size_t>(m_image.bytesPerLine()));
        cv::resize(frame, mat, mat.size(), 0, 0, cv::INTER_AREA);
        cv::cvtColor(mat, mat, cv::COLOR_RGB2BGR);
        emit imageReady(m_image);
    }
    //! TODO
    void timerEvent(QTimerEvent *ev)
    {
        if (ev->timerId() != m_timer.timerId()) return;
        process(m_frame);
        m_frame.release();
        m_timer.stop();
    }

//! TODO
public:
    //! TODO
    Converter(QObject * parent = nullptr)
        : QObject(parent)
        , m_processAll(true)
    { }
    //! TODO
    bool processAll() const { return m_processAll; }
    //! TODO
    void setProcessAll(bool all) { m_processAll = all; }
    //! TODO
    Q_SIGNAL void imageReady(const QImage &);
    //! TODO
    QImage image() const { return m_image; }
    //! TODO
    Q_SLOT void processFrame(const cv::Mat &frame)
    {
        if (m_processAll) process(frame); else queue(frame);
    }

//! TODO
public:
    //! TODO
    QBasicTimer m_timer;
    //! TODO
    cv::Mat m_frame;
    //! TODO
    QImage m_image;
    //! TODO
    bool m_processAll;
};

#endif // CONVERTER_H
