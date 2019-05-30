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
    //Q_PROPERTY(bool   processAll READ processAll WRITE setProcessAll)

//! constructors
public:
    //! TODO
    Converter(QObject * parent = nullptr)
        : QObject(parent)
        //, m_processAll(true)
    { }

//! methods
public:
    //! TODO
//    void queue(const cv::Mat &cv_image)
//    {
//        //if (!_cv_image.empty()) qDebug() << "Converter dropped cv_image!";
//        _cv_image = cv_image;
//        // if (! m_timer.isActive()) m_timer.start(0, this);
//    }
    //!
    void process(const cv::Mat & other)
    {
        // why does this have to be this type?
        Q_ASSERT(other.type() == CV_8UC3);

        int width  = static_cast<int>(other.cols / 3.0);
        int height = static_cast<int>(other.rows / 3.0);
        // resize if need be
        if (_qml_image.size() != QSize { width, height })
        {
            _qml_image = QImage(width, height, QImage::Format_RGB888);
        }
        // is this the copy?
        cv::Mat mat(height, width, CV_8UC3, _qml_image.bits(), static_cast<size_t>(_qml_image.bytesPerLine()));
        cv::resize(other, mat, mat.size(), 0, 0, cv::INTER_AREA);
        cv::cvtColor(mat, mat, cv::COLOR_RGB2BGR);
        qDebug() << "emitting imageReady";
        emit imageReady(_qml_image);
    }
//    //! TODO
//    void timerEvent(QTimerEvent *ev)
//    {
//        if (ev->timerId() != m_timer.timerId()) return;
//        process(_cv_image);
//        _cv_image.release();
//        m_timer.stop();
//    }

//! TODO

    //! TODO
    //bool processAll() const { return m_processAll; }
    //! TODO
    //void setProcessAll(bool all) { m_processAll = all; }
    //! TODO
    Q_SIGNAL void imageReady(const QImage & image);
    //! TODO
    QImage image() const { return _qml_image; }
    //! TODO
    Q_SLOT void processFrame(const cv::Mat & cv_image)
    {
        //if (m_processAll) process(cv_image); else queue(cv_image);
        process(cv_image);
        qDebug() << "Processing frame!";
    }

//! TODO
public:
    //! TODO
    //QBasicTimer m_timer;
    //! TODO
    cv::Mat _cv_image;
    //! TODO
    QImage _qml_image;
    //! TODO
    //bool m_processAll;
};

#endif // CONVERTER_H
