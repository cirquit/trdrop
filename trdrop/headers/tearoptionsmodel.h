#ifndef TEAROPTIONSMODEL_H
#define TEAROPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/tearoptions.h"

//!
class TearOptionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //!
    TearOptionsModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //!
    enum FPSOptionsRoles
    {
        ColorPickNameRole          = Qt::UserRole
      , ColorPickTooltipRole       = Qt::UserRole + 1
      , ColorPickValueRole         = Qt::UserRole + 2
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _tear_options_list.size();
    }
    //! a getter for the _role_names to enable the access via QML
    QHash<int, QByteArray> roleNames() const override { return _role_names; }
    //! QAbstractModel function which is called if a read in QML happens
    QVariant data(const QModelIndex & index,int role) const override
    {
        int row = index.row();
        switch (role)
        {
            case ColorPickNameRole:
                return _tear_options_list[row].tear_plot_color.name();
            case ColorPickTooltipRole:
                return _tear_options_list[row].tear_plot_color.tooltip();
            case ColorPickValueRole:
                return _tear_options_list[row].tear_plot_color.color();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if      (role == ColorPickNameRole)    _tear_options_list[row].tear_plot_color.setName(value.toString());
        else if (role == ColorPickTooltipRole) _tear_options_list[row].tear_plot_color.setTooltip(value.toString());
        else if (role == ColorPickValueRole)   _tear_options_list[row].tear_plot_color.setColor(value.toString());
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
    Q_INVOKABLE void revertModelToDefault()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _tear_options_list[id].revert_to_default();
        }
        resetModel();
    }

//! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[ColorPickNameRole]    = "colorName";
        _role_names[ColorPickTooltipRole] = "colorTooltip";
        _role_names[ColorPickValueRole]   = "color";
   }
    //! TODO
    void _init_options()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _tear_options_list.append(TearOptions(id));
        }
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! TODO
    QList<TearOptions> _tear_options_list;
};


#endif // TEAROPTIONSMODEL_H
