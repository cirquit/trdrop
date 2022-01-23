#pragma once

#include <QtTest>
#include <test_suite.h>

#include <models/video.h>

namespace trdrop {

class FFMPEGTests : public TestSuite {
    Q_OBJECT

public:
    FFMPEGTests();

private slots:
    /// @brief Called before the first test function is executed
    void init_test_case();
    /// @brief Called after the last test function was executed
    void cleanup_test_case();
    /// @brief Called before each test function is executed
    void init();
    /// @brief Called after every test function is executed
    void cleanup();

private slots:
    void init_Video_class_without_errors();
    void open_video_without_errors();
};
}
