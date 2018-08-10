#include "tbb/parallel_for_each.h"
#include "tbb/parallel_reduce.h"

#include <iostream>
#include <numeric>
#include <vector>

int main()
{
    std::vector<int> vs(1000, 1);

    tbb::parallel_for_each(begin(vs), end(vs), [](auto& v) {
        v += 5;
    });

    typedef tbb::blocked_range<std::vector<int>::iterator> Range;
    int r = tbb::parallel_reduce(Range(begin(vs), end(vs)), 0,
                                 [](const Range& r, int init)
                                 {
                                     return std::accumulate(begin(r), end(r), init);
                                 },
                                 std::plus<int>());

    std::cout << "Result = " << r << "\n";

    return r == 6000 ? 0 : 1;
}
