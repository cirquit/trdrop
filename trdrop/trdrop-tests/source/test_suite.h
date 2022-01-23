#pragma once

#include <QObject>
#include <QString>
#include <QtTest/QtTest>
#include <vector>

namespace trdrop {

class TestSuite : public QObject {
    Q_OBJECT
public:
    explicit TestSuite(const QString& _test_name = "");
    virtual ~TestSuite();
    QString test_name;
    static std::vector<TestSuite*>& test_list();
};
}
