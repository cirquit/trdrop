#ifndef FILEITEMLIST_H
#define FILEITEMLIST_H
#include <QAbstractListModel>
#include <QStandardItemModel>
#include <QDebug>
#include "fileitem.h"

//! TODO
class FileItemList : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QAbstractItemModel* model READ model CONSTANT)
    Q_DISABLE_COPY(FileItemList)

//! constructor
public:
    //! main constructor
    FileItemList(QObject* parent = nullptr)
        : QObject(parent)
    {
        _model = new QStandardItemModel(this);
        _model->insertColumn(0);
        _add_default_elements();
    }
    // TODO destructor for _model (?)

//! methods
public:
    //! adds a default fileitem
    Q_SLOT void addDefaultFileItem()
    {
        const FileItem file_item;
        _add_file_item(file_item);
    }

    //! a custom get function to access another elements properties by row index
    Q_SLOT QVariant get(int row_index)
    {
        return _model->data(
                    _model->index(row_index, 0));
    }

    //! open the file and do stuff later
    Q_SLOT void openFile(int index, QString filename)
    {
        qDebug() << index << ", " << filename << '\n';
        // open file and do stuff and verify if
    }

    //! remove the item at the index from the model
    Q_SLOT void removeItem(int index)
    {
        _model->removeRow(index);
    }

//! getter methods for Q_PROPERTY
public:
    //! model getter
    QAbstractItemModel * model() const { return _model;}

//! methods
private:
    //! add file item object
    void _add_file_item(const FileItem & file_item)
    {
        const int newRow = _model->rowCount();
        _model->insertRow(newRow);
        _model->setData(_model->index(newRow,0)
                      , QVariant::fromValue(file_item)
                      , Qt::EditRole);
    }

    //! add three default items
    void _add_default_elements()
    {
        addDefaultFileItem();
        addDefaultFileItem();
        addDefaultFileItem();
    }

//! member
private:
    //! the model which is used by a QML ListView
    QAbstractItemModel * _model;
};
#endif // FILEITEMLIST_H
