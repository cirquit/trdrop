#ifndef FPSOPTIONSMODEL_H
#define FPSOPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/fileoptions.h"

//!
class FPSOptionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //!
    FPSOptionsModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //!
    enum FPSOptionsRoles
    {
        Option01NameRole    = Qt::UserRole
      , Option01TooltipRole = Qt::UserRole + 1
      , Option01ValueRole   = Qt::UserRole + 2
      , Option02NameRole    = Qt::UserRole + 3
      , Option02TooltipRole = Qt::UserRole + 4
      , Option02ValueRole   = Qt::UserRole + 5
      , Option03NameRole    = Qt::UserRole + 6
      , Option03TooltipRole = Qt::UserRole + 7
      , Option03ValueRole   = Qt::UserRole + 8
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _file_options_list.size();
    }
    //! a getter for the _role_names to enable the access via QML
    QHash<int, QByteArray> roleNames() const override { return _role_names; }
    //! QAbstractModel function which is called if a read in QML happens
    QVariant data(const QModelIndex & index,int role) const override
    {
        int row = index.row();
        switch (role)
        {
            case Option01NameRole:
                return _file_options_list[row].option_01.name();
            case Option01TooltipRole:
                return _file_options_list[row].option_01.tooltip();
            case Option01ValueRole:
                return _file_options_list[row].option_01.value();
            case Option02NameRole:
                return _file_options_list[row].option_02.name();
            case Option02TooltipRole:
                return _file_options_list[row].option_02.tooltip();
            case Option02ValueRole:
                return _file_options_list[row].option_02.value();
            case Option03NameRole:
                return _file_options_list[row].option_03.name();
            case Option03TooltipRole:
                return _file_options_list[row].option_03.tooltip();
            case Option03ValueRole:
                return _file_options_list[row].option_03.value();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if      (role == Option01NameRole)    _file_options_list[row].option_01.setName(value.toString());
        else if (role == Option01TooltipRole) _file_options_list[row].option_01.setTooltip(value.toString());
        else if (role == Option01ValueRole)   _file_options_list[row].option_01.setValue(value.toBool());
        else if (role == Option02NameRole)    _file_options_list[row].option_02.setName(value.toString());
        else if (role == Option02TooltipRole) _file_options_list[row].option_02.setTooltip(value.toString());
        else if (role == Option02ValueRole)   _file_options_list[row].option_02.setValue(value.toBool());
        else if (role == Option03NameRole)    _file_options_list[row].option_03.setName(value.toString());
        else if (role == Option03TooltipRole) _file_options_list[row].option_03.setTooltip(value.toString());
        else if (role == Option03ValueRole)   _file_options_list[row].option_03.setValue(value.toBool());
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
//! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[Option01NameRole]    = "option01Name";
        _role_names[Option01TooltipRole] = "option01Tooltip";
        _role_names[Option01ValueRole]   = "option01Value";
        _role_names[Option02NameRole]    = "option02Name";
        _role_names[Option02TooltipRole] = "option02Tooltip";
        _role_names[Option02ValueRole]   = "option02Value";
        _role_names[Option03NameRole]    = "option03Name";
        _role_names[Option03TooltipRole] = "option03Tooltip";
        _role_names[Option03ValueRole]   = "option03Value";
    }
    //! TODO
    void _init_options()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _file_options_list.append(FileOptions(id));
        }
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //!
    QList<FileOptions> _file_options_list;
};

#endif // FPSOPTIONSMODEL_H
