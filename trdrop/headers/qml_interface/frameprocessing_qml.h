#ifndef FRAMEPROCESSING_QML_H
#define FRAMEPROCESSING_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"
#include "headers/cpp_interface/frameprocessing.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/frametimemodel.h"
#include "headers/cpp_interface/framerateoptions.h"
#include "headers/cpp_interface/tearoptions.h"
#include "headers/cpp_interface/tearmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! QML wrapper to calculate the meta data for frames
class FrameProcessingQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    FrameProcessingQML(std::shared_ptr<FramerateModel> shared_framerate_model
                     , std::shared_ptr<FrametimeModel> shared_frametime_model
                     , std::shared_ptr<QList<FramerateOptions>> shared_fps_options_list
                     , std::shared_ptr<QList<TearOptions>> shared_tear_options_list
                     , std::shared_ptr<GeneralOptionsModel> shared_general_options_model
                     , std::shared_ptr<TearModel> shared_tear_model
                     , QObject * parent = nullptr)
        : QObject(parent)
        , _shared_fps_options_list(shared_fps_options_list)
        , _shared_tear_options_list(shared_tear_options_list)
        , _shared_framerate_model(shared_framerate_model)
        , _shared_frametime_model(shared_frametime_model)
        , _shared_general_options_model(shared_general_options_model)
        , _shared_tear_model(shared_tear_model)
    { }

//! methods
public:
    //! trigger if processing is finished (image list may be difference frames depending on the options)
    Q_SIGNAL void framesReady(const QList<cv::Mat> & cv_image_list);
    //! main processing logic
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {
        // calculate the differences between the frames and return the resulting b/w frames
        const QList<cv::Mat> & difference_mat_list = _frame_processing.check_for_difference(
                                                         cv_image_list
                                                       , _shared_fps_options_list
                                                       , _shared_tear_options_list);
        // meta data
        const QList<double> framerate_list    = _frame_processing.get_framerates();
        const QList<double> frametime_list    = _frame_processing.get_frametimes();
        const std::vector<TearData> tear_list = _frame_processing.get_tear_indices();
        // set meta data in the corresponding models
        for (int i = 0; i < framerate_list.size(); ++i) {
            _shared_framerate_model->set_framerate_at(i, framerate_list[i]);
            _shared_frametime_model->set_frametime_at(i, frametime_list[i]);
            _shared_tear_model->add_tears(tear_list);
        }
        // return the difference frames if set in the options
        const bool render_delta_frames = _shared_general_options_model->get_enable_delta_rendering();
        const bool frames_available    = !difference_mat_list.empty();
        if (render_delta_frames && frames_available)
        {
            emit framesReady(difference_mat_list);
        } else {
            emit framesReady(cv_image_list);
        }
    }
    //! resets all models
    Q_INVOKABLE void resetState(const QList<quint8> recorded_framerate_list)
    {
        _shared_framerate_model->reset_model();
        _shared_frametime_model->reset_model();
        _shared_tear_model->reset_state();
        _frame_processing.reset_state(recorded_framerate_list);
    }

// methods
private:
    //! framerate options for all videos, accessable via video_index
    std::shared_ptr<QList<FramerateOptions>> _shared_fps_options_list;
    //! tear options for all videos, accessable via video_index
    std::shared_ptr<QList<TearOptions>> _shared_tear_options_list;
    //! holds the framerate for all videos
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! holds the frametime for all videos
    std::shared_ptr<FrametimeModel> _shared_frametime_model;
    //! misc general options
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
    //! holds tears for all videos
    std::shared_ptr<TearModel> _shared_tear_model;
    //! internal processing object
    FrameProcessing _frame_processing;

};


#endif // FRAMEPROCESSING_QML_H
