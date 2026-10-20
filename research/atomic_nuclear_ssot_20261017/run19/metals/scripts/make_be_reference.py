#!/usr/bin/env python3
"""Independent Decimal80 substitution of the three exact VF1996 fact rows."""
import csv
import decimal
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "data/vf1996_be_rr_rows.dat"
output = root / "provenance/VF1996_BE_DECIMAL_REFERENCE.csv"
rows = []
with decimal.localcontext() as ctx:
    ctx.prec = 80
    D = decimal.Decimal
    for line in source.read_text().splitlines():
        label, z, n, a, b, t0, t1 = line.split()
        a, b, t0, t1 = map(D, (a, b, t0, t1))
        for t in (3, 10, 100, 10000, 1000000, 1000000000):
            x = (D(t) / t0).sqrt()
            y = (D(t) / t1).sqrt()
            value = a / (x * (1 + x) ** (1 - b) * (1 + y) ** (1 + b))
            rows.append({"formed_ion": label, "final_charge": int(z) - int(n),
                         "T_K": t, "alpha_cm3_s_decimal80": str(value),
                         "rounded_f64": repr(float(value))})
with output.open("x", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
receipt = {"scope": "18 coefficient substitutions, Decimal80, no trajectory or benchmark",
           "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
           "references": len(rows), "precision_decimal_digits": 80}
(root / "provenance/BE_DECIMAL_REFERENCE_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"receipt": receipt, "at_10000K": [r for r in rows if r["T_K"] == 10000]}, indent=2))
