#ifndef TEAR_DATA_H
#define TEAR_DATA_H

#include <vector>
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
    //! a tear (not necessearly in order, e.g row 0, 2, 3 from a 4 row frame is still 75%)
    double get_tear_percentage() const
    {
        // count of the rows where tears were detected
        const double tear_row_count  = static_cast<double>(_tear_rows.size());
        // count of all rows for this frame
        const double frame_row_count = static_cast<double>(_frame_row_count);
        // calculate the percentage
        return  tear_row_count / frame_row_count;
    }
// member
private:
    //! TODO
    size_t         _frame_row_count;
    //! TODO
    std::vector<quint64> _tear_rows;
};

#endif // TEAR_DATA_H
