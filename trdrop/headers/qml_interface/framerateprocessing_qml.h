#ifndef FRAMERATEPROCESSING_QML_H
#define FRAMERATEPROCESSING_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"
#include "headers/cpp_interface/framerateprocessing.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/frametimemodel.h"
#include "headers/cpp_interface/fpsoptions.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! TODO
class FramerateProcessingQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    FramerateProcessingQML(std::shared_ptr<FramerateModel> shared_framerate_model
                         , std::shared_ptr<FrametimeModel> shared_frametime_model
                         , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list
                         , std::shared_ptr<GeneralOptionsModel> shared_general_options_model
                         , QObject * parent = nullptr)
        : QObject(parent)
        , _shared_fps_options_list(shared_fps_options_list)
        , _shared_framerate_model(shared_framerate_model)
        , _shared_frametime_model(shared_frametime_model)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void framesReady(const QList<cv::Mat> & cv_image_list);
    //! TODO
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {
        //
        _framerate_processing.check_for_difference(cv_image_list, _shared_fps_options_list);
        //
        const QList<double> framerate_list = _framerate_processing.get_framerates();
        const QList<double> frametime_list = _framerate_processing.get_frametimes();

        for (int i = 0; i < framerate_list.size(); ++i) {
            _shared_framerate_model->set_framerate_at(i, framerate_list[i]);
            _shared_frametime_model->set_frametime_at(i, frametime_list[i]);
        }
        emit framesReady(cv_image_list);
    }
    //! TODO
    Q_INVOKABLE void resetState(const QList<quint8> recorded_framerate_list)
    {
        _shared_framerate_model->reset_model();
        _shared_frametime_model->reset_model();
        _framerate_processing.reset_state(recorded_framerate_list);
    }

// methods
private:
    //! TODO
    std::shared_ptr<QList<FPSOptions>> _shared_fps_options_list;
    //! TODO
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! TODO
    std::shared_ptr<FrametimeModel> _shared_frametime_model;
    //! TODO
    FramerateProcessing _framerate_processing;

};


#endif // FRAMERATEPROCESSING_QML_H
