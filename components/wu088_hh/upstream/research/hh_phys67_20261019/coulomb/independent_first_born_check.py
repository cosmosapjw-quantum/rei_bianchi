#!/usr/bin/env python3
"""Independent exact angular identity check: recurrence + integration by parts.

No numerical radial campaign is launched.  This construction uses neither
the target's factorial formula for Legendre coefficients nor its binomial
Laurent expansion, and compares the two exact exp(+-2R) coefficients.
"""
from pathlib import Path
import hashlib
import json
from time import perf_counter

import sympy as sp
from wu088_hh.phys67_first_born import angular_laurent_pairs

start = perf_counter()
t = sp.symbols("t")
sep = sp.Rational(7, 10)
rows = []
for ell, other, radius in ((0, 0, 27), (1, 0, 55), (3, 2, 65), (21, 20, 27), (21, 20, 65)):
    mu = -t / sep + (sep**2 - t**2) / (2 * sep * radius)

    def legendre_recurrence(degree):
        prev, curr = sp.Poly(1, t), sp.Poly(mu, t)
        if degree == 0:
            return prev
        for j in range(1, degree):
            prev, curr = curr, ((2*j+1)*sp.Poly(mu, t)*curr-j*prev).mul_ground(sp.Rational(1, j+1))
        return curr

    poly = legendre_recurrence(ell) * legendre_recurrence(other) * sp.Poly(1+(t+1)/radius, t)
    moments = [(sp.Rational(1, 2), -sp.Rational(1, 2))]
    for n in range(1, poly.degree()+1):
        a, b = moments[-1]
        moments.append(((-sep)**n/2+sp.Rational(n, 2)*a,
                        -sep**n/2+sp.Rational(n, 2)*b))
    direct = tuple(sum(poly.nth(n)*moments[n][i] for n in range(poly.degree()+1)) for i in range(2))
    target = angular_laurent_pairs(ell, other)
    expected = tuple(sum(sp.Rational(p[i].numerator, p[i].denominator)/sp.Integer(radius)**j
                         for j, p in enumerate(target)) for i in range(2))
    assert direct == expected
    rows.append({"ell": ell, "ellprime": other, "radius": radius,
                 "exact_exp_plus_coefficient_match": direct[0] == expected[0],
                 "exact_exp_minus_coefficient_match": direct[1] == expected[1]})

root = Path(__file__).resolve().parents[3]
receipt = {
    "schema": "PHYS67_FIRST_BORN_INDEPENDENT_EXACT_ANGULAR_CHECK_V1",
    "result": "PASS_SCOPED", "execution": "completed", "exit_code": 0,
    "target_code_sha256": hashlib.sha256((root / "src/wu088_hh/phys67_first_born.py").read_bytes()).hexdigest(),
    "check_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "construction": "Legendre three-term recurrence and exponential moment integration-by-parts recurrence",
    "rows": rows, "wall_seconds": perf_counter()-start,
    "scope": "exact angular Laurent identity at five selected pairs/radii; structural derivation in review",
    "radial_quadrature_repeated": False, "HH_R10": "OFF",
}
output = Path(__file__).with_name("FIRST_BORN_INDEPENDENT_CHECK.json")
output.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"result": receipt["result"], "cases": len(rows), "seconds": receipt["wall_seconds"]}))
