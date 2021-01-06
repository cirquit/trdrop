#ifndef EXPORTCONTROLLER_QML_H
#define EXPORTCONTROLLER_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include <QDir>
#include <memory>
#include "headers/qml_models/exportoptionsmodel.h"
#include "headers/qml_models/imageformatmodel.h"
#include "headers/cpp_interface/frameratemodel.h"
#include "opencv2/opencv.hpp"
#include "opencv2/highgui.hpp"

//! QML wrapper to save images and csv
class ExporterQML : public QObject {

    Q_OBJECT
    Q_PROPERTY(bool _is_exporting READ isExporting WRITE setIsExporting)

//! constructors
public:
    //! initializes the exporter
    ExporterQML(std::shared_ptr<ExportOptionsModel> export_options_model
              , std::shared_ptr<ImageFormatModel>   imageformat_model
              , std::shared_ptr<FramerateModel> shared_framerate_model
              , QObject * parent = nullptr)
        : QObject(parent)
        , _is_exporting(false)
        , _frame_count(0)
        , _prefix_zeros(10)
        , _export_options_model(export_options_model)
        , _imageformat_model(imageformat_model)
        , _file_opened(false)
        , _shared_framerate_model(shared_framerate_model)
        , _active_video_count(0)
    { }

//! methods
public:
    //! signal to wait for if the export is finished for the frame
    Q_SIGNAL void imageReady(const QImage & image);
    //! exporter may request next images on start of the exporting process
    Q_SIGNAL void requestNextImages();
    //! saves the image and appends the framerates into the csv
    Q_SLOT void processImage(const QImage & image)
    {
        if (isExporting())
        {
            if (_export_options_model->export_as_imagesequence())
            {
                QString filepath = _create_image_file_path();
                image.save(filepath);
            }
            if (_export_options_model->export_csv())
            {
                _append_framerates();
            }
            _frame_count += 1;
        }
        emit imageReady(image);
    }
    //! on export finish trigger
    Q_SLOT void finishExporting()
    {
        _close_csv_file();
        qDebug() << "ExporterQML:finishExporting triggered";
        _frame_count = 0;
        _file_item_list.clear();
        stopExporting();
    }
    //! on start exporting trigger
    Q_INVOKABLE void startExporting()
    {
        setIsExporting(true);
        emit requestNextImages();
    }
    //! temporarly stop exporting
    Q_INVOKABLE void stopExporting()
    {
        setIsExporting(false);
    }
    //! setter
    Q_SLOT void setIsExporting(bool other){ _is_exporting = other; }
    //! getter
    Q_SLOT bool isExporting(){ return _is_exporting; }
    //! save the amount of current videos to be processed and their name (used for csv export)
    Q_SLOT void updateVideoCount(QList<QVariant> fileItemList)
    {
        _active_video_count = fileItemList.size();
        _file_item_list.clear();
        for(int i = 0; i < fileItemList.size(); ++i)
        {
            QString file_path = fileItemList[i].toString();
            QFileInfo file_info(file_path);
            _file_item_list.append(file_info.baseName());
        }
    }

//! methods
private:
    //! hardcoded filename with the same directory as the exported imagesequence
    QString _create_csv_file_path() const
    {
        QString directory_path = _export_options_model->get_export_directory();
        QString csv_filename = _export_options_model->get_csv_filename();
        return QDir(directory_path).filePath(csv_filename);
    }
    //! opens the filehandle
    void _open_csv_file()
    {
        QString csv_file_name = _create_csv_file_path();
        std::unique_ptr<QFile> new_file = std::unique_ptr<QFile>(new QFile(csv_file_name));
        _csv_file_handle = std::move(new_file);
    }
    //! closes the filehandle if it's opened
    void _close_csv_file()
    {
        if (_file_opened)
        {
            _csv_file_handle->close();
        }
        _file_opened = false;

    }
    //! appends the current framerates to the csv file, opens it if need be
    void _append_framerates()
    {
        if (!_file_opened)
        {
            _open_csv_file();
            _file_opened = true;
            _csv_file_handle->open(QIODevice::Append | QIODevice::Text);
            QTextStream stream(&(*_csv_file_handle));
            for (int i = 0; i < _active_video_count; ++i)
            {
                stream << "FPS " << _file_item_list[i];
                if (i < _active_video_count - 1) stream << ",";
                if (i == _active_video_count - 1) stream << "\n";
            }
        }

        QTextStream stream(&(*_csv_file_handle));
        std::vector<double> framerates = _shared_framerate_model->get_framerates();

        for (int i = 0; i < _active_video_count; ++i)
        {
            stream << framerates[i];
            if (i < _active_video_count - 1) stream << ",";
            if (i == _active_video_count - 1) stream << "\n";
        }
    }
    //! constructos the image filepath from the directory, imageprefix and extention
    QString _create_image_file_path() const
    {
        QString directory_path = _export_options_model->get_export_directory();
        if (!QDir(directory_path).exists())
        {
            QDir().mkdir(directory_path);
        }
        QString imagesequence_prefix = _export_options_model->get_imagesequence_prefix();
        QString image_postfix = _imageformat_model->get_active_value().name();
        return QDir(directory_path).filePath(imagesequence_prefix + _get_frame_count() + image_postfix);
    }
    //! TODO make _prefix_zeros dependent on the amount of frames
    //! This looks wrong on so many levels, maybe use printf or something
    //! returns the framecount as string with prefixed zeros
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
    //! is set via QML
    bool _is_exporting;
    //! used for constructing the image filepath
    quint64 _frame_count;
    //! how many numbers should the image filepath have
    const quint8 _prefix_zeros;
    //! used to get image filepath + misc export options
    std::shared_ptr<ExportOptionsModel> _export_options_model;
    //! used to extract the image extention
    std::shared_ptr<ImageFormatModel> _imageformat_model;
    //! filehandle
    std::unique_ptr<QFile> _csv_file_handle;
    //! is set via QML
    bool _file_opened;
    //! use to get the current framerates for csv file exporting
    std::shared_ptr<FramerateModel> _shared_framerate_model;
    //! video count update through the fileitem model and its signal (see FileWindow.qml)
    int _active_video_count = 0;
    //! storage for the video paths
    QList<QString> _file_item_list;
};

#endif // EXPORTCONTROLLER_QML_H
