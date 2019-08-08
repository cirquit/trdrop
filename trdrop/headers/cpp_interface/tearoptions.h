#ifndef TEAROPTIONS_H
#define TEAROPTIONS_H

#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/colorpickitem.h"
#include "headers/cpp_interface/valueitem.h"
#include "headers/cpp_interface/textedititem.h"

//! holds the tear options for a video
class TearOptions
{
// constructors
public:
    //! default constructor
    TearOptions(const quint8 video_id)
        : video_id(video_id)
    {
        _init_member();
    }

// methods
public:
    //! initializes the values to default
    void revert_to_default()
    {
        _init_member();
    }

// methods
private:
    //! default initialization
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
    //! current video id
    quint8       video_id;
    //! tears may have a different color
    ColorPickItem tear_plot_color;
    //! used in the calculation of tears
    ValueItem<double> dismiss_tear_percentage;
    //! option may be disabled
    bool enabled;
};

#endif // TEAROPTIONS_H
