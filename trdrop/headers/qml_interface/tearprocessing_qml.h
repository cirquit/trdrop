#ifndef TEARPROCESSING_QML_H
#define TEARPROCESSING_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"
#include "headers/cpp_interface/tearprocessing.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/fpsoptions.h"

//! TODO
class TearProcessingQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    TearProcessingQML(std::shared_ptr<FramerateModel> shared_framerate_model
                    , std::shared_ptr<QList<FPSOptions>> shared_fps_options_list
                    , QObject * parent = nullptr)
        : QObject(parent)
        , _shared_fps_options_list(shared_fps_options_list)
        , _shared_framerate_model(shared_framerate_model)
    { }
//    TearProcessingQML(QObject * parent = nullptr)

//! methods
public:
    //! TODO
    Q_SIGNAL void framesReady(const QList<cv::Mat> & cv_image_list);
    //! TODO
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {

        QList<TearData> teardata_list = _tear_processing.check_for_tears(cv_image_list, _shared_fps_options_list);

        for (int i = 0; i < teardata_list.size(); ++i) {
            //_shared_framerate_model->set_tear_at(i, tear_list[i]);
            //if (frametime_list[i] != 0) qDebug() << frametime_list[i] << "ms";
            //qDebug() << "TearProcessingQML::processFrames() - tear percentage[" << i << "]: " << teardata_list[i].get_tear_percentage();
        }
        emit framesReady(cv_image_list);
    }
    //! TODO
    Q_INVOKABLE void resetState()
    {
        _shared_framerate_model->reset_model();
        _tear_processing.reset_state();
    }

private:

    std::shared_ptr<QList<FPSOptions>> _shared_fps_options_list;
    //! TODO
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! TODO
    TearProcessing _tear_processing;

};


#endif // TEARPROCESSING_QML_H
