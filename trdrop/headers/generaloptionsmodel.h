#ifndef GENERALOPTIONSMODEL_H
#define GENERALOPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/checkboxitem.h"

//!
class GeneralOptionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //! initialize the model with #default_items and prepare the role names
    GeneralOptionsModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_checkboxes();
        _setup_role_names();
    }
    //! manage the access to FileItem member from QML
    enum GeneralOptionsRoles
    {
        EnableViewNameRole    = Qt::UserRole
      , EnableViewTooltipRole = Qt::UserRole + 1
      , EnableViewValueRole   = Qt::UserRole + 2
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return 1;
    }
    //! a getter for the _role_names to enable the access via QML
    QHash<int, QByteArray> roleNames() const override { return _role_names; }
    //! QAbstractModel function which is called if a read in QML happens
    QVariant data(const QModelIndex & index,int role) const override
    {
        Q_UNUSED(index)
        switch (role)
        {
            case EnableViewNameRole:
                return _enable_view.name();
            case EnableViewTooltipRole:
                return _enable_view.tooltip();
            case EnableViewValueRole:
                return _enable_view.value();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        Q_UNUSED(index)
        if      (role == EnableViewNameRole) _enable_view.setName(value.toString());
        else if (role == EnableViewTooltipRole) _enable_view.setTooltip(value.toString());
        else if (role == EnableViewValueRole) _enable_view.setValue(value.toBool());
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
        _role_names[EnableViewNameRole] = "enableViewName";
        _role_names[EnableViewTooltipRole] = "enableViewTooltip";
        _role_names[EnableViewValueRole] = "enableViewValue";
    }
    //!TODO
    void _init_checkboxes()
    {
        _enable_view.setName("Enable View");
        _enable_view.setTooltip("Renders the exported frame in the main window (Disabling may improve export speed)");
        _enable_view.setValue(false);
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! enables rendering of the images
    CheckBoxItem _enable_view;
};


#endif // GENERALOPTIONSMODEL_H
