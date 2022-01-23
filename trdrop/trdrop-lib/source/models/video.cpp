#include "video.h"
#include <iostream>

using namespace trdrop::models;

Video::Video(QObject* parent)
    : QObject(parent)
{
    _format_context = avformat_alloc_context();
    if (!_format_context) {
        qDebug() << "Video::Video - error when allocating _format_context: " << _format_context << '\n';
    }
}

void Video::open_video(QString absolute_path)
{
    qDebug() << "Video::open_video: Trying to open path \"" << absolute_path << "\"\n";

    //const char* new_path = "/home/asa/Documents/github-repos/trdrop/test-videos/kevin-chili-yuv420p-libvpx-vp8.mkv";
    char temp[1000];
    int ret = avformat_open_input(&_format_context, absolute_path.toStdString().c_str(), nullptr, nullptr);
    if (ret != 0) {
        av_strerror(ret, temp, static_cast<size_t>(1000));
        qDebug() << temp;
        qDebug()
            << "Video::open_video: error when opening input \"" << absolute_path << "\": " << ret << '\n';
    }
    if (ret == 0) {
        qDebug() << "File format: " << _format_context->iformat->name << '\n';
    }
}

Video::~Video()
{
    avformat_close_input(&_format_context);
}
