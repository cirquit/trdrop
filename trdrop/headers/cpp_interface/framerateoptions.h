#ifndef FRAMERATEOPTIONS_H
#define FRAMERATEOPTIONS_H

#include <QPainter>
#include <memory>
#include <random>
#include <iostream>
#include <cstdlib>

#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/colorpickitem.h"
#include "headers/cpp_interface/valueitem.h"
#include "headers/cpp_interface/textedititem.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/qml_models/resolutionsmodel.h"

//! holds all the framerate options of a single video
//! is reponsible for the paint_ method of the framerate text
class FramerateOptions
{
// constructors
public:
    //! takes the responsible video_id and several models as we need to access them to be able to paint the framerate text
    FramerateOptions(const quint8 video_id
                   , std::shared_ptr<FramerateModel> shared_framerate_model
                   , std::shared_ptr<ResolutionsModel> shared_resolution_model)
        : video_id(video_id)
        , enabled(false) // initialized by default to false, because revert_to_default button in options should not reset this
        , _shared_framerate_model(shared_framerate_model)
        , _shared_resolution_model(shared_resolution_model)
        , text_shadow(41, 41, 41) // dark grey
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
    void paint_fps_text(QPainter * painter, const int x, const int y, const size_t frame_index)
    {
        const int x_offset = _get_shadow_text_offset();
        const int y_offset = x_offset;

        QFont displayed_text_font = displayed_text.font();
        if (displayed_text_fontsize_override)
        {
            displayed_text_font.setPointSize(_get_font_size());
        }
        // draw shadow
        painter->setPen(text_shadow);
        painter->setFont(displayed_text_font);
        painter->drawText(x + x_offset, y + y_offset, _get_full_text(frame_index));
        // draw real text
        painter->setPen(fps_plot_color.color());
        painter->setFont(displayed_text_font);
        painter->drawText(x, y, _get_full_text(frame_index));
    }

// methods
private:
    //! default initialization of the options
    void _init_member()
    {
        fps_plot_color.setName("Framerate plot color");
        fps_plot_color.setTooltip("Color of the framerate and frametime graph of this video index");
        fps_plot_color.setColor(_get_random_color());

        pixel_difference.setName("Pixel difference");
        pixel_difference.setTooltip("Pixel Difference Margin (0 - 255)\n\
    Currently every frame is converted to greyscale and compared on a pixel basis. Greater is more \"forgiving\"\n\
    Example: \"5\" - The difference in color may be up to 5 to NOT trigger a new frame");
        pixel_difference.setValue(0);
        pixel_difference.setEnabled(true);

        displayed_text.setName("Framerate text:");
        displayed_text.setTooltip("The text which will be shown in the left corner of each video with the framerate");
        displayed_text.setValue("FPS:");
        displayed_text.setEnabled(true);
        displayed_text.setFont(QFont("Fjalla One", 18));

        displayed_text_fontsize_override = true;

        rel_fps_text_x_position.setName("Relative FPS Text X Pos.");
        rel_fps_text_x_position.setTooltip("");
        rel_fps_text_x_position.setValue(0.05);

        rel_fps_text_y_position.setName("Relative FPS Text Y Pos.");
        rel_fps_text_y_position.setTooltip("");
        rel_fps_text_y_position.setValue(0.1);
    }
    //! adds the framerate prefix text defined in the options to the framerate of the designated video
    QString _get_full_text(const size_t frame_index) const
    {
        double framerate = _shared_framerate_model->get_framerate_history(video_id)[frame_index];
        return displayed_text.value() + " " + QString::number(framerate, 10, 1);
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
        else if (current_size == QSize(3840, 2160)) return 60;
        qDebug() << "FPSOptions::_get_font_size() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 13;
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
        qDebug() << "FramerateOptions::_get_shadow_text_offset() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 3;
    }
    //! custom palettes so the default color is not white
    QString _get_random_color()
    {
        QList<QString> colors { "#cdf6cb", "#ecd2e5", "#a8cc9a", "#c1eae0"
                              , "#6ac4cd", "#a2ebeb", "#e6f2f4", "#ff7cc2" };
        int index = rand() % (colors.size());
        QString color = colors[index];
        return color;
    }

// member
public:
    //! hold the id (starting from 0) of the responsible video
    quint8 video_id;
    //! framerate color, used for text and plot color
    ColorPickItem fps_plot_color;
    //! how big can the difference in the RGB space get between two pixels for us to detect a difference
    ValueItem<quint32> pixel_difference;
    //! prefix text of the framerate
    TextEditItem displayed_text;
    //! are these fpsoptions enabled
    bool enabled;
    //! should the fontsize be ignored (to fit the automatic scaling of the plot)
    bool displayed_text_fontsize_override;
    //! framerate model (to get the current framerate)
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! the current resolution might be needed to adapt the fontsize automatically (currently not used)
    std::shared_ptr<ResolutionsModel> _shared_resolution_model;
    //! to create a shadow effect we draw the text with an offset first
    QColor text_shadow;
    //! X fps text position (relative to the viewport, between (0,1) where 0 is the most left
    ValueItem<double> rel_fps_text_x_position;
    //! Y fps text position (relative to the viewport, between (0,1) where 0 is the top
    ValueItem<double> rel_fps_text_y_position;
};

#endif // FRAMERATEOPTIONS_H
