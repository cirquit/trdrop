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

// added macro to replace a C function with a C++ equivalent, as it does not compile with g++
// see this link: https://github.com/joncampbell123/composite-video-simulator/issues/5
#ifdef av_err2str
#undef av_err2str
#include <string>
av_always_inline std::string av_err2string(int errnum)
{
    char str[AV_ERROR_MAX_STRING_SIZE];
    return av_make_error_string(str, AV_ERROR_MAX_STRING_SIZE, errnum);
}
#define av_err2str(err) av_err2string(err).c_str()
#endif // av_err2str

namespace trdrop {
namespace models {

class TRDROPLIB_EXPORT Video : public QObject {
    Q_OBJECT
public:
    explicit Video(QObject* parent = nullptr);
    ~Video() override;

public:
    /// @brief Fills the header information of the video container into the `format_context` member
    /// Returns true for successful opening, false for a failure
    /// qDebug is populate in case of failure
    bool open_video(QString absolute_path);

public:
    /// @brief holds the header information of the video container
    AVFormatContext* _format_context = nullptr;
};
}
}
