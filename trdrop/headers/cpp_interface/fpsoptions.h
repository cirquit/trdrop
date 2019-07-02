#ifndef FPSOptions_H
#define FPSOptions_H

#include <QPainter>
#include <memory>

#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/colorpickitem.h"
#include "headers/cpp_interface/valueitem.h"
#include "headers/cpp_interface/textedititem.h"
#include "headers/cpp_interface/frameratemodel.h"

class FPSOptions
{
// constructors
public:
    //! TODO
    FPSOptions(const quint8 video_id
             , std::shared_ptr<FramerateModel> shared_framerate_model)
        : video_id(video_id)
        , _shared_framerate_model(shared_framerate_model)
    {
        _init_member();
    }

// methods
public:
    //! TODO
    void revert_to_default()
    {
        _init_member();
    }
    //! TODO
    void paint_fps_text(QPainter * painter, int x, int y)
    {
        painter->setPen(fps_plot_color.color());
        painter->setFont(displayed_text.font());
        painter->drawText(x, y, _get_full_text());
    }

// methods
private:
    //! TODO
    void _init_member()
    {
        fps_plot_color.setName("Framerate plot color");
        fps_plot_color.setTooltip("Color of the framerate graph of this video index in the framerate plot");
        fps_plot_color.setColor("#FAFAFA");

        pixel_difference.setName("Pixel difference");
        pixel_difference.setTooltip("Pixel Difference Margin\n \
    example: 0  - RGB values have to be identical to not detect a new frame\n \
    example: 5  - maximum summarized difference between each RGB channel can be 5");
        pixel_difference.setValue(0);
        pixel_difference.setEnabled(true);

        displayed_text.setName("Framerate text:");
        displayed_text.setTooltip("The text which will be shown in the left corner of each video with the framerate");
        displayed_text.setValue("FPS:");
        displayed_text.setEnabled(true);
        displayed_text.setFont(QFont("Helvetica", 15));

        enabled = false;
    }
    //! TODO
    QString _get_full_text() const
    {
        double framerate = _shared_framerate_model->get_framerate_at(video_id);
        return displayed_text.value() + " " + QString::number(framerate);
    }

// member
public:
    //! TODO
    quint8       video_id;
    //! TODO
    ColorPickItem fps_plot_color;
    //! TODO
    ValueItem<quint32> pixel_difference;
    //! TODO
    TextEditItem displayed_text;
    //! TODO
    bool enabled;
    //! TODO
    std::shared_ptr<FramerateModel> _shared_framerate_model;

};

#endif // FPSOptions_H
