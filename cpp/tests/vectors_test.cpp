#include <cassert>
#include <cmath>
#include <cstdio>

#include "telco_capacity/capacity.h"
#include "vectors.inc"

int main() {
  int count = 0;
  for (const auto& vector : VECTORS) {
    assert(telco_capacity::available_capacity(
               vector.total, vector.allocated, vector.buffer) ==
           vector.available);
    assert(std::fabs(telco_capacity::utilization_pct(
                         vector.total, vector.allocated, vector.buffer) -
                     vector.utilization) <
           0.000001);
    std::printf("ok   golden vector %s\n", vector.name);
    count++;
  }
  assert(telco_capacity::can_support(250, 250));
  assert(!telco_capacity::can_support(249, 250));
  std::printf("%d golden vectors passed\n", count);
}
