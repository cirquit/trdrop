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

bool Video::open_video(QString absolute_path)
{
    int ret = avformat_open_input(&_format_context, absolute_path.toStdString().c_str(), nullptr, nullptr);
    if (ret != 0) {
        qDebug()
            << "Video::open_video: error when opening video:\n"
            << "  - path:" << absolute_path << "\n"
            << "  - error code:" << ret << '\n'
            << "  - ffmpeg code error:" << QString::fromStdString(av_err2string(ret)) << '\n';
    }
    return ret == 0;
}

Video::~Video()
{
    avformat_close_input(&_format_context);
}
