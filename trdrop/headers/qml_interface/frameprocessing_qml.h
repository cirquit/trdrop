#ifndef FRAMEPROCESSING_QML_H
#define FRAMEPROCESSING_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"
#include "headers/cpp_interface/frameprocessing.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/frametimemodel.h"
#include "headers/cpp_interface/fpsoptions.h"
#include "headers/cpp_interface/tearoptions.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! TODO
class FrameProcessingQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    FrameProcessingQML(std::shared_ptr<FramerateModel> shared_framerate_model
                         , std::shared_ptr<FrametimeModel> shared_frametime_model
                         , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list
                         , std::shared_ptr<QList<TearOptions>> shared_tear_options_list
                         , std::shared_ptr<GeneralOptionsModel> shared_general_options_model
                         , QObject * parent = nullptr)
        : QObject(parent)
        , _shared_fps_options_list(shared_fps_options_list)
        , _shared_tear_options_list(shared_tear_options_list)
        , _shared_framerate_model(shared_framerate_model)
        , _shared_frametime_model(shared_frametime_model)
        , _shared_general_options_model(shared_general_options_model)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void framesReady(const QList<cv::Mat> & cv_image_list);
    //! TODO
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {
        // calculate the differences between the frames and return the resulting b/w frames
        QList<cv::Mat> difference_mat_list = _frame_processing.check_for_difference(
                                                 cv_image_list
                                               , _shared_fps_options_list
                                               , _shared_tear_options_list);
        //
        const QList<double> framerate_list = _frame_processing.get_framerates();
        const QList<double> frametime_list = _frame_processing.get_frametimes();

        for (int i = 0; i < framerate_list.size(); ++i) {
            _shared_framerate_model->set_framerate_at(i, framerate_list[i]);
            _shared_frametime_model->set_frametime_at(i, frametime_list[i]);
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
    //! TODO
    Q_INVOKABLE void resetState(const QList<quint8> recorded_framerate_list)
    {
        _shared_framerate_model->reset_model();
        _shared_frametime_model->reset_model();
        _frame_processing.reset_state(recorded_framerate_list);
    }

// methods
private:
    //! TODO
    std::shared_ptr<QList<FPSOptions>> _shared_fps_options_list;
    //! TODO
    std::shared_ptr<QList<TearOptions>> _shared_tear_options_list;
    //! TODO
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! TODO
    std::shared_ptr<FrametimeModel> _shared_frametime_model;
    //! TODO
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
    //! TODO
    FrameProcessing _frame_processing;

};


#endif // FRAMEPROCESSING_QML_H
