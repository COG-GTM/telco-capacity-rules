#include <cassert>
#include <cmath>
#include <cstring>
#include <string>

#include "telco_rules/billing.h"
#include "billing_vectors.inc"
#include "billing_invoice_vectors.inc"

namespace {

void close_to(double actual, double expected) {
  assert(std::fabs(actual - expected) < 1e-9);
}

telco_rules::Account account(const BillingInvoiceVector& vector) {
  telco_rules::Account account;
  account.province = vector.province;
  account.plan_fee = vector.plan_fee;
  account.included_gb = vector.included_gb;
  account.prev_plan_fee = vector.prev_plan_fee;
  account.plan_chg_day = vector.plan_chg_day;
  account.line_cnt = vector.line_cnt;
  account.promo_amt = vector.promo_amt;
  account.promo_dt = vector.promo_dt;
  account.susp_start = vector.susp_start;
  account.susp_end = vector.susp_end;
  account.prior_bal = vector.prior_bal;
  account.prior_due = vector.prior_due;
  account.loyalty_pct = vector.loyalty_pct;
  return account;
}

}  // namespace

int main() {
  telco_rules::Profile meridian = telco_rules::meridian_profile();
  telco_rules::Profile vantage = telco_rules::vantage_legacy_profile();

  for (const auto& vector : BILLING_INVOICE_VECTORS) {
    telco_rules::Account account_value = account(vector);
    telco_rules::Invoice invoice = telco_rules::compute_invoice(
        meridian, account_value, vector.usage_mb, vector.period);
    close_to(invoice.plan_charge, vector.plan_charge);
    close_to(invoice.line_discount, vector.line_discount);
    close_to(invoice.recurring, vector.recurring);
    close_to(invoice.overage_charges, vector.overage_charges);
    close_to(invoice.suspension_credit, vector.suspension_credit);
    close_to(invoice.promo_credit, vector.promo_credit);
    close_to(invoice.late_fee, vector.late_fee);
    close_to(invoice.subtotal, vector.subtotal);
    close_to(invoice.loyalty, vector.loyalty);
    close_to(invoice.federal_tax, vector.federal_tax);
    close_to(invoice.provincial_tax, vector.provincial_tax);
    close_to(invoice.total, vector.total);
  }

  for (const auto& vector : BILLING_VECTORS) {
    double actual = 0.0;
    if (std::strcmp(vector.fn, "usage_gb_rounded") == 0) {
      actual = static_cast<double>(telco_rules::usage_gb_rounded(1024485));
    } else if (std::strcmp(vector.fn, "overage_gb") == 0) {
      actual = static_cast<double>(telco_rules::overage_gb(1024485, 1000));
    } else if (std::strcmp(vector.fn, "rate_overage") == 0) {
      actual = telco_rules::rate_overage(vantage, 1024485, 1000);
    } else if (std::strcmp(vector.fn, "prorated_plan_charge") == 0) {
      actual = telco_rules::prorated_plan_charge(
          vantage, 310, 620, 31, "2026-07");
    } else if (std::strcmp(vector.fn, "promo_is_live") == 0) {
      actual = telco_rules::promo_is_live(
                   vantage, "2026-06-24", "2026-07")
                   ? 1.0
                   : 0.0;
    } else if (std::strcmp(vector.fn, "suspension_credit") == 0) {
      actual = telco_rules::suspension_credit(
          vantage, 620, 10, 14, "2026-07");
    } else {
      assert(false);
    }
    close_to(actual, vector.expected);
  }
}
