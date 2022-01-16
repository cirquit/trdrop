#include "test_suite.h"
#include <QDebug>

namespace trdrop {

TestSuite::TestSuite(const QString& _testName)
    : QObject()
    , testName(_testName)
{
    qDebug() << "Creating test suite from" << testName;
    testList().push_back(this);
    qDebug() << testList().size() << "test suite(s) recorded";
    qDebug() << "-------------------------------";
}

TestSuite::~TestSuite()
{
    //qDebug() << "Destroying test suite" << testName;
}

std::vector<TestSuite*>& TestSuite::testList()
{
    static std::vector<TestSuite*> instance = std::vector<TestSuite*>();
    return instance;
}
}
