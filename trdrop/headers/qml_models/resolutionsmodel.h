#ifndef RESOLUTIONSSMODEL_H
#define RESOLUTIONSSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/cpp_interface/resolution.h"

//! qml model wrapper around resolutions
class ResolutionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //! default constructor
    ResolutionsModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //! role names
    enum ResolutionsModelRoles
    {
        ResolutionPickNameRole = Qt::UserRole + 60
      , ResolutionPickSizeRole = Qt::UserRole + 61
    };
//! methods
public:
    //! amount of possible resolutions in _resolutions_list
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
    //! tells the views that the model's state has changed, triggers a recomputation of each delegate
    Q_INVOKABLE void resetModel()
    {
        beginResetModel();
        endResetModel();
    }
    //! getter
    Q_INVOKABLE QVariant getSizeAt(const int & row)
    {
        QModelIndex q = createIndex(row, 0);
        return data(q, ResolutionPickSizeRole);
    }
    //! need this to make drop-down lists work (enabled signalizes the "current" options)
    Q_INVOKABLE void setActiveValueAt(const int & row)
    {
        for (int i = 0; i < _resolutions_list.size(); ++i)
        {
            bool enabled = i == row;
            _resolutions_list[i].setEnabled(enabled);
        }
        qDebug() << "ResolutionModel(c++): setActiveValueAt: " << row;
    }
    //! need this to make drop-down lists work (enabled signalizes the "current" options)
    Q_INVOKABLE QVariant getActiveSize()
    {
        return get_active_size();
    }
    //! need this to make drop-down lists work (enabled signalizes the "current" options)
    Resolution get_active_value()
    {
        for (int i = 0; i < _resolutions_list.size(); ++i) {
            if (_resolutions_list[i].enabled())
            {
                return _resolutions_list[i];
            }
        }
        qDebug() << "ResolutionModel::getActiveValue() - no resolution selected, this should never happen. Returning first element";
        return _resolutions_list[0];
    }
    //! need this to make drop-down lists work (enabled signalizes the "current" options)
    QSize get_active_size()
    {
        return get_active_value().size();
    }

    //! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[ResolutionPickNameRole] = "resolutionName";
        _role_names[ResolutionPickSizeRole] = "resolution";
   }
    //! initial options, currently supporting only 16:9
    void _init_options()
    {
        // currently only 16:9
        _resolutions_list.push_back(Resolution(QSize(960, 540),    true));
        _resolutions_list.push_back(Resolution(QSize(1280, 720),  false));
        //_resolutions_list.push_back(Resolution(QSize(1280, 1080), false));
        _resolutions_list.push_back(Resolution(QSize(1600, 900),  false));
        _resolutions_list.push_back(Resolution(QSize(1920, 1080), false));
        _resolutions_list.push_back(Resolution(QSize(2048, 1152), false));
        //_resolutions_list.push_back(Resolution(QSize(2560, 1440), false));
        _resolutions_list.push_back(Resolution(QSize(2560, 1440), false));
        _resolutions_list.push_back(Resolution(QSize(3840, 2160), false));
        //_resolutions_list.push_back(Resolution(QSize(4096, 2160), false));
        //_resolutions_list.push_back(Resolution(QSize(5120, 2160), false));
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! the "model"
    QList<Resolution> _resolutions_list;
};


#endif // EXPORTOPTIONSMODEL_H
