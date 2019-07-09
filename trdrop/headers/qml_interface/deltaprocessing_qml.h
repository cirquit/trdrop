#ifndef DELTAPROCESSING_QML_H
#define DELTAPROCESSING_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"
#include "headers/cpp_interface/deltaprocessing.h"
#include "headers/cpp_interface/fpsoptions.h"
#include "headers/qml_models/generaloptionsmodel.h"

//! converts the images from cv::Mat to QImage
class DeltaProcessingQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    DeltaProcessingQML(std::shared_ptr<QList<FPSOptions>> shared_fps_options_list
                     , std::shared_ptr<GeneralOptionsModel> shared_general_options_model
                     , QObject * parent = nullptr)
        : QObject(parent)
        , _shared_general_options_model(shared_general_options_model)
        , _shared_fps_options_list(shared_fps_options_list)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void framesReady(const QList<cv::Mat> & cv_image_list);
    //! TODO
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {
        // TODO get this from global settings
        if (_shared_general_options_model->get_enable_delta_rendering())
        {
            const QList<cv::Mat> difference_frames = _delta_processing.check_for_difference(cv_image_list, _shared_fps_options_list);
            if (difference_frames.empty())
            {
                emit framesReady(cv_image_list);
            } else {
                emit framesReady(difference_frames);
            }
        } else {
            emit framesReady(cv_image_list);
        }
    }
    //! TODO
    Q_INVOKABLE void resetState()
    {
        _delta_processing.reset_state();
    }

private:
    //! TODO
    std::shared_ptr<GeneralOptionsModel> _shared_general_options_model;
    //! TODO
    std::shared_ptr<QList<FPSOptions>> _shared_fps_options_list;
    //! TODO
    DeltaProcessing _delta_processing;

};
#endif // DELTAPROCESSING_QML_H
