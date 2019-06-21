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
        ColorPickNameRole          = Qt::UserRole + 30
      , ColorPickTooltipRole       = Qt::UserRole + 31
      , ColorPickValueRole         = Qt::UserRole + 32
      , PixelDifferenceNameRole    = Qt::UserRole + 33
      , PixelDifferenceTooltipRole = Qt::UserRole + 34
      , PixelDifferenceValueRole   = Qt::UserRole + 35
      , PixelDifferenceEnabledRole = Qt::UserRole + 36
      , DisplayedTextNameRole      = Qt::UserRole + 37
      , DisplayedTextTooltipRole   = Qt::UserRole + 38
      , DisplayedTextValueRole     = Qt::UserRole + 39
      , DisplayedTextFontRole      = Qt::UserRole + 40
      , DisplayedTextEnabledRole   = Qt::UserRole + 41
      , FPSOptionsEnabled          = Qt::UserRole + 42
    };
//! methods
public:
    //! TODO
    Q_SIGNAL void propagateFPSOptions(const QList<FPSOptions> fpsOptionsList);
    //! TODO
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
        int row = index.row();
        switch (role)
        {
            case ColorPickNameRole:
                return _fps_options_list[row].fps_plot_color.name();
            case ColorPickTooltipRole:
                return _fps_options_list[row].fps_plot_color.tooltip();
            case ColorPickValueRole:
                return _fps_options_list[row].fps_plot_color.color();
            case PixelDifferenceNameRole:
                return _fps_options_list[row].pixel_difference.name();
            case PixelDifferenceTooltipRole:
                return _fps_options_list[row].pixel_difference.tooltip();
            case PixelDifferenceValueRole:
                return _fps_options_list[row].pixel_difference.value();
            case PixelDifferenceEnabledRole:
                return _fps_options_list[row].pixel_difference.enabled();
            case DisplayedTextNameRole:
                 return _fps_options_list[row].displayed_text.name();
            case DisplayedTextTooltipRole:
                 return _fps_options_list[row].displayed_text.tooltip();
            case DisplayedTextValueRole:
                 return _fps_options_list[row].displayed_text.value();
            case DisplayedTextFontRole:
                 return _fps_options_list[row].displayed_text.font();
            case DisplayedTextEnabledRole:
                 return _fps_options_list[row].displayed_text.enabled();
            case FPSOptionsEnabled:
                 return _fps_options_list[row].enabled;
            default:
                return QVariant();
        }
    }
    //! QAbstractModel function which is called if an assignment in QML happens
    bool setData(const QModelIndex & index, const QVariant & value, int role) override
    {
        int row = index.row();
        if      (role == ColorPickNameRole)          _fps_options_list[row].fps_plot_color.setName(value.toString());
        else if (role == ColorPickTooltipRole)       _fps_options_list[row].fps_plot_color.setTooltip(value.toString());
        else if (role == ColorPickValueRole)         _fps_options_list[row].fps_plot_color.setColor(value.toString());
        else if (role == PixelDifferenceNameRole)    _fps_options_list[row].pixel_difference.setName(value.toString());
        else if (role == PixelDifferenceTooltipRole) _fps_options_list[row].pixel_difference.setTooltip(value.toString());
        else if (role == PixelDifferenceValueRole)   _fps_options_list[row].pixel_difference.setValue(value.toUInt());
        else if (role == PixelDifferenceEnabledRole) _fps_options_list[row].pixel_difference.setEnabled(value.toBool());
        else if (role == DisplayedTextNameRole)      _fps_options_list[row].displayed_text.setName(value.toString());
        else if (role == DisplayedTextTooltipRole)   _fps_options_list[row].displayed_text.setTooltip(value.toString());
        else if (role == DisplayedTextValueRole)     _fps_options_list[row].displayed_text.setValue(value.toString());
        else if (role == DisplayedTextFontRole)      _fps_options_list[row].displayed_text.setFont(value.value<QFont>());
        else if (role == DisplayedTextEnabledRole)   _fps_options_list[row].displayed_text.setEnabled(value.toBool());
        else if (role == FPSOptionsEnabled)          _fps_options_list[row].enabled = value.toBool();
        else return false;
        QModelIndex toIndex(createIndex(rowCount() - 1, index.column()));
        emit dataChanged(index, toIndex);
        emit propagateFPSOptions(_fps_options_list);
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
    //! apply the pixel difference to all indices
    Q_INVOKABLE void applyColor(const QVariant & value, const int & row)
    {
        QModelIndex q = createIndex(row, 0);
        setData(q, value, ColorPickValueRole);
    }
    //! TODO
    Q_INVOKABLE void revertModelToDefault()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _fps_options_list[id].revert_to_default();
        }
        resetModel();
    }
    //! TODO
    Q_INVOKABLE void updateEnabledRows(const QList<QVariant> filePaths)
    {
        int video_count = filePaths.size();
        for(int i = 0; i < _fps_options_list.size(); ++i)
        {
            const bool loaded_file = i < video_count;
            QModelIndex q = createIndex(i, 0);
            setData(q, loaded_file, FPSOptionsEnabled);
        }
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
        _role_names[PixelDifferenceEnabledRole] = "pixelDifferenceEnabled";

        _role_names[DisplayedTextNameRole]      = "displayedTextName";
        _role_names[DisplayedTextTooltipRole]   = "displayedTextTooltip";
        _role_names[DisplayedTextValueRole]     = "displayedText";
        _role_names[DisplayedTextFontRole]      = "displayedTextFont";
        _role_names[DisplayedTextEnabledRole]   = "displayedTextEnabled";

        _role_names[FPSOptionsEnabled] = "fpsOptionsEnabled";
    }
    //! TODO
    void _init_options()
    {
        for (quint8 id = 0; id < 3; ++id) {
            _fps_options_list.append(FPSOptions(id));
        }
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! TODO
    QList<FPSOptions> _fps_options_list;
};

#endif // FPSOPTIONSMODEL_H
