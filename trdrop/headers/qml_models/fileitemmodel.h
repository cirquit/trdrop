#ifndef FILEITEMMODEL_H
#define FILEITEMMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include <QFileInfo>
#include <QStandardPaths>
#include <cmath>

#include "headers/cpp_interface/fileitem.h"

//! qml wrapper a file list
class FileItemModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //! initialize the model with #default_items and prepare the role names
    FileItemModel(quint8 default_items
                , QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _setup_role_names();
        for (quint8 i = 0; i < default_items; ++i)
        {
            appendDefaultFileItem();
        }
    }
    //! manage the access to FileItem member from QML
    enum FileItemRoles
    {
        FilePathRole          = Qt::UserRole
      , SizeMBRole            = Qt::UserRole + 1
      , RecordedFramerateRole = Qt::UserRole + 2
      , QtFilePathRole        = Qt::UserRole + 3
      , FileSelectedRole      = Qt::UserRole + 4
    };
//! methods
public:
    //! number of elements in the _file_item_list which correlate to the rows
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _file_item_list.size();
    }
    //! a getter for the _role_names to enable the access via QML
    QHash<int, QByteArray> roleNames() const override { return _role_names; }
    //! QAbstractModel function which is called if a read in QML happens
    QVariant data(const QModelIndex & index,int role) const override
    {
        int row = index.row();
        // if the index is out of bounds, return QVariant
        if(row < 0 || row >= _file_item_list.size()) { return QVariant(); }
        // otherwise get the item
        const FileItem & file_item = _file_item_list.at(row);
        // check which member is accessed and return accordingly
        switch (role)
        {
            case FilePathRole:
                return file_item.filePath();
            case SizeMBRole:
                return file_item.sizeMB();
            case QtFilePathRole:
                return file_item.qtFilePath();
            case FileSelectedRole:
                return file_item.fileSelected();
            case RecordedFramerateRole:
                return file_item.recordedFramerate();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        FileItem & file_item = _file_item_list[index.row()];
        if (role == FilePathRole) file_item.setFilePath(value.toString());
        else if (role == SizeMBRole) file_item.setSizeMB(value.toUInt());
        else if (role == QtFilePathRole) file_item.setQtFilePath(value.toString());
        else if (role == FileSelectedRole) file_item.setFileSelected(value.toBool());
        else if (role == RecordedFramerateRole) file_item.setRecordedFramerate(value.toDouble());
        else return false;
        QModelIndex toIndex(createIndex(rowCount() - 1, index.column()));
        emit dataChanged(index, toIndex);
        return true ;
    }
    //! calling c++ QStandardPaths to use them in QML
    Q_INVOKABLE QVariant getDefaultMoviesDirectory() const
    {
        return QStandardPaths::writableLocation(QStandardPaths::MoviesLocation);
    }
    //! tells the views that the model's state has changed, triggers a recomputation of each delegate
    Q_INVOKABLE void resetModel()
    {
        beginResetModel();
        endResetModel();
    }
    //! adds a default (empty) fileitem
    Q_INVOKABLE void appendDefaultFileItem()
    {
        const FileItem file_item;
        _append_file_item(file_item);
    }
    //! callable from QML to remove the item
    Q_INVOKABLE void remove(int index)
    {
        emit beginRemoveRows(QModelIndex(), index, index);
        _file_item_list.removeAt(index);
        emit endRemoveRows();
    }
    //! checks if the fileSelected property of the item at the index is set
    Q_INVOKABLE QVariant isFileSelected(int index)
    {
        return QVariant::fromValue(_file_item_list.at(index).fileSelected());
    }
    //! returns the amount of fileitems with a path
    Q_INVOKABLE QVariant filesSelectedCount()
    {
        quint8 file_selected_count = 0;
        std::for_each(_file_item_list.begin(), _file_item_list.end(), [&](const FileItem & fileitem)
        {
            file_selected_count += fileitem.fileSelected() ? 1 : 0;
        });
        return QVariant::fromValue(file_selected_count);
    }
    //! get the filesize in megabyte, QFileInfo.size() returns byte
    Q_INVOKABLE QVariant getFileSize(const QString & url) const
    {
        // pow(2,10)   ~ KB
        // pow(2,10)^2 ~ MB
        return QFileInfo(url).size() / (std::pow(2,10) * std::pow(2,10));
    }
    //! wrapper to trigger the updateFileItemPaths signal from qml
    Q_INVOKABLE void emitFilePaths(const QList<QVariant> visual_file_path_list)
    {
        emit updateFileItemPaths(visual_file_path_list);
    }
    //! sets the recorded framerates based on the file_path_list (TODO zip lists) in the model
    Q_INVOKABLE void setRecordedFramerates(const QList<QVariant> visual_file_path_list
                                         , const QList<double> recorded_framerates)
    {
        for (int i = 0; i < visual_file_path_list.size(); ++i)
        {
            const int visual_index = i;
            const QString visual_file_path   = visual_file_path_list[visual_index].toString();
            const double  recorded_framerate = recorded_framerates[visual_index];
            for(int j = 0; j < _file_item_list.size(); ++j)
            {
                const QString model_file_path = _file_item_list[j].filePath();
                if (visual_file_path == model_file_path)
                {
                    QModelIndex q = createIndex(j, 0);
                    setData(q, recorded_framerate, RecordedFramerateRole);
                }
            }
        }
    }
    //! signal to wait from this model if any filepaths have changed
    Q_SIGNAL void updateFileItemPaths(const QList<QVariant> & filePaths);
//! methods
public:
    //! returns a const fileitem list to get the file information for a cv::VideoCapture
    const QList<FileItem> get_file_item_list() const { return _file_item_list; }
//! methods
private:
    //! set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[FilePathRole]          = "filePath";
        _role_names[SizeMBRole]            = "sizeMB";
        _role_names[QtFilePathRole]        = "qtFilePath";
        _role_names[FileSelectedRole]      = "fileSelected";
        _role_names[RecordedFramerateRole] = "recordedFramerate";
    }
    //! add file item object
    void _append_file_item(const FileItem file_item)
    {
        int new_row = rowCount();
        emit beginInsertRows(QModelIndex(), new_row, new_row);
        _file_item_list.append(file_item);
        emit endInsertRows();
    }
//! member
private:
    //! container which stored the fileitems, in other words the "model"
    QList<FileItem> _file_item_list;
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
};

#endif // FILEITEMMODEL_H
