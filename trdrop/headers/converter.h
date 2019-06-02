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

//! constructors
public:
    //! TODO
    Converter(QObject * parent = nullptr)
        : QObject(parent)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void imagesReady(const QList<QImage> & qml_image_list);
    //! TODO
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {
        qDebug() << "Processing " << cv_image_list.size() << " frame(s)!";
        _prepare_image_list(cv_image_list.size());
        for (int i = 0; i < cv_image_list.size(); ++i)
        {
            _process_frame_to_image(cv_image_list.at(i), i);
        }
        qDebug() << "emitting imagesReady";
        emit imagesReady(_qml_image_list);
    }

private:
    //! TODO
    void _process_frame_to_image(const cv::Mat & frame, const int index)
    {
        // why does this have to be this type?
        Q_ASSERT(frame.type() == CV_8UC3);
        int width  = static_cast<int>(frame.cols / 3.0);
        int height = static_cast<int>(frame.rows / 3.0);
        // resize if need be
        if (_qml_image_list.at(index).size() != QSize { width, height })
        {
            _qml_image_list.replace(index, QImage(width, height, QImage::Format_RGB888));
        }
        QImage & local_image = _qml_image_list[index];
        // copy bits by a pointer to the image data
        cv::Mat mat(height
                  , width
                  , CV_8UC3
                  , local_image.bits()
                  , static_cast<size_t>(_qml_image_list.at(index).bytesPerLine()));
        cv::resize(frame, mat, mat.size(), 0, 0, cv::INTER_AREA);
        cv::cvtColor(mat, mat, cv::COLOR_RGB2BGR);
    }
    //! expands or reduces the _qml_image_list to the frame_list_size
    void _prepare_image_list(int frame_list_size)
    {
        bool expand_image_list = frame_list_size > _qml_image_list.size();
        if (expand_image_list)
        {
             for (int i = _qml_image_list.size(); i <  frame_list_size; ++i)
             {
                 // expand to the video resolution of the video source
                 _qml_image_list.push_back(_get_default_qimage());
             }
        }

        bool reduce_image_list = frame_list_size < _qml_image_list.size();
        if (reduce_image_list)
        {
            _qml_image_list.clear();
            for (int i = 0; i <  frame_list_size; ++i)
            {
                // TODO
                _qml_image_list.push_back(_get_default_qimage());
            }
        }
    }
    //! TODO, expand to the video sizes of the frames
    QImage _get_default_qimage() { return QImage(); }

//! TODO
public:
    //! TODO update _process_frame_to_image and everything else
    QList<QImage> _qml_image_list;
};

#endif // CONVERTER_H
