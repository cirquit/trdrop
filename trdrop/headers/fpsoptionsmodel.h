#ifndef FPSOPTIONSMODEL_H
#define FPSOPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/fpsoptions.h"

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
        ColorPickNameRole          = Qt::UserRole
      , ColorPickTooltipRole       = Qt::UserRole + 1
      , ColorPickValueRole         = Qt::UserRole + 2
      , PixelDifferenceNameRole    = Qt::UserRole + 3
      , PixelDifferenceTooltipRole = Qt::UserRole + 4
      , PixelDifferenceValueRole   = Qt::UserRole + 5
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
            case ColorPickNameRole:
                return _file_options_list[row].fps_plot_color.name();
            case ColorPickTooltipRole:
                return _file_options_list[row].fps_plot_color.tooltip();
            case ColorPickValueRole:
                return _file_options_list[row].fps_plot_color.color();
            case PixelDifferenceNameRole:
                return _file_options_list[row].pixel_difference.name();
            case PixelDifferenceTooltipRole:
                return _file_options_list[row].pixel_difference.tooltip();
            case PixelDifferenceValueRole:
                return _file_options_list[row].pixel_difference.value();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if      (role == ColorPickNameRole)          _file_options_list[row].fps_plot_color.setName(value.toString());
        else if (role == ColorPickTooltipRole)       _file_options_list[row].fps_plot_color.setTooltip(value.toString());
        else if (role == ColorPickValueRole)         _file_options_list[row].fps_plot_color.setColor(value.toString());
        else if (role == PixelDifferenceNameRole)    _file_options_list[row].pixel_difference.setName(value.toString());
        else if (role == PixelDifferenceTooltipRole) _file_options_list[row].pixel_difference.setTooltip(value.toString());
        else if (role == PixelDifferenceValueRole)   _file_options_list[row].pixel_difference.setValue(value.toUInt());
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
    //! apply the pixel difference to all indices
    Q_INVOKABLE void applyPixelDifference(const QVariant & value)
    {
        QModelIndex q0 = createIndex(0, 0);
        QModelIndex q1 = createIndex(1, 0);
        QModelIndex q2 = createIndex(2, 0);
        setData(q0, value, PixelDifferenceValueRole);
        setData(q1, value, PixelDifferenceValueRole);
        setData(q2, value, PixelDifferenceValueRole);
    }

//! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[ColorPickNameRole]    = "colorName";
        _role_names[ColorPickTooltipRole] = "colorTooltip";
        _role_names[ColorPickValueRole]   = "color";
        _role_names[PixelDifferenceNameRole]    = "pixelDifferenceName";
        _role_names[PixelDifferenceTooltipRole] = "pixelDifferenceTooltip";
        _role_names[PixelDifferenceValueRole]   = "pixelDifference";
    }
    //! TODO
    void _init_options()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _file_options_list.append(FPSOptions(id));
        }
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //!
    QList<FPSOptions> _file_options_list;
};

#endif // FPSOPTIONSMODEL_H
