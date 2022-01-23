#pragma once

#include <QDebug>
#include <QObject>
#include <trdrop-lib_global.h>

extern "C" {
#include <libavcodec/avcodec.h>
#include <libavdevice/avdevice.h>
#include <libavfilter/avfilter.h>
#include <libavfilter/buffersink.h>
#include <libavfilter/buffersrc.h>
#include <libavformat/avformat.h>
#include <libavutil/audio_fifo.h>
#include <libavutil/imgutils.h>
#include <libavutil/opt.h>
#include <libavutil/timestamp.h>
#include <libswresample/swresample.h>
#include <libswscale/swscale.h>
}

namespace trdrop {
namespace models {

class TRDROPLIB_EXPORT Video : public QObject {
    Q_OBJECT
public:
    explicit Video(QObject* parent = nullptr);
    ~Video() override;

public:
    /// @brief Fills the header information of the video container into the `format_context` member
    void open_video(QString absolute_path);

public:
    /// @brief holds the header information of the video container
    AVFormatContext* _format_context = nullptr;
};
}
}
