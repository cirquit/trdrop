#ifndef QML_IMAGEVIEWER_H
#define QML_IMAGEVIEWER_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

class QMLImageViewer : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(QImage image READ image WRITE setImage USER true)

public:
    QMLImageViewer(QQuickItem *parent = nullptr)
        : QQuickPaintedItem(parent)
    { }
    //! TODO
    QImage image() const { return _image; }
    //! TODO
    Q_SIGNAL void doneRendering();
    //! TODO
    Q_SLOT void setImage(const QImage & other) {
        // if paintEvent has not finished updating, we discard the frame
        //if (!_finished_painting) qDebug() << "Viewer dropped frame!";

        bool same_resolution    = _image.size() == other.size();
        bool same_format        = _image.format() == other.format();
        bool same_line_bytesize = _image.bytesPerLine() == other.bytesPerLine();
        // copy bit by bit if image meta data is the same
        if (same_resolution && same_format && same_line_bytesize)
        {
            std::copy_n(other.bits(), other.sizeInBytes(), _image.bits());
        } // benchmark this copy compared to std::copy_n
        else { _image = other.copy(); }
        // now we should start painting if a paintEvent is triggered
        //_finished_painting = false;
        // TODO rescale widget on source sizechange?
        if (other.size() != size()) {
            setWidth(other.size().width());
            setHeight(other.size().height());
            setTextureSize(other.size());
        }
        // TODO is this like a model update?
        update();
    }
    //! TODO
    void paint(QPainter * painter)
    {
        painter->drawImage(0, 0, _image);
        emit doneRendering();
    }

private:
    QString _name;
    QColor _color;
    //! TODO
    QImage _image;
};

#endif // QML_IMAGEVIEWER_H
