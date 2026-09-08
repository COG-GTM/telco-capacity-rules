# Telco capacity rules

`available_mbps = max(total - allocated - maintenance_buffer, 0)`.

`utilization_pct = (allocated + maintenance_buffer) * 100 / total`, 0 when `total <= 0`, rounded half-up to 2 decimals, and not capped.

`can_support = available >= requested`.

`vantage-telco` consumes these rules through a pip git dependency, while `meridian-telco` consumes the C++ rules through a header include. Run the Python suite with `pip install ./python pytest && pytest python/tests`; run the C++ suite with `make -C cpp test`.

## Billing rules

The `telco_rules` library shares Meridian's billing behaviour by default while
also expressing Vantage's legacy profile. The default `Profile` values are:

| Field | Meridian default |
| --- | ---: |
| `overage_unit` | `OverageUnit::GbCeil` |
| `overage_rate` | `10.00` per GB |
| `billing_month_days` | `30` (`0` means calendar days) |
| `promo_mode` | `PromoMode::IssueCycle` |
| `promo_valid_days` | `30` |
| `suspension_credit` | `false` |
| `provincial_tax_base` | `ProvincialTaxBase::PostLoyalty` |
| `late_fee_grace_days` | `10` |
| `late_fee_pct` | `1.5` |
| `rounding` | `Rounding::PerLine` |

The header-only C++ implementation covers usage rating, proration, promotions,
suspensions, line discounts, late fees, tax, loyalty credits, and invoice
assembly. `vantage_legacy_profile()` selects exact-MB overage at `0.012` per
MB, calendar-day proration, rolling 30-day promotions, suspension credits,
pre-loyalty provincial tax, and round-at-total reporting.

Meridian will include the header in phase 2:

```sh
g++ -I<telco-capacity-rules>/cpp/include ...
```

```cpp
#include "telco_rules/billing.h"
```

Vantage installs the Python package directly from Git:

```sh
pip install git+https://github.com/COG-GTM/telco-capacity-rules
```

The shared invoice vectors in `spec/billing_vectors.json` were generated from
Meridian's 2026-07 register, including Beacon Manufacturing / `TN-0001`.
Per-rule examples live in `spec/billing_rule_vectors.json`; both C++ and
Python test suites assert against these files. CI runs the C++ vectors with
`make -C cpp test` and the Python vectors after installing `./python`.
