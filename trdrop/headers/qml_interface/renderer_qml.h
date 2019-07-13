#ifndef IMAGEVIEWER_QML_H
#define IMAGEVIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>


// TODO only for shared pointer
#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"

#include "headers/cpp_interface/fpsoptions.h"
#include "headers/qml_models/exportoptionsmodel.h"

class RendererQML : public QObject
{
    Q_OBJECT

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    RendererQML(std::shared_ptr<QList<FPSOptions>> shared_fps_options_list
              , QQuickItem *parent = nullptr)
        : QObject(parent)
        , _shared_fps_options_list(shared_fps_options_list)
    { }

//! methods
public:
    //! signal to wait for to render the full image
    Q_SIGNAL void imageReady(const QImage & image);

    //! TODO
    Q_SLOT void processImage(QImage qml_image)
    {
        if (qml_image.isNull()) return;

        _qml_image = qml_image.copy();

        QPainter painter;
        painter.begin(&qml_image);

        _draw_fps_text(painter);
        _draw_framerate_graph(painter);
        _draw_frametime_graph(painter);

        painter.end();
        emit imageReady(qml_image);
    }
    //! TODO
    Q_SLOT void redraw()
    {
        processImage(_qml_image);
    }

private:
    //! TODO
    void _draw_fps_text(QPainter & painter)
    {
        int video_count  = _get_video_count();
        int image_width  = _qml_image.size().width();
        int image_height = _qml_image.size().height();

        for(int i = 0; i < _shared_fps_options_list->size(); ++i)
        {
            const bool options_enabled = (*_shared_fps_options_list)[i].enabled;
            const bool text_enabled    = (*_shared_fps_options_list)[i].displayed_text.enabled();
            if (options_enabled && text_enabled)
            {
                int x_padding = static_cast<int>(image_width / 28);
                int x_step = static_cast<int>(image_width / video_count);
                int y_step = static_cast<int>(image_height / 12);
                int x = x_padding + x_step * i; // width
                int y = y_step; // height
                (*_shared_fps_options_list)[i].paint_fps_text(&painter, x, y);
            }
        }
    }
    //! TODO
    void _draw_framerate_graph(QPainter & painter)
    {
        Q_UNUSED(painter);
    }
    //! TODO
    void _draw_frametime_graph(QPainter & painter)
    {
        Q_UNUSED(painter);
    }
    //! TODO dirty, get this from FileWindow
    int _get_video_count()
    {
        int video_count = 0;
        for(int i = 0; i < _shared_fps_options_list->size(); ++i)
        {
            if ((*_shared_fps_options_list)[i].enabled) ++video_count;
        }
        return video_count;
    }

//! member
private:
    //! cached image to draw onto
    QImage _qml_image;
    //! TODO
    std::shared_ptr<QList<FPSOptions>> _shared_fps_options_list;
};

#endif // IMAGEVIEWER_QML_H
