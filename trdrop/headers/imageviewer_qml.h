#ifndef IMAGEVIEWER_QML_H
#define IMAGEVIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

class ImageViewerQML : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(bool _emit_rendering_signal READ emitRenderingSignal WRITE setEmitRenderingSignal NOTIFY emitRenderingSignalChanged)

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    ImageViewerQML(QQuickItem *parent = nullptr)
        : QQuickPaintedItem(parent)
        , _emit_rendering_signal(false)
    {
        //! TODO refactor to some global settings
        setImplicitSize(960, 540);
    }

//! methods
public:
    //! QML changed signal for property
    Q_SIGNAL void emitRenderingSignalChanged();
    //! signal to wait for to use the rendered image
    Q_SIGNAL void doneRendering();
    //! resized the texture, width and height of this item
    Q_SLOT void resize(QSize size)
    {
        setWidth(size.width());
        setHeight(size.height());
        setTextureSize(size);
    }
    //! TODO
    Q_SLOT void drawDefaultImage()
    {
        const QSize default_size(960, 540);
        _qml_image = QImage(default_size, QImage::Format_RGB888);
        _qml_image.fill(QColor(255, 255, 255));
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
        painter->drawImage(0, 0, _qml_image);
        if (_emit_rendering_signal)
        {
            emit doneRendering();
        }
    }
    //! QML getter
    bool emitRenderingSignal(){ return _emit_rendering_signal; }
    //! QML setter
    void setEmitRenderingSignal(bool other) { _emit_rendering_signal = other; }

//! member
private:
    //! if set, allows after the execution of the paint() method to emit the doneRendering() signal
    bool _emit_rendering_signal;
    //! image to be rendered in the pixmap
    QImage _qml_image;
};

#endif // IMAGEVIEWER_QML_H
