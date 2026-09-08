"""Shared telco capacity calculations."""

from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from typing import Any

__version__ = "0.1.0"
RULE = "available = total_capacity - allocated - maintenance_buffer"


def available_capacity(
    total_mbps: int, allocated_mbps: int, maintenance_buffer_mbps: int = 0
) -> int:
    return max(total_mbps - allocated_mbps - maintenance_buffer_mbps, 0)


def utilization_pct(
    total_mbps: int, allocated_mbps: int, maintenance_buffer_mbps: int = 0
) -> float:
    if total_mbps <= 0:
        return 0.0
    percentage = (
        Decimal(allocated_mbps + maintenance_buffer_mbps) * Decimal(100)
        / Decimal(total_mbps)
    )
    return float(percentage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def can_support(available_mbps: int, requested_mbps: int) -> bool:
    return available_mbps >= requested_mbps


def vectors() -> list[dict[str, Any]]:
    """Return the shared capacity test vectors packaged with this distribution."""
    vector_path = Path(__file__).with_name("vectors.json")
    return json.loads(vector_path.read_text(encoding="utf-8"))
