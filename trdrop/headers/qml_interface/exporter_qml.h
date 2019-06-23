#ifndef EXPORTCONTROLLER_QML_H
#define EXPORTCONTROLLER_QML_H

#include <QObject>
#include <QImage>
#include <QDebug>

class ExporterQML : public QObject {

    Q_OBJECT
    Q_PROPERTY(bool _is_exporting READ isExporting WRITE setIsExporting)
//! constructors
public:
    //! default constructor, the default size is dependent on the first row of the resolutionModel
    ExporterQML(QObject * parent = nullptr)
        : QObject(parent)
        , _is_exporting(false)
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
        emit imageReady(image);
//        if (isExporting())
//        {
//            qDebug() << "ExporterQML:exportImage: processing image";
//            emit requestNextImages();
//        } else {
//            //qDebug() << "ExporterQML:exportImage: not exporting anything";
//        }
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
        // TODO
    }
    //! TODO
    Q_SLOT void setIsExporting(bool other){ _is_exporting = other; }
    //! TODO
    Q_SLOT bool isExporting(){ return _is_exporting; }

//! member
public:
    //! TODO
    bool _is_exporting;
    //QImage _qml_image;
};

#endif // EXPORTCONTROLLER_QML_H
