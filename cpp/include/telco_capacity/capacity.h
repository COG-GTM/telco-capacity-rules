#ifndef TELCO_CAPACITY_CAPACITY_H
#define TELCO_CAPACITY_CAPACITY_H

#include <algorithm>

namespace telco_capacity {

inline int available_capacity(int total, int allocated, int buffer = 0) {
  return std::max(total - allocated - buffer, 0);
}

inline double utilization_pct(int total, int allocated, int buffer = 0) {
  if (total <= 0) return 0.0;
  const long long numerator =
      static_cast<long long>(allocated + buffer) * 10000;
  const long long rounded = (numerator + total / 2) / total;
  return static_cast<double>(rounded) / 100.0;
}

inline bool can_support(int available, int requested) {
  return available >= requested;
}

constexpr const char* RULE =
    "AVAIL_CAP_MBPS = TOTAL_CAP_MBPS - ALLOC_CAP_MBPS - MAINT_BUFFER_MBPS";

}  // namespace telco_capacity

#endif
