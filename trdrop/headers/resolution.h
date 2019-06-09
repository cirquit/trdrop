#ifndef RESOLUTION_H
#define RESOLUTION_H

#include <QSize>
#include <QString>

class Resolution
{
// constructors
public:
    //! TODO
    Resolution(const QSize size)
        : _size(size)
    { }
// methods
public:
    //! TODO
    void setSize(const QSize other){ _size = other; }
    //! TODO
    QSize size() const { return _size; }
    //! TODO
    QString name() const { return QString::number(_size.width()) + "x" + QString::number(_size.height()); }
// member
private:
    //! TODO
    QSize _size;
};


#endif // RESOLUTION_H
