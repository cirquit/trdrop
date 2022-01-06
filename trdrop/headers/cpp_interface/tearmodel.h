#ifndef TEAR_MODEL_H
#define TEAR_MODEL_H

#include <QPainter>
#include <memory>
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/tearoptions.h"
#include "headers/cpp_interface/teardata.h"
#include "headers/qml_models/resolutionsmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! holds all the tears
class TearModel
{
// constructors
public:
    //! model with shared options
    TearModel(std::shared_ptr<QList<TearOptions>> shared_tear_options_list
           , std::shared_ptr<ResolutionsModel> shared_resolution_model
           , std::shared_ptr<GeneralOptionsModel> shared_general_options_model)
        : _shared_tear_options_list(shared_tear_options_list)
        , _shared_resolution_model(shared_resolution_model)
        , _shared_general_options_model(shared_general_options_model)
        // todo, move this to a separate file.
        , _text_color(255, 255, 255) // white
        , _videoframecount(0)
        , _y_tear_pos("TearPos: ")
        , _cbheight("Border Height: ")
        , _cbcount("Border Count per Frame: ")
        , _videoframe("Video Frame: ")
        , _videoheight("Video Height: ")
        , _frametime("Current Frametime: ")
    { }

// methods
public:
    //! top left is (0,0)
    void draw_tears(QPainter * painter)
    {
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setRenderHint(QPainter::HighQualityAntialiasing);
        //_draw_cbdebugtext(painter);
        _draw_tears(painter);
    }
    //! draws tear+color border debug text
    void _draw_cbdebugtext(QPainter * painter)
    {
        const int video_height = _get_video_height();
        _videoframecount += 1; // todo: move this else where so when this
                               // gets rerun when changing settings it doesn't increment
        int frame_count = _videoframecount;
        // placeholders, make variables
        const int cbheight             = 32;
        const int cbcount              = 32;
        const int videoframe           = frame_count - 1; 
        const double frametime         = 16.667; // todo: get value from frametime model
        const int y_tear_pos           = 128;    // todo: get value from TearData
        painter->setFont(QFont("Fjalla One", 10));

        const QString y_tear_pos_text = _y_tear_pos + QString::number(y_tear_pos) + " ";
        const QString cbheight_text = _cbheight + QString::number(cbheight) + " ";
        const QString cbcount_text = _cbcount + QString::number(cbcount) + " ";
        const QString videoframe_text = _videoframe + QString::number(videoframe) + " ";
        const QString videoheight_text = _videoheight + QString::number(video_height) + " ";
        const QString frametime_text = _frametime + QString::number(frametime) + " ";
        const QString all_text = y_tear_pos_text + cbheight_text + cbcount_text + videoframe_text + videoheight_text + frametime_text;

        const int x_init_pos = 32; // rtss has 32 pixel color border
        const int y_init_pos = 120;

        painter->setPen(_text_color);
        painter->drawText(x_init_pos, y_init_pos, all_text);
    }
    //! copies the new tears at the end of the _tear_list
    void add_tears(std::vector<TearData> other)
    {
        _tear_list.insert( _tear_list.end(), other.begin(), other.end() );
    }
    //! deletes the _tear_list
    void reset_state()
    {
        _tear_list.clear();
    }
// methods
private:
    int _get_video_height()
    {
        QSize current_size = _shared_resolution_model->get_active_size();
        if      (current_size == QSize(960, 540))   return  540;
        else if (current_size == QSize(1280, 720))  return  720;
        else if (current_size == QSize(1600, 900))  return  900;
        else if (current_size == QSize(1920, 1080)) return 1080;
        else if (current_size == QSize(2048, 1152)) return 1152;
        else if (current_size == QSize(2560, 1440)) return 1440;
        else if (current_size == QSize(3840, 2160)) return 2160;
        qDebug() << "TearBorderDebug::_get_video_height() - there is no case for the current resolution(" << current_size << "), this should never happen";
        return 540;
    }
    //! draws every tear and deletes them if they are done rendering
    void _draw_tears(QPainter * painter)
    {
        for (size_t i = 0; i < _tear_list.size(); ++i) {
            int video_index = static_cast<int>(_tear_list[i].get_video_index());
            QColor tear_color = (*_shared_tear_options_list)[video_index].tear_plot_color.color();
            _tear_list[i].draw(painter, _shared_resolution_model->get_active_size(), tear_color);
        }
        _tear_list.erase(std::remove_if(_tear_list.begin(),
                                        _tear_list.end(),
                                        [](const TearData & tear_data){ return tear_data.done_rendering(); })
                        , _tear_list.end());
    }

// member
private:
    // color border debug stuff
    QColor _text_color;
    qint64 _videoframecount;
    QString _y_tear_pos;
    QString _cbheight;
    QString _cbcount;
    QString _videoframe;
    QString _videoheight;
    QString _frametime;
    //! holds all the tears for all videos
    std::vector<TearData> _tear_list;
    //! needed for the color
    std::shared_ptr<QList<TearOptions>> _shared_tear_options_list;
    //! holds the current resolution
    std::shared_ptr<ResolutionsModel> _shared_resolution_model;
    //! not used currently
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
};

#endif // TEAR_MODEL_H
