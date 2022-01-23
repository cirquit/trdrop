#include "ffmpeg_tests.h"

namespace trdrop {

static FFMPEGTests instance;

FFMPEGTests::FFMPEGTests()
    : TestSuite("FFMPEGTests")
{
}

void FFMPEGTests::init_test_case()
{
}

void FFMPEGTests::cleanup_test_case()
{
}

void FFMPEGTests::init()
{
}

void FFMPEGTests::cleanup()
{
}

void FFMPEGTests::init_Video_class_without_errors()
{
    models::Video video;
    QCOMPARE(static_cast<bool>(video._format_context), true);
}

void FFMPEGTests::open_video_without_errors()
{
    models::Video video;
    QString test_video_directory = QString::fromUtf8(std::getenv("TRDROP_TEST_VIDEO_DIRECTORY"));
    QString video_01 = "kevin-chili-yuv420p-libx264.mp4";
    QDir video_01_absolute_path = QDir::cleanPath(test_video_directory + QDir::separator() + video_01);
    video.open_video(video_01_absolute_path.path());
}
}
