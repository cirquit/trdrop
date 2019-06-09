#ifndef IMAGEVIEWER_QML_H
#define IMAGEVIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

class ImageViewerQML : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(bool _allow_painting READ allowPainting WRITE setAllowPainting NOTIFY allowPaintingChanged)

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    ImageViewerQML(QQuickItem *parent = nullptr)
        : QQuickPaintedItem(parent)
        , _allow_painting(true)
    { }

//! methods
public:
    //! QML changed signal for property
    Q_SIGNAL void allowPaintingChanged();
    //! signal to wait for to use the rendered image
    Q_SIGNAL void doneRendering();
    //! resized the texture, width and height of this item
    Q_SLOT void resize(QSize size)
    {
        setWidth(size.width());
        setHeight(size.height());
        setTextureSize(size);
    }
    //! triggers a repainting of the pixmap when the image is copied
    Q_SLOT void setImage(const QImage & qml_image)
    {
        resize(qml_image.size());
        _qml_image = qml_image.copy();
        update();
    }
    //! draws the image on the drawable space of the element and triggers a doneRendering signal when its finished
    void paint(QPainter * painter)
    {
        if (_allow_painting)
        {
            painter->drawImage(0, 0, _qml_image);
            emit doneRendering();
        }
    }
    //! QML getter
    bool allowPainting(){ return _allow_painting; }
    //! QML setter
    void setAllowPainting(bool other) { _allow_painting = other; }

//! member
private:
    //! if set, allows the execution of the paint() method
    bool _allow_painting;
    //! image to be rendered in the pixmap
    QImage _qml_image;
};

#endif // IMAGEVIEWER_QML_H
