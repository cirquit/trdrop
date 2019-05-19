#ifndef VALUEITEM_H
#define VALUEITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//!
class ValueItem
{

//! constructor
public:
    //! TODO
    ValueItem()
        : _name("")
        , _tooltip("")
        , _value(0)
    { }

    //! set all member
    ValueItem(QString name
            , QString tooltip
            , quint64 value)
        : _name(name)
        , _tooltip(tooltip)
        , _value(value)
    { }

    ValueItem(const ValueItem & other) = default;
    ValueItem & operator=(const ValueItem & other) = default;

//! setter methods
public:
    void setName(const QString & _other){ _name = _other; }
    void setTooltip(const QString & _other){ _tooltip = _other; }
    void setValue(const quint64 & _other){ _value = _other; }

//! getter methods
public:
    QString name()    const { return _name; }
    QString tooltip() const { return _tooltip; }
    quint64 value()   const { return _value; }

//! member
private:
    QString _name;    // name which is shown in the view for the checkbox
    QString _tooltip; // tooltip which is shown on hover over the checkbox / text
    quint64 _value;   // value
};


#endif // VALUEITEM_H
