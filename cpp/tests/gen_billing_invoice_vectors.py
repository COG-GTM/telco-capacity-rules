import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
vectors = json.loads((ROOT / "spec" / "billing_vectors.json").read_text())
output = Path(__file__).with_name("billing_invoice_vectors.inc")
invoice_vectors = json.loads((ROOT / "spec" / "billing_vectors.json").read_text())

with output.open("w", encoding="utf-8") as stream:
    stream.write(
        "struct BillingInvoiceVector { const char* province; double plan_fee; "
        "long included_gb; double prev_plan_fee; int plan_chg_day; int line_cnt; "
        "double promo_amt; const char* promo_dt; int susp_start; int susp_end; "
        "double prior_bal; const char* prior_due; double loyalty_pct; long usage_mb; "
        "const char* period; double plan_charge; double line_discount; "
        "double recurring; double overage_charges; double suspension_credit; "
        "double promo_credit; double late_fee; double subtotal; double loyalty; "
        "double federal_tax; double provincial_tax; double total; };\n"
    )
    stream.write("static const BillingInvoiceVector BILLING_INVOICE_VECTORS[] = {\n")
    for vector in invoice_vectors:
        account = vector["account"]
        expected = vector["expected"]
        stream.write(
            '  {"%s", %.17g, %d, %.17g, %d, %d, %.17g, "%s", %d, %d, '
            '%.17g, "%s", %.17g, %d, "%s", %.17g, %.17g, %.17g, %.17g, '
            '%.17g, %.17g, %.17g, %.17g, %.17g, %.17g, %.17g, %.17g},\n'
            % (
                account["province"],
                account["plan_monthly_fee"],
                account["included_gb"],
                account["previous_plan_fee"],
                account["plan_change_day"],
                account["line_count"],
                account["promo_credit_amount"],
                account["promo_issued_on"],
                account["suspension_start_day"],
                account["suspension_end_day"],
                account["prior_balance"],
                account["prior_due_date"],
                account["loyalty_discount_pct"],
                vector["usage_mb"],
                vector["period"],
                expected["plan_charge"],
                expected["line_discount"],
                expected["recurring"],
                expected["overage_charges"],
                expected["suspension_credit"],
                expected["promo_credit"],
                expected["late_fee"],
                expected["subtotal"],
                expected["loyalty"],
                expected["federal_tax"],
                expected["provincial_tax"],
                expected["total"],
            )
        )
    stream.write("};\n")
