#ifndef GENERALOPTIONSMODEL_H
#define GENERALOPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/valueitem.h"

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
        EnableViewNameRole              = Qt::UserRole
      , EnableViewTooltipRole           = Qt::UserRole + 1
      , EnableViewValueRole             = Qt::UserRole + 2
      , EnableFramerateNameRole         = Qt::UserRole + 3
      , EnableFramerateTooltipRole      = Qt::UserRole + 4
      , EnableFramerateValueRole        = Qt::UserRole + 5
      , EnableTearsNameRole             = Qt::UserRole + 6
      , EnableTearsTooltipRole          = Qt::UserRole + 7
      , EnableTearsValueRole            = Qt::UserRole + 8
      , EnableFrametimeNameRole         = Qt::UserRole + 9
      , EnableFrametimeTooltipRole      = Qt::UserRole + 10
      , EnableFrametimeValueRole        = Qt::UserRole + 11
      , EnableDeltaRenderingNameRole    = Qt::UserRole + 12
      , EnableDeltaRenderingTooltipRole = Qt::UserRole + 13
      , EnableDeltaRenderingValueRole   = Qt::UserRole + 14
      , FramerateRangeNameRole          = Qt::UserRole + 15
      , FramerateRangeTooltipRole       = Qt::UserRole + 16
      , FramerateRangeValueRole         = Qt::UserRole + 17
      , FrametimeRangeNameRole          = Qt::UserRole + 18
      , FrametimeRangeTooltipRole       = Qt::UserRole + 19
      , FrametimeRangeValueRole         = Qt::UserRole + 20
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
            case EnableFramerateNameRole:
                return _enable_fps_analysis.name();
            case EnableFramerateTooltipRole:
                return _enable_fps_analysis.tooltip();
            case EnableFramerateValueRole:
                return _enable_fps_analysis.value();
            case EnableTearsNameRole:
                return _enable_tear_analysis.name();
            case EnableTearsTooltipRole:
                return _enable_tear_analysis.tooltip();
            case EnableTearsValueRole:
                return _enable_tear_analysis.value();
            case EnableFrametimeNameRole:
                return _enable_frametime_analysis.name();
            case EnableFrametimeTooltipRole:
                return _enable_frametime_analysis.tooltip();
            case EnableFrametimeValueRole:
                return _enable_frametime_analysis.value();
            case EnableDeltaRenderingNameRole:
                return _enable_delta_rendering.name();
            case EnableDeltaRenderingTooltipRole:
                return _enable_delta_rendering.tooltip();
            case EnableDeltaRenderingValueRole:
                return _enable_delta_rendering.value();
            case FramerateRangeNameRole:
                return _framerate_plot_range.name();
            case FramerateRangeTooltipRole:
                return _framerate_plot_range.tooltip();
            case FramerateRangeValueRole:
                return _framerate_plot_range.value();
            case FrametimeRangeNameRole:
                return _frametime_plot_range.name();
            case FrametimeRangeTooltipRole:
                return _frametime_plot_range.tooltip();
            case FrametimeRangeValueRole:
                return _frametime_plot_range.value();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        Q_UNUSED(index)
        if (role == EnableViewValueRole) _enable_view.setValue(value.toBool());
        else if (role == EnableFramerateValueRole) _enable_fps_analysis.setValue(value.toBool());
        else if (role == EnableTearsValueRole) _enable_tear_analysis.setValue(value.toBool());
        else if (role == EnableFrametimeValueRole) _enable_frametime_analysis.setValue(value.toBool());
        else if (role == EnableDeltaRenderingValueRole) _enable_delta_rendering.setValue(value.toBool());
        else if (role == FramerateRangeValueRole) _framerate_plot_range.setValue(static_cast<quint8>(value.toUInt()));
        else if (role == FrametimeRangeValueRole) _frametime_plot_range.setValue(static_cast<quint8>(value.toUInt()));
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
        _init_checkboxes();
        resetModel();
    }
    //! TODO
    Q_INVOKABLE QVariant enabledFramerateAnalysis() { return _enable_fps_analysis.value(); }
    //! TODO
    Q_INVOKABLE QVariant enabledTearAnalysis()      { return _enable_tear_analysis.value(); }


//! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[EnableViewNameRole]              = "enableViewName";
        _role_names[EnableViewTooltipRole]           = "enableViewTooltip";
        _role_names[EnableViewValueRole]             = "enableViewValue";
        _role_names[EnableFramerateNameRole]         = "enableFramerateName";
        _role_names[EnableFramerateTooltipRole]      = "enableFramerateTooltip";
        _role_names[EnableFramerateValueRole]        = "enableFramerateValue";
        _role_names[EnableTearsNameRole]             = "enableTearsName";
        _role_names[EnableTearsTooltipRole]          = "enableTearsTooltip";
        _role_names[EnableTearsValueRole]            = "enableTearsValue";
        _role_names[EnableFrametimeNameRole]         = "enableFrametimeName";
        _role_names[EnableFrametimeTooltipRole]      = "enableFrametimeTooltip";
        _role_names[EnableFrametimeValueRole]        = "enableFrametimeValue";
        _role_names[EnableDeltaRenderingNameRole]    = "enableDeltaRenderingName";
        _role_names[EnableDeltaRenderingTooltipRole] = "enableDeltaRenderingTooltip";
        _role_names[EnableDeltaRenderingValueRole]   = "enableDeltaRenderingValue";
        _role_names[FramerateRangeNameRole]          = "framerateRangeName";
        _role_names[FramerateRangeTooltipRole]       = "framerateRangeTooltip";
        _role_names[FramerateRangeValueRole]         = "framerateRangeValue";
        _role_names[FrametimeRangeNameRole]          = "frametimeRangeName";
        _role_names[FrametimeRangeTooltipRole]       = "frametimeRangeTooltip";
        _role_names[FrametimeRangeValueRole]         = "frametimeRangeValue";
    }
    //!TODO
    void _init_checkboxes()
    {
        _enable_view.setName("Enable View");
        _enable_view.setTooltip("Renders the exported frame in the main window (Disabling may improve export speed)");
        _enable_view.setValue(true);

        _enable_fps_analysis.setName("Enable framerate analysis");
        _enable_fps_analysis.setTooltip("Renders the framerate plot and framerate text");
        _enable_fps_analysis.setValue(true);

        _enable_tear_analysis.setName("Enable tear analysis");
        _enable_tear_analysis.setTooltip("Renders the tears in the framerate plot");
        _enable_tear_analysis.setValue(true);

        _enable_frametime_analysis.setName("Enable frametime analysis");
        _enable_frametime_analysis.setTooltip("Renders the frametime plot");
        _enable_frametime_analysis.setValue(true);

        _enable_delta_rendering.setName("Enable delta rendering");
        _enable_delta_rendering.setTooltip("Renders the difference between two consecutive frames (greyscale)");
        _enable_delta_rendering.setValue(false);

        _framerate_plot_range.setName("Plot range:");
        _framerate_plot_range.setTooltip("Length of the framerate plot in seconds (x-axis)");
        _framerate_plot_range.setValue(60);

        _frametime_plot_range.setName("Plot range:");
        _frametime_plot_range.setTooltip("Length of the frametime plot in seconds (x-axis)");
        _frametime_plot_range.setValue(30);

    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! enables rendering of the images
    CheckBoxItem _enable_view;
    //! TODO
    CheckBoxItem _enable_fps_analysis;
    //! TODO
    CheckBoxItem _enable_tear_analysis;
    //! TODO
    CheckBoxItem _enable_frametime_analysis;
    //! TODO
    CheckBoxItem _enable_delta_rendering;
    //! TODO
    ValueItem<quint8> _framerate_plot_range;
    //! TODO
    ValueItem<quint8> _frametime_plot_range;


};

#endif // GENERALOPTIONSMODEL_H
