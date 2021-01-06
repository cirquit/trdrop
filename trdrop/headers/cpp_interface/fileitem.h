#ifndef FILEITEM_H
#define FILEITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//! manages the filepath and different meta data for a video file
class FileItem
{
//! constructors
public:
    //! default constructor
    FileItem()
        : _file_path("")
        , _size_mb(0)
        , _qt_file_path("")
        , _file_selected(false)
        , _recorded_framerate(0.0)
    { }
    //! copy constructor
    FileItem(const FileItem & other) = default;
    //! assignment operator
    FileItem & operator=(const FileItem & other) = default;

//! setter methods
public:
    void setFilePath(const QString & _other){ _file_path = _other; }
    void setSizeMB(const quint32 & _other){ _size_mb = _other; }
    void setQtFilePath(const QString & _other){ _qt_file_path = _other; }
    void setFileSelected(const bool & _other){ _file_selected = _other; }
    void setRecordedFramerate(const double & _other){ _recorded_framerate = _other; }
//! getter methods
public:
    QString filePath()          const { return _file_path; }
    quint32 sizeMB()            const { return _size_mb; }
    QString qtFilePath()        const { return _qt_file_path; }
    bool    fileSelected()      const { return _file_selected; }
    double  recordedFramerate() const { return _recorded_framerate; }
    bool    isDefault()         const { return _file_path == "" && _size_mb == 0; }
//! member
private:
    //! raw file path
    QString _file_path;
    //! size in megabyte of the selected file
    quint32 _size_mb;
    //! qt file path (with file:// as prefix)
    QString _qt_file_path;
    //! is a file currently selected for this item (e.g is _file_path filled "correctly")
    bool    _file_selected;
    //! with how many frames per second was this file recorded
    double  _recorded_framerate;
};

#endif // FILEITEM_H
