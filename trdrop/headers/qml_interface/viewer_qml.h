#ifndef VIEWER_QML_H
#define VIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

class ViewerQML : public QQuickPaintedItem
{
    Q_OBJECT

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    ViewerQML(QQuickItem *parent = nullptr)
        : QQuickPaintedItem(parent)
    {
        //! TODO refactor to some global settings
        setImplicitSize(960, 540);
    }

//! methods
public:
    //! TODO
    Q_SIGNAL void requestNextImages();
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
    //! triggers a repainting of the pixmap when the image is copied and drawn
    Q_SLOT void setImage(const QImage & qml_image, QVariant draw_image)
    {
        _draw_image = draw_image.toBool();
        if (draw_image.toBool())
        {
            _qml_image = qml_image.scaledToHeight(static_cast<int>(size().height()), Qt::SmoothTransformation);
        }
        update();
    }
    //! draws the image on the drawable space of the element and request new frames
    //! this is inside this method because I'm not sure if the drawing is async
    void paint(QPainter * painter)
    {
        if (_draw_image)
        {
            int x_padding = 0;
            if (size().width() > _qml_image.width())
            {
                x_padding = static_cast<int>((size().width() - _qml_image.width()) / 2);
            }
            painter->drawImage(0 + x_padding, 0, _qml_image);
        }
        emit requestNextImages();
    }

//! member
private:
    //! image to be rendered
    QImage _qml_image;
    //! TODO
    bool _draw_image;
};


#endif // VIEWER_QML_H
