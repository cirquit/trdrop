#ifndef VIDEOFORMATMODEL_H
#define VIDEOFORMATMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/cpp_interface/videoformat.h"

//! TODO
class VideoFormatModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //!
    VideoFormatModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //!
    enum VideoFormatModelRoles
    {
        VideoFormatNameRole  = Qt::UserRole + 80
      , VideoFormatValueRole = Qt::UserRole + 81
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _videoformat_list.size();
    }
    //! a getter for the _role_names to enable the access via QML
    QHash<int, QByteArray> roleNames() const override { return _role_names; }
    //! QAbstractModel function which is called if a read in QML happens
    QVariant data(const QModelIndex & index,int role) const override
    {
        Q_UNUSED(index);
        int row = index.row();
        switch (role)
        {
            case VideoFormatNameRole:
                return _videoformat_list[row].name();
            case VideoFormatValueRole:
                return _videoformat_list[row].value();
            default:
                return QVariant();
        }
    }
    //! tells the views that the model's state has changed -> this triggers a "recompution" of the delegate
    Q_INVOKABLE void resetModel()
    {
        beginResetModel();
        endResetModel();
    }
    //! TODO
    Q_INVOKABLE QVariant getValueAt(const int & row)
    {
        QModelIndex q = createIndex(row, 0);
        return data(q, VideoFormatValueRole);
    }
    //! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[VideoFormatNameRole] =  "videoFormatName";
        _role_names[VideoFormatValueRole] = "videoFormatValue";
   }
    //! TODO
    void _init_options()
    {
        _videoformat_list.push_back(VideoFormat(VideoFormatType::AVI));
        _videoformat_list.push_back(VideoFormat(VideoFormatType::MP4));
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! TODO
    QList<VideoFormat> _videoformat_list;
};


#endif // VIDEOFORMATMODEL_H
