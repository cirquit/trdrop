#ifndef IMAGEFORMAT_H
#define IMAGEFORMAT_H

#include <QtDebug>
#include <QString>

//! enumerating our supported formats
enum ImageFormatType
{
    JPEG = 0
  , PNG  = 1
  , TIFF = 2
  , BMP  = 3
};

//! image format wrapper for qml dropdown and enum <-> string convertion
class ImageFormat
{
// constructors
public:
    //! default constructor
    ImageFormat(const ImageFormatType imageformat_type
              , bool enabled)
        : _imageformat_type(imageformat_type)
        , _enabled(enabled)
    { }
// methods
public:
    //! returns the enum
    ImageFormatType value() const { return _imageformat_type; }
    //! convertion between enum <-> string
    QString name() const {
        switch (_imageformat_type) {
            case JPEG:
                return ".jpg";
            case PNG:
                return ".png";
            case TIFF:
                return ".tiff";
            case BMP:
                return ".bmp";
            default:
                qDebug() << "ImageFormat::name() was called with unknown ImageFormatType " << _imageformat_type << ", using .jpg";
                return ".jpg";
        }
    }
    //! getter
    bool enabled() const { return _enabled; }
    //! setter
    void setEnabled(bool other){ _enabled = other; }

// member
private:
    //! current value
    ImageFormatType _imageformat_type;
    //! used to save the currently selected value in the dropdown list (QML), managed from outside
    bool            _enabled;
};

#endif // IMAGEFORMAT_H
