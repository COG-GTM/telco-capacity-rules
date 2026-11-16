# Telco capacity rules

Single source of truth for capacity availability math across the telco OSS
stacks. The full rule is in [SPEC.md](SPEC.md):

`available_mbps = max(total - allocated - maintenance_buffer, 0)`.

`utilization_pct = (allocated + maintenance_buffer) * 100 / total`, 0 when `total <= 0`, rounded half-up to 2 decimals, and not capped.

`can_support = available >= requested`.

The maintenance buffer is reserved capacity and is never sellable.

## Consuming the rules

Python (`vantage-telco`), as a pip git dependency:

```bash
pip install "telco-capacity-rules @ git+https://github.com/COG-GTM/telco-capacity-rules.git@<ref>#subdirectory=python"
```

```python
from telco_capacity import available_capacity, utilization_pct, vectors
```

C++ (`meridian-telco`), header-only via git submodule (or copy
`cpp/include/telco_capacity/capacity.h`):

```bash
git submodule add https://github.com/COG-GTM/telco-capacity-rules.git third_party/telco-capacity-rules
# compile with -Ithird_party/telco-capacity-rules/cpp/include
```

```cpp
#include "telco_capacity/capacity.h"
int avail = telco_capacity::available_capacity(total, allocated, buffer);
```

## Tests

`spec/vectors.json` holds the golden vectors both suites run.

```bash
pip install ./python pytest && pytest python/tests
make -C cpp test
```
