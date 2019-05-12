//#ifndef FILEMODEL_H
//#define FILEMODEL_H

//#include <QDebug>
//#include <QString>
//#include <QVector>
//#include <QAbstractListModel>
//#include "fileitem.h"

//class FileModel : public QAbstractListModel
//{
//    Q_OBJECT
//    Q_ENUMS(FileItemRoles)

//public:
//    enum FileItemRoles {
//        NameRole = Qt::UserRole + 1,
//        ContainerRole,
//        SizeMBRole,
//        PositionRole,
//        FileSelectedRole,
//    };

//    using QAbstractListModel::QAbstractListModel;

//    //! TODO
//    QHash<int,QByteArray> roleNames() const override {
//        return { { NameRole, "name" },
//                 { ContainerRole, "container" },
//                 { SizeMBRole, "size_mb" },
//                 { PositionRole, "position"},
//                 { FileSelectedRole, "file_selected"},
//        };
//    }

//    //! TODO
//    int rowCount(const QModelIndex & parent = QModelIndex()) const override {
//        if (parent.isValid())
//            return 0;
//        return m_list.size();
//    }

//    //! TODO
//    bool setData(const QModelIndex &index, const QVariant &value, int role) override
//    {
//        if (!hasIndex(index.row(), index.column(), index.parent()) || !value.isValid())
//            return false;

//        FileItem &item = m_list[index.row()];
//        if (role == ContainerRole) item.container = value.toString();
//        else if (role == NameRole) item.name = value.toString();
//        else if (role == SizeMBRole) item.size_mb = value.toUInt();
//        else if (role == PositionRole) item.position = static_cast<uint8_t>(value.toUInt());
//        else if (role == FileSelectedRole) item.file_selected = value.toBool();
//        else return false;

//        emit dataChanged(index, index, { role } );

//        return true ;
//    }

//    //! TODO
//    QVariant data(const QModelIndex & index, int role = Qt::DisplayRole) const override {
//        if (!hasIndex(index.row(), index.column(), index.parent()))
//            return {};

//        const FileItem &item = m_list.at(index.row());
//        if (role == ContainerRole) return item.container;
//        if (role == NameRole) return item.name;
//        if (role == SizeMBRole) return item.size_mb;
//        if (role == PositionRole) return item.position;
//        if (role == FileSelectedRole) return item.file_selected;

//        return {};
//    }

//    //! TODO
//    Qt::ItemFlags flags(const QModelIndex &index) const override
//    {
//        return QAbstractListModel::flags(index) | Qt::ItemIsEditable;
//    }

//    //! TODO
//    Q_INVOKABLE void remove(int index)
//    {
//        m_list.remove(index);
//    }

//    Q_INVOKABLE void append(struct FileItem file_item)
//    {
//        m_list.append(file_item);
//    }

//private:
//    QVector<FileItem> m_list = {
//        { "Test 01", "AVI", 0, 0, false },
//        { "Test 02", "MP4", 0, 0, false },
//        { "Test 03", "AVI", 0, 0, false }
//    };
//};

//#endif // FILEMODEL_H
