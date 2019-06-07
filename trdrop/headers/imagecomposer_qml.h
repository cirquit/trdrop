#ifndef IMAGECOMPOSER_QML_H
#define IMAGECOMPOSER_QML_H

#include <QObject>
#include <QPainter>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"

//! converts the images from cv::Mat to QImage
class ImageComposerQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    ImageComposerQML(QObject * parent = nullptr)
        : QObject(parent)
        , _size(QSize(1280, 1080))
    { }

//! methods
public:
    //! signal to wait for to render the full image
    Q_SIGNAL void imageReady(const QImage & composed_image);
    //! side by side only right now
    Q_SLOT void processImages(const QList<QImage> & _qml_image_list)
    {
        if (_qml_image_list.size() == 3)
        {
            const QImage centered_image_01 = _get_center_from_image(_qml_image_list[0], 2);
            const QImage centered_image_02 = _get_center_from_image(_qml_image_list[1], 2);
            const QImage centered_image_03 = _get_center_from_image(_qml_image_list[2], 3);

            _qml_image = QImage(_size.width(), _size.height(), QImage::Format_RGB888);
            QPainter painter;
            painter.begin(&_qml_image);
            painter.drawImage(0, 0, centered_image_01);
            painter.drawImage(static_cast<int>(_size.width() / 3.0),     0, centered_image_02);
            painter.drawImage(static_cast<int>(_size.width() / 3.0) * 2, 0, centered_image_03);
            painter.end();
        }
        if (_qml_image_list.size() == 2)
        {
            const QImage centered_image_01 = _get_center_from_image(_qml_image_list[0], 2);
            const QImage centered_image_02 = _get_center_from_image(_qml_image_list[1], 2);

            _qml_image = QImage(_size.width(), _size.height(), QImage::Format_RGB888);
            QPainter painter;
            painter.begin(&_qml_image);
            painter.drawImage(0, 0, centered_image_01);
            painter.drawImage(static_cast<int>(_size.width() / 2.0), 0, centered_image_02);
            painter.end();
        }
        if (_qml_image_list.size() == 1)
        {
            _qml_image = _qml_image_list[0].copy();
            _qml_image.scaledToWidth(_size.width());
            _qml_image.scaledToHeight(_size.height());
        }
        emit imageReady(_qml_image);
    }
    //! TODO
    Q_SLOT void resizeComposition(const QSize & size)
    {
        _size = size;
        _qml_image.scaledToWidth(_size.width());
        _qml_image.scaledToHeight(_size.height());
        emit imageReady(_qml_image);
    }

private:
    //!
    QImage _get_center_from_image(const QImage & image, quint8 video_count)
    {
        const int single_video_width  = static_cast<int>(_size.width()  / static_cast<double>(video_count));
        const int single_video_height = static_cast<int>(_size.height() / static_cast<double>(video_count));

        const int center_x = static_cast<int>(image.width() / 2.0);
        const int center_y = static_cast<int>(image.width() / 2.0);

        const int modified_x = center_x - static_cast<int>(single_video_width / 2.0);
        const int modified_y = center_y - static_cast<int>(single_video_height / 2.0);
        return image.copy(modified_x, modified_y, single_video_width, single_video_height);
    }

//! member
public:
    //!
    QImage _qml_image;
    //!
    QSize  _size;
};


#endif // IMAGECOMPOSER_QML_H
