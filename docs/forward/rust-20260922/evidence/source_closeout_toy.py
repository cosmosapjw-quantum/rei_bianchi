#!/usr/bin/env python3
"""Exact arithmetic witnesses for source closeout; never executes Rust/JAX."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / "docs/forward/rust-20260922"
PINS = {
    "monolithic_model_b2a.py": "3d806e1c1d3bb523bb3c339d1a141f67d7f10069",
    "node_lift_operator.py": "6f5c13f02d0e549e581a02d3c4d8b8313b209bbf",
}

def main():
    source_pins = []
    for name, expected in PINS.items():
        b = (DOC / "source_subset/python" / name).read_bytes()
        actual = hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()
        assert actual == expected
        source_pins.append(actual)
    # Independent global polynomial, against translated interval coefficients.
    knots = [F(-2), F(1, 2), F(4)]
    coeffs = [[F(1), F(1)], [F(-8), F(-1, 2)],
              [F(41, 2), F(-3, 4)], [F(-16), F(7, 8)]]
    points = [-2, -1, 0, F(1, 2), 1, 2, 3, 4]
    expected = [-16, F(-5, 2), 1, F(7, 8), F(1, 2), 2, F(23, 2), 35]
    rows = []
    for x, want in zip(points, expected):
        x = F(x)
        i = 0 if x < knots[1] else 1
        dx = x - knots[i]
        polynomial = x**3 - 2*x**2 + x/2 + 1
        translated = sum(coeffs[j][i] * dx**(3-j) for j in range(4))
        assert polynomial == translated == want
        rows.append({"x":str(x), "expected":str(want), "exact_agreement":True})
    n = [F(1), F(2), F(3), F(4)]
    red = [F(1,10), F(2,10), F(3,10), F(4,10)]
    transfer = [-red[i]*n[i] + (red[i+1]*n[i+1] if i < 3 else 0) for i in range(4)]
    assert sum(transfer) == -F(1,10)
    p = [F(0), F(2), F(0), F(6)]
    assert [q*F(16)/sum(p) for q in p] == [0,4,0,12]
    for rate in [F(-8), F(0), F(8)]:
        pos = [q/sum(p)*max(rate,0) for q in p]
        neg = [q/sum(p)*max(-rate,0) for q in p]
        assert sum(a-b for a,b in zip(pos,neg)) == rate
        assert all(a*b == 0 for a,b in zip(pos,neg))
    # CGS->SI prefactor ratio: (c/100)(sigma/10000)/(L/100)^3 = c sigma/L^3.
    assert F(1,100)*F(1,10000)/F(1,100)**3 == 1
    assert F(10)**6 * F(1,10000) * F(1,100) == 1
    assert (F(1)+3)**3 == 64
    result = {
        "grade":"EXACT_RATIONAL_TOY_AND_SOURCE_IDENTITY_ONLY",
        "source_blobs":source_pins,
        "cubic_evaluation_rows":rows,
        "exact_identity_checks":8,
        "rust_executed":False,
        "jax_executed":False,
        "implementation_verified":False,
    }
    print(json.dumps(result,indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
