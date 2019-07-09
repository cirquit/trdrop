#ifndef RESOLUTION_H
#define RESOLUTION_H

#include <QSize>
#include <QString>

class Resolution
{
// constructors
public:
    //! TODO
    Resolution(const QSize size, const bool enabled)
        : _size(size)
        , _enabled(enabled)
    { }
// methods
public:
    //! TODO
    void setSize(const QSize other){ _size = other; }
    //! TODO
    QSize size() const { return _size; }
    //! TODO
    void setEnabled(const bool other){ _enabled = other; }
    //! TODO
    bool enabled() const { return _enabled; }
    //! TODO
    QString name() const { return QString::number(_size.width()) + "x" + QString::number(_size.height()); }
// member
private:
    //! TODO
    QSize _size;
    //! TODO
    bool _enabled;

};


#endif // RESOLUTION_H
