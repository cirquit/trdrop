#ifndef IMAGEFORMAT_H
#define IMAGEFORMAT_H

#include <QtDebug>
#include <QString>

//! TODO
enum ImageFormatType
{
    JPEG = 0
  , PNG  = 1
};

//! TODO
class ImageFormat
{
// constructors
public:
    //! TODO
    ImageFormat(const ImageFormatType imageformat_type)
        : _imageformat_type(imageformat_type)
    { }
// methods
public:
    //! TODO
    ImageFormatType value() const { return _imageformat_type; }
    //! TODO
    QString name() const {
        switch (_imageformat_type) {
            case JPEG:
                return ".jpg";
            case PNG:
                return ".png";
            default:
                qDebug() << "ImageFormat::name() was called with unknown ImageFormatType " << _imageformat_type << ", using .jpg";
                return ".jpg";
        }
    }
// member
private:
    //! TODO
    ImageFormatType _imageformat_type;
};

#endif // IMAGEFORMAT_H
