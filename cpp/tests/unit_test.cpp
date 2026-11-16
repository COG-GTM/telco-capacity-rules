#include <cassert>
#include <cmath>
#include <cstring>

#include "telco_capacity/capacity.h"

using telco_capacity::available_capacity;
using telco_capacity::can_support;
using telco_capacity::utilization_pct;

static bool near(double a, double b) { return std::fabs(a - b) < 0.000001; }

int main() {
  assert(available_capacity(1000, 600, 150) == 250);

  assert(available_capacity(1000, 600) == 400);
  assert(near(utilization_pct(1000, 600), 60.0));

  assert(available_capacity(100, 90, 50) == 0);
  assert(available_capacity(100, 150) == 0);

  assert(available_capacity(0, 0, 0) == 0);
  assert(near(utilization_pct(0, 50, 25), 0.0));
  assert(near(utilization_pct(-10, 50, 25), 0.0));

  assert(near(utilization_pct(1000, 600, 150), 75.0));
  assert(near(utilization_pct(100, 90, 50), 140.0));

  assert(near(utilization_pct(3000, 1000, 333), 44.43));
  assert(near(utilization_pct(800, 1, 0), 0.13));

  assert(can_support(250, 250));
  assert(!can_support(249, 250));

  assert(std::strcmp(telco_capacity::RULE,
                     "AVAIL_CAP_MBPS = TOTAL_CAP_MBPS - ALLOC_CAP_MBPS - "
                     "MAINT_BUFFER_MBPS") == 0);
}
