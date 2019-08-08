#ifndef VALUEITEM_H
#define VALUEITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//! QML wrapper around any value
template <typename VALUE>
class ValueItem
{

//! constructor
public:
    //! default init
    ValueItem()
        : _name("")
        , _tooltip("")
        , _value(VALUE())
        , _enabled(true)
    { }

    //! manual init
    ValueItem(QString name
            , QString tooltip
            , VALUE value
            , bool enabled)
        : _name(name)
        , _tooltip(tooltip)
        , _value(value)
        , _enabled(enabled)
    { }
    //! copy + assign constructors
    ValueItem(const ValueItem & other) = default;
    ValueItem & operator=(const ValueItem & other) = default;

//! setter methods
public:
    void setName(const QString & _other){ _name = _other; }
    void setTooltip(const QString & _other){ _tooltip = _other; }
    void setValue(const VALUE & _other){ _value = _other; }
    void setEnabled(const bool & _other){ _enabled = _other; }

//! getter methods
public:
    QString name()    const { return _name; }
    QString tooltip() const { return _tooltip; }
    VALUE   value()   const { return _value; }
    bool    enabled() const { return _enabled; }

//! member
private:
    QString _name;    // name which is shown in the view for the checkbox
    QString _tooltip; // tooltip which is shown on hover over the checkbox / text
    VALUE   _value;   // value
    bool    _enabled; // is this item enabled (possibly used for visible)
};


#endif // VALUEITEM_H
