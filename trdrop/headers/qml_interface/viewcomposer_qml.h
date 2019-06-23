#ifndef IMAGEVIEWER_QML_H
#define IMAGEVIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QScopedPointer>
#include <QOpenGLFramebufferObject>
#include <QColor>

#include "headers/cpp_interface/fpsoptions.h"

class ViewerComposerQML : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(bool _emit_rendering_signal READ emitRenderingSignal WRITE setEmitRenderingSignal NOTIFY emitRenderingSignalChanged)

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    ViewerComposerQML(QQuickItem *parent = nullptr)
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
        // TODO dirty
        int video_count = 0;
        for(int i = 0; i < _fps_option_list.size(); ++i)
        {
            if (_fps_option_list[i].enabled) ++video_count;
        }

        for(int i = 0; i < _fps_option_list.size(); ++i)
        {
            if (_fps_option_list[i].enabled)
            {
                painter->setPen(_fps_option_list[i].fps_plot_color.color());

                int x_padding = static_cast<int>(size().width() / 28);
                int x_step = static_cast<int>(size().width() / video_count);
                int y_step = static_cast<int>(size().height() / 15);
                int x = x_padding + x_step * i; // width
                int y = y_step; // height
                painter->setFont(_fps_option_list[i].displayed_text.font());
                painter->drawText(x, y, _fps_option_list[i].displayed_text.value());
            }
        }
        if (_emit_rendering_signal)
        {
            emit doneRendering();
        }
    }
    //! TODO
    Q_SLOT void setFPSOptions(const QList<FPSOptions> fpsOptionsList)
    {
        _fps_option_list = fpsOptionsList;
        update();
    }
    //! QML getter
    Q_SLOT bool emitRenderingSignal(){ return _emit_rendering_signal; }
    //! QML setter
    Q_SLOT void setEmitRenderingSignal(bool other) { _emit_rendering_signal = other; }

//! member
private:
    //! if set, allows after the execution of the paint() method to emit the doneRendering() signal
    bool _emit_rendering_signal;
    //! image to be rendered in the pixmap
    QImage _qml_image;
    //! TODO
    QList<FPSOptions> _fps_option_list;
};

#endif // IMAGEVIEWER_QML_H
