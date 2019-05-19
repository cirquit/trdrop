#ifndef TEXTEDITITEM_H
#define TEXTEDITITEM_H


#include <QObject>
#include <QString>
#include <QFont>
#include <QInternal>

//! TODO
class TextEditItem
{

//! constructor
public:
    //! TODO
    TextEditItem()
        : _name("")
        , _tooltip("")
        , _value("")
        , _font(QFont())
        , _enabled(true)
    { }

    //! set all member
    TextEditItem(QString name
            , QString tooltip
            , QString value
            , QFont font
            , bool enabled)
        : _name(name)
        , _tooltip(tooltip)
        , _value(value)
        , _font(font)
        , _enabled(enabled)
    { }

    TextEditItem(const TextEditItem & other) = default;
    TextEditItem & operator=(const TextEditItem & other) = default;

//! setter methods
public:
    void setName(const QString & _other){ _name = _other; }
    void setTooltip(const QString & _other){ _tooltip = _other; }
    void setValue(const QString & _other){ _value = _other; }
    void setFont(const QFont & _other){ _font = _other; }
    void setEnabled(const bool & _other){ _enabled = _other; }

//! getter methods
public:
    QString name()    const { return _name; }
    QString tooltip() const { return _tooltip; }
    QString value()   const { return _value; }
    QFont   font()    const { return _font; }
    bool    enabled() const { return _enabled; }

//! member
private:
    QString _name;    // name which is shown in the view for the checkbox
    QString _tooltip; // tooltip which is shown on hover over the checkbox / text
    QString _value;   // text
    QFont   _font;    // font of the text
    bool    _enabled; // is this item enabled (possibly used for visible)
};



#endif // TEXTEDITITEM_H
