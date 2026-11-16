import pytest

from telco_capacity import RULE, available_capacity, can_support, utilization_pct


def test_available_subtracts_allocated_and_buffer():
    assert available_capacity(1000, 600, 150) == 250


def test_buffer_defaults_to_zero():
    assert available_capacity(1000, 600) == 400
    assert utilization_pct(1000, 600) == 60.0


def test_available_is_floored_at_zero():
    assert available_capacity(100, 90, 50) == 0
    assert available_capacity(100, 150) == 0


@pytest.mark.parametrize("total", [0, -10])
def test_non_positive_total(total):
    assert available_capacity(total, 0, 0) == 0
    assert utilization_pct(total, 50, 25) == 0.0


def test_utilization_counts_buffer_and_is_not_capped():
    assert utilization_pct(1000, 600, 150) == 75.0
    assert utilization_pct(100, 90, 50) == 140.0


def test_utilization_rounds_half_up():
    assert utilization_pct(3000, 1000, 333) == 44.43
    assert utilization_pct(800, 1, 0) == 0.13


def test_can_support_is_inclusive():
    assert can_support(250, 250)
    assert not can_support(249, 250)


def test_rule_names_the_buffer():
    assert RULE == "available = total_capacity - allocated - maintenance_buffer"
