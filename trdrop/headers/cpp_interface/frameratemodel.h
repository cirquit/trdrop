#ifndef FRAMERATEMODEL_H
#define FRAMERATEMODEL_H

#include <QDebug>
#include <deque>
#include <vector>

//! holds the framerates for all videos + framerate history
class FramerateModel
{
//! constructors
public:
    //! saving the history for at most 180 ticks as we restrict this in the GUI
    FramerateModel()
        : _max_video_count(3)
        , _max_history_ticks(180)
    {
        _init_member();
    }

//! methods
public:
    //! sets the framerate at the video index, removes the oldest value
    void set_framerate_at(const quint8 index, const double value)
    {
        set_framerate_at(static_cast<size_t>(index), value);
    }
    //! sets the framerate at the video index, removes the oldest value
    void set_framerate_at(const int index, const double value)
    {
        set_framerate_at(static_cast<size_t>(index), value);
    }
    //! sets the framerate at the video index, removes the oldest value
    //! we hold the dp
    void set_framerate_at(const size_t index, const double value)
    {
        _framerates[index] = value;
        _framerate_history[index].push_front(value);
        _framerate_history[index].pop_back();
    }
    //! get the current framerate for the video index
    double get_framerate_at_front(const size_t index) const
    {
        return _framerate_history[index].front();
    }
    //! TODO
    std::vector<double> get_framerates() const
    {
        return _framerates;
    }
    //! TODO
    double get_framerate_at(const quint8 index) const
    {
        return get_framerate_at(static_cast<size_t>(index));
    }
    //! TODO
    double get_framerate_at(const int index) const
    {
        return get_framerate_at(static_cast<size_t>(index));
    }
    //! TODO
    double get_framerate_at(const size_t index) const
    {
        return _framerates[index];
    }
    //! TODO
    std::deque<double> get_framerate_history(const size_t index) const
    {
        return _framerate_history[index];
    }
    //! TODO
    double get_max_framerate_bounds() const
    {
        double framerate = 0;
        for (size_t i = 0; i < _max_video_count; ++i)
        {
            const std::deque<double> & framerate_history = get_framerate_history(i);
            auto result = std::max_element(framerate_history.begin(), framerate_history.end());
            if (result == framerate_history.end())
                qDebug() << "FramerateModel::get_max_framerate_bounds() - framerate_history is empty. This should never happen";
            else {
                if (framerate < *result)
                {
                    framerate = *result;
                }
            }
        }
        return framerate;
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
        _framerate_history.clear();
        for (size_t i = 0; i < _max_video_count; ++i)
        {
            _framerates.push_back(0.0);
            _framerate_history.push_back(std::deque<double>(_max_history_ticks, 0.0));
        }
    }

private:
    //! TODO
    const size_t _max_video_count;
    //! how long do we want to save the framerates?
    const size_t _max_history_ticks;
    //! TODO
    std::vector<double> _framerates;
    //! TODO
    std::vector<std::deque<double>> _framerate_history;

};

#endif // FRAMERATEMODEL_H
