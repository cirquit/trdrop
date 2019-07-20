#ifndef FRAMETIMEMODEL_H
#define FRAMETIMEMODEL_H

#include <QDebug>
#include <deque>
#include <vector>

//! TODO
class FrametimeModel
{

//! constructors
public:
    //! Holds the frametime information
    //! saving the history for 180 ticks as we restrict this in the GUI
    FrametimeModel()
        : _max_video_count(3)
        , _max_history_ticks(180)
    {
        _init_member();
    }

//! methods
public:
    //! TODO
    void set_frametime_at(const quint8 index, const double value)
    {
        set_frametime_at(static_cast<size_t>(index), value);
    }
    //! TODO
    void set_frametime_at(const int index, const double value)
    {
        set_frametime_at(static_cast<size_t>(index), value);
    }
    //! TODO
    void set_frametime_at(const size_t index, const double value)
    {
        _frametimes[index] = value;
        _frametime_history[index].push_front(value);
        _frametime_history[index].pop_back();
    }
    //! TODO
    double get_frametime_at(const quint8 index) const
    {
        return get_frametime_at(static_cast<size_t>(index));
    }
    //! TODO
    double get_frametime_at(const int index) const
    {
        return get_frametime_at(static_cast<size_t>(index));
    }
    //! TODO
    double get_frametime_at(const size_t index) const
    {
        return _frametimes[index];
    }
    //! TODO
    std::deque<double> get_frametime_history(const size_t index) const
    {
        return _frametime_history[index];
    }
    //! TODO
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
        _frametimes.clear();
        _frametime_history.clear();
        for (size_t i = 0; i < _max_video_count; ++i)
        {
            _frametimes.push_back(0.0);
            _frametime_history.push_back(std::deque<double>(_max_history_ticks, 0.0));
        }
    }

private:
    //! TODO
    size_t              _max_video_count;
    //! how long do we want to save the frametimes?
    const size_t _max_history_ticks;
    //! TODO
    std::vector<double> _frametimes;
    //! TODO
    std::vector<std::deque<double>> _frametime_history;

};

#endif // FRAMETIMEMODEL_H
