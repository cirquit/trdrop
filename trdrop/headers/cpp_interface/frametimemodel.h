#ifndef FRAMETIMEMODEL_H
#define FRAMETIMEMODEL_H

#include <QDebug>
#include <deque>
#include <vector>

//! holds the frametimes for all videos + history
class FrametimeModel
{
//! constructors
public:
    //! holds the frametime information
    //! saving the history for 180 ticks as we restrict this in the GUI
    FrametimeModel()
        : _max_video_count(3)
        , _max_history_ticks(180)
    {
        _init_member();
    }

//! methods
public:
    //! sets the frametime at the video index, removes the oldest value
    void set_frametime_at(const quint8 index, const double value)
    {
        set_frametime_at(static_cast<size_t>(index), value);
    }
    //! sets the frametime at the video index, removes the oldest value
    void set_frametime_at(const int index, const double value)
    {
        set_frametime_at(static_cast<size_t>(index), value);
    }
    //! sets the frametime at the video index, removes the oldest value
    void set_frametime_at(const size_t index, const double value)
    {
        _frametimes[index] = value;
        _frametime_history[index].push_front(value);
        _frametime_history[index].pop_back();
    }
    //! returns all current frametimes for each video
    std::vector<double> get_frametimes() const
    {
        return _frametimes;
    }
    //! get the current frametime for the video index
    double get_frametime_at(const quint8 index) const
    {
        return get_frametime_at(static_cast<size_t>(index));
    }
    //! get the current frametime for the video index
    double get_frametime_at(const int index) const
    {
        return get_frametime_at(static_cast<size_t>(index));
    }
    //! get the current frametime for the video index
    double get_frametime_at(const size_t index) const
    {
        return _frametimes[index];
    }
    //! returns the full framerate history for a video index
    std::deque<double> get_frametime_history(const size_t index) const
    {
        return _frametime_history[index];
    }
    //! get the maximum frametime over all videos
    double get_max_frametime_bounds() const
    {
        double frametime = 0;
        for (size_t i = 0; i < _max_video_count; ++i)
        {
            const std::deque<double> & frametime_history = get_frametime_history(i);
            auto result = std::max_element(frametime_history.begin(), frametime_history.end());
            if (result == frametime_history.end())
                qDebug() << "FrametimeModel::get_max_frametime_bounds() - frametime_history is empty. This should never happen";
            else {
                if (frametime < *result)
                {
                    frametime = *result;
                }
            }
        }
        return frametime;
    }
    //! resets the model to the initial configuration
    void reset_model()
    {
        _init_member();
    }
//! methods
private:
    //! initial configuration (nulled)
    void _init_member()
    {
        _frametimes.clear();
        _frametime_history.clear();
        for (size_t i = 0; i < _max_video_count; ++i)
        {
            _frametimes.push_back(0.0);
            _frametime_history.push_back(std::deque<double>(_max_history_ticks, 0.0));
        }
    }

private:
    //! maximum amount of videos we can process
    size_t              _max_video_count;
    //! how long do we want to save the framerates
    const size_t _max_history_ticks;
    //! holds the current frametimes for each video
    std::vector<double> _frametimes;
    //! all frametime histories, accessable by video index
    std::vector<std::deque<double>> _frametime_history;

};

#endif // FRAMETIMEMODEL_H
