#ifndef IMAGEVIEWER_H
#define IMAGEVIEWER_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include <QPainter>
#include <QWidget>

//! TODO
class ImageViewer : public QWidget
{
    Q_OBJECT
    Q_PROPERTY(QImage image READ image WRITE setImage USER true)

//! TODO
public:
    //! TODO
    ImageViewer(QWidget * parent = nullptr) : QWidget(parent) { }
    //! TODO
    Q_SLOT void setImage(const QImage &img) {
        if (!painted) qDebug() << "Viewer dropped frame!";
        if (m_img.size() == img.size()
            && m_img.format() == img.format()
            && m_img.bytesPerLine() == img.bytesPerLine())
        {
            std::copy_n(img.bits(), img.sizeInBytes(), m_img.bits());
        }
        else { m_img = img.copy(); }
        painted = false;
        if (m_img.size() != size()) { setFixedSize(m_img.size()); }
        update();
    }
    //! TODO
    QImage image() const { return m_img; }
    //! TODO
    void paintEvent(QPaintEvent *)
    {
        QPainter p(this);
        if (!m_img.isNull()) {
            setAttribute(Qt::WA_OpaquePaintEvent);
            p.drawImage(0, 0, m_img);
            painted = true;
        }
    }

//! TODO
public:
    bool painted = true;
    QImage m_img;
};

#endif // IMAGEVIEWER_H
