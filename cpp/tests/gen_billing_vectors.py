import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
vectors = json.loads((ROOT / "spec" / "billing_rule_vectors.json").read_text())
output = Path(__file__).with_name("billing_vectors.inc")

with output.open("w", encoding="utf-8") as stream:
    stream.write(
        "struct BillingVector { const char* profile; const char* fn; "
        "double expected; };\n"
    )
    stream.write("static const BillingVector BILLING_VECTORS[] = {\n")
    for vector in vectors:
        expected = vector["expected"]
        if isinstance(expected, bool):
            expected = 1.0 if expected else 0.0
        stream.write(
            '  {"%s", "%s", %.17g},\n'
            % (vector["profile"], vector["fn"], expected)
        )
    stream.write("};\n")
