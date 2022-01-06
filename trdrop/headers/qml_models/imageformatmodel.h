#ifndef IMAGEFORMATMODEL_H
#define IMAGEFORMATMODEL_H

#include <QAbstractTableModel>
#include <QDebug>
#include "headers/cpp_interface/imageformat.h"

//! qml model wrapper for imageformat
class ImageFormatModel : public QAbstractListModel
{
    Q_OBJECT
//! constructors
public:
    //! default constructor
    ImageFormatModel(QObject * parent = nullptr)
        : QAbstractListModel(parent)
    {
        _init_options();
        _setup_role_names();
    }
    //! role names
    enum ImageFormatModelRoles
    {
        ImageFormatNameRole  = Qt::UserRole + 70
      , ImageFormatValueRole = Qt::UserRole + 71
    };
//! methods
public:
    //! number of possible imageformats
    int rowCount(const QModelIndex & parent = QModelIndex()) const override
    {
        Q_UNUSED(parent)
        return _imageformat_list.size();
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
            case ImageFormatNameRole:
                return _imageformat_list[row].name();
            case ImageFormatValueRole:
                return _imageformat_list[row].value();
            default:
                return QVariant();
        }
    }
    //! tells the views that the model's state has changed, triggers a recomputation of each delegate
    Q_INVOKABLE void resetModel()
    {
        beginResetModel();
        endResetModel();
    }
    //! need this to make drop-down lists work (enabled signalizes the "current" options)
    Q_INVOKABLE void setActiveValueAt(const int & row)
    {
        for (int i = 0; i < _imageformat_list.size(); ++i)
        {
            bool enabled = i == row;
            _imageformat_list[i].setEnabled(enabled);
        }
    }
    //! need this to set the active value on the load, cause the ComboBox accesses data() with row 0 on startup, without checking the enabled values
    Q_INVOKABLE QVariant getActiveValueIndex()
    {
        for (int i = 0; i < _imageformat_list.size(); ++i) {
            if (_imageformat_list[i].enabled())
            {
                int row = i;
                return row;
            }
        }
        qDebug() << "ImageFormatModel::getActiveValueIndex() - no resolution selected, this should never happen. Returning first element";
        return 0;
    }

    //! get the currently selected option
    ImageFormat get_active_value()
    {
        for (int i = 0; i < _imageformat_list.size(); ++i) {
            if (_imageformat_list[i].enabled())
            {
                return _imageformat_list[i];
            }
        }
        qDebug() << "ImageFormatModel::getActiveValue() - no imageformat selected, this should never happen. Returning first element";
        return _imageformat_list[0];
    }
    //! methods
private:
    //! Set names to the role name hash container (QHash<int, QByteArray>)
    void _setup_role_names()
    {
        _role_names[ImageFormatNameRole]  = "imageFormatName";
        _role_names[ImageFormatValueRole] = "imageFormatValue";
   }
    //! initial setting (jpg is default)
    void _init_options()
    {
        _imageformat_list.push_back(ImageFormat(ImageFormatType::JPEG, true));
        _imageformat_list.push_back(ImageFormat(ImageFormatType::TIFF, false));
    }

//! member
private:
    //! used by the QAbstractListModel to save the role names from QML
    QHash<int, QByteArray> _role_names;
    //! the "model"
    QList<ImageFormat> _imageformat_list;
};

#endif // IMAGEFORMATMODEL_H
