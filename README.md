# Telco capacity rules

`available_mbps = max(total - allocated - maintenance_buffer, 0)`.

`utilization_pct = (allocated + maintenance_buffer) * 100 / total`, 0 when `total <= 0`, rounded half-up to 2 decimals, and not capped.

`can_support = available >= requested`.

`vantage-telco` consumes these rules through a pip git dependency, while `meridian-telco` consumes the C++ rules through a header include.

The same rules are implemented in Python (`python/telco_capacity/`) and as a header-only C++17 library (`cpp/include/telco_capacity/capacity.h`); both are tested against the shared vectors in `spec/vectors.json`, and `python/telco_capacity/vectors.json` must stay identical to it. See [docs/architecture.md](docs/architecture.md) for the layout and a diagram.

## Running the tests

Python (3.9 or later; a virtual environment is recommended):

```sh
pip install ./python pytest
pytest python/tests
```

The tests import the installed package, so reinstall `./python` after changing it. C++ (needs a C++17 compiler, `make` and `python3`, which generates the test vectors):

```sh
make -C cpp test
```

The C++ test binary prints nothing when every check passes.
