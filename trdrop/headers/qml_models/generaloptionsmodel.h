#ifndef GENERALOPTIONSMODEL_H
#define GENERALOPTIONSMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/cpp_interface/checkboxitem.h"
#include "headers/cpp_interface/valueitem.h"

//! qml wrapper around general options
class GeneralOptionsModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //! initialize the model with #default_items and prepare the role names
    GeneralOptionsModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //! manage the access to FileItem member from QML
    enum GeneralOptionsRoles
    {
        EnableFramerateNameRole             = Qt::UserRole
      , EnableFramerateTooltipRole          = Qt::UserRole + 1
      , EnableFramerateValueRole            = Qt::UserRole + 2
      , EnableTearsNameRole                 = Qt::UserRole + 3
      , EnableTearsTooltipRole              = Qt::UserRole + 4
      , EnableTearsValueRole                = Qt::UserRole + 5
      , EnableFrametimeNameRole             = Qt::UserRole + 6
      , EnableFrametimeTooltipRole          = Qt::UserRole + 7
      , EnableFrametimeValueRole            = Qt::UserRole + 8
      , EnableDeltaRenderingNameRole        = Qt::UserRole + 9
      , EnableDeltaRenderingTooltipRole     = Qt::UserRole + 10
      , EnableDeltaRenderingValueRole       = Qt::UserRole + 11
      , FramerateRangeNameRole              = Qt::UserRole + 12
      , FramerateRangeTooltipRole           = Qt::UserRole + 13
      , FramerateRangeValueRole             = Qt::UserRole + 14
      , FrametimeRangeNameRole              = Qt::UserRole + 15
      , FrametimeRangeTooltipRole           = Qt::UserRole + 16
      , FrametimeRangeValueRole             = Qt::UserRole + 17
      , FramerateMaxFPSNameRole             = Qt::UserRole + 18
      , FramerateMaxFPSTooltipRole          = Qt::UserRole + 19
      , FramerateMaxFPSValueRole            = Qt::UserRole + 20
      , FrametimeMaxMSNameRole              = Qt::UserRole + 21
      , FrametimeMaxMSTooltipRole           = Qt::UserRole + 22
      , FrametimeMaxMSValueRole             = Qt::UserRole + 23
      , EnableFrametimeCenteringNameRole    = Qt::UserRole + 24
      , EnableFrametimeCenteringTooltipRole = Qt::UserRole + 25
      , EnableFrametimeCenteringValueRole   = Qt::UserRole + 26
      , EnableXAxisTextNameRole             = Qt::UserRole + 27
      , EnableXAxisTextTooltipRole          = Qt::UserRole + 28
      , EnableXAxisTextValueRole            = Qt::UserRole + 29
    };
//! methods
public:
    //! row count of our model
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
            case FramerateMaxFPSNameRole:
                return _framerate_max_fps.name();
            case FramerateMaxFPSTooltipRole:
                return _framerate_max_fps.tooltip();
            case FramerateMaxFPSValueRole:
                return _framerate_max_fps.value();
            case FrametimeMaxMSNameRole:
                return _frametime_max_ms.name();
            case FrametimeMaxMSTooltipRole:
                return _frametime_max_ms.tooltip();
            case FrametimeMaxMSValueRole:
                return _frametime_max_ms.value();
            case EnableFrametimeCenteringNameRole:
                return _enable_framerate_centering.name();
            case EnableFrametimeCenteringTooltipRole:
                return _enable_framerate_centering.tooltip();
            case EnableFrametimeCenteringValueRole:
                return _enable_framerate_centering.value();
            case EnableXAxisTextNameRole:
                return _enable_x_axis_text.name();
            case EnableXAxisTextTooltipRole:
                return _enable_x_axis_text.tooltip();
            case EnableXAxisTextValueRole:
                return _enable_x_axis_text.value();
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        Q_UNUSED(index)
        if (role == EnableFramerateValueRole) _enable_fps_analysis.setValue(value.toBool());
        else if (role == EnableTearsValueRole) _enable_tear_analysis.setValue(value.toBool());
        else if (role == EnableFrametimeValueRole) _enable_frametime_analysis.setValue(value.toBool());
        else if (role == EnableDeltaRenderingValueRole) _enable_delta_rendering.setValue(value.toBool());
        else if (role == FramerateRangeValueRole) _framerate_plot_range.setValue(static_cast<int>(value.toUInt()));
        else if (role == FrametimeRangeValueRole) _frametime_plot_range.setValue(static_cast<int>(value.toUInt()));
        else if (role == FramerateMaxFPSValueRole) _framerate_max_fps.setValue(static_cast<int>(value.toUInt()));
        else if (role == FrametimeMaxMSValueRole) _frametime_max_ms.setValue(static_cast<int>(value.toUInt()));
        else if (role == EnableFrametimeCenteringValueRole) _enable_framerate_centering.setValue(value.toBool());
        else if (role == EnableXAxisTextValueRole) _enable_x_axis_text.setValue(value.toBool());
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
    //! inits default options and triggers an update for all "listeners"
    Q_INVOKABLE void revertModelToDefault()
    {
        _init_options();
        resetModel();
    }
    //! getter
    bool get_enable_delta_rendering() { return _enable_delta_rendering.value(); }
    //! getter
    bool get_enable_frametime_analysis() { return _enable_frametime_analysis.value(); }
    //! getter
    bool get_enable_framerate_analysis() { return _enable_fps_analysis.value(); }
    //! getter
    bool get_enable_tear_analysis() { return _enable_tear_analysis.value(); }
    //! getter
    int get_framerate_range() { return _framerate_plot_range.value(); }
    //! getter
    int get_frametime_range() { return _frametime_plot_range.value(); }
    //! getter
    int get_framerate_max_fps() { return _framerate_max_fps.value(); }
    //! getter
    int get_frametime_max_ms() { return _frametime_max_ms.value(); }
    //! getter
    bool get_enable_framerate_centering() { return _enable_framerate_centering.value(); }
    //! getter
    bool get_enable_x_axis_text() { return _enable_x_axis_text.value(); }
//! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[EnableFramerateNameRole]             = "enableFramerateName";
        _role_names[EnableFramerateTooltipRole]          = "enableFramerateTooltip";
        _role_names[EnableFramerateValueRole]            = "enableFramerateValue";
        _role_names[EnableTearsNameRole]                 = "enableTearsName";
        _role_names[EnableTearsTooltipRole]              = "enableTearsTooltip";
        _role_names[EnableTearsValueRole]                = "enableTearsValue";
        _role_names[EnableFrametimeNameRole]             = "enableFrametimeName";
        _role_names[EnableFrametimeTooltipRole]          = "enableFrametimeTooltip";
        _role_names[EnableFrametimeValueRole]            = "enableFrametimeValue";
        _role_names[EnableDeltaRenderingNameRole]        = "enableDeltaRenderingName";
        _role_names[EnableDeltaRenderingTooltipRole]     = "enableDeltaRenderingTooltip";
        _role_names[EnableDeltaRenderingValueRole]       = "enableDeltaRenderingValue";
        _role_names[FramerateRangeNameRole]              = "framerateRangeName";
        _role_names[FramerateRangeTooltipRole]           = "framerateRangeTooltip";
        _role_names[FramerateRangeValueRole]             = "framerateRangeValue";
        _role_names[FrametimeRangeNameRole]              = "frametimeRangeName";
        _role_names[FrametimeRangeTooltipRole]           = "frametimeRangeTooltip";
        _role_names[FrametimeRangeValueRole]             = "frametimeRangeValue";
        _role_names[FramerateMaxFPSNameRole]             = "framerateMaxFPSName";
        _role_names[FramerateMaxFPSTooltipRole]          = "framerateMaxFPSTooltip";
        _role_names[FramerateMaxFPSValueRole]            = "framerateMaxFPSValue";
        _role_names[FrametimeMaxMSNameRole]              = "frametimeMaxMSName";
        _role_names[FrametimeMaxMSTooltipRole]           = "frametimeMaxMSTooltip";
        _role_names[FrametimeMaxMSValueRole]             = "frametimeMaxMSValue";
        _role_names[EnableFrametimeCenteringNameRole]    = "enableFramerateCenteringName";
        _role_names[EnableFrametimeCenteringTooltipRole] = "enableFramerateCenteringTooltip";
        _role_names[EnableFrametimeCenteringValueRole]   = "enableFramerateCenteringValue";
        _role_names[EnableXAxisTextNameRole]             = "enableXAxisTextName";
        _role_names[EnableXAxisTextTooltipRole]          = "enableXAxisTextTooltip";
        _role_names[EnableXAxisTextValueRole]            = "enableXAxisTextValue";
    }
    //! initial setting
    void _init_options()
    {
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

        _framerate_plot_range.setName("Analysis range:");
        _framerate_plot_range.setTooltip("Length of the framerate plot in frames (x-axis)");
        _framerate_plot_range.setValue(60);

        _framerate_max_fps.setName("Max FPS:");
        _framerate_max_fps.setTooltip("Height of the framerate plot in framerate (y-axis)");
        _framerate_max_fps.setValue(60);

        _frametime_plot_range.setName("Analysis range:");
        _frametime_plot_range.setTooltip("Length of the frametime plot in frames (x-axis)");
        _frametime_plot_range.setValue(60);

        _frametime_max_ms.setName("Max Frametime:");
        _frametime_max_ms.setTooltip("Height of the frametime plot in ms (y-axis)");
        _frametime_max_ms.setValue(100);

        _enable_framerate_centering.setName("Enable FPS graph centering");
        _enable_framerate_centering.setTooltip("The center of the framerate plot is now showing the \"current\" framerate, not the right most edge");
        _enable_framerate_centering.setValue(false);

        _enable_x_axis_text.setName("Enable framerate analysis range text");
        _enable_x_axis_text.setTooltip("Draws the framerate anaylsis range text below the framerate plot");
        _enable_x_axis_text.setValue(true);
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! essentially a bool
    CheckBoxItem _enable_fps_analysis;
    //! essentially a bool
    CheckBoxItem _enable_tear_analysis;
    //! essentially a bool
    CheckBoxItem _enable_frametime_analysis;
    //! essentially a bool
    CheckBoxItem _enable_delta_rendering;
    //! wrapped int
    ValueItem<int> _framerate_plot_range;
    //! wrapped int
    ValueItem<int> _framerate_max_fps;
    //! wrapped int
    ValueItem<int> _frametime_plot_range;
    //! wrapped int
    ValueItem<int> _frametime_max_ms;
    //! essentially a bool
    CheckBoxItem _enable_framerate_centering;
    //! essentially a bool
    CheckBoxItem _enable_x_axis_text;
};

#endif // GENERALOPTIONSMODEL_H
