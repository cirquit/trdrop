#pragma once

#include <QObject>
#include <QString>
#include <QtTest/QtTest>
#include <vector>

namespace trdrop {

class TestSuite : public QObject {
    Q_OBJECT
public:
    explicit TestSuite(const QString& _testName = "");
    virtual ~TestSuite();
    QString testName;
    static std::vector<TestSuite*>& testList();
};
}
