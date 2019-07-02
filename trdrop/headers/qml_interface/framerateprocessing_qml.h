#ifndef FRAMERATEPROCESSING_QML_H
#define FRAMERATEPROCESSING_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"
#include "headers/cpp_interface/framerateprocessing.h"
#include "headers/cpp_interface/frameratemodel.h"

//! converts the images from cv::Mat to QImage
class FramerateProcessingQML : public QObject {

    Q_OBJECT

//! constructors
public:
    //! default constructor
    FramerateProcessingQML(std::shared_ptr<FramerateModel> shared_framerate_model,
                           QObject * parent = nullptr)
        : QObject(parent)
        , _shared_framerate_model(shared_framerate_model)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void framesReady(const QList<cv::Mat> & cv_image_list);
    //! TODO
    Q_SLOT void processFrames(const QList<cv::Mat> & cv_image_list)
    {
        //
        _framerate_processing.check_for_difference(cv_image_list);
        //
        //
        const QList<double> framerate_list = _framerate_processing.get_framerates();

        //qDebug() << "FPS:";
        for (int i = 0; i < framerate_list.size(); ++i) {
            _shared_framerate_model->set_framerate_at(i, framerate_list[i]);
          //  qDebug() << "    " << framerate_list[i];
        }
        emit framesReady(cv_image_list);
    }

private:
    //! TODO
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! TODO
    FramerateProcessing _framerate_processing;

};


#endif // FRAMERATEPROCESSING_QML_H
