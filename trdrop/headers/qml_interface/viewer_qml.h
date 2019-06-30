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
        //drawDefaultImage();
    }

//! methods
public:
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
    //! triggers a repainting of the pixmap when the image is copied
    Q_SLOT void setImage(const QImage & qml_image)
    {
        resize(qml_image.size());
        //qDebug() << "ViewerQML::setImage - " << qml_image;
        _qml_image = qml_image.copy();
        update();
    }
    //! draws the image on the drawable space of the element
    void paint(QPainter * painter)
    {
        painter->drawImage(0, 0, _qml_image);
        emit requestNextImages();
    }

//! member
private:
    //! image to be rendered
    QImage _qml_image;
};


#endif // VIEWER_QML_H
