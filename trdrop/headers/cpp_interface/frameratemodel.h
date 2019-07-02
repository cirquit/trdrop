#ifndef FRAMERATEMODEL_H
#define FRAMERATEMODEL_H

#include <QDebug>
#include <vector>

//! TODO
class FramerateModel
{

//! constructors
public:
    //! TODO
    FramerateModel()
        : _max_video_count(3)
    {
        _init_member();
    }

//! methods
public:
    //! TODO
    void set_framerate_at(quint8 index, double value)
    {
        set_framerate_at(static_cast<size_t>(index), value);
    }
    //! TODO
    void set_framerate_at(int index, double value)
    {
        set_framerate_at(static_cast<size_t>(index), value);
    }
    //! TODO
    void set_framerate_at(size_t index, double value)
    {
        _framerates[index] = value;
    }
    //! TODO
    double get_framerate_at(quint8 index) const
    {
        return get_framerate_at(static_cast<size_t>(index));
    }
    //! TODO
    double get_framerate_at(int index) const
    {
        return get_framerate_at(static_cast<size_t>(index));
    }
    //! TODO
    double get_framerate_at(size_t index) const
    {
        return _framerates[index];
    }
    //! TODO
    void reset_model()
    {
        _init_member();
    }

//! methods
private:
    //! TODO
    void _init_member()
    {
        _framerates.clear();
        for (size_t i = 0; i < _max_video_count; ++i)
        {
            _framerates.push_back(0.0);
        }
    }
private:
    //! TODO
    size_t              _max_video_count;
    //! TODO
    std::vector<double> _framerates;

};

#endif // FRAMERATEMODEL_H
