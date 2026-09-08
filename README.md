# Telco capacity rules

`available_mbps = max(total - allocated - maintenance_buffer, 0)`.

`utilization_pct = (allocated + maintenance_buffer) * 100 / total`, 0 when `total <= 0`, rounded half-up to 2 decimals, and not capped.

`can_support = available >= requested`.

`vantage-telco` consumes these rules through a pip git dependency, while `meridian-telco` consumes the C++ rules through a header include. Run the Python suite with `pip install ./python pytest && pytest python/tests`; run the C++ suite with `make -C cpp test`.
