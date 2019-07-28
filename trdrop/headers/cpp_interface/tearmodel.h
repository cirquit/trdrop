#ifndef TEAR_MODEL_H
#define TEAR_MODEL_H

#include <QPainter>
#include <memory>
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/tearoptions.h"
#include "headers/cpp_interface/teardata.h"
#include "headers/qml_models/resolutionsmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"

class TearModel
{
// constructors
public:
    //! TODO
    TearModel(std::shared_ptr<QList<TearOptions>> shared_tear_options_list
           , std::shared_ptr<ResolutionsModel> shared_resolution_model
           , std::shared_ptr<GeneralOptionsModel> shared_general_options_model)
        : _shared_tear_options_list(shared_tear_options_list)
        , _shared_resolution_model(shared_resolution_model)
        , _shared_general_options_model(shared_general_options_model)
    { }

// methods
public:
    //! top left is (0,0)
    void draw_tears(QPainter * painter)
    {
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setRenderHint(QPainter::HighQualityAntialiasing);
        _draw_tears(painter);
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
    //! TODO
    std::vector<TearData> _tear_list;
    //! TODO
    std::shared_ptr<QList<TearOptions>> _shared_tear_options_list;
    //! TODO
    std::shared_ptr<ResolutionsModel> _shared_resolution_model;
    //! TODO
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
};

#endif // TEAR_MODEL_H
