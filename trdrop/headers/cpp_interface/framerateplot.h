#ifndef FRAMERATEPLOT_H
#define FRAMERATEPLOT_H

#include <QPainter>
#include <memory>
#include <cmath>
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/framerateoptions.h"
#include "headers/qml_models/resolutionsmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! "Painter" class for the framerate plot
class FrameratePlot
{
// constructors
public:
    //! constructor with the shared options and models
    FrameratePlot(std::shared_ptr<FramerateModel> shared_framerate_model
       , std::shared_ptr<QList<FramerateOptions>> shared_fps_options_list
       , std::shared_ptr<ResolutionsModel> shared_resolution_model
       , std::shared_ptr<GeneralOptionsModel> shared_general_options_model)
        : _shared_framerate_model(shared_framerate_model)
        , _shared_framerate_options_list(shared_fps_options_list)
        , _shared_resolution_model(shared_resolution_model)
        , _shared_general_options_model(shared_general_options_model)
        , _plot_outline_color(236, 236, 236)   // almost white
        , _plot_innerline_color(255, 255, 255, 100) // pure white + 40% opactiy
        , _plot_text_color(255, 255, 255) // white
        , _text_shadow(41, 41, 41) // dark grey
        , _segment_count(4) // we want to split the plot into 4 bars
        , _eyecandy_text("Framerate (fps)")
        , _x_axis_prefix_text("ANALYSIS RANGE: ")
    { }

// methods
public:
    //! top left is (0,0), painter has to be pointed to the image by the renderer
    //! order of drawing functions is essential
    void draw_framerate_plot(QPainter * painter, bool enable_framerate_centering, bool enable_triangle_centering, bool enable_bg_shadow, bool enable_x_axis_text)
    {
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setRenderHint(QPainter::HighQualityAntialiasing);

        _set_plot_bounds();
        if (enable_bg_shadow)
        {
            _draw_bg_shadow(painter);
        }
        _draw_plot_outline(painter);
        _draw_plot_inner_lines(painter);
        if (enable_framerate_centering)
        {
            _draw_center_line(painter);
        }
        if (enable_triangle_centering)
        {
            _draw_center_triangle(painter);
        }
        _draw_framerates(painter);
        _draw_text(painter);
        _draw_eyecandy_text(painter);
        if (enable_x_axis_text)
        {
            _draw_x_axis_text(painter);
        }
    }

// methods
private:
    //! fills the member `_plot_outline` which is the reference for all future function calls
    void _set_plot_bounds()
    {
        // make it dependent on the current resolution
        const QSize current_size = _shared_resolution_model->get_active_size();
        const int image_width    = current_size.width();
        const int image_height   = current_size.height();
        // paddings
        const int x_left_right_padding  = image_width / 25;
        const int y_bottom_padding      = image_height / 18;
        // dimensions
        const int plot_height = image_height / 5;
        const int plot_width = image_width - (2 * x_left_right_padding);
        // top left position
        const int x_pos = x_left_right_padding;
        const int y_pos = image_height - plot_height - y_bottom_padding;
        // set the member
        _plot_outline = QRect(x_pos, y_pos, plot_width, plot_height);
    }
    void _draw_bg_shadow(QPainter * painter)
    {
        painter->setBrush(QColor(0, 0, 0, 180)); // todo: make this adjustable
        painter->setPen(QColor(0, 0, 0, 0));     // transparent for rectangle to draw
        painter->drawRect(_plot_outline);
    }
    //! draws a rectangle based on the resolution
    //! NO constants INDEPEDENT of the resolution may be used
    void _draw_plot_outline(QPainter * painter)
    {
        const int x_pos = _plot_outline.x();
        const int y_pos = _plot_outline.y();
        const int plot_height = _plot_outline.height();
        const int plot_width = _plot_outline.width();

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
            const int x_pos = x_end_pos_init + _plot_outline.width() / 100;

            // get framerate as text (1 - ...) is because we draw from top to bottom
            const double percent = 1 - static_cast<double>(i) / static_cast<double>(_segment_count);
            const double max_framerate = _get_max_framerate();
            const QString framerate_text = QString::number(static_cast<int>(percent * max_framerate));

            // draw shadow
            const int x_offset = _get_shadow_text_offset();
            const int y_offset = x_offset;
            painter->setPen(_text_shadow);
            painter->drawText(x_pos + x_offset, y_pos + y_offset, framerate_text);
            // draw text
            painter->setPen(_plot_text_color);
            painter->drawText(x_pos, y_pos, framerate_text);
        }
    }
    //! draws the text above the plot
    void _draw_eyecandy_text(QPainter * painter)
    {
        painter->setFont(_get_eyecandy_text_font());

        const int y_init_pos = _plot_outline.y();
        const int x_init_pos = _plot_outline.x() + _plot_outline.width();

        const int y_bottom_padding = _plot_outline.height() / 10;
        const int x_right_padding  = _plot_outline.width() / 10;

        const int x_pos = x_init_pos - x_right_padding;
        const int y_pos = y_init_pos - y_bottom_padding;

        // draw shadow
        const int x_offset = _get_shadow_text_offset();
        const int y_offset = x_offset;
        painter->setPen(_text_shadow);
        painter->drawText(x_pos + x_offset, y_pos + y_offset, _eyecandy_text);
        // draw text
        painter->setPen(_plot_text_color);
        painter->drawText(x_pos, y_pos, _eyecandy_text);
    }
    //! draws the text below the plot
    void _draw_x_axis_text(QPainter * painter)
    {
        painter->setFont(_get_eyecandy_text_font());

        const int framerate_analysis_range = (*_shared_general_options_model).get_framerate_range();
        const QString framerate_analysis_range_text = _x_axis_prefix_text + QString::number(framerate_analysis_range) + " frames";

        const int y_init_pos = _plot_outline.y() + _plot_outline.height();
        const int x_init_pos = _plot_outline.x() + _plot_outline.width() / 2;

        const int y_bottom_padding = _plot_outline.height() / 4.4;
        const int x_right_padding  = _plot_outline.width() / 7.8;

        const int x_pos = x_init_pos - x_right_padding;
        const int y_pos = y_init_pos + y_bottom_padding;

        // draw shadow
        const int x_offset = _get_shadow_text_offset();
        const int y_offset = x_offset;
        painter->setPen(_text_shadow);
        painter->drawText(x_pos + x_offset, y_pos + y_offset, framerate_analysis_range_text);
        // draw text
        painter->setPen(_plot_text_color);
        painter->drawText(x_pos, y_pos, framerate_analysis_range_text);
    }
    //! draws a vertical center line
    void _draw_center_line(QPainter * painter)
    {
        const int y_init_pos = _plot_outline.y();
        const int x_init_pos = _plot_outline.x() + _plot_outline.width() / 2;

        const int y_bottom_padding = _plot_outline.height() / 80;

        const int x_pos = x_init_pos;
        const int y_pos = y_init_pos + y_bottom_padding;
        // define vertical line
        QPoint top_line_point(x_pos, y_pos);
        QPoint bottom_line_point(x_pos, y_pos + _plot_outline.height() * 0.98);
        // draw white line
        painter->setPen(_get_centerline_pen());
        painter->drawLine(top_line_point, bottom_line_point);
    }
    //! draws all framerates graphs options are enabled
    void _draw_framerates(QPainter * painter)
    {
        for (int i = 0; i < (*_shared_framerate_options_list).size(); ++i)
        {
            if ((*_shared_framerate_options_list)[i].enabled)
            {
                _draw_framerate(painter, i);
            }
        }
    }
    //! draws the graph into the plot by connecting the samples with lines (from right to left)
    void _draw_framerate(QPainter * painter, const int video_count)
    {
        const std::deque<double> & framerate_history = _shared_framerate_model->get_framerate_history(static_cast<size_t>(video_count));
        // set pen to the correct color and line width
        painter->setPen(_get_framerate_pen(video_count));
        // how many ticks do we want to display
        const int framerate_ticks = _shared_general_options_model->get_framerate_range();
        // will always be positive, history is fixed in frameratemodel and ticks are restricted by GUI
        const size_t size_difference = framerate_history.size() - framerate_ticks;
        // need the maximums to calculate the position of the point
        const size_t max_index = framerate_history.size() - size_difference;
        const double max_framerate = _get_max_framerate();
        QPoint previous_point;
        size_t index = 0; // TODO implement enumerate
        // iterating in reverse, stitching every point with each other to draw lines instead of points
        std::for_each(framerate_history.rbegin() + size_difference
                    , framerate_history.rend()
                    , [&](const double framerate)
        {
            QPoint framerate_point = _to_plot_coords(framerate, max_framerate, index, max_index);
            if (index == 0)
            {
                painter->drawPoint(framerate_point);
                previous_point = framerate_point;
            } else {
                painter->drawLine(previous_point, framerate_point);
                previous_point = framerate_point;
            }
            index++;
        });
    }
    //! calculates the x,y position of the framerate based on its index and value
    QPoint _to_plot_coords(const double framerate
                         , const double max_framerate
                         , const size_t index
                         , const size_t max_size)
    {
        // calculate x
        const int    plot_width   = _plot_outline.width();
        const double x_percentage = static_cast<double>(index) / static_cast<double>(max_size - 1);
        const int    x_pos_rel    = static_cast<int>(x_percentage * static_cast<double>(plot_width));
        const int    x_pos        = x_pos_rel + _plot_outline.x();
        // calculate y
        const int    plot_height  = _plot_outline.height();
        const double y_percentage = framerate / max_framerate;
        const double y_inverted   = 1 - y_percentage; // reversing because y = 0 in the top
        const int    y_pos_rel    = static_cast<int>(y_inverted * static_cast<double>(plot_height));
        const int    y_pos        = y_pos_rel + _plot_outline.y();

        return QPoint(x_pos, y_pos);
    }
    //! draws the pointing arrow in the center
    void _draw_center_triangle(QPainter * painter)
    {
        const int y_init_pos = _plot_outline.y();
        const int x_init_pos = _plot_outline.x() + _plot_outline.width() / 2;

        const int y_bottom_padding = _plot_outline.height() / 25 + 2; // hard coded 2 pixel difference so it looks nice on the 960x resolution, doesnt matter on 4k

        const int x_pos = x_init_pos;
        const int y_pos = y_init_pos - y_bottom_padding;

        // drawing a unilateral triangle, pointing downwards. The bottom point is the x/y-pos
        const int triangle_side_length = _plot_outline.width() / 60;
        const int c = triangle_side_length;
        const int b = triangle_side_length;
        // a^2 + b^2 = c^2 => a = sqrt(c^2 - b^2)
        // taking half of b cause we need the height at the center of b
        const int triangle_height = std::sqrt(std::pow(c, 2) - std::pow(b / 2, 2));
        const int top_left_x = x_pos - triangle_side_length / 2;
        const int top_left_y = y_pos - triangle_height;
        const int top_right_x = x_pos + triangle_side_length / 2;
        const int top_right_y = y_pos - triangle_height;

        // construct the triangle as polygon
        QPolygon triangle;
        QPoint top_left(top_left_x, top_left_y);
        QPoint bottom(x_pos, y_pos);
        QPoint top_right(top_right_x, top_right_y);
        triangle << top_left << bottom << top_right;

        // draw filled polygon
        QBrush brush(_plot_outline_color);
        brush.setStyle(Qt::SolidPattern);
        painter->setPen(_get_outerline_pen());
        painter->setBrush(brush);
        painter->drawPolygon(triangle);
    }
// methods
private:
    //! resolution adaptive outerline pen
    QPen _get_outerline_pen()
    {
        QPen pen;
        pen.setWidth(_get_outline_thickness());
        pen.setColor(_plot_outline_color);
        pen.setJoinStyle(Qt::MiterJoin); // hard corners
        return pen;
    }
    //! resolution adaptive outerline pen
    QPen _get_centerline_pen()
    {
        QPen pen;
        pen.setWidth(_get_outline_thickness());
        QColor color = _plot_outline_color;
        pen.setColor(color);
        pen.setJoinStyle(Qt::MiterJoin); // hard corners
        return pen;
    }
    //! resolution adaptive outerline pen
    QPen _get_centerline_shadow_pen()
    {
        QPen pen;
        pen.setWidth(_get_outline_thickness());
        QColor color = _text_shadow;
        pen.setColor(color);
        pen.setJoinStyle(Qt::MiterJoin); // hard corners
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
    QPen _get_framerate_pen(const int video_index)
    {
        const QColor plot_color = (*_shared_framerate_options_list)[video_index].fps_plot_color.color();
        QPen pen;
        pen.setStyle(Qt::SolidLine);
        pen.setWidth(_get_plotline_thickness());
        pen.setBrush(plot_color);
        pen.setCapStyle(Qt::RoundCap);
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
        if      (current_size == QSize(960, 540))   return 8;
        else if (current_size == QSize(1280, 720))  return 12;
        else if (current_size == QSize(1600, 900))  return 15;
        else if (current_size == QSize(1920, 1080)) return 20;
        else if (current_size == QSize(2048, 1152)) return 22;
        else if (current_size == QSize(2560, 1440)) return 29;
        else if (current_size == QSize(3840, 2160)) return 35;
        qDebug() << "FrameratePlot::_get_font_size() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 13;
    }
    //! resolution adaptive font size
    int _get_eyecandy_font_size()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 8 + 3;
        else if (current_size == QSize(1280, 720))  return 12 + 3;
        else if (current_size == QSize(1600, 900))  return 15 + 3;
        else if (current_size == QSize(1920, 1080)) return 20 + 3;
        else if (current_size == QSize(2048, 1152)) return 22 + 3;
        else if (current_size == QSize(2560, 1440)) return 29 + 3;
        else if (current_size == QSize(3840, 2160)) return 35 + 12;
        qDebug() << "FrameratePlot::_get_eyecandy_font_size() - there is no case for the current resolution(" << current_size << "), this should never happen";
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
        qDebug() << "FrameratePlot::_get_font_spacing() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 0.3;
    }
    //! resolution adaptive line size
    int _get_outline_thickness()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 3;
        else if (current_size == QSize(1280, 720))  return 3;
        else if (current_size == QSize(1600, 900))  return 5;
        else if (current_size == QSize(1920, 1080)) return 5;
        else if (current_size == QSize(2048, 1152)) return 7;
        else if (current_size == QSize(2560, 1440)) return 7;
        else if (current_size == QSize(3840, 2160)) return 10;
        qDebug() << "Plot::_get_outline_thickness() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 3;
    }
    //! resolution adaptive line size
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
        qDebug() << "FrameratePlot::_get_innerline_thickness() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 2;
    }
    //! resolution adaptive line size
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
        qDebug() << "Plot::_get_plotline_thickness() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 3;
    }
    //! the manually set max framerate is the default as long as we dont overstep the real framerate bounds, then we scale as usual
    double _get_max_framerate() const
    {
        const double manual_set_max_framerate = _shared_general_options_model->get_framerate_max_fps();
        const double real_max_framerate = _shared_framerate_model->get_max_framerate_bounds();
        if (manual_set_max_framerate < real_max_framerate)
        return manual_set_max_framerate;
    }
    //! get text offset for shadows below the text
    int _get_shadow_text_offset()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return 2;
        else if (current_size == QSize(1280, 720))  return 3;
        else if (current_size == QSize(1600, 900))  return 4;
        else if (current_size == QSize(1920, 1080)) return 4;
        else if (current_size == QSize(2048, 1152)) return 5;
        else if (current_size == QSize(2560, 1440)) return 5;
        else if (current_size == QSize(3840, 2160)) return 7;
        qDebug() << "FrameratePlot::_get_shadow_text_offset() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 3;
    }

// member
private:
    //! all the framerates are stored here
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! used to check if the current framerate rendering is enabled
    std::shared_ptr<QList<FramerateOptions>> _shared_framerate_options_list;
    //! holds the current resolution
    std::shared_ptr<ResolutionsModel> _shared_resolution_model;
    //! used to get the framerate plot range
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
    //! text that is positioned below the x axis
    QString _x_axis_prefix_text;
};

#endif // FRAMERATEPLOT_H
