"""New exact rational checks of HE36 derivation; no integration or donor execution."""
from fractions import Fraction as F
from pathlib import Path
import json
import time
import hashlib

start = time.perf_counter()

def add(p, q):
    out = p.copy()
    for k, v in q.items():
        out[k] = out.get(k, F(0)) + v
    return {k: v for k, v in out.items() if v}

def mul(p, q):
    out = {}
    for k, v in p.items():
        for ell, w in q.items():
            key = tuple(x + y for x, y in zip(k, ell))
            out[key] = out.get(key, F(0)) + v * w
    return {k: v for k, v in out.items() if v}

def scale(p, value):
    return {k: F(value) * v for k, v in p.items() if value * v}

def power(p, exponent):
    result = {(0, 0, 0, 0, 0): F(1)}
    for _ in range(exponent):
        result = mul(result, p)
    return result

def variable(i):
    key = tuple(int(j == i) for j in range(5))
    return {key: F(1)}

a, b, alpha, k1, k2 = [variable(i) for i in range(5)]
ab = mul(a, b)
AA = add(add(mul(power(a, 2), alpha), scale(mul(ab, k1), 2)), mul(power(b, 2), k2))
BB = add(add(mul(power(b, 2), alpha), scale(mul(ab, k1), 2)), mul(power(a, 2), k2))
CC = mul(ab, add(add(alpha, k2), scale(k1, -2)))
det = add(mul(AA, BB), scale(power(CC, 2), -1))
rhs = mul(power(add(a, b), 2), add(mul(power(add(a, scale(b, -1)), 2), mul(alpha, k2)), scale(mul(mul(ab, k1), add(alpha, k2)), 2)))
det_residual = add(det, scale(rhs, -1))
assert not det_residual

def xmaxwell(k):
    value = F(1)
    for j in range(k):
        value *= F(3, 2) + j
    return value

def weighted_moment(k, coefficients):
    return sum((coef * xmaxwell(k + p) for p, coef in enumerate(coefficients)), F(0))

K1 = [F(1)]
K2 = [F(5, 2), F(-2), F(2, 5)]
moments = [[weighted_moment(j, K) for j in range(3)] for K in [K1, K2]]
assert moments == [[F(1), F(3, 2), F(15, 4)], [F(1), F(3, 2), F(27, 4)]]
assert all(m[0] * m[2] >= m[1] * m[1] for m in moments)
stf = [F(4, 15) * m[2] for m in moments]
assert stf == [F(1), F(9, 5)]

def blocks(a, b, alpha, k1, k2):
    return (a*a*alpha + 2*a*b*k1 + b*b*k2,
            b*b*alpha + 2*a*b*k1 + a*a*k2,
            a*b*(alpha - 2*k1 + k2))

equal_blocks = [blocks(F(1, 2), F(1, 2), m[0], F(2, 3)*m[1], F(4, 15)*m[2]) for m in moments]
assert equal_blocks == [(F(1), F(1), F(0)), (F(6, 5), F(6, 5), F(1, 5))]
loss_rates = [[x[0] - abs(x[2]), x[0] + abs(x[2])] for x in equal_blocks]
assert loss_rates == [[F(1), F(1)], [F(1), F(7, 5)]]

s = F(1, 2)
power_k1 = F(2, 3) * (s + F(3, 2))
power_k2 = F(4, 15) * (s + F(3, 2)) * (s + F(5, 2))
power_block = blocks(F(1, 2), F(1, 2), F(1), power_k1, power_k2)
assert power_block == (F(79, 60), F(79, 60), F(-1, 60))
assert [power_block[0] - abs(power_block[2]), power_block[0] + abs(power_block[2])] == [F(13, 10), F(4, 3)]

source = Path(__file__).read_bytes()
report = {
    "status": "PASS_EXACT_RATIONAL_SCOPED",
    "method": "standard-library rational polynomial coefficient expansion and Maxwell Gamma-recursion moments",
    "checks": {
        "finite_mass_determinant_residual_polynomial": {},
        "equal_alpha_beta_counterexample_moments": [[str(v) for v in m] for m in moments],
        "stationary_loss_coefficients": [str(v) for v in stf],
        "equal_mass_finite_blocks": [[str(v) for v in m] for m in equal_blocks],
        "equal_mass_finite_loss_rates": [[str(v) for v in m] for m in loss_rates],
        "constant_cross_section_negative_cross_block": [str(v) for v in power_block],
        "constant_cross_section_loss_rates": ["13/10", "4/3"],
        "positive_moment_determinants": [str(m[0]*m[2]-m[1]*m[1]) for m in moments]
    },
    "source_sha256": hashlib.sha256(source).hexdigest(),
    "wall_seconds": time.perf_counter() - start,
    "old_scientific_replays": 0,
    "new_ivps": 0,
    "new_renders": 0,
    "new_empirical_rate_admissions": 0,
    "limitations": ["No production kernel was tested", "No birth or outgoing differential moments supplied", "Grad first variation only", "No empirical fitted second-derivative accuracy certificate"]
}
Path(__file__).with_name("CHECKS.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
