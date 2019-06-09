#ifndef RESOLUTIONSSMODEL_H
#define RESOLUTIONSSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/resolution.h"

//!
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
    enum ExportOptionsModelRoles
    {
        ResolutionPickNameRole          = Qt::UserRole + 60
      , ResolutionPickWidthRole         = Qt::UserRole + 61
      , ResolutionPickHeightRole        = Qt::UserRole + 62
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _fps_options_list.size();
    }
    //! a getter for the _role_names to enable the access via QML
    QHash<int, QByteArray> roleNames() const override { return _role_names; }
    //! QAbstractModel function which is called if a read in QML happens
    QVariant data(const QModelIndex & index,int role) const override
    {
        Q_UNUSED(index);
        switch (role)
        {
            case ResolutionPickNameRole:
                return _tear_options_list[row].tear_plot_color.name();
            case ResolutionPickTooltipRole:
                return _tear_options_list[row].tear_plot_color.tooltip();
            case ResolutionPickValueRole:
                return _tear_options_list[row].tear_plot_color.color();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if      (role == ResolutionPickNameRole)    _tear_options_list[row].tear_plot_color.setName(value.toString());
        else if (role == ResolutionPickValueRole)   _tear_options_list[row].tear_plot_color.setColor(value.toString());
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
    //! apply the color to the designated row
    Q_INVOKABLE void applyColor(const QVariant & value, const int & row)
    {
        QModelIndex q = createIndex(row, 0);
        setData(q, value, ColorPickValueRole);
    }

    //! apply the pixel difference to all indices
    Q_INVOKABLE void applyTearPercentage(const QVariant & value)
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
        _role_names[ColorPickNameRole]          = "colorName";
        _role_names[ColorPickTooltipRole]       = "colorTooltip";
        _role_names[ColorPickValueRole]         = "color";
        _role_names[PixelDifferenceNameRole]    = "pixelDifferenceName";
        _role_names[PixelDifferenceTooltipRole] = "pixelDifferenceTooltip";
        _role_names[PixelDifferenceValueRole]   = "pixelDifference";
   }
    //! TODO
    void _init_options()
    {
        _resolutions_list.push_back(Resolution(QSize(960, 540)));
        _resolutions_list.push_back(Resolution(QSize(1920, 1080)));
        _resolutions_list.push_back(Resolution(QSize(3840, 2160)));

    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! TODO
    QList<Resolution> _resolutions_list;
    _


};


#endif // EXPORTOPTIONSMODEL_H
