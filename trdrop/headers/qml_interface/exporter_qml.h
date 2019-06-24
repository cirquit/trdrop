#ifndef EXPORTCONTROLLER_QML_H
#define EXPORTCONTROLLER_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>
#include "opencv2/opencv.hpp"

class ExporterQML : public QObject {

    Q_OBJECT
    Q_PROPERTY(bool _is_exporting READ isExporting WRITE setIsExporting)
//! constructors
public:
    //! default constructor, the default size is dependent on the first row of the resolutionModel
    ExporterQML(QObject * parent = nullptr)
        : QObject(parent)
        , _is_exporting(false)
        , _frame_count(0)
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


//! member
public:
    //! TODO
    bool _is_exporting;

    quint64 _frame_count;
};

#endif // EXPORTCONTROLLER_QML_H
