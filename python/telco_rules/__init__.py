"""Shared telco billing rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import math
from pathlib import Path
from typing import Any

__version__ = "0.2.0"


class OverageUnit(Enum):
    GB_CEIL = "gb_ceil"
    EXACT_MB = "exact_mb"


class PromoMode(Enum):
    ISSUE_CYCLE = "issue_cycle"
    ROLLING_DAYS = "rolling_days"


class ProvincialTaxBase(Enum):
    POST_LOYALTY = "post_loyalty"
    PRE_LOYALTY = "pre_loyalty"


class Rounding(Enum):
    PER_LINE = "per_line"
    AT_TOTAL = "at_total"


@dataclass
class Profile:
    overage_unit: OverageUnit = OverageUnit.GB_CEIL
    overage_rate: float = 10.00
    billing_month_days: int = 30
    promo_mode: PromoMode = PromoMode.ISSUE_CYCLE
    promo_valid_days: int = 30
    suspension_credit: bool = False
    provincial_tax_base: ProvincialTaxBase = ProvincialTaxBase.POST_LOYALTY
    late_fee_grace_days: int = 10
    late_fee_pct: float = 1.5
    rounding: Rounding = Rounding.PER_LINE


@dataclass
class TaxRates:
    federal_pct: float
    provincial_pct: float
    federal_label: str
    provincial_label: str


@dataclass
class Account:
    province: str = ""
    plan_fee: float = 0.0
    included_gb: int = 0
    prev_plan_fee: float = 0.0
    plan_chg_day: int = 0
    line_cnt: int = 1
    promo_amt: float = 0.0
    promo_dt: str = ""
    susp_start: int = 0
    susp_end: int = 0
    prior_bal: float = 0.0
    prior_due: str = ""
    loyalty_pct: float = 0.0


@dataclass
class Invoice:
    usage_mb: int
    usage_gb_rated: int
    overage_gb: int
    overage_mb: int
    plan_charge: float
    line_discount: float
    recurring: float
    overage_charges: float
    suspension_credit: float
    promo_credit: float
    late_fee: float
    subtotal: float
    loyalty: float
    federal_tax: float
    provincial_tax: float
    total: float
    federal_label: str
    provincial_label: str


@dataclass
class Date:
    y: int = 0
    m: int = 0
    d: int = 0
    ok: bool = False


def _field(value: str, offset: int, width: int) -> int:
    if offset + width > len(value):
        return -1
    part = value[offset : offset + width]
    if not part.isdigit():
        return -1
    return int(part)


def parse_date(value: str | None) -> Date:
    value = value or ""
    if len(value) < 10:
        return Date()
    year = _field(value, 0, 4)
    month = _field(value, 5, 2)
    day = _field(value, 8, 2)
    return Date(year, month, day, year > 0 and month > 0 and day > 0)


def period_start(value: str) -> Date:
    value = value or ""
    if len(value) < 7:
        return Date(d=1)
    year = _field(value, 0, 4)
    month = _field(value, 5, 2)
    return Date(year, month, 1, year > 0 and month > 0)


def _serial_day(date: Date) -> int:
    year = date.y - int(date.m <= 2)
    era = (year if year >= 0 else year - 399) // 400
    year_of_era = year - era * 400
    day_of_year = (153 * (date.m + (-3 if date.m > 2 else 9)) + 2) // 5
    day_of_year += date.d - 1
    day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100
    day_of_era += day_of_year
    return era * 146097 + day_of_era - 719468


def days_between(date_from: Date, date_to: Date) -> int:
    return _serial_day(date_to) - _serial_day(date_from)


def calendar_days_in_month(year: int, month: int) -> int:
    lengths = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if month < 1 or month > 12:
        return 30
    if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        return 29
    return lengths[month - 1]


def meridian_profile() -> Profile:
    return Profile()


def vantage_legacy_profile() -> Profile:
    return Profile(
        overage_unit=OverageUnit.EXACT_MB,
        overage_rate=0.012,
        billing_month_days=0,
        promo_mode=PromoMode.ROLLING_DAYS,
        promo_valid_days=30,
        suspension_credit=True,
        provincial_tax_base=ProvincialTaxBase.PRE_LOYALTY,
        rounding=Rounding.AT_TOTAL,
    )


def money(amount: float) -> float:
    return math.floor(amount * 100.0 + 0.5) / 100.0


def _rounded(profile: Profile, amount: float) -> float:
    return amount if profile.rounding is Rounding.AT_TOTAL else money(amount)


def usage_gb_rounded(usage_mb: int) -> int:
    gb = abs(usage_mb) // 1024
    if usage_mb < 0:
        gb = -gb
    remainder = usage_mb - gb * 1024
    if remainder:
        gb += 1
    return gb


def overage_gb(usage_mb: int, included_gb: int) -> int:
    rated = usage_gb_rounded(usage_mb)
    return 0 if rated <= included_gb else rated - included_gb


def overage_mb(usage_mb: int, included_gb: int) -> int:
    return max(usage_mb - included_gb * 1024, 0)


def rate_overage(profile: Profile, usage_mb: int, included_gb: int) -> float:
    units = (
        overage_mb(usage_mb, included_gb)
        if profile.overage_unit is OverageUnit.EXACT_MB
        else overage_gb(usage_mb, included_gb)
    )
    return units * profile.overage_rate


def days_in_period(profile: Profile, period: str) -> int:
    if profile.billing_month_days != 0:
        return profile.billing_month_days
    start = period_start(period)
    if not start.ok:
        return 30
    return calendar_days_in_month(start.y, start.m)


def daily_rate(profile: Profile, monthly_fee: float, period: str) -> float:
    return monthly_fee / days_in_period(profile, period)


def prorated_plan_charge(
    profile: Profile,
    monthly_fee: float,
    prev_monthly_fee: float,
    change_day: int,
    period: str,
) -> float:
    if change_day <= 0:
        return _rounded(profile, monthly_fee)
    total_days = days_in_period(profile, period)
    days_on_old = max(0, min(change_day - 1, total_days))
    days_on_new = total_days - days_on_old
    old_part = _rounded(profile, daily_rate(profile, prev_monthly_fee, period) * days_on_old)
    new_part = _rounded(profile, daily_rate(profile, monthly_fee, period) * days_on_new)
    return _rounded(profile, old_part + new_part)


def promo_is_live(profile: Profile, issued_on: str | None, period: str) -> bool:
    issued = parse_date(issued_on)
    cycle = period_start(period)
    if not issued.ok or not cycle.ok:
        return False
    if profile.promo_mode is PromoMode.ISSUE_CYCLE:
        return issued.y == cycle.y and issued.m == cycle.m
    return _serial_day(issued) + profile.promo_valid_days >= _serial_day(cycle)


def promo_credit(
    profile: Profile, amount: float, issued_on: str | None, period: str
) -> float:
    if amount <= 0.0 or not promo_is_live(profile, issued_on, period):
        return 0.0
    return _rounded(profile, amount)


def suspended_days(start_day: int, end_day: int) -> int:
    if start_day <= 0 or end_day < start_day:
        return 0
    return end_day - start_day + 1


def suspension_credit(
    profile: Profile,
    monthly_fee: float,
    start_day: int,
    end_day: int,
    period: str,
) -> float:
    days = suspended_days(start_day, end_day)
    if not profile.suspension_credit or days == 0:
        return 0.0
    return _rounded(profile, daily_rate(profile, monthly_fee, period) * days)


def multi_line_pct(line_count: int) -> float:
    if line_count >= 10:
        return 10.0
    if line_count >= 3:
        return 5.0
    return 0.0


def multi_line_discount(profile: Profile, recurring_charge: float, line_count: int) -> float:
    return _rounded(profile, recurring_charge * multi_line_pct(line_count) / 100.0)


def days_past_due(due_date: str | None, period: str) -> int:
    due = parse_date(due_date)
    cycle = period_start(period)
    if not due.ok or not cycle.ok:
        return 0
    return max(days_between(due, cycle), 0)


def late_fee(
    profile: Profile, prior_balance: float, due_date: str | None, period: str
) -> float:
    if prior_balance <= 0.0 or days_past_due(due_date, period) <= profile.late_fee_grace_days:
        return 0.0
    return _rounded(profile, prior_balance * profile.late_fee_pct / 100.0)


def rates_for_province(province: str) -> TaxRates:
    if province == "BC":
        return TaxRates(5.0, 7.0, "GST", "PST")
    if province == "AB":
        return TaxRates(5.0, 0.0, "GST", "")
    if province == "ON":
        return TaxRates(13.0, 0.0, "HST", "")
    if province == "QC":
        return TaxRates(5.0, 9.975, "GST", "QST")
    return TaxRates(5.0, 0.0, "GST", "")


def federal_tax(profile: Profile, pre_discount_amount: float, rates: TaxRates) -> float:
    return _rounded(profile, pre_discount_amount * rates.federal_pct / 100.0)


def provincial_tax(
    profile: Profile,
    pre_discount_amount: float,
    discount: float,
    rates: TaxRates,
) -> float:
    if rates.provincial_pct <= 0.0:
        return 0.0
    base = (
        pre_discount_amount
        if profile.provincial_tax_base is ProvincialTaxBase.PRE_LOYALTY
        else pre_discount_amount - discount
    )
    return _rounded(profile, max(base, 0.0) * rates.provincial_pct / 100.0)


def loyalty_discount(profile: Profile, amount: float, loyalty_pct: float) -> float:
    return _rounded(profile, amount * loyalty_pct / 100.0)


def compute_invoice(
    profile: Profile, account: dict[str, Any], usage_mb: int, period: str
) -> dict[str, Any]:
    def value(name: str, default: Any) -> Any:
        item = account.get(name)
        return default if item is None else item

    native = Account(
        province=value("province", ""),
        plan_fee=float(value("plan_monthly_fee", 0) or 0),
        included_gb=int(value("included_gb", 0) or 0),
        prev_plan_fee=float(value("previous_plan_fee", 0) or 0),
        plan_chg_day=int(value("plan_change_day", 0) or 0),
        line_cnt=int(value("line_count", 1) or 1),
        promo_amt=float(value("promo_credit_amount", 0) or 0),
        promo_dt=value("promo_issued_on", "") or "",
        susp_start=int(value("suspension_start_day", 0) or 0),
        susp_end=int(value("suspension_end_day", 0) or 0),
        prior_bal=float(value("prior_balance", 0) or 0),
        prior_due=value("prior_due_date", "") or "",
        loyalty_pct=float(value("loyalty_discount_pct", 0) or 0),
    )
    plan_charge = prorated_plan_charge(
        profile, native.plan_fee, native.prev_plan_fee, native.plan_chg_day, period
    )
    line_discount = multi_line_discount(profile, plan_charge, native.line_cnt)
    recurring = _rounded(profile, plan_charge - line_discount)
    overage_charges = _rounded(profile, rate_overage(profile, usage_mb, native.included_gb))
    suspension = suspension_credit(
        profile, native.plan_fee, native.susp_start, native.susp_end, period
    )
    promo = promo_credit(profile, native.promo_amt, native.promo_dt, period)
    fee = late_fee(profile, native.prior_bal, native.prior_due, period)
    subtotal = max(recurring + overage_charges + fee - suspension - promo, 0.0)
    subtotal = _rounded(profile, subtotal)
    rates = rates_for_province(native.province)
    loyalty = loyalty_discount(profile, subtotal, native.loyalty_pct)
    federal = federal_tax(profile, subtotal, rates)
    provincial = provincial_tax(profile, subtotal, loyalty, rates)
    total = _rounded(profile, subtotal - loyalty + federal + provincial)
    invoice = Invoice(
        usage_mb,
        usage_gb_rounded(usage_mb),
        overage_gb(usage_mb, native.included_gb),
        overage_mb(usage_mb, native.included_gb),
        plan_charge,
        line_discount,
        recurring,
        overage_charges,
        suspension,
        promo,
        fee,
        subtotal,
        loyalty,
        federal,
        provincial,
        total,
        rates.federal_label,
        rates.provincial_label,
    )
    if profile.rounding is Rounding.AT_TOTAL:
        for field_name in (
            "plan_charge",
            "line_discount",
            "recurring",
            "overage_charges",
            "suspension_credit",
            "promo_credit",
            "late_fee",
            "subtotal",
            "loyalty",
            "federal_tax",
            "provincial_tax",
            "total",
        ):
            setattr(invoice, field_name, money(getattr(invoice, field_name)))
    return {
        "usage_mb": invoice.usage_mb,
        "usage_gb_rated": invoice.usage_gb_rated,
        "overage_gb": invoice.overage_gb,
        "overage_mb": invoice.overage_mb,
        "plan_charge": invoice.plan_charge,
        "line_discount": invoice.line_discount,
        "recurring": invoice.recurring,
        "overage_charges": invoice.overage_charges,
        "suspension_credit": invoice.suspension_credit,
        "promo_credit": invoice.promo_credit,
        "late_fee": invoice.late_fee,
        "subtotal": invoice.subtotal,
        "loyalty": invoice.loyalty,
        "federal_tax": invoice.federal_tax,
        "provincial_tax": invoice.provincial_tax,
        "total": invoice.total,
        "federal_label": invoice.federal_label,
        "provincial_label": invoice.provincial_label,
    }


def vectors() -> list[dict[str, Any]]:
    return json.loads(
        (Path(__file__).with_name("vectors.json")).read_text(encoding="utf-8")
    )


def billing_vectors() -> list[dict[str, Any]]:
    return json.loads(
        (Path(__file__).with_name("billing_vectors.json")).read_text(encoding="utf-8")
    )


__all__ = [
    "Account",
    "Date",
    "Invoice",
    "OverageUnit",
    "Profile",
    "PromoMode",
    "ProvincialTaxBase",
    "Rounding",
    "TaxRates",
    "billing_vectors",
    "calendar_days_in_month",
    "compute_invoice",
    "daily_rate",
    "days_between",
    "days_in_period",
    "days_past_due",
    "federal_tax",
    "late_fee",
    "loyalty_discount",
    "meridian_profile",
    "money",
    "multi_line_discount",
    "multi_line_pct",
    "overage_gb",
    "overage_mb",
    "parse_date",
    "period_start",
    "prorated_plan_charge",
    "promo_credit",
    "promo_is_live",
    "provincial_tax",
    "rate_overage",
    "rates_for_province",
    "suspended_days",
    "suspension_credit",
    "usage_gb_rounded",
    "vantage_legacy_profile",
    "vectors",
]
