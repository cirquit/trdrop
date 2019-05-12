#ifndef ANIMAL_H
#define ANIMAL_H

#include <QString>

//!
class Animal
{
public:
    Animal(const QString &type, const QString &size)
        : m_type(type), m_size(size)
    { }

    Animal()
        : m_type("Test")
        , m_size("10")
    { }

    QString type() const { return m_type; }

    QString size() const { return m_size; }

    void setType(QString q) {
        m_type = q;
    }

private:
    QString m_type;
    QString m_size;
};




#endif // ANIMAL_H
