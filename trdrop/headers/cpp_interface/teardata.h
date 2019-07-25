#ifndef TEAR_DATA_H
#define TEAR_DATA_H

#include <vector>
#include <QDebug>
#include <QObject>

//! wrapper for everything which defines tears for a single frame
class TearData
{
// constructors
public:
    //! initialized with the maximum frame_row_count
    TearData(size_t frame_row_count)
        : _frame_row_count(frame_row_count)
    { }

// methods
public:
    //! getter
    std::vector<quint64> get_tear_rows() const { return _tear_rows; }
    //! explicit copy
    void set_tear_rows(const std::vector<quint64> _other) { _tear_rows = _other; }
    //! returns a percentage between 0 and 1, where 0 means 0% tears and 0.75 means 75% of the whole frame was detected as
    //! if the result is below the dismiss_tear_percentage, we return 0, as these lines may be false positives
    double get_tear_percentage(const double dismiss_tear_percentage) const
    {
        // count of the rows where tears were detected
        const double tear_row_count  = static_cast<double>(_tear_rows.size());
        // count of all rows for this frame
        const double frame_row_count = static_cast<double>(_frame_row_count);
        // calculate the percentage
        const double percentage = tear_row_count / frame_row_count;
        if (percentage > dismiss_tear_percentage) return percentage;
        return 0;
    }
    //! returns a percentage between 0 and 1, where 0 means the two frames were identical,
    //!  and 1 means that every line is different in a least one column
    double get_diff_percentage(const double dismiss_tear_percentage) const
    {
        return 1 - get_tear_percentage(dismiss_tear_percentage);
    }
// member
public:
    //! TODO
    size_t         _frame_row_count;
    //! TODO
    std::vector<quint64> _tear_rows;
};

#endif // TEAR_DATA_H
