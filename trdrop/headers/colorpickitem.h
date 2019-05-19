#ifndef COLORPICKITEM_H
#define COLORPICKITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//!
class ColorPickItem
{

//! constructor
public:
    //! TODO
    ColorPickItem()
        : _name("")
        , _tooltip("")
        , _color("#FFFFFF")
    { }

    //! set all member
    ColorPickItem(QString name
                , QString tooltip
                , QString color)
        : _name(name)
        , _tooltip(tooltip)
        , _color(color)
    { }

    ColorPickItem(const ColorPickItem & other) = default;
    ColorPickItem & operator=(const ColorPickItem & other) = default;

//! setter methods
public:
    void setName(const QString & _other){ _name = _other; }
    void setTooltip(const QString & _other){ _tooltip = _other; }
    void setColor(const QString & _other){ _color = _other; }

//! getter methods
public:
    QString name()    const { return _name; }
    QString tooltip() const { return _tooltip; }
    QString color()   const { return _color; }

//! member
private:
    QString _name;    // name which is shown in the view for the checkbox
    QString _tooltip; // tooltip which is shown on hover over the checkbox / text
    QString _color;   // color value as hex -> #FFFFFF
};



#endif // COLORPICKITEM_H
