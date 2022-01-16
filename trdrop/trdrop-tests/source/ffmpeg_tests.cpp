#include "ffmpeg_tests.h"

namespace trdrop {

static FFMPEGTests instance;

FFMPEGTests::FFMPEGTests()
    : TestSuite("FFMPEGTests")
{
}

void FFMPEGTests::initTestCase()
{
}

void FFMPEGTests::cleanupTestCase()
{
}

void FFMPEGTests::init()
{
}

void FFMPEGTests::cleanup()
{
}

void FFMPEGTests::instantiating_FFMPEGTests_returnsCorrectly()
{
    QCOMPARE(true, false);
}

void FFMPEGTests::exampleMath_returnsIncorrectly()
{
    QCOMPARE(1 + 1, 3);
}

void FFMPEGTests::exampleMath_returnsCorrectly()
{
    QCOMPARE(1 + 1, 2);
}
}
