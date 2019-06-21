#ifndef EXPORT_QML_H
#define EXPORT_QML_H

#include <QObject>
#include <QPainter>
#include <QStyleOptionGraphicsItem>
#include <QQuickPaintedItem>

class ExportQML : public QObject
{
    Q_OBJECT

public:
    ExportQML(QObject * parent = nullptr)
        : QObject(parent)
    { }

    //! TODO
    Q_INVOKABLE void save(QQuickPaintedItem *item)
    {
        if (item->width() == 0) return;
        QPixmap pix(static_cast<int>(item->width())
                  , static_cast<int>(item->height()));
        QPainter painter(&pix);
        QStyleOptionGraphicsItem option;
        item->paint(&painter);
        pix.save("blub_01.png");
    }
};

#endif // EXPORT_QML_H
