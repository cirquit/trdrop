#ifndef TEAR_DATA_H
#define TEAR_DATA_H

#include <vector>
#include <tuple>
#include <QPainter>
#include <QDebug>

class TearData
{
// constructors
public:

    //! holds the indices which defined a tear and the according video_index
    TearData(size_t index_A, size_t index_B, size_t video_index, size_t video_count, int original_video_heigth)
        : _index_A(index_A)
        , _index_B(index_B)
        , _video_index(video_index)
        , _video_count(video_count)
        , _original_video_height(original_video_heigth)
        , _tear_visibility_count(25) // TODO refactor this
        , _rendered_count(0)
    { }
// methods
public:
    //! draws the tear as a line, adaptive to multiple videos
    void draw(QPainter * painter, const QSize resolution, const QColor tear_color)
    {
        // resized video resolution
        const int height = resolution.height();
        const int width  = resolution.width();
        // calculate the tear position and apply to the current video resolution
        const double height_percentage = static_cast<double>(_index_A) / static_cast<double>(_original_video_height);
        const int y_pos = static_cast<int>(height * height_percentage);
        // calculate the start and end of the line
        const double individual_video_width = static_cast<double>(width) / static_cast<double>(_video_count);
        const int x_pos     = static_cast<int>(individual_video_width * _video_index);
        const int x_end_pos = static_cast<int>(x_pos + individual_video_width);
        // set the pen (color + opacity + width)
        painter->setPen(_get_pen(tear_color, resolution));
        // draw line
        painter->drawLine(x_pos, y_pos, x_end_pos, y_pos);
        // increment the amount of rendered times to adapt the pen for the future
        _rendered_count += 1;
    }
    //! getter
    size_t get_video_index() const { return _video_index; }
    //! getter (first index is always smaller than the second one)
    std::tuple<size_t, size_t> get_indices() const { return std::make_tuple(_index_A, _index_B); }
    //! if _rendered_count is greater than _tear_visibility_count, we should stop rendering
    bool done_rendering() const { return _get_rendering_percentage() > 1.0; }
// methods
private:
    //! returns the pen with the accoring opacity and size dependent on the _rendered_count
    QPen _get_pen(QColor color, const QSize resolution) const
    {
        color.setRgb(color.red(), color.green(), color.blue(), _get_opacity());
        QPen pen;
        pen.setBrush(color);
        pen.setStyle(Qt::SolidLine);
        pen.setWidth(_get_pen_width(resolution));
        pen.setCapStyle(Qt::FlatCap);
        return pen;
    }
    //! returns 0 to 225 (starting at 255 and going to 0 by increased _rendered_count)
    int _get_opacity() const
    {
        const double rendering_percentage = _get_rendering_percentage();
        const double inverted_percentage = 1- rendering_percentage;
        return static_cast<int>(inverted_percentage * 255.0);
    }
    //! returns 1 - 9 (starting at 1 and going to 9 by increased _rendered_count)
    int _get_pen_width(const QSize resolution) const
    {
        int max_size = 0;
        if      (resolution == QSize(960, 540))   max_size = 6 + 1;
        else if (resolution == QSize(1280, 720))  max_size = 6 + 1;
        else if (resolution == QSize(1600, 900))  max_size = 6 + 2;
        else if (resolution == QSize(1920, 1080)) max_size = 6 + 3;
        else if (resolution == QSize(2048, 1152)) max_size = 6 + 3;
        else if (resolution == QSize(2560, 1440)) max_size = 6 + 4;
        else if (resolution == QSize(3840, 2160)) max_size = 6 + 6;
        else qDebug() << "TearData::_get_pen_width() - there is no case for the current resolution(" << resolution << "), this should never happen";
        const double rendering_percentage = _get_rendering_percentage();
        return 1 + static_cast<int>(rendering_percentage * max_size);
    }
    //! how many frames are already rendered, normalize from 0 to 1
    double _get_rendering_percentage() const { return static_cast<double>(_rendered_count) / static_cast<double>(_tear_visibility_count); }
// member
private:
    //! TODO
    size_t _index_A;
    //! TODO
    size_t _index_B;
    //! TODO
    size_t _video_index;
    //! TODO
    size_t _video_count;
    //! TODO
    int    _original_video_height;
    //! show the tear for these amount of frames
    size_t _tear_visibility_count;
    //! TODO
    size_t _rendered_count;
};


#endif // TEAR_DATA_H
