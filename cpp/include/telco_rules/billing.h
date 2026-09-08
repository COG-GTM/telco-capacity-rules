#ifndef TELCO_RULES_BILLING_H
#define TELCO_RULES_BILLING_H

#include <cmath>
#include <cstring>
#include <string>

namespace telco_rules {

enum class OverageUnit { GbCeil, ExactMb };
enum class PromoMode { IssueCycle, RollingDays };
enum class ProvincialTaxBase { PostLoyalty, PreLoyalty };
enum class Rounding { PerLine, AtTotal };

struct Profile {
  OverageUnit overage_unit = OverageUnit::GbCeil;
  double overage_rate = 10.00;
  int billing_month_days = 30;
  PromoMode promo_mode = PromoMode::IssueCycle;
  int promo_valid_days = 30;
  bool suspension_credit = false;
  ProvincialTaxBase provincial_tax_base = ProvincialTaxBase::PostLoyalty;
  int late_fee_grace_days = 10;
  double late_fee_pct = 1.5;
  Rounding rounding = Rounding::PerLine;
};

struct TaxRates {
  double federal_pct;
  double provincial_pct;
  std::string federal_label;
  std::string provincial_label;
};

struct Account {
  std::string province;
  double plan_fee = 0.0;
  long included_gb = 0;
  double prev_plan_fee = 0.0;
  int plan_chg_day = 0;
  int line_cnt = 1;
  double promo_amt = 0.0;
  std::string promo_dt;
  int susp_start = 0;
  int susp_end = 0;
  double prior_bal = 0.0;
  std::string prior_due;
  double loyalty_pct = 0.0;
};

struct Invoice {
  long usage_mb = 0;
  long usage_gb_rated = 0;
  long overage_gb = 0;
  long overage_mb = 0;
  double plan_charge = 0.0;
  double line_discount = 0.0;
  double recurring = 0.0;
  double overage_charges = 0.0;
  double suspension_credit = 0.0;
  double promo_credit = 0.0;
  double late_fee = 0.0;
  double subtotal = 0.0;
  double loyalty = 0.0;
  double federal_tax = 0.0;
  double provincial_tax = 0.0;
  double total = 0.0;
  std::string federal_label;
  std::string provincial_label;
};

struct Date {
  int y = 0;
  int m = 0;
  int d = 0;
  bool ok = false;
};

inline int digit(char value) {
  return value >= '0' && value <= '9' ? value - '0' : -1;
}

inline int field(const std::string& value, int offset, int width) {
  if (offset + width > static_cast<int>(value.size())) return -1;
  int result = 0;
  for (int i = 0; i < width; ++i) {
    int part = digit(value[offset + i]);
    if (part < 0) return -1;
    result = result * 10 + part;
  }
  return result;
}

inline Date parse_date(const std::string& value) {
  Date out;
  if (value.size() < 10) return out;
  out.y = field(value, 0, 4);
  out.m = field(value, 5, 2);
  out.d = field(value, 8, 2);
  out.ok = out.y > 0 && out.m > 0 && out.d > 0;
  return out;
}

inline Date period_start(const std::string& value) {
  Date out;
  out.d = 1;
  if (value.size() < 7) return out;
  out.y = field(value, 0, 4);
  out.m = field(value, 5, 2);
  out.ok = out.y > 0 && out.m > 0;
  return out;
}

inline long serial_day(const Date& date) {
  int y = date.y;
  y -= date.m <= 2;
  long era = (y >= 0 ? y : y - 399) / 400;
  unsigned yoe = static_cast<unsigned>(y - era * 400);
  unsigned doy = static_cast<unsigned>(
      (153 * (date.m + (date.m > 2 ? -3 : 9)) + 2) / 5 + date.d - 1);
  unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + static_cast<long>(doe) - 719468;
}

inline long days_between(const Date& from, const Date& to) {
  return serial_day(to) - serial_day(from);
}

inline int calendar_days_in_month(int year, int month) {
  static const int lengths[12] = {31, 28, 31, 30, 31, 30,
                                  31, 31, 30, 31, 30, 31};
  if (month < 1 || month > 12) return 30;
  if (month == 2 &&
      ((year % 4 == 0 && year % 100 != 0) || year % 400 == 0)) {
    return 29;
  }
  return lengths[month - 1];
}

inline Profile meridian_profile() {
  return Profile{};
}

inline Profile vantage_legacy_profile() {
  Profile profile;
  profile.overage_unit = OverageUnit::ExactMb;
  profile.overage_rate = 0.012;
  profile.billing_month_days = 0;
  profile.promo_mode = PromoMode::RollingDays;
  profile.promo_valid_days = 30;
  profile.suspension_credit = true;
  profile.provincial_tax_base = ProvincialTaxBase::PreLoyalty;
  profile.rounding = Rounding::AtTotal;
  return profile;
}

inline double money(double amount) {
  return std::floor(amount * 100.0 + 0.5) / 100.0;
}

inline double rounded(const Profile& profile, double amount) {
  return profile.rounding == Rounding::AtTotal ? amount : money(amount);
}

inline long usage_gb_rounded(long usage_mb) {
  long gb = usage_mb / 1024;
  if (usage_mb % 1024) ++gb;
  return gb;
}

inline long overage_gb(long usage_mb, long included_gb) {
  long gb = usage_gb_rounded(usage_mb);
  return gb <= included_gb ? 0 : gb - included_gb;
}

inline long overage_mb(long usage_mb, long included_gb) {
  long included_mb = included_gb * 1024;
  long overage = usage_mb - included_mb;
  return overage > 0 ? overage : 0;
}

inline double rate_overage(const Profile& profile, long usage_mb,
                           long included_gb) {
  long units = profile.overage_unit == OverageUnit::ExactMb
                   ? overage_mb(usage_mb, included_gb)
                   : overage_gb(usage_mb, included_gb);
  return static_cast<double>(units) * profile.overage_rate;
}

inline int days_in_period(const Profile& profile, const std::string& period) {
  if (profile.billing_month_days != 0) return profile.billing_month_days;
  Date start = period_start(period);
  if (!start.ok) return 30;
  return calendar_days_in_month(start.y, start.m);
}

inline double daily_rate(const Profile& profile, double monthly_fee,
                         const std::string& period) {
  return monthly_fee / static_cast<double>(days_in_period(profile, period));
}

inline double prorated_plan_charge(const Profile& profile, double monthly_fee,
                                   double prev_monthly_fee, int change_day,
                                   const std::string& period) {
  if (change_day <= 0) return rounded(profile, monthly_fee);
  int total_days = days_in_period(profile, period);
  int days_on_old = change_day - 1;
  if (days_on_old < 0) days_on_old = 0;
  if (days_on_old > total_days) days_on_old = total_days;
  int days_on_new = total_days - days_on_old;
  double old_part =
      rounded(profile, daily_rate(profile, prev_monthly_fee, period) *
                           static_cast<double>(days_on_old));
  double new_part =
      rounded(profile, daily_rate(profile, monthly_fee, period) *
                           static_cast<double>(days_on_new));
  return rounded(profile, old_part + new_part);
}

inline bool promo_is_live(const Profile& profile, const std::string& issued_on,
                          const std::string& period) {
  Date issued = parse_date(issued_on);
  Date cycle = period_start(period);
  if (!issued.ok || !cycle.ok) return false;
  if (profile.promo_mode == PromoMode::IssueCycle) {
    return issued.y == cycle.y && issued.m == cycle.m;
  }
  return serial_day(issued) + profile.promo_valid_days >= serial_day(cycle);
}

inline double promo_credit(const Profile& profile, double amount,
                           const std::string& issued_on,
                           const std::string& period) {
  if (amount <= 0.0 || !promo_is_live(profile, issued_on, period)) return 0.0;
  return rounded(profile, amount);
}

inline int suspended_days(int start_day, int end_day) {
  if (start_day <= 0 || end_day < start_day) return 0;
  return end_day - start_day + 1;
}

inline double suspension_credit(const Profile& profile, double monthly_fee,
                                int start_day, int end_day,
                                const std::string& period) {
  int days = suspended_days(start_day, end_day);
  if (!profile.suspension_credit || days == 0) return 0.0;
  return rounded(profile, daily_rate(profile, monthly_fee, period) * days);
}

inline double multi_line_pct(int line_count) {
  if (line_count >= 10) return 10.0;
  if (line_count >= 3) return 5.0;
  return 0.0;
}

inline double multi_line_discount(const Profile& profile,
                                  double recurring_charge, int line_count) {
  return rounded(profile,
                 recurring_charge * multi_line_pct(line_count) / 100.0);
}

inline long days_past_due(const std::string& due_date,
                          const std::string& period) {
  Date due = parse_date(due_date);
  Date cycle = period_start(period);
  if (!due.ok || !cycle.ok) return 0;
  long days = days_between(due, cycle);
  return days > 0 ? days : 0;
}

inline double late_fee(const Profile& profile, double prior_balance,
                       const std::string& due_date,
                       const std::string& period) {
  if (prior_balance <= 0.0 ||
      days_past_due(due_date, period) <= profile.late_fee_grace_days) {
    return 0.0;
  }
  return rounded(profile, prior_balance * profile.late_fee_pct / 100.0);
}

inline TaxRates rates_for_province(const std::string& province) {
  if (province == "BC") return {5.0, 7.0, "GST", "PST"};
  if (province == "AB") return {5.0, 0.0, "GST", ""};
  if (province == "ON") return {13.0, 0.0, "HST", ""};
  if (province == "QC") return {5.0, 9.975, "GST", "QST"};
  return {5.0, 0.0, "GST", ""};
}

inline double federal_tax(const Profile& profile, double pre_discount_amount,
                          const TaxRates& rates) {
  return rounded(profile, pre_discount_amount * rates.federal_pct / 100.0);
}

inline double provincial_tax(const Profile& profile, double pre_discount_amount,
                             double discount, const TaxRates& rates) {
  if (rates.provincial_pct <= 0.0) return 0.0;
  double base = profile.provincial_tax_base == ProvincialTaxBase::PreLoyalty
                    ? pre_discount_amount
                    : pre_discount_amount - discount;
  if (base < 0.0) base = 0.0;
  return rounded(profile, base * rates.provincial_pct / 100.0);
}

inline double loyalty_discount(const Profile& profile, double amount,
                               double loyalty_pct) {
  return rounded(profile, amount * loyalty_pct / 100.0);
}

inline Invoice compute_invoice(const Profile& profile, const Account& account,
                               long usage_mb, const std::string& period) {
  Invoice invoice;
  invoice.usage_mb = usage_mb;
  invoice.usage_gb_rated = usage_gb_rounded(usage_mb);
  invoice.overage_gb = overage_gb(usage_mb, account.included_gb);
  invoice.overage_mb = overage_mb(usage_mb, account.included_gb);

  double plan_charge = prorated_plan_charge(
      profile, account.plan_fee, account.prev_plan_fee, account.plan_chg_day,
      period);
  double line_discount =
      multi_line_discount(profile, plan_charge, account.line_cnt);
  double recurring = rounded(profile, plan_charge - line_discount);
  double overage_charges =
      rounded(profile, rate_overage(profile, usage_mb, account.included_gb));
  double suspension =
      suspension_credit(profile, account.plan_fee, account.susp_start,
                        account.susp_end, period);
  double promo =
      promo_credit(profile, account.promo_amt, account.promo_dt, period);
  double fee =
      late_fee(profile, account.prior_bal, account.prior_due, period);

  double subtotal = recurring + overage_charges + fee - suspension - promo;
  if (subtotal < 0.0) subtotal = 0.0;
  subtotal = rounded(profile, subtotal);

  TaxRates rates = rates_for_province(account.province);
  double loyalty = loyalty_discount(profile, subtotal, account.loyalty_pct);
  double federal = federal_tax(profile, subtotal, rates);
  double provincial = provincial_tax(profile, subtotal, loyalty, rates);
  double total = rounded(profile, subtotal - loyalty + federal + provincial);

  invoice.plan_charge = plan_charge;
  invoice.line_discount = line_discount;
  invoice.recurring = recurring;
  invoice.overage_charges = overage_charges;
  invoice.suspension_credit = suspension;
  invoice.promo_credit = promo;
  invoice.late_fee = fee;
  invoice.subtotal = subtotal;
  invoice.loyalty = loyalty;
  invoice.federal_tax = federal;
  invoice.provincial_tax = provincial;
  invoice.total = total;
  invoice.federal_label = rates.federal_label;
  invoice.provincial_label = rates.provincial_label;

  if (profile.rounding == Rounding::AtTotal) {
    invoice.plan_charge = money(invoice.plan_charge);
    invoice.line_discount = money(invoice.line_discount);
    invoice.recurring = money(invoice.recurring);
    invoice.overage_charges = money(invoice.overage_charges);
    invoice.suspension_credit = money(invoice.suspension_credit);
    invoice.promo_credit = money(invoice.promo_credit);
    invoice.late_fee = money(invoice.late_fee);
    invoice.subtotal = money(invoice.subtotal);
    invoice.loyalty = money(invoice.loyalty);
    invoice.federal_tax = money(invoice.federal_tax);
    invoice.provincial_tax = money(invoice.provincial_tax);
    invoice.total = money(invoice.total);
  }
  return invoice;
}

}  // namespace telco_rules

#endif
