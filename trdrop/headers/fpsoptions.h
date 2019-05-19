#ifndef FPSOptions_H
#define FPSOptions_H

#include "headers/checkboxitem.h"
#include "headers/colorpickitem.h"
#include "headers/valueitem.h"
#include "headers/textedititem.h"

class FPSOptions
{
// constructors
public:
    //! TODO
    FPSOptions(quint8 & video_id)
        : video_id(video_id)
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

// methods
private:
    //! TODO
    void _init_member()
    {
        fps_plot_color.setName("Framerate plot color");
        fps_plot_color.setTooltip("Color of the framerate plot");
        fps_plot_color.setColor("#FAFAFA");

        pixel_difference.setName("Pixel difference");
        pixel_difference.setTooltip("Pixel Difference Margin\n \
    example: 0  - RGB values have to be identical to not detect a new frame\n \
    example: 5  - maximum summarized difference between each RGB channel can be 5");
        pixel_difference.setValue(0);
        pixel_difference.setEnabled(true);

        displayed_text.setName("Framerate text");
        displayed_text.setTooltip("The text which will be shown in the left corner of each video with the framerate");
        displayed_text.setValue("FPS:");
        displayed_text.setEnabled(true);
        displayed_text.setFont(QFont("Helvetica", 15));
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
};

#endif // FPSOptions_H
