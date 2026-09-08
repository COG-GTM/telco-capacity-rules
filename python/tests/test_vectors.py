import json
from pathlib import Path

from telco_capacity import available_capacity, utilization_pct, vectors


def test_spec_vectors():
    spec_vectors = json.loads(
        (Path(__file__).parents[2] / "spec" / "vectors.json").read_text()
    )
    assert vectors() == spec_vectors
    for vector in spec_vectors:
        assert available_capacity(
            vector["total"], vector["allocated"], vector["buffer"]
        ) == vector["available"]
        assert utilization_pct(
            vector["total"], vector["allocated"], vector["buffer"]
        ) == vector["utilization_pct"]
