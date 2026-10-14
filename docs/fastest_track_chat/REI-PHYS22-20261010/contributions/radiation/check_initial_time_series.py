#!/usr/bin/env python3
"""New PHYS22 exact time-jet check; no PHYS21 kernel implementation imported.

Expand original directional E, lambda, exp(-integral lambda), and source births
as rational polynomials in (epsilon, cohort age, birth time). All comparisons
concern NEW initial-time coefficients, birth delays, or their time-jet ledgers.
No gas IVP, native execution, or full-history transport is performed.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from math import factorial
from pathlib import Path

N = 4
ZERO = (0, 0, 0)  # epsilon, age u, birth b


class Poly:
    def __init__(self, terms=None):
        self.a = {k: F(v) for k, v in (terms or {}).items()
                  if v and k[0] <= 2 and k[1] + k[2] <= N}

    @staticmethod
    def scalar(x):
        return Poly({ZERO: F(x)})

    def __add__(self, other):
        if not isinstance(other, Poly):
            other = Poly.scalar(other)
        out = dict(self.a)
        for k, v in other.a.items():
            out[k] = out.get(k, F(0)) + v
        return Poly(out)

    __radd__ = __add__

    def __neg__(self):
        return Poly({k: -v for k, v in self.a.items()})

    def __sub__(self, other):
        return self + (-other if isinstance(other, Poly) else -F(other))

    def __mul__(self, other):
        if not isinstance(other, Poly):
            other = Poly.scalar(other)
        out = {}
        for a, va in self.a.items():
            for b, vb in other.a.items():
                k = tuple(a[j] + b[j] for j in range(3))
                if k[0] <= 2 and k[1] + k[2] <= N:
                    out[k] = out.get(k, F(0)) + va * vb
        return Poly(out)

    __rmul__ = __mul__

    def pow_nonnegative(self, n):
        answer = Poly.scalar(1)
        for _ in range(n):
            answer = answer * self
        return answer

    def exp_zero(self):
        if self.a.get(ZERO, F(0)):
            raise ValueError("exp_zero requires zero scalar term")
        answer = Poly.scalar(1)
        term = Poly.scalar(1)
        for k in range(1, N + 1):
            term = term * self * F(1, k)
            answer = answer + term
        return answer

    def unit_power(self, power):
        if self.a.get(ZERO, F(0)) != 1:
            raise ValueError("unit_power requires scalar term one")
        z = self - 1
        answer = Poly.scalar(1)
        term = Poly.scalar(1)
        choose = F(1)
        for k in range(1, N + 1):
            term = term * z
            choose *= F(power - (k - 1), k)
            answer = answer + choose * term
        return answer

    def integrate_age(self):
        return Poly({(e, u + 1, b): v / (u + 1)
                     for (e, u, b), v in self.a.items()})

    def eps2_initial(self):
        return {u: v for (e, u, b), v in self.a.items() if e == 2 and b == 0}

    def eps2_birth_integral(self):
        # Integral_0^t (t-b)^u b^b db = u! b!/(u+b+1)! t^(u+b+1).
        answer = {}
        for (e, u, b), v in self.a.items():
            if e == 2:
                n = u + b + 1
                answer[n] = answer.get(n, F(0)) + v * F(
                    factorial(u) * factorial(b), factorial(n))
        return {k: v for k, v in answer.items() if v}


U = Poly({(0, 1, 0): 1})
BIRTH = Poly({(0, 0, 1): 1})
EPS = Poly({(1, 0, 0): 1})
SIGMA = (F(2), F(-1, 2), F(-3, 2))
Q = sum(x * x for x in SIGMA)
# Consumed Q2/Q4 exact angular rule from PHYS21; no old moment test replay.
DIRECTION_SQUARE_CLASSES = [
    ((F(1), F(0), F(0)), F(2, 15)),
    ((F(0), F(1), F(0)), F(2, 15)),
    ((F(0), F(0), F(1)), F(2, 15)),
    ((F(1, 3), F(1, 3), F(1, 3)), F(3, 5)),
]


def spectrum(terms, energy_power):
    """Term (amplitude at 0, absolute-time derivative, energy exponent)."""
    return sum(((a0 + a1 * (BIRTH + U)) * energy_power(p)
                for a0, a1, p in terms), Poly())


def value(terms, eb, derivative=0, absolute_time_derivative=False):
    return sum(((a1 if absolute_time_derivative else a0)
                * F(p) ** derivative * eb ** p for a0, a1, p in terms), F(0))


def curvature(terms, eb, derivative=0, absolute_time_derivative=False):
    return value(terms, eb, derivative + 2, absolute_time_derivative) + 3 * value(
        terms, eb, derivative + 1, absolute_time_derivative)


def multiply_by_energy(terms):
    return [(a0, a1, p + 1) for a0, a1, p in terms]


def heat_terms(terms, chi):
    return multiply_by_energy(terms) + [(-chi * a0, -chi * a1, p)
                                       for a0, a1, p in terms]


def directional_jets(case):
    averaged = {key: Poly() for key in ["N", "A", "U", "EA", "shear_work", "L"]}
    for m2, weight in DIRECTION_SQUARE_CLASSES:
        exponentials = [(-2 * sig * EPS * U).exp_zero() for sig in SIGMA]
        r_squared = sum((m * ex for m, ex in zip(m2, exponentials)), Poly())
        def energy_power(p):
            return (case["Eb"] ** p * (-p * case["H"] * U).exp_zero()
                    * r_squared.unit_power(F(p, 2)))
        energy = energy_power(1)
        lam = spectrum(case["lambda"], energy_power)
        survival = (-lam.integrate_age()).exp_zero()
        endpoint = spectrum(case["L"], energy_power)
        sigma_numerator = sum((m * sig * ex for m, sig, ex in
                               zip(m2, SIGMA, exponentials)), Poly())
        shear_work = (EPS * survival * energy * sigma_numerator
                      * r_squared.unit_power(F(-1)))
        rays = {"N": survival, "A": survival * lam, "U": survival * energy,
                "EA": survival * lam * energy, "shear_work": shear_work,
                "L": survival * endpoint}
        for key in averaged:
            averaged[key] = averaged[key] + weight * rays[key]
    return averaged


def jet_derivative(jet):
    return {k - 1: k * v for k, v in jet.items() if k}


def jet_sum(*weighted_jets):
    answer = {}
    for weight, jet in weighted_jets:
        for k, v in jet.items():
            answer[k] = answer.get(k, F(0)) + weight * v
    return {k: v for k, v in answer.items() if v}


def within(jet, n):
    return {k: v for k, v in jet.items() if k <= n and v}


def encode_jet(jet):
    return {str(k): str(v) for k, v in sorted(jet.items())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    destination = Path(args.output)
    if destination.exists():
        raise SystemExit("Refusing to overwrite output")
    generic_lam = [(F(3, 7), F(-2, 11), 2), (F(1, 19), F(1, 23), -3)]
    inverse_lam = [(F(2, 7), F(1, 17), -3)]
    gray_lam = [(F(3, 8), F(1, 7), 0)]
    cases = [
        {"name": "mixed_spectrum_nonstationary", "H": F(1, 13), "Eb": F(2),
         "lambda": generic_lam,
         "L": [(F(5, 9), F(4, 15), -1), (F(2, 5), F(0), 3)]},
        {"name": "inverse_cube_events", "H": F(1, 29), "Eb": F(3, 2),
         "lambda": inverse_lam, "L": inverse_lam},
        {"name": "gray_events", "H": F(1, 31), "Eb": F(5, 3),
         "lambda": gray_lam, "L": gray_lam},
        {"name": "generic_survival", "H": F(1, 11), "Eb": F(7, 5),
         "lambda": [(F(5, 7), F(-1, 13), -2)], "L": [(F(1), F(0), 0)]},
        {"name": "mixed_primary_heat", "H": F(1, 13), "Eb": F(2),
         "lambda": generic_lam, "L": heat_terms(generic_lam, F(9, 7))},
        {"name": "isolated_curvature_zero", "H": F(1, 10), "Eb": F(1),
         "lambda": [(F(5), F(0), -1), (F(1), F(0), 2)],
         "L": [(F(5), F(0), -1), (F(1), F(0), 2)]},
    ]
    checks = []
    outputs = []
    def check(name, actual, expected):
        passed = actual == expected
        checks.append({"name": name, "passed": passed,
                       "actual": actual if isinstance(actual, dict) else str(actual),
                       "expected": expected if isinstance(expected, dict) else str(expected)})
    for case in cases:
        jets = directional_jets(case)
        eb, hubble, lam_terms, l_terms = case["Eb"], case["H"], case["lambda"], case["L"]
        lam = value(lam_terms, eb)
        dlambda = value(lam_terms, eb, 1)
        clambda = curvature(lam_terms, eb)
        tclambda = curvature(lam_terms, eb, absolute_time_derivative=True) - hubble * curvature(lam_terms, eb, 1)
        endpoint = value(l_terms, eb)
        dl = value(l_terms, eb, 1)
        cl = curvature(l_terms, eb)
        abs_cl = curvature(l_terms, eb, absolute_time_derivative=True)
        tcl = abs_cl - hubble * curvature(l_terms, eb, 1)
        k3 = tcl - lam * cl - dl * dlambda - endpoint * clambda / 3
        initial = {key: item.eps2_initial() for key, item in jets.items()}
        births = {key: item.eps2_birth_integral() for key, item in jets.items()}
        pre = case["name"] + ":"
        check(pre + "initial_t2_t3", encode_jet(within(initial["L"], 3)),
              encode_jet({k: v for k, v in {2: Q * cl / 15, 3: Q * k3 / 15}.items() if v}))
        check(pre + "continuous_birth_t3_t4", encode_jet(within(births["L"], 4)),
              encode_jet({k: v for k, v in {3: Q * cl / 45,
                         4: Q * (abs_cl / 12 + k3 / 4) / 15}.items() if v}))
        survival3 = -Q * clambda / 45
        survival4 = Q * (dlambda ** 2 / 4 + lam * clambda / 3 - tclambda / 4) / 15
        check(pre + "survival_initial_t3_t4", encode_jet(within(initial["N"], 4)),
              encode_jet({k: v for k, v in {3: survival3, 4: survival4}.items() if v}))
        check(pre + "survival_birth_first_order", encode_jet(within(births["N"], 4)),
              encode_jet({4: survival3 / 4} if survival3 else {}))
        check(pre + "initial_count_jet_ledger", encode_jet(within(jet_derivative(initial["N"]), 3)),
              encode_jet(within(jet_sum((-1, initial["A"])), 3)))
        check(pre + "continuous_count_jet_ledger", encode_jet(within(jet_derivative(births["N"]), 4)),
              encode_jet(within(jet_sum((-1, births["A"])), 4)))
        check(pre + "initial_energy_jet_ledger", encode_jet(within(jet_derivative(initial["U"]), 3)),
              encode_jet(within(jet_sum((-hubble, initial["U"]),
                                      (-1, initial["EA"]), (-1, initial["shear_work"])), 3)))
        check(pre + "continuous_energy_jet_ledger", encode_jet(within(jet_derivative(births["U"]), 4)),
              encode_jet(within(jet_sum((-hubble, births["U"]),
                                      (-1, births["EA"]), (-1, births["shear_work"])), 4)))
        outputs.append({"name": case["name"], "H": str(hubble), "Eb": str(eb),
                        "lambda_terms": [[str(x) for x in row] for row in lam_terms],
                        "L_terms": [[str(x) for x in row] for row in l_terms],
                        "CL": str(cl), "k3": str(k3), "C_lambda": str(clambda),
                        "initial_jets": {k: encode_jet(v) for k, v in initial.items()},
                        "birth_integrated_jets": {k: encode_jet(v) for k, v in births.items()}})
    by_name = {case["name"]: case for case in outputs}
    inverse = by_name["inverse_cube_events"]
    check("degenerate_inverse_cube_event_starts_t3", min(map(int, inverse["initial_jets"]["A"])), 3)
    check("degenerate_inverse_cube_count_starts_t4", min(map(int, inverse["initial_jets"]["N"])), 4)
    check("degenerate_gray_event_identically_zero_through_t4", by_name["gray_events"]["initial_jets"]["A"], {})
    check("isolated_curvature_zero_does_not_kill_t3", by_name["isolated_curvature_zero"]["k3"], "-12")
    result = {
        "schema_version": "1.0", "task": "REI-PHYS22_INITIAL_TIME_COUPLED_SHEAR_RESPONSE",
        "contributor": "/root/phys22_radiation", "evidence_state": "exact rational computational check",
        "method": "Original directional energy/hazard/survival formal epsilon-time-birth series; exact angular Q4 and Beta birth integrals; no PHYS21 formula implementation imported",
        "scope": "Six declared normalized smooth diagnostics; new initial-time/source-order coefficients and time-jet count/energy identities",
        "not_claimed": ["actual FT03 numerical gas coefficient", "gas IVP", "native implementation correctness", "finite-time error enclosure", "replay of closed PHYS21 checks"],
        "convention": "epsilon^2 coefficient, half the second epsilon derivative; time jets use raw monomial coefficients without factorial",
        "truncation": {"epsilon_degree": 2, "cohort_age_plus_birth_degree": N,
                       "birth_integral_max_degree": N + 1},
        "sigma": [str(x) for x in SIGMA], "trace_sigma_squared": str(Q),
        "units": "diagnostic rational time/energy scales normalized; formula dimensions checked separately in note",
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "cases": outputs, "checks": checks,
        "passed": sum(c["passed"] for c in checks), "total": len(checks),
        "exact_failure_count": sum(not c["passed"] for c in checks),
        "preserved": {"physical": "HOLD", "legacy_interval": "[160,161] FAIL",
                      "tick": 160, "auxiliary_escape": "FAIL", "HH_RCT_CR": "OFF",
                      "precision_atomic": "PARKED"}}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": result["passed"], "total": result["total"],
                      "exact_failure_count": result["exact_failure_count"],
                      "output_sha256": sha256(destination.read_bytes()).hexdigest()}))
    raise SystemExit(0 if result["exact_failure_count"] == 0 else 1)


if __name__ == "__main__":
    main()
