#ifndef FILEITEM_H
#define FILEITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//! FileItem class which manages the name and meta data of a video file
class FileItem
{
    Q_GADGET
    Q_PROPERTY(QString name         READ name         WRITE setName        ) // NOTIFY nameChanged)
    Q_PROPERTY(quint32 sizeMB       READ sizeMB       WRITE setSizeMB      ) // NOTIFY sizeMBChanged)
    Q_PROPERTY(quint8  position     READ position     WRITE setPosition    ) // NOTIFY positionChanged)
    Q_PROPERTY(QString container    READ container    WRITE setContainer   ) // NOTIFY containerChanged)
    Q_PROPERTY(bool    fileSelected READ fileSelected WRITE setFileSelected) // NOTIFY fileSelectionChanged)

//! constructor
public:
    //! default constructor creates a default initialization for each member
    //! file_selected is set to false
    FileItem()
        : _name("")
        , _size_mb(0)
        , _position(0)
        , _container("")
        , _file_selected(false)
    { }

    //! used for debugging
    FileItem(const QString & name)
        : _name(name)
        , _size_mb(0)
        , _position(0)
        , _container("Default container")
        , _file_selected(true)
    { }

    FileItem(const FileItem & other) = default;
    FileItem & operator=(const FileItem & other) = default;

//! setter methods for Q_PROPERTY
public:
    void setName(const QString & _other){ _name = _other; } // emit nameChanged(); }
    void setSizeMB(const quint32 & _other){ _size_mb = _other; } // emit sizeMBChanged(); }
    void setPosition(const quint8 & _other){ _position = _other; } // emit positionChanged(); }
    void setContainer(const QString & _other){ _container = _other; } // emit containerChanged(); }
    void setFileSelected(const bool & _other){ _file_selected = _other; } //emit fileSelectionChanged(); }

//! getter methods for Q_PROPERTY
public:
    QString name()         const { return _name; }
    quint32 sizeMB()       const { return _size_mb; }
    quint8  position()     const { return _position; }
    QString container()    const { return _container; }
    bool    fileSelected() const { return _file_selected; }

//! change signals for Q_PROPERTY
//signals:
//    void nameChanged();
//    void sizeMBChanged();
//    void positionChanged();
//    void containerChanged();
//    void fileSelectionChanged();

//! member
private:
    QString _name;          // file path
    quint32 _size_mb;       // size in megabyte of the selected file
    quint8  _position;      // position in the file management list
    QString _container;     // container type
    bool    _file_selected; // is a file currently selected for this item
};

#endif // FILEITEM_H
