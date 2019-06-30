#ifndef EXPORTCONTROLLER_QML_H
#define EXPORTCONTROLLER_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include <QDir>
#include "headers/qml_models/exportoptionsmodel.h"
#include "opencv2/opencv.hpp"
#include "opencv2/highgui.hpp"

class ExporterQML : public QObject {

    Q_OBJECT
    Q_PROPERTY(bool _is_exporting READ isExporting WRITE setIsExporting)
//! constructors
public:
    //! default constructor, the default size is dependent on the first row of the resolutionModel
    ExporterQML(std::shared_ptr<ExportOptionsModel> export_options_model
              , QObject * parent = nullptr)
        : QObject(parent)
        , _is_exporting(false)
        , _frame_count(0)
        , _prefix_zeros(10)
        , _export_options_models(export_options_model)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void imageReady(const QImage & image);
    //! TODO
    Q_SIGNAL void requestNextImages();
    //! TODO
    Q_SLOT void processImage(const QImage & image)
    {
        // _qml_image = image.copy();
        qDebug() << "ExporterQML::processImage()";
        if (isExporting())
        {
            QString filepath = _create_image_file_path();
            image.save(filepath);
            _frame_count += 1;
        }
        emit imageReady(image);
    }
    //! TODO
    Q_SLOT void finishExporting()
    {
        // TODO
        qDebug() << "ExporterQML:finishExporting triggered";
        stopExporting();
    }

    //! TODO
    Q_INVOKABLE void startExporting()
    {
        setIsExporting(true);
        emit requestNextImages();
    }
    //! TODO
    Q_INVOKABLE void stopExporting()
    {
        setIsExporting(false);
        _frame_count = 0;
    }
    //! TODO
    Q_SLOT void setIsExporting(bool other){ _is_exporting = other; }
    //! TODO
    Q_SLOT bool isExporting(){ return _is_exporting; }

//! methods
private:
    //! TODO
    QString _create_image_file_path() const
    {
        QString directory_path = _export_options_models->getExportDirectory();
        QString imagesequence_prefix = _export_options_models->getImagesequencePrefix();
        return QDir(directory_path).filePath(imagesequence_prefix + _get_frame_count() + ".jpg");
    }
    //! TODO make _prefix_zeros dependent on the amount of frames
    //! This looks wrong on so many levels, maybe use printf or something
    QString _get_frame_count() const
    {
        QString frame_count = QString::number(_frame_count);
        int difference = std::abs(_prefix_zeros - frame_count.size());
        while (difference > 0)
        {
            frame_count = "0" + frame_count;
            difference -= 1;
        }
        return frame_count;
    }

//! member
public:
    //! TODO
    bool _is_exporting;
    //! TODO
    quint64 _frame_count;
    //! TODO
    const quint8 _prefix_zeros;
    //! this is shared because it is only dependent on how to save sources
    std::shared_ptr<ExportOptionsModel> _export_options_models;


};

#endif // EXPORTCONTROLLER_QML_H
