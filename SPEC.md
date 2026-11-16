# Capacity availability rule

This repository is the single source of truth for capacity availability math
across the Meridian (C++) and Vantage (Python) OSS stacks. Both stacks call the
implementations here instead of carrying their own arithmetic.

## Inputs

All figures are integer Mbps.

| Name | Meaning |
| --- | --- |
| `total_mbps` | Provisioned capacity of the site, location or link. |
| `allocated_mbps` | Capacity already sold or assigned. |
| `maintenance_buffer_mbps` | Capacity reserved for maintenance windows and failover headroom. Defaults to 0. |

## Rule

```
available_mbps  = max(total_mbps - allocated_mbps - maintenance_buffer_mbps, 0)
utilization_pct = (allocated_mbps + maintenance_buffer_mbps) * 100 / total_mbps
                  (0 when total_mbps <= 0)
can_support     = available_mbps >= requested_mbps
```

- The maintenance buffer is reserved capacity. It is **never sellable**, so it is
  subtracted before availability is quoted, and it counts towards utilization.
- `available_mbps` is floored at 0; it is never negative, even when
  `allocated + buffer` exceeds `total`.
- `utilization_pct` is rounded half-up to 2 decimal places and is not capped at
  100, so an over-committed link reports more than 100%.
- A non-positive `total_mbps` has 0% utilization and 0 available.

Meridian field naming of the same rule:

```
AVAIL_CAP_MBPS = TOTAL_CAP_MBPS - ALLOC_CAP_MBPS - MAINT_BUFFER_MBPS
```

## Implementations

| Language | Location | API |
| --- | --- | --- |
| Python | `python/telco_capacity/` | `available_capacity(total, allocated, buffer=0)`, `utilization_pct(total, allocated, buffer=0)`, `can_support(available, requested)` |
| C++ (header-only) | `cpp/include/telco_capacity/capacity.h` | `telco_capacity::available_capacity`, `telco_capacity::utilization_pct`, `telco_capacity::can_support` |

## Golden test vectors

`spec/vectors.json` is the shared set of cases (normal, buffer exceeding the
remainder, zero total, zero buffer, rounding, ...). Each entry has `name`,
`total`, `allocated`, `buffer` and the expected `available` and
`utilization_pct`. The Python suite, the C++ suite and every downstream consumer
run the same file, which is what guarantees parity between the stacks. The
Python package ships a copy (`python/telco_capacity/vectors.json`, exposed as
`telco_capacity.vectors()`); the Python suite asserts it is identical to the
spec file.

Changing the rule means changing this document, `spec/vectors.json` and both
implementations in the same pull request.
