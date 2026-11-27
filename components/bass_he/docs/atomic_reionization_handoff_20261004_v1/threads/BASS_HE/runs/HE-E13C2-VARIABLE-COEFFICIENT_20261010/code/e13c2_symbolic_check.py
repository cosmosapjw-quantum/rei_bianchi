#!/usr/bin/env python3
"""Exact rational Taylor-jet checks for E13C2.

Uses only Python's standard library. The reference is direct formal Picard
integration of the variable-coefficient ODE, independently of the compact
cubic formulas in the note. No actual photon/gas history is evaluated.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import hashlib
import json
import platform
import sys


NAMES = (
    "h", "u", "p0", "q0", "q1", "q2", "L0", "L1", "L2",
    "l0", "l1", "l2", "w0", "w1", "w2", "Em", "chi",
)
INDEX = {name: i for i, name in enumerate(NAMES)}
ZERO_MONOMIAL = (0,) * len(NAMES)
ORDER = 3


class Polynomial:
    def __init__(self, terms=None):
        self.terms = {
            monomial: Fraction(coefficient)
            for monomial, coefficient in (terms or {}).items()
            if coefficient and monomial[0] + monomial[1] <= ORDER
        }

    @staticmethod
    def number(value):
        if isinstance(value, Polynomial):
            return value
        return Polynomial({ZERO_MONOMIAL: Fraction(value)})

    @staticmethod
    def symbol(name):
        exponent = list(ZERO_MONOMIAL)
        exponent[INDEX[name]] = 1
        return Polynomial({tuple(exponent): Fraction(1)})

    def __add__(self, other):
        terms = dict(self.terms)
        for monomial, coefficient in self.number(other).terms.items():
            terms[monomial] = terms.get(monomial, Fraction(0)) + coefficient
        return Polynomial(terms)

    __radd__ = __add__

    def __neg__(self):
        return Polynomial({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.number(other))

    def __rsub__(self, other):
        return self.number(other) - self

    def __mul__(self, other):
        terms = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in self.number(other).terms.items():
                monomial = tuple(a + b for a, b in zip(m1, m2))
                if monomial[0] + monomial[1] <= ORDER:
                    terms[monomial] = terms.get(monomial, Fraction(0)) + c1 * c2
        return Polynomial(terms)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * (Fraction(1) / Fraction(other))

    def __pow__(self, power):
        if not isinstance(power, int) or power < 0:
            raise ValueError("nonnegative integer powers only")
        result = self.number(1)
        for _ in range(power):
            result = result * self
        return result

    def integrate_u(self):
        terms = {}
        for monomial, coefficient in self.terms.items():
            m = list(monomial)
            m[1] += 1
            if m[0] + m[1] <= ORDER:
                terms[tuple(m)] = coefficient / m[1]
        return Polynomial(terms)

    def at_u_h(self):
        terms = {}
        for monomial, coefficient in self.terms.items():
            m = list(monomial)
            m[0] += m[1]
            m[1] = 0
            terms[tuple(m)] = terms.get(tuple(m), Fraction(0)) + coefficient
        return Polynomial(terms)

    def zero_symbols(self, names):
        indices = [INDEX[name] for name in names]
        return Polynomial({
            m: c for m, c in self.terms.items()
            if all(m[i] == 0 for i in indices)
        })

    def to_json(self):
        def name(monomial):
            factors = []
            for variable, power in zip(NAMES, monomial):
                if power:
                    factors.append(variable if power == 1 else f"{variable}^{power}")
            return "*".join(factors) or "1"
        return {name(m): str(c) for m, c in sorted(self.terms.items())}


variables = {name: Polynomial.symbol(name) for name in NAMES}
h, u, p0 = (variables[name] for name in ("h", "u", "p0"))
q0, q1, q2 = (variables[name] for name in ("q0", "q1", "q2"))
L0, L1, L2 = (variables[name] for name in ("L0", "L1", "L2"))
l0, l1, l2 = (variables[name] for name in ("l0", "l1", "l2"))
w0, w1, w2 = (variables[name] for name in ("w0", "w1", "w2"))
Em, chi = (variables[name] for name in ("Em", "chi"))
tau = u - h / 2
q = q0 + q1 * tau + q2 * tau**2 / 2
L = L0 + L1 * tau + L2 * tau**2 / 2
lam = l0 + l1 * tau + l2 * tau**2 / 2
w = w0 + w1 * tau + w2 * tau**2 / 2
energy_weight = 1 - tau + tau**2 / 2 - tau**3 / 6


def picard(source, attenuation, initial):
    value = Polynomial.number(initial)
    # Each integration increases degree in h,u. Four iterations suffice
    # through total degree 3, and one further iteration checks stabilization.
    for _ in range(4):
        value = initial + (source - attenuation * value).integrate_u()
    stable = initial + (source - attenuation * value).integrate_u()
    if stable.terms != value.terms:
        raise AssertionError("formal Picard jet did not stabilize")
    return value


P = picard(q, L, p0)
Phat = picard(q0, L0, p0)
e = P - Phat
end = e.at_u_h()
f = q0 - L0 * p0
d = q1 - L1 * p0
cubic = h**3 / 24


def integral(value):
    return value.integrate_u().at_u_h()


checks = []


def check(name, calculated, expected, domain):
    calculated = Polynomial.number(calculated)
    expected = Polynomial.number(expected)
    difference = calculated - expected
    checks.append({
        "id": name,
        "passed": not difference.terms,
        "domain": domain,
        "difference_exact_rational_polynomial": difference.to_json(),
        "calculated_cubic_jet": calculated.to_json(),
    })


check(
    "photon_endpoint",
    end,
    cubic * (q2 - L2 * p0 + 2 * L0 * q1 - 2 * L1 * q0),
    "variable q,L; shared starting stock; smooth event-free Taylor jet",
)
general = integral(w * (lam * P - l0 * Phat))
direct = integral(w * (lam - l0) * Phat)
feedback = integral(w * lam * e)
check(
    "general_weight_absorption",
    general,
    cubic * (w0 * l2 * p0 + 2 * l1 * (w1 * p0 + w0 * f) - 2 * w0 * l0 * d),
    "arbitrary smooth weight with independently specified derivatives",
)
check(
    "direct_coefficient_variation",
    direct,
    cubic * (w0 * l2 * p0 + 2 * l1 * (w1 * p0 + w0 * f)),
    "selected exact split direct term: delta_lambda * frozen_P",
)
check(
    "photon_feedback",
    feedback,
    -h**3 * w0 * l0 * d / 12,
    "selected exact split feedback: continuous_lambda * delta_P",
)
count = integral(lam * P - l0 * Phat)
absorbed_energy = integral(energy_weight * (lam * P - l0 * Phat))
redshift = integral(energy_weight * e)
source_count = integral(q - q0)
source_energy = integral(energy_weight * (q - q0))
count_expected = cubic * (l2 * p0 + 2 * l1 * f - 2 * l0 * d)
energy_expected = cubic * (l2 * p0 + 2 * l1 * (f - p0) - 2 * l0 * d)
check("species_count", count, count_expected, "w=1")
check(
    "species_absorption_energy",
    absorbed_energy,
    energy_expected,
    "B difference divided by epsilon * E_mid; exact exponential weight jet",
)
check(
    "species_heat",
    Em * absorbed_energy - chi * count,
    cubic * ((Em - chi) * (l2 * p0 + 2 * l1 * f - 2 * l0 * d) - 2 * Em * l1 * p0),
    "Q difference divided by epsilon; fixed chi distinct from cutoff",
)
check("redshift", redshift, -h**3 * d / 12, "Z divided by epsilon * E_mid")
check("source_count", source_count, cubic * q2, "integral delta_q")
check(
    "source_energy",
    source_energy,
    cubic * (q2 - 2 * q1),
    "injected energy divided by epsilon * E_mid",
)
all_counts = integral(L * P - L0 * Phat)
all_energy = integral(energy_weight * (L * P - L0 * Phat))
end_energy = (1 - h / 2 + h**2 / 8 - h**3 / 48) * end
check(
    "number_ledger",
    end + all_counts - source_count,
    0,
    "same initial photon stock; sum_i lambda_i = L",
)
check(
    "energy_ledger",
    end_energy + all_energy + redshift - source_energy,
    0,
    "retains E_end/E_mid = exp(-h/2), including its formal jet",
)
check(
    "constant_coefficients_limit",
    end.zero_symbols(("q1", "q2", "L1", "L2")),
    0,
    "constant q,L give identical photon models",
)
check(
    "homogeneous_affine_opacity_limit",
    end.zero_symbols(("q0", "q1", "q2", "L2")),
    0,
    "q=0 and affine L; scalar integrated optical depth is midpoint exact",
)
check(
    "constant_opacity_linear_source_limit",
    end.zero_symbols(("q2", "L1", "L2")),
    h**3 * L0 * q1 / 12,
    "q source-gradient attenuation covariance has positive sign",
)
check(
    "constant_source_linear_opacity_limit",
    end.zero_symbols(("q1", "q2", "L2")),
    -h**3 * L1 * q0 / 12,
    "newborn survival feedback has negative opacity-gradient sign",
)
r = (q - q0) - (L - L0) * Phat
e1 = picard(r, L0, Polynomial.number(0))
remainder = picard(-(L - L0) * e, L0, Polynomial.number(0))
check(
    "duhamel_linear_response_remainder_jet",
    e - e1 - remainder,
    0,
    "formal jet of exact identity (e-e1)' + L0(e-e1) = -delta_L * e",
)

report = {
    "schema": "bass-he-e13c2-formal-taylor-verification-v1",
    "claim_status": "implementation-verified",
    "method": "exact Fraction sparse-polynomial Picard jet, no sampled parameter values",
    "formal_order": ORDER,
    "polynomial_truncation": "total degree of h,u; all physical coefficient symbols algebraically independent",
    "python": platform.python_version(),
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "counts": {"passed": sum(c["passed"] for c in checks), "total": len(checks)},
    "all_passed": all(c["passed"] for c in checks),
    "limitations": [
        "formal smooth event-free Taylor identities only",
        "no interval enclosure or certified remainder",
        "no numerical photon history, source evaluation, or gas advancement",
        "p0 can replace frozen midpoint stock only in the cubic leading coefficient",
        "exact Duhamel identity itself is directly derived in the accompanying note; this checks its cubic jet",
    ],
    "environment_notes": [
        "sympy import absent in both default and primary runtime Python",
        "no installation attempted; standard-library exact arithmetic used",
    ],
    "checks": checks,
}
output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("E13C2_SYMBOLIC_VERIFICATION.json")
output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"all_passed": report["all_passed"], "counts": report["counts"], "output": str(output)}))
sys.exit(0 if report["all_passed"] else 1)
