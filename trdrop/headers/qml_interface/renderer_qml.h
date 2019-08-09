#ifndef IMAGEVIEWER_QML_H
#define IMAGEVIEWER_QML_H

#include <QtQuick/QQuickPaintedItem>
#include <QPainter>
#include <QColor>

#include <memory>
#include "headers/cpp_interface/framerateoptions.h"
#include "headers/qml_models/exportoptionsmodel.h"
#include "headers/cpp_interface/framerateplot.h"
#include "headers/cpp_interface/frametimeplot.h"

#include "headers/cpp_interface/tearmodel.h"

//! Renders all visual elements (plots / text / tears) onto the qimage
class RendererQML : public QObject
{
    Q_OBJECT

//! constructors
public:
    //! default constructor
    RendererQML(std::shared_ptr<QList<FramerateOptions>> shared_fps_options_list
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
    //! paints all elements and emits imageReady when done
    Q_SLOT void processImage(QImage qml_image)
    {
        // if somehow the image is null, we don't terminate (should not happen)
        if (qml_image.isNull()) return;

        // convert to alpha
        if (_shared_export_options_model->export_as_overlay())
        {
            qml_image = QImage(qml_image.size(), QImage::Format_ARGB32);
            qml_image.fill(Qt::transparent);
        } else {
            _qml_image = qml_image.copy();
        }

        QPainter painter;
        painter.begin(&qml_image);

        // paint framerate dependent "widgets"
        if (_shared_general_options_model->get_enable_framerate_analysis())
        {
            _draw_fps_text(painter);
            _draw_framerate_graph(painter);
        }
        // paint frametime dependent "widgets"
        if (_shared_general_options_model->get_enable_frametime_analysis())
        {
            _draw_frametime_graph(painter);
        }
        // paint tear depedent "widgets"
        if (_shared_general_options_model->get_enable_tear_analysis())
        {
            _draw_tears(painter);
        }

        painter.end();
        emit imageReady(qml_image);
    }
    //! can be triggered if options change
    Q_SLOT void redraw()
    {
        processImage(_qml_image);
    }

//! methods
private:
    //! paint framerate text
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
    //! calls the underlying instance to draw the graph
    void _draw_framerate_graph(QPainter & painter)
    {
        _shared_framerate_plot_instance->draw_framerate_plot(&painter);
    }
    //! calls the underlying instance to draw the graph
    void _draw_frametime_graph(QPainter & painter)
    {
        _shared_frametime_plot_instance->draw_frametime_plot(&painter);
    }
    //! calls each tearmodel to draw each tear
    void _draw_tears(QPainter & painter)
    {
        _shared_tear_model->draw_tears(&painter);
    }
    //! returns the amount of videos loaded (slightly dirty)
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
    //! used to get te video_count
    std::shared_ptr<QList<FramerateOptions>> _shared_fps_options_list;
    //! used to check what needs to be drawn
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
    //! used to check if overlay only is exported
    std::shared_ptr<ExportOptionsModel> _shared_export_options_model;
    //! used draw the framerate plot
    std::shared_ptr<FrameratePlot> _shared_framerate_plot_instance;
    //! used to draw frametime plot
    std::shared_ptr<FrametimePlot> _shared_frametime_plot_instance;
    //! used to draw the tears
    std::shared_ptr<TearModel> _shared_tear_model;
};

#endif // IMAGEVIEWER_QML_H
