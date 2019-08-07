#ifndef FRAMETIMEPLOT_H
#define FRAMETIMEPLOT_H

#include <QPainter>
#include <memory>
#include "headers/cpp_interface/frametimemodel.h"
#include "headers/cpp_interface/framerateoptions.h"
#include "headers/qml_models/resolutionsmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"

class FrametimePlot
{
// constructors
public:
    //! TODO
    FrametimePlot(std::shared_ptr<FrametimeModel> shared_frametime_model
       , std::shared_ptr<QList<FramerateOptions>> shared_fps_options_list
       , std::shared_ptr<ResolutionsModel> shared_resolution_model
       , std::shared_ptr<GeneralOptionsModel> shared_general_options_model)
        : _shared_frametime_model(shared_frametime_model)
        , _shared_fps_options_list(shared_fps_options_list)
        , _shared_resolution_model(shared_resolution_model)
        , _shared_general_options_model(shared_general_options_model)
        , _plot_outline_color(236, 236, 236) // almost white
        , _plot_innerline_color(193, 193, 193) // light grey
        , _plot_text_color(255, 255, 255) // white
        , _text_shadow(41, 41, 41) // dark grey
        , _segment_count(3) // we want to split the plot into 3 bars
        , _eyecandy_text("FRAMETIME IN MS")
    { }

// methods
public:
    //! top left is (0,0)
    void draw_frametime_plot(QPainter * painter)
    {
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setRenderHint(QPainter::HighQualityAntialiasing);

        _draw_plot_outline(painter);
        _draw_plot_inner_lines(painter);
        _draw_text(painter);
        _draw_eyecandy_text(painter);
        _draw_frametimes(painter);
    }

// methods
private:
    //! draws a rectangle based on the resolution and sets the _plot_outline member for every successor to use
    void _draw_plot_outline(QPainter * painter)
    {
        // make it dependent on the current resolution
        const QSize current_size = _shared_resolution_model->get_active_size();
        const int image_width    = current_size.width();
        const int image_height   = current_size.height();
        // paddings
        const int x_left_right_padding     = image_width / 25;
        const int y_bottom_padding         = image_height / 18;
        const int y_framerate_plot_padding = image_height / 20;
        // dimensions
        const int plot_height = image_height / 5;
        const int plot_width  = image_width / 4 - x_left_right_padding;
        // framerate plot height to add
        const int framerate_plot_height = image_height / 5;
        // top left position
        const int x_pos = x_left_right_padding;
        const int y_pos = image_height
                          - plot_height
                          - framerate_plot_height
                          - y_bottom_padding
                          - y_framerate_plot_padding;
        // set the member
        _plot_outline = QRect(x_pos, y_pos, plot_width, plot_height);
        // draw the x and y axis of the rect
        painter->setPen(_get_outerline_pen());
        // x axis
        painter->drawLine(x_pos,              y_pos + plot_height
                        , x_pos + plot_width, y_pos + plot_height);
        // y axis
        painter->drawLine(x_pos,  y_pos
                        , x_pos , y_pos + plot_height);
    }
    //! drawing lines from top to bottom because Rect's x,y is top left
    void _draw_plot_inner_lines(QPainter * painter)
    {
        painter->setPen(_get_innerline_pen());
        // height
        const int segment_height   = _plot_outline.height() / _segment_count;
        const int y_start_pos_init = _plot_outline.y();
        // width
        const int x_start_pos_init = _plot_outline.x();
        const int x_end_pos_init   = _plot_outline.x() + _plot_outline.width();
        // draw a line for each segment
        for (int i = 0; i < _segment_count; ++i)
        {
            // x does not change
            const int x_start_pos = x_start_pos_init;
            const int x_end_pos   = x_end_pos_init;
            // calculate the y_pos (height)
            const int y_pos = y_start_pos_init + i * segment_height;
            painter->drawLine(x_start_pos, y_pos
                            , x_end_pos,   y_pos);
        }
    }
    //! drawing text from the top down -> e.g. 60 -> 45 -> 30 etc.
    //! aligning the text to the lines is done through the _get_font_spacing() method
    void _draw_text(QPainter * painter)
    {
        painter->setFont(_get_text_font());
        const int segment_height   = _plot_outline.height() / _segment_count;
        const int y_start_pos_init = _plot_outline.y();
        const int x_end_pos_init   = _plot_outline.x() + _plot_outline.width();
        // draw text for each line (always one more than the segments)
        for (int i = 0; i < _segment_count + 1; ++i)
        {
            // calculating y_pos (height)
            const int additional_height = static_cast<int>
                                         (    static_cast<double>((i + _get_font_spacing()))
                                            * static_cast<double>(segment_height)
                                         );
            const int y_pos = y_start_pos_init + additional_height;
            // calculating x_pos, TODO check this for different ratios
            const int x_pos = x_end_pos_init + _plot_outline.width() / 30;

            // get framerate as text (1 - ...) is because we draw from top to bottom
            const double percent = 1 - static_cast<double>(i) / static_cast<double>(_segment_count);
            const double max_framerate = _shared_frametime_model->get_max_frametime_bounds();
            const QString framerate_text = QString::number(static_cast<int>(percent * max_framerate));

            // draw shadow
            const int x_offset = 2;
            const int y_offset = 2;
            painter->setPen(_text_shadow);
            painter->drawText(x_pos + x_offset, y_pos + y_offset, framerate_text);
            // draw text
            painter->setPen(_plot_text_color);
            painter->drawText(x_pos, y_pos, framerate_text);
        }
    }
    //! draws the eyecandy text, which is similar to a title for the plot
    void _draw_eyecandy_text(QPainter * painter)
    {
        painter->setFont(_get_eyecandy_text_font());

        const int y_init_pos = _plot_outline.y();
        const int x_init_pos = _plot_outline.x() + _plot_outline.width();

        const int y_bottom_padding = _plot_outline.height() / 10;
        const int x_right_padding  = static_cast<int>(_plot_outline.width() / 1.45);

        const int x_pos = x_init_pos - x_right_padding;
        const int y_pos = y_init_pos - y_bottom_padding;

        // draw shadow
        const int x_offset = 2;
        const int y_offset = 2;
        painter->setPen(_text_shadow);
        painter->drawText(x_pos + x_offset, y_pos + y_offset, _eyecandy_text);
        // draw text
        painter->setPen(_plot_text_color);
        painter->drawText(x_pos, y_pos, _eyecandy_text);
    }
    //! TODO
    void _draw_frametimes(QPainter * painter)
    {
        for (int i = 0; i < (*_shared_fps_options_list).size(); ++i)
        {
            if ((*_shared_fps_options_list)[i].enabled)
            {
                _draw_frametime(painter, i);
            }
        }
    }
    //! TODO
    void _draw_frametime(QPainter * painter, const int video_count)
    {
        const std::deque<double> & ft_history = _shared_frametime_model->get_frametime_history(static_cast<size_t>(video_count));
        // set pen to the correct color and line width
        painter->setPen(_get_frametime_pen(video_count));
        // how many ticks do we want to display
        const uint8_t frametime_ticks = _shared_general_options_model->get_frametime_range();
        // will always be positive, history is fixed in frameratemodel and ticks are restrict
        const size_t size_difference = ft_history.size() - frametime_ticks;
        // need the maximums to calculate the position of the point
        const size_t max_index = ft_history.size() - size_difference;
        const double max_frametime = _shared_frametime_model->get_max_frametime_bounds();
        QPoint previous_point;
        size_t index = 0; // TODO implement enumerate
        // iterating in reverse, stitching every point with each other to draw lines instead of points
        std::for_each(ft_history.rbegin() + size_difference
                    , ft_history.rend()
                    , [&](const double frametime)
        {
            QPoint frametime_point = _to_plot_coords(frametime, max_frametime, index, max_index);
            if (index == 0)
            {
                painter->drawPoint(frametime_point);
                previous_point = frametime_point;
            } else {
                painter->drawLine(previous_point, frametime_point);
                previous_point = frametime_point;
            }
            index++;
        });
    }
    //! calculates the x,y position of the framerate based on its index and value
    QPoint _to_plot_coords(const double frametime
                         , const double max_frametime
                         , const size_t index
                         , const size_t max_size)
    {
        // caluclate x
        const int    plot_width   = _plot_outline.width();
        const double x_percentage = static_cast<double>(index) / static_cast<double>(max_size - 1);
        const int    x_pos_rel    = static_cast<int>(x_percentage * static_cast<double>(plot_width));
        const int    x_pos        = x_pos_rel + _plot_outline.x();
        // calculate y
        const int    plot_height  = _plot_outline.height();
        const double y_percentage = frametime / max_frametime;
        const double y_inverted   = 1 - y_percentage; // reversing because y = 0 in the top
        const int    y_pos_rel    = static_cast<int>(y_inverted * static_cast<double>(plot_height));
        const int    y_pos        = y_pos_rel + _plot_outline.y();

        return QPoint(x_pos, y_pos);
    }
    //! resolution adaptive outerline pen
    QPen _get_outerline_pen()
    {
        QPen pen;
        pen.setWidth(_get_outline_thickness());
        pen.setColor(_plot_outline_color);
        pen.setJoinStyle(Qt::MiterJoin); // hard counters
        return pen;
    }
    //! resolution adaptive innerline pen
    QPen _get_innerline_pen()
    {
        QPen pen;
        pen.setWidth(_get_innerline_thickness());
        pen.setColor(_plot_innerline_color);
        return pen;
    }
    //! resolution adaptive pen with the color corresponding the the video index
    QPen _get_frametime_pen(const int video_index)
    {
        const QColor plot_color = (*_shared_fps_options_list)[video_index].fps_plot_color.color();
        QPen pen;
        pen.setStyle(Qt::SolidLine);
        pen.setWidth(_get_plotline_thickness());
        pen.setBrush(plot_color);
        pen.setCapStyle(Qt::FlatCap);
        pen.setJoinStyle(Qt::RoundJoin);
        return pen;
    }
    //! resolution adaptive font
    QFont _get_text_font()
    {
        return QFont("Fjalla One", _get_font_size());
    }
    //! resolution adaptive font
    QFont _get_eyecandy_text_font()
    {
        return QFont("Fjalla One", _get_eyecandy_font_size());
    }
    //! resolution adaptive font size
    int _get_font_size()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 13;
        else if (current_size == QSize(1280, 720))  return 18;
        else if (current_size == QSize(1600, 900))  return 22;
        else if (current_size == QSize(1920, 1080)) return 27;
        else if (current_size == QSize(2048, 1152)) return 30;
        else if (current_size == QSize(2560, 1440)) return 37;
        else if (current_size == QSize(3840, 2160)) return 51;
        qDebug() << "FrametimePlot::_get_font_size() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 13;
    }
    //! TODO
    int _get_eyecandy_font_size()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 13 + 3;
        else if (current_size == QSize(1280, 720))  return 18 + 3;
        else if (current_size == QSize(1600, 900))  return 22 + 3;
        else if (current_size == QSize(1920, 1080)) return 27 + 3;
        else if (current_size == QSize(2048, 1152)) return 30 + 3;
        else if (current_size == QSize(2560, 1440)) return 37 + 3;
        else if (current_size == QSize(3840, 2160)) return 51 + 12;
        qDebug() << "FrametimePlot::_get_eyecandy_font_size() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 13;
    }
    //! currently supporting only 16:9
    double _get_font_spacing()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 0.3;
        else if (current_size == QSize(1280, 720))  return 0.3;
        else if (current_size == QSize(1600, 900))  return 0.3;
        else if (current_size == QSize(1920, 1080)) return 0.3;
        else if (current_size == QSize(2048, 1152)) return 0.3;
        else if (current_size == QSize(2560, 1440)) return 0.3;
        else if (current_size == QSize(3840, 2160)) return 0.3;
        qDebug() << "FrametimePlot::_get_font_spacing() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 0.3;
    }
    //! TODO
    int _get_outline_thickness()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 3;
        else if (current_size == QSize(1280, 720))  return 3;
        else if (current_size == QSize(1600, 900))  return 4;
        else if (current_size == QSize(1920, 1080)) return 4;
        else if (current_size == QSize(2048, 1152)) return 5;
        else if (current_size == QSize(2560, 1440)) return 5;
        else if (current_size == QSize(3840, 2160)) return 7;
        qDebug() << "FrametimePlot::_get_outline_thickness() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 3;
    }
    //! TODO
    int _get_innerline_thickness()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 1;
        else if (current_size == QSize(1280, 720))  return 1;
        else if (current_size == QSize(1600, 900))  return 2;
        else if (current_size == QSize(1920, 1080)) return 2;
        else if (current_size == QSize(2048, 1152)) return 3;
        else if (current_size == QSize(2560, 1440)) return 3;
        else if (current_size == QSize(3840, 2160)) return 5;
        qDebug() << "FrametimePlot::_get_innerline_thickness() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 2;
    }
    //! TODO
    int _get_plotline_thickness()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 3;
        else if (current_size == QSize(1280, 720))  return 3;
        else if (current_size == QSize(1600, 900))  return 4;
        else if (current_size == QSize(1920, 1080)) return 4;
        else if (current_size == QSize(2048, 1152)) return 5;
        else if (current_size == QSize(2560, 1440)) return 5;
        else if (current_size == QSize(3840, 2160)) return 7;
        qDebug() << "FrametimePlot::_get_plotline_thickness() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 3;
    }

// member
private:
    //! shared model from main.cpp
    std::shared_ptr<FrametimeModel> _shared_frametime_model;
    //! shared model from main.cpp
    std::shared_ptr<QList<FramerateOptions>> _shared_fps_options_list;
    //! shared model from main.cpp
    std::shared_ptr<ResolutionsModel> _shared_resolution_model;
    //! shared model from main.cpp
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
    //! color of the outer lines of the plot
    QColor _plot_outline_color;
    //! color of the inner lines of the plot
    QColor _plot_innerline_color;
    //! color of the text next to the plot
    QColor _plot_text_color;
    //! text shadow color for the framerates next to the plot
    QColor _text_shadow;
    //! drawable rect if one needs to draw the framerates
    QRect _plot_outline;
    //! plot is split in this many segments
    const int _segment_count;
    //! similar to a title for the plot
    QString _eyecandy_text;
};


#endif // FRAMETIMEPLOT_H
