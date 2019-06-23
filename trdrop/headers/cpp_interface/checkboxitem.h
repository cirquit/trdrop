#ifndef CHECKBOXITEM_H
#define CHECKBOXITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//!
class CheckBoxItem
{

//! constructor
public:
    CheckBoxItem()
        : _name("")
        , _tooltip("")
        , _value(false)
    { }

    //! set all member
    CheckBoxItem(QString name
               , QString tooltip
               , bool default_value)
        : _name(name)
        , _tooltip(tooltip)
        , _value(default_value)
    { }

    CheckBoxItem(const CheckBoxItem & other) = default;
    CheckBoxItem & operator=(const CheckBoxItem & other) = default;

//! setter methods
public:
    void setName(const QString & _other){ _name = _other; }
    void setTooltip(const QString & _other){ _tooltip = _other; }
    void setValue(const bool & _other){ _value = _other; }

//! getter methods
public:
    QString name()    const { return _name; }
    QString tooltip() const { return _tooltip; }
    bool    value()   const { return _value; }

//! member
private:
    QString _name;    // name which is shown in the view for the checkbox
    QString _tooltip; // tooltip which is shown on hover over the checkbox / text
    bool    _value;   // checkbox value
};


#endif // CHECKBOXITEM_H
