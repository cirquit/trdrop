#ifndef TEAROPTIONSMODEL_H
#define TEAROPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include <memory>
#include "headers/cpp_interface/tearoptions.h"


//!
class TearOptionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //!
    TearOptionsModel(std::shared_ptr<QList<TearOptions>> shared_tear_options_list
                   , QObject * parent = nullptr)
        : QAbstractListModel(parent)
        , _shared_tear_options_list(shared_tear_options_list)
    {
        _init_options();
        _setup_role_names();
    }
    //!
    enum TearOptionsRoles
    {
        ColorPickNameRole                = Qt::UserRole + 50
      , ColorPickTooltipRole             = Qt::UserRole + 51
      , ColorPickValueRole               = Qt::UserRole + 52
      , DismissTearPercentageNameRole    = Qt::UserRole + 53
      , DismissTearPercentageTooltipRole = Qt::UserRole + 54
      , DismissTearPercentageValueRole   = Qt::UserRole + 55
      , TearOptionsEnabled               = Qt::UserRole + 56
    };
//! methods
public:
    //!
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _shared_tear_options_list->size();
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
                return (*_shared_tear_options_list)[row].tear_plot_color.name();
            case ColorPickTooltipRole:
                return (*_shared_tear_options_list)[row].tear_plot_color.tooltip();
            case ColorPickValueRole:
                return (*_shared_tear_options_list)[row].tear_plot_color.color();
            case DismissTearPercentageNameRole:
                return (*_shared_tear_options_list)[row].dismiss_tear_percentage.name();
            case DismissTearPercentageTooltipRole:
                return (*_shared_tear_options_list)[row].dismiss_tear_percentage.tooltip();
            case DismissTearPercentageValueRole:
                return (*_shared_tear_options_list)[row].dismiss_tear_percentage.value();
            case TearOptionsEnabled:
                return (*_shared_tear_options_list)[row].enabled;
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if      (role == ColorPickNameRole)      (*_shared_tear_options_list)[row].tear_plot_color.setName(value.toString());
        else if (role == ColorPickTooltipRole)   (*_shared_tear_options_list)[row].tear_plot_color.setTooltip(value.toString());
        else if (role == ColorPickValueRole)     (*_shared_tear_options_list)[row].tear_plot_color.setColor(value.toString());
        else if (role == DismissTearPercentageNameRole)    (*_shared_tear_options_list)[row].dismiss_tear_percentage.setName(value.toString());
        else if (role == DismissTearPercentageTooltipRole) (*_shared_tear_options_list)[row].dismiss_tear_percentage.setTooltip(value.toString());
        else if (role == DismissTearPercentageValueRole)   (*_shared_tear_options_list)[row].dismiss_tear_percentage.setValue(static_cast<double>(value.toUInt()));
        else if (role == TearOptionsEnabled)         (*_shared_tear_options_list)[row].enabled = value.toBool();
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
            (*_shared_tear_options_list)[id].revert_to_default();
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
        setData(q0, value, DismissTearPercentageValueRole);
        setData(q1, value, DismissTearPercentageValueRole);
        setData(q2, value, DismissTearPercentageValueRole);
    }
    //! TODO
    Q_INVOKABLE void updateEnabledRows(const QList<QVariant> filePaths)
    {
        int video_count = filePaths.size();
        for(int i = 0; i < _shared_tear_options_list->size(); ++i)
        {
            const bool loaded_file = i < video_count;
            QModelIndex q = createIndex(i, 0);
            setData(q, loaded_file, TearOptionsEnabled);
        }
    }
//! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[ColorPickNameRole]                = "colorName";
        _role_names[ColorPickTooltipRole]             = "colorTooltip";
        _role_names[ColorPickValueRole]               = "color";
        _role_names[DismissTearPercentageNameRole]    = "dismissTearPercentageName";
        _role_names[DismissTearPercentageTooltipRole] = "dismissTearPercentageTooltip";
        _role_names[DismissTearPercentageValueRole]   = "dismissTearPercentage";
        _role_names[TearOptionsEnabled]               = "tearOptionsEnabled";
   }
    //! TODO
    void _init_options()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _shared_tear_options_list->append(TearOptions(id));
        }
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! TODO
    std::shared_ptr<QList<TearOptions>> _shared_tear_options_list;
};


#endif // TEAROPTIONSMODEL_H
