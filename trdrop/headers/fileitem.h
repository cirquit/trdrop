#ifndef FILEITEM_H
#define FILEITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//! FileItem class which manages the name and meta data of a video file
class FileItem
{

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

    FileItem(const FileItem & other) = default;
    FileItem & operator=(const FileItem & other) = default;

//! setter methods
public:
    void setName(const QString & _other){ _name = _other; }
    void setSizeMB(const quint32 & _other){ _size_mb = _other; }
    void setPosition(const quint8 & _other){ _position = _other; }
    void setContainer(const QString & _other){ _container = _other; }
    void setFileSelected(const bool & _other){ _file_selected = _other; }

//! getter methods
public:
    QString name()         const { return _name; }
    quint32 sizeMB()       const { return _size_mb; }
    quint8  position()     const { return _position; }
    QString container()    const { return _container; }
    bool    fileSelected() const { return _file_selected; }

//! member
private:
    QString _name;          // file path
    quint32 _size_mb;       // size in megabyte of the selected file
    quint8  _position;      // position in the file management list
    QString _container;     // container type
    bool    _file_selected; // is a file currently selected for this item
};

#endif // FILEITEM_H
