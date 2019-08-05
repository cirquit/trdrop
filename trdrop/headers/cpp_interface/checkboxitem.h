#ifndef CHECKBOXITEM_H
#define CHECKBOXITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//! a wrapper around a bool value with name and tooltip parameters
class CheckBoxItem
{
//! constructor
public:
    //! default constructor
    CheckBoxItem()
        : _name("")
        , _tooltip("")
        , _value(false)
    { }
    //! set members manually
    CheckBoxItem(QString name
               , QString tooltip
               , bool default_value)
        : _name(name)
        , _tooltip(tooltip)
        , _value(default_value)
    { }
    //! copy constructor
    CheckBoxItem(const CheckBoxItem & other) = default;
    //! assignment operator
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
    //! name which is shown in the view for the checkbox
    QString _name;
    //! tooltip which is shown on hover over the checkbox / text
    QString _tooltip;
    //! checkbox value
    bool    _value;
};


#endif // CHECKBOXITEM_H
