import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
vectors = json.loads((ROOT / "spec" / "vectors.json").read_text())
output = Path(__file__).with_name("vectors.inc")

with output.open("w", encoding="utf-8") as stream:
    stream.write("struct CapacityVector { int total; int allocated; int buffer; int available; double utilization; };\n")
    stream.write("static const CapacityVector VECTORS[] = {\n")
    for vector in vectors:
        stream.write(
            "  {%d, %d, %d, %d, %.2f},\n"
            % (
                vector["total"],
                vector["allocated"],
                vector["buffer"],
                vector["available"],
                vector["utilization_pct"],
            )
        )
    stream.write("};\n")
