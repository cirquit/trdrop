#ifndef TEAROPTIONS_H
#define TEAROPTIONS_H

#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/colorpickitem.h"
#include "headers/cpp_interface/valueitem.h"
#include "headers/cpp_interface/textedititem.h"

//! TODO
class TearOptions
{
// constructors
public:
    //! TODO
    TearOptions(quint8 & video_id)
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
        tear_plot_color.setName("Tear plot color:");
        tear_plot_color.setTooltip("Color of the tears in the framerate plot");
        tear_plot_color.setColor("#FAFAFA");

        dismiss_tear_percentage.setName("Dismissed tear percentage:");
        dismiss_tear_percentage.setTooltip("Tears that are smaller than this amount of the image are dismissed");
        dismiss_tear_percentage.setValue(10.0);

        enabled = false;
    }

// member
public:
    //! TODO
    quint8       video_id;
    //! TODO
    ColorPickItem tear_plot_color;
    //! TODO
    ValueItem<double> dismiss_tear_percentage;
    //! TODO
    bool enabled;
//    //! TODO
//    TextEditItem displayed_text;
};

#endif // TEAROPTIONS_H
