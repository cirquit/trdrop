#ifndef ANIMALMODEL_H
#define ANIMALMODEL_H

#include <QAbstractListModel>
#include <QStringList>
#include <qqmlcontext.h>
#include "animal.h"
#include <QDebug>

//!
class AnimalModel : public QAbstractListModel
{
    Q_OBJECT

public:

    Q_INVOKABLE void addDefault()  {

      m_animals.append(Animal());
      qDebug() << m_animals.size() << '\n';
      QModelIndex topLeft = createIndex(0,m_animals.size());
      //emit dataChanged(topLeft, topLeft);
      // emit rowsInserted(topLeft, 0, 0, nullptr);
     }

    void setName(const QString &name);
    enum AnimalRoles {
        TypeRole = Qt::UserRole + 1,
        SizeRole
    };

    AnimalModel(QObject *parent = nullptr)
        : QAbstractListModel(parent)
    {
    }


    void setContext(QQmlContext *ctx) {
        m_ctx = ctx;
    }


    void addAnimal(const Animal &animal)
    {
        //beginInsertRows(QModelIndex(), rowCount(), rowCount());
        m_animals << animal;
        //endInsertRows();
    }

    int rowCount(const QModelIndex & parent) const {
        Q_UNUSED(parent);
        return m_animals.count();
    }

    QVariant data(const QModelIndex & index, int role) const {
        if (index.row() < 0 || index.row() >= m_animals.count())
            return QVariant();

        const Animal &animal = m_animals[index.row()];
        if (role == TypeRole)
            return animal.type();
        else if (role == SizeRole)
            return animal.size();
        return QVariant();
    }

    QHash<int, QByteArray> roleNames() const {
        QHash<int, QByteArray> roles;
        roles[TypeRole] = "type";
        roles[SizeRole] = "size";
        return roles;
    }

private:
    QList<Animal> m_animals;
    QQmlContext*  m_ctx;

};

#endif // ANIMALMODEL_H
