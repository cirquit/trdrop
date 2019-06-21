#ifndef EXPORTCONTROLLER_QML_H
#define EXPORTCONTROLLER_QML_H

#include <QObject>
#include <QDebug>

class ExportControllerQML : public QObject {

    Q_OBJECT
    Q_PROPERTY(bool _is_exporting READ isExporting WRITE setIsExporting)
//! constructors
public:
    //! default constructor, the default size is dependent on the first row of the resolutionModel
    ExportControllerQML(QObject * parent = nullptr)
        : QObject(parent)
    { }

//! methods
public:
    //! TODO
    Q_SIGNAL void stopExporting();
    //! TODO
    Q_SIGNAL void startExporting();
    //! TODO
    Q_INVOKABLE void invokeStartExporting()
    {
        setIsExporting(true);
        emit startExporting();
    }
    //! TODO
    Q_INVOKABLE void invokeStopExporting()
    {
        setIsExporting(false);
        emit stopExporting();
    }
    //! TODO
    Q_SLOT void setIsExporting(bool other){ _is_exporting = other; }
    //! TODO
    Q_SLOT bool isExporting(){ return _is_exporting; }

//! member
public:
    //! TODO
    bool _is_exporting;

};

#endif // EXPORTCONTROLLER_QML_H
