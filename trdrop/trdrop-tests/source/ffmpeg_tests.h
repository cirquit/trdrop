#pragma once

#include <QtTest>

#include <test_suite.h>

namespace trdrop {

class FFMPEGTests : public TestSuite {
    Q_OBJECT

public:
    FFMPEGTests();

private slots:
    /// @brief Called before the first test function is executed
    void initTestCase();
    /// @brief Called after the last test function was executed
    void cleanupTestCase();
    /// @brief Called before each test function is executed
    void init();
    /// @brief Called after every test function is executed
    void cleanup();

private slots:
    void instantiating_FFMPEGTests_returnsCorrectly();
    void exampleMath_returnsCorrectly();
    void exampleMath_returnsIncorrectly();
};
}
