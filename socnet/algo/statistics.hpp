#ifndef STATISTICS_HPP
#define STATISTICS_HPP

#include <cmath>
#include <iostream>
#include <vector>

template<typename T>
class Statistics
{
    std::vector<T> mean;
    std::vector<T> m2;
    std::vector<T> count;
    unsigned int sz;

  public:
    Statistics(const int n, T val)
      : sz(n)
    {
        for (unsigned int i = 0; i < sz; i++) {
            mean.push_back(val);
            m2.push_back(val);
            count.push_back(val);
        }
        return;
    }

    int size() { return sz; }
    std::vector<T> get_mean() { return mean; }
    std::vector<T> get_m2() { return m2; }
    std::vector<T> get_count() { return count; }

    void add_value(const unsigned int id, const T value)
    {
        if (id >= sz)
            std::cerr << "Error in " << __FILE__ << " at line " << __LINE__
                      << "|-> Statistics add_value(" << id << "," << value
                      << ");" << std::endl;

        T delta = value - mean[id];
        count[id] += 1.0;
        mean[id] += delta / count[id];
        T delta2 = value - mean[id];
        m2[id] += delta * delta2;

        return;
    }
};
#endif // STATISTICS_HPP