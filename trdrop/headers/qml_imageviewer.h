#ifndef QML_IMAGEVIEWER_H
#define QML_IMAGEVIEWER_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

class QMLImageViewer : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(QImage _test USER true) // image WRITE setImage USER true)
    Q_PROPERTY(bool _allow_painting READ allowPainting WRITE setAllowPainting NOTIFY allowPaintingChanged)

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    QMLImageViewer(QQuickItem *parent = nullptr)
        : QQuickPaintedItem(parent)
        , _allow_painting(true)
    {
        // TODO refractor this from cofngi
        _qml_image_list.reserve(3);
    // TODO from config
    // setHeight
    // setWidth
    // setTextureSize()
    }

//! methods
public:
    //! QML changed signal for property
    Q_SIGNAL void allowPaintingChanged();
    //! signal to wait and request the next frame
    Q_SIGNAL void doneRendering();
    //! resized the texture, width and height of this item
    Q_SLOT void resize(QSize size)
    {
        setWidth(size.width());
        setHeight(size.height());
        setTextureSize(size);
    }
    //! copies all the images and does the necessary preprocessing to show them
    Q_SLOT void setImages(const QList<QImage> & qml_image_list) {

        _test = qml_image_list[0].copy();
        resize(qml_image_list[0].size());
        // copy all images to our image list
        // for (int i = 0; i < qml_image_list.size(); ++i)
        // {
        //     const QImage & other = qml_image_list[i];
        //     _copy_image_to_list(other, i);
        // }
        // remove unneeded ones
        //const bool too_many_allocated_images = qml_image_list.size() < _qml_image_list.size();
        //if (too_many_allocated_images)
        //{
        //    const int image_count = _qml_image_list.size() - qml_image_list.size();
        //    auto from_iter = _qml_image_list.end() - image_count;
        //    _qml_image_list.erase(from_iter, _qml_image_list.end());
        //}

        // triggers an event in the QML Scene Graph which triggers a repainting when it's ready
        update();
        // TODO why does it not update
    }
    //! draws the image on the drawable space of the element and
    //! might trigger a doneRendering signal if its finished
    void paint(QPainter * painter)
    {
        bool images_available = _qml_image_list.size() > 0;
        qDebug() << "got here!";
        painter->drawImage(0, 0, _test);
        emit doneRendering();
        if (_allow_painting && images_available)
        {

            // combine the images based on the layout
            if (_qml_image_list.size() == 3)
            {
                painter->drawImage(0, 0, _qml_image_list[0]);
            }
            if (_qml_image_list.size() == 2)
            {
                painter->drawImage(0, 0, _qml_image_list[0]);
            }
            if (_qml_image_list.size() == 1)
            {
                painter->drawImage(0, 0, _qml_image_list[0]);
            }
            emit doneRendering();
        }
    }
    //! QML getter
    bool allowPainting(){ return _allow_painting; }
    //! QML setter
    void setAllowPainting(bool other) { _allow_painting = other; }

    //! methods
private:
    //! simply copies the incoming image to the image at that index in the qml_image_list
    //! TODO rescale?
    void _copy_image_to_list(const QImage & other, int index)
    {
        bool no_image_allocated_yet = index + 1 > _qml_image_list.size();
        if (no_image_allocated_yet) { _qml_image_list.push_back(other); return; }

        //QImage & image =;
        //bool same_resolution    = image.size() == other.size();
        //bool same_format        = image.format() == other.format();
        //bool same_line_bytesize = image.bytesPerLine() == other.bytesPerLine();
        // copy bit by bit if image meta data is the same
        //if (same_resolution && same_format && same_line_bytesize)
        //{
        //    std::copy_n(other.bits(), other.sizeInBytes(), image.bits());
        //} // benchmark this copy compared to std::copy_n
        //else {
            _qml_image_list[index] = other.copy();
    //}
    }

//! member
private:
    //! if set, allows the execution of the paint() method
    bool _allow_painting;
    //! hold all the images which are to be rendered
    QList<QImage> _qml_image_list;
    //!
    QImage _test;
};

#endif // QML_IMAGEVIEWER_H
