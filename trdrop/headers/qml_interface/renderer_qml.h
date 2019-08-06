#ifndef IMAGEVIEWER_QML_H
#define IMAGEVIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

#include <memory>
#include "headers/cpp_interface/fpsoptions.h"
#include "headers/qml_models/exportoptionsmodel.h"
#include "headers/cpp_interface/framerateplot.h"
#include "headers/cpp_interface/frametimeplot.h"

#include "headers/cpp_interface/tearmodel.h"

class RendererQML : public QObject
{
    Q_OBJECT

//! constructors
public:
    //! quick painted item, essentially a label with a drawable interface
    RendererQML(std::shared_ptr<QList<FPSOptions>> shared_fps_options_list
              , std::shared_ptr<GeneralOptionsModel> shared_general_options_model
              , std::shared_ptr<ExportOptionsModel> shared_export_options_model
              , std::shared_ptr<FrameratePlot> shared_framerate_plot_instance
              , std::shared_ptr<FrametimePlot> shared_frametime_plot_instance
              , std::shared_ptr<TearModel> shared_tear_model
              , QQuickItem *parent = nullptr)
        : QObject(parent)
        , _shared_fps_options_list(shared_fps_options_list)
        , _shared_general_options_model(shared_general_options_model)
        , _shared_export_options_model(shared_export_options_model)
        , _shared_framerate_plot_instance(shared_framerate_plot_instance)
        , _shared_frametime_plot_instance(shared_frametime_plot_instance)
        , _shared_tear_model(shared_tear_model)
    { }

//! methods
public:
    //! signal to wait for to render the full image
    Q_SIGNAL void imageReady(const QImage & image);
    //! TODO
    Q_SLOT void processImage(QImage qml_image)
    {
        if (qml_image.isNull()) return;

        if (_shared_export_options_model->export_as_overlay())
        {
            _qml_image = QImage(qml_image.size(), QImage::Format_ARGB32);
            _qml_image.fill(Qt::transparent);
        } else {
            _qml_image = qml_image.copy();
        }

        QPainter painter;
        painter.begin(&qml_image);

        if (_shared_general_options_model->get_enable_framerate_analysis())
        {
            _draw_fps_text(painter);
            _draw_framerate_graph(painter);
        }
        if (_shared_general_options_model->get_enable_frametime_analysis())
        {
            _draw_frametime_graph(painter);
        }
        if (_shared_general_options_model->get_enable_tear_analysis())
        {
            _draw_tears(painter);
        }

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

        // this positioning logic is not inside the fps options as we need the index
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
        _shared_framerate_plot_instance->draw_framerate_plot(&painter);
    }
    //! TODO
    void _draw_frametime_graph(QPainter & painter)
    {
        _shared_frametime_plot_instance->draw_frametime_plot(&painter);
    }
    //! TODO
    void _draw_tears(QPainter & painter)
    {
        _shared_tear_model->draw_tears(&painter);
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
    //! TODO
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
    //! TODO
    std::shared_ptr<ExportOptionsModel> _shared_export_options_model;
    //! TODO
    std::shared_ptr<FrameratePlot> _shared_framerate_plot_instance;
    //! TODO
    std::shared_ptr<FrametimePlot> _shared_frametime_plot_instance;
    //! TODO
    std::shared_ptr<TearModel> _shared_tear_model;
};

#endif // IMAGEVIEWER_QML_H
