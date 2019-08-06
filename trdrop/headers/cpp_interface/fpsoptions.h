#ifndef FPSOPTIONS_H
#define FPSOPTIONS_H

#include <QPainter>
#include <memory>

#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/colorpickitem.h"
#include "headers/cpp_interface/valueitem.h"
#include "headers/cpp_interface/textedititem.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/qml_models/resolutionsmodel.h"

//! holds all the framerate options of a single video
//! is reponsible for the paint_ method of the framerate text
class FPSOptions
{
// constructors
public:
    //! takes the responsible video_id and several models as we need to access them to be able to paint the framerate text
    FPSOptions(const quint8 video_id
             , std::shared_ptr<FramerateModel> shared_framerate_model
             , std::shared_ptr<ResolutionsModel> shared_resolution_model)
        : video_id(video_id)
        , enabled(false) // initialized by default to false, because revert_to_default button in options should not reset this
        , _shared_framerate_model(shared_framerate_model)
        , _shared_resolution_model(shared_resolution_model)
        , _text_shadow(41, 41, 41) // dark grey
    {
        _init_member();
    }

// methods
public:
    //! resets the saved options to our default configuration
    void revert_to_default()
    {
        _init_member();
    }
    //! paints the framerate text at the position x, y (top-left is 0,0)
    void paint_fps_text(QPainter * painter, int x, int y)
    {
        int x_offset = 2;
        int y_offset = 2;
        // draw shadow
        painter->setPen(_text_shadow);
        painter->setFont(displayed_text.font());
        painter->drawText(x + x_offset, y + y_offset, _get_full_text());
        // draw real text
        painter->setPen(fps_plot_color.color());
        painter->setFont(displayed_text.font());
        painter->drawText(x, y, _get_full_text());
    }

// methods
private:
    //! default initialization of the options
    void _init_member()
    {
        fps_plot_color.setName("Framerate plot color");
        fps_plot_color.setTooltip("Color of the framerate graph of this video index in the framerate plot");
        fps_plot_color.setColor("#FAFAFA");

        pixel_difference.setName("Pixel difference");
        pixel_difference.setTooltip("Pixel Difference Margin (0 - 255)\n \
    Currently every frame is converted to greyscale and compared on a pixel basis. Greater is more \"forgiving\"\n\
    Example: \"5\" - The difference in color may be up to 5 to NOT trigger a new frame");
        pixel_difference.setValue(0);
        pixel_difference.setEnabled(true);

        displayed_text.setName("Framerate text:");
        displayed_text.setTooltip("The text which will be shown in the left corner of each video with the framerate");
        displayed_text.setValue("FPS:");
        displayed_text.setEnabled(true);
        displayed_text.setFont(QFont("Fjalla One", 18));
    }
    //! adds the framerate prefix text defined in the options to the current framerate of the designated video
    QString _get_full_text() const
    {
        double framerate = _shared_framerate_model->get_framerate_at(video_id);
        return displayed_text.value() + " " + QString::number(framerate, 10, 1);
    }

// member
public:
    //! hold the id (starting from 0) of the responsible video
    quint8       video_id;
    //! framerate color, used for text and plot color
    ColorPickItem fps_plot_color;
    //! how big can the difference in the RGB space get between two pixels for us to detect a difference
    ValueItem<quint32> pixel_difference;
    //! prefix text of the framerate
    TextEditItem displayed_text;
    //! is this option enabled
    bool enabled;
    //! framerate model (to get the current framerate)
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! the current resolution might be needed to adapt the fontsize automatically (currently not used)
    std::shared_ptr<ResolutionsModel> _shared_resolution_model;
    //! to create a shadow effect we draw the text with an offset first
    QColor _text_shadow;
};

#endif // FPSOPTIONS_H
