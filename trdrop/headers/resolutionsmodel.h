#ifndef RESOLUTIONSSMODEL_H
#define RESOLUTIONSSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/resolution.h"

//! TODO
class ResolutionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //!
    ResolutionsModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //!
    enum ResolutionsModelRoles
    {
        ResolutionPickNameRole = Qt::UserRole + 60
      , ResolutionPickSizeRole = Qt::UserRole + 61
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _resolutions_list.size();
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
            case ResolutionPickNameRole:
                return _resolutions_list[row].name();
            case ResolutionPickSizeRole:
                return _resolutions_list[row].size();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if (role == ResolutionPickSizeRole) _resolutions_list[row].setSize(value.toSize());
        else return false;
        QModelIndex toIndex(createIndex(rowCount() - 1, index.column()));
        emit dataChanged(index, toIndex);
        return true;
    }
    //! tells the views that the model's state has changed -> this triggers a "recompution" of the delegate
    Q_INVOKABLE void resetModel()
    {
        beginResetModel();
        endResetModel();
    }
    //! TODO
    Q_INVOKABLE QVariant getSizeAt(const int & row)
    {
        QModelIndex q = createIndex(row, 0);
        return data(q, ResolutionPickSizeRole);
    }
    //! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[ResolutionPickNameRole] = "resolutionName";
        _role_names[ResolutionPickSizeRole] = "resolution";
   }
    //! TODO
    void _init_options()
    {
        _resolutions_list.push_back(Resolution(QSize(960, 540)));
        _resolutions_list.push_back(Resolution(QSize(1280, 720)));
        _resolutions_list.push_back(Resolution(QSize(1280, 1080)));
        _resolutions_list.push_back(Resolution(QSize(1600, 900)));
        _resolutions_list.push_back(Resolution(QSize(1920, 1080)));
        _resolutions_list.push_back(Resolution(QSize(2048, 1080)));
        _resolutions_list.push_back(Resolution(QSize(2560, 1440)));
        _resolutions_list.push_back(Resolution(QSize(3840, 1080)));
        _resolutions_list.push_back(Resolution(QSize(3840, 2160)));
        _resolutions_list.push_back(Resolution(QSize(4096, 2160)));
        _resolutions_list.push_back(Resolution(QSize(5120, 2160)));
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! TODO
    QList<Resolution> _resolutions_list;
};


#endif // EXPORTOPTIONSMODEL_H
