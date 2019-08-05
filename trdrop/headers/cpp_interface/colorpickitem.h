#ifndef COLORPICKITEM_H
#define COLORPICKITEM_H

#include <QObject>
#include <QString>
#include <QInternal>

//! a wrapper around a QString value which is a hex-code for QColor (TODO) with name and tooltip parameters
class ColorPickItem
{

//! constructor
public:
    //! default constructor
    ColorPickItem()
        : _name("")
        , _tooltip("")
        , _color("#FFFFFF")
    { }
    //! set members manually
    ColorPickItem(QString name
                , QString tooltip
                , QString color)
        : _name(name)
        , _tooltip(tooltip)
        , _color(color)
    { }
    //! copy constructor
    ColorPickItem(const ColorPickItem & other) = default;
    //! assignment operator
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
    //! name which is shown in the view for the checkbox
    QString _name;
    //! tooltip which is shown on hover over the checkbox / text
    QString _tooltip;
    //! color value as hex -> #FFFFFF
    QString _color;
};



#endif // COLORPICKITEM_H
