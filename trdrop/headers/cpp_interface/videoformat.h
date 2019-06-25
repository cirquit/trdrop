#ifndef VIDEOFORMAT_H
#define VIDEOFORMAT_H

#include <QtDebug>
#include <QString>

//! TODO
enum VideoFormatType
{
    AVI = 0
  , MP4 = 1
};

//! TODO
class VideoFormat
{
// constructors
public:
    //! TODO
    VideoFormat(const VideoFormatType videoformat_type)
        : _videoformat_type(videoformat_type)
    { }
// methods
public:
    //! TODO
    VideoFormatType value() const { return _videoformat_type; }
    //! TODO
    QString name() const {
        switch (_videoformat_type) {
            case AVI:
                return ".avi";
            case MP4:
                return ".mp4";
            default:
                qDebug() << "VideoFormat::name() was called with unknown VideoFormatType " << _videoformat_type << ", using .mp4";
                return ".mp4";
        }
    }
// member
private:
    //! TODO
    VideoFormatType _videoformat_type;
};


#endif // VIDEOFORMAT_H
