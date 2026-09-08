import json
from pathlib import Path

from telco_rules import (
    billing_vectors,
    compute_invoice,
    days_in_period,
    overage_gb,
    promo_is_live,
    prorated_plan_charge,
    rate_overage,
    suspended_days,
    suspension_credit,
    vantage_legacy_profile,
    meridian_profile,
    usage_gb_rounded,
)


ROOT = Path(__file__).parents[2]


def test_billing_invoice_vectors_match_spec_and_package():
    spec_vectors = json.loads((ROOT / "spec" / "billing_vectors.json").read_text())
    assert billing_vectors() == spec_vectors
    profile = meridian_profile()
    for vector in spec_vectors:
        actual = compute_invoice(
            profile, vector["account"], vector["usage_mb"], vector["period"]
        )
        for field, expected in vector["expected"].items():
            assert actual[field] == expected


def test_billing_rule_vectors():
    vectors = json.loads((ROOT / "spec" / "billing_rule_vectors.json").read_text())
    meridian = meridian_profile()
    vantage = vantage_legacy_profile()
    for vector in vectors:
        profile = meridian if vector["profile"] == "meridian" else vantage
        args = vector["args"]
        if vector["fn"] == "usage_gb_rounded":
            actual = usage_gb_rounded(args["usage_mb"])
        elif vector["fn"] == "overage_gb":
            actual = overage_gb(args["usage_mb"], args["included_gb"])
        elif vector["fn"] == "rate_overage":
            actual = rate_overage(profile, args["usage_mb"], args["included_gb"])
        elif vector["fn"] == "prorated_plan_charge":
            actual = prorated_plan_charge(
                profile,
                args["monthly_fee"],
                args["previous_monthly_fee"],
                args["change_day"],
                args["period"],
            )
        elif vector["fn"] == "promo_is_live":
            actual = promo_is_live(profile, args["issued_on"], args["period"])
        elif vector["fn"] == "suspension_credit":
            actual = suspension_credit(
                profile,
                args["monthly_fee"],
                args["start_day"],
                args["end_day"],
                args["period"],
            )
        else:
            raise AssertionError(f"unknown function {vector['fn']}")
        assert actual == vector["expected"]


def test_legacy_profile_examples():
    profile = vantage_legacy_profile()
    assert days_in_period(profile, "2026-07") == 31
    assert suspended_days(10, 14) == 5
    assert rate_overage(profile, 1024 * 1000 + 485, 1000) == 5.82
    assert promo_is_live(profile, "2026-06-24", "2026-07")
    assert suspension_credit(profile, 620, 10, 14, "2026-07") == 620 / 31 * 5
