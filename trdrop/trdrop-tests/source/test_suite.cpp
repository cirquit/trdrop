#include "test_suite.h"
#include <QDebug>

namespace trdrop {

TestSuite::TestSuite(const QString& _test_name)
    : QObject()
    , test_name(_test_name)
{
    qDebug() << "Creating test suite from" << test_name;
    test_list().push_back(this);
    qDebug() << test_list().size() << "test suite(s) recorded";
    qDebug() << "-------------------------------";
}

TestSuite::~TestSuite()
{
    //qDebug() << "Destroying test suite" << testName;
}

std::vector<TestSuite*>& TestSuite::test_list()
{
    static std::vector<TestSuite*> instance = std::vector<TestSuite*>();
    return instance;
}
}
