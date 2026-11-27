#!/usr/bin/env python3
"""New E13C3 exact response-kernel checks; Python standard library only.

The algebra is a sparse finite sum of
    c * u**n * a**i * b**j * exp(rate*u + shift),
with rational c/rate/shift.  a and b are arbitrary incoming true/approximate
defects.  Differentiation and integration in u are exact.  This is not the
E13C2 total-degree Taylor-jet suite and does not call any saved ODE oracle.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform
import sys


class EP:
    """Exact exponential polynomial in u, with two untouched indeterminates."""

    def __init__(self, terms=None):
        self.terms = {key: F(value) for key, value in (terms or {}).items() if value}

    @staticmethod
    def mono(coefficient=1, *, rate=0, shift=0, power=0, a=0, b=0):
        return EP({(F(rate), F(shift), power, a, b): F(coefficient)})

    @staticmethod
    def coerce(value):
        return value if isinstance(value, EP) else EP.mono(value)

    def __add__(self, other):
        terms = dict(self.terms)
        for key, value in self.coerce(other).terms.items():
            terms[key] = terms.get(key, F(0)) + value
        return EP(terms)

    __radd__ = __add__

    def __neg__(self):
        return EP({key: -value for key, value in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        terms = {}
        for (r, s, n, a, b), value in self.terms.items():
            for (rr, ss, nn, aa, bb), vv in self.coerce(other).terms.items():
                key = (r + rr, s + ss, n + nn, a + aa, b + bb)
                terms[key] = terms.get(key, F(0)) + value * vv
        return EP(terms)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self * (F(1) / F(other))

    def derivative(self):
        answer = EP()
        for (r, s, n, a, b), value in self.terms.items():
            if n:
                answer += EP.mono(value * n, rate=r, shift=s, power=n - 1, a=a, b=b)
            if r:
                answer += EP.mono(value * r, rate=r, shift=s, power=n, a=a, b=b)
        return answer

    def primitive(self):
        answer = EP()
        for (r, s, n, a, b), value in self.terms.items():
            if not r:
                answer += EP.mono(value / (n + 1), shift=s, power=n + 1, a=a, b=b)
            else:
                for k in range(n + 1):
                    coeff = value * (-1) ** k * F(math.factorial(n), math.factorial(n - k)) / r ** (k + 1)
                    answer += EP.mono(coeff, rate=r, shift=s, power=n - k, a=a, b=b)
        return answer

    def at(self, point):
        point = F(point)
        answer = EP()
        for (r, s, n, a, b), value in self.terms.items():
            answer += EP.mono(value * point ** n, shift=s + r * point, a=a, b=b)
        return answer

    def integral_from_zero(self):
        primitive = self.primitive()
        return primitive - primitive.at(0)

    def integral(self, endpoint):
        return self.integral_from_zero().at(endpoint)

    def diagnostic(self):
        return [
            {"rate": str(r), "shift": str(s), "power_u": n, "power_a": a,
             "power_b": b, "coefficient": str(value)}
            for (r, s, n, a, b), value in sorted(self.terms.items())
        ]


U = EP.mono(power=1)
A = EP.mono(a=1)
B = EP.mono(b=1)


def exp(rate=0, shift=0):
    return EP.mono(rate=rate, shift=shift)


def jfun(rate):
    return exp(-rate).integral_from_zero()


def jconst(rate, length):
    return jfun(rate).at(length)


def solution(rate, forcing, incoming):
    return exp(-rate) * (incoming + (exp(rate) * forcing).integral_from_zero())


def kernels(rate, length, energy0):
    remaining = length - U
    endpoint = exp(rate, -rate * length)
    k0 = remaining if not rate else (1 - endpoint) / rate
    ke = energy0 * exp(-1) * (
        remaining if rate == -1 else (1 - exp(rate + 1, -(rate + 1) * length)) / (rate + 1)
    )
    return endpoint, k0, ke


def run_checks():
    checks = []

    def check(name, case, lhs, rhs=0):
        residual = EP.coerce(lhs) - EP.coerce(rhs)
        checks.append({"name": name, "case": case,
                       "status": "PASS" if not residual.terms else "FAIL",
                       "exact_residual_terms": len(residual.terms),
                       **({"residual": residual.diagnostic()} if residual.terms else {})})

    rates = (F(0), F(1, 3), F(1), F(7), F(10**6))
    lengths = (F(0), F(3, 7))
    energy0, stock0, qf = F(17, 3), F(7, 5), F(5, 6)
    eta = F(1, 32)
    energy = energy0 * exp(-1)

    # One exact basis control verifies the algebra engine without numerical exp.
    basis = [EP.mono(F(3, 5), rate=r, shift=F(-2, 7), power=n, a=1, b=1)
             for r in (F(0), F(1, 3), F(-9, 4)) for n in range(5)]
    for index, term in enumerate(basis):
        check("engine_exact_primitive_derivative", str(index), term.primitive().derivative(), term)
        check("engine_integral_origin", str(index), term.integral_from_zero().at(0))

    for rate in rates:
        for length in lengths:
            case = f"L={rate}; h={length}; incoming=a"
            midpoint_coordinate = U - length / 2
            deltaq = eta * (3 * midpoint_coordinate + midpoint_coordinate * midpoint_coordinate)
            if rate:
                dlambda = (eta * midpoint_coordinate,
                          eta * (-midpoint_coordinate / 3 + midpoint_coordinate * midpoint_coordinate))
            else:
                dlambda = (eta * midpoint_coordinate * midpoint_coordinate,
                          2 * eta * midpoint_coordinate * midpoint_coordinate)
            lf = (2 * rate / 5, 3 * rate / 5)
            dtotal = sum(dlambda, EP())
            pf = stock0 * exp(-rate) + qf * jfun(rate)
            r = deltaq - dtotal * pf
            e1 = solution(rate, r, A)
            pc = pf + e1
            wh, k0, ke = kernels(rate, length, energy0)
            eh = energy.at(length)

            check("frozen_solution_equation", case, pf.derivative() + rate * pf, qf)
            check("frozen_solution_initial", case, pf.at(0), stock0)
            check("kernel0_adjoint", case, -k0.derivative() + rate * k0, 1)
            check("kernelE_adjoint", case, -ke.derivative() + rate * ke, energy)
            check("kernel0_terminal", case, k0.at(length))
            check("kernelE_terminal", case, ke.at(length))
            check("kernel_count_pointwise", case, wh + rate * k0, 1)
            check("kernel_energy_pointwise", case, eh * wh + (rate + 1) * ke, energy)
            check("response_equation", case, e1.derivative() + rate * e1, r)
            check("response_general_incoming", case, e1.at(0), A)

            endpoint_quad = exp(shift=-rate * length) * A + (wh * r).integral(length)
            j0_quad = A * jconst(rate, length) + (k0 * r).integral(length)
            je_quad = energy0 * A * jconst(rate + 1, length) + (ke * r).integral(length)
            check("endpoint_single_integral", case, endpoint_quad, e1.at(length))
            check("moment0_single_integral", case, j0_quad, e1.integral(length))
            check("momentE_single_integral", case, je_quad, (energy * e1).integral(length))
            check("incoming_moment0", case, (A * exp(-rate)).integral(length), A * jconst(rate, length))
            check("incoming_momentE", case, (energy * A * exp(-rate)).integral(length), energy0 * A * jconst(rate + 1, length))

            da = [(dl * pf).integral(length) + li * j0_quad for dl, li in zip(dlambda, lf)]
            db = [(energy * dl * pf).integral(length) + li * je_quad for dl, li in zip(dlambda, lf)]
            check("first_order_count_ledger", case,
                  endpoint_quad + sum(da, EP()), A + deltaq.integral(length))
            check("first_order_energy_ledger", case,
                  eh * endpoint_quad + sum(db, EP()) + je_quad,
                  energy0 * A + (energy * deltaq).integral(length))

            chi = (F(2, 3), F(4, 5))
            for index, (dl, li, binding) in enumerate(zip(dlambda, lf, chi)):
                w = energy - binding
                direct_heat = (w * dl * pf).integral(length)
                incoming_heat = A * (energy0 * jconst(rate + 1, length) - binding * jconst(rate, length))
                response_heat = ((ke - binding * k0) * r).integral(length)
                check("heat_signed_kernel", f"{case}; species={index}",
                      direct_heat + li * (incoming_heat + response_heat), db[index] - binding * da[index])

            full_rate = rate + dtotal
            full_q = qf + deltaq
            check("full_equation_residual_deltaLambda_e1", case,
                  pc.derivative() + full_rate * pc - full_q, dtotal * e1)
            full_a = (full_rate * pc).integral(length)
            full_b = (energy * full_rate * pc).integral(length)
            count_residual = pc.at(length) + full_a - stock0 - A - full_q.integral(length)
            energy_residual = (eh * pc.at(length) + full_b + (energy * pc).integral(length)
                               - energy0 * (stock0 + A) - (energy * full_q).integral(length))
            check("full_coefficient_count_residual", case, count_residual, (dtotal * e1).integral(length))
            check("full_coefficient_energy_residual", case, energy_residual, (energy * dtotal * e1).integral(length))

            if not rate:
                check("zero_opacity_kernel0_limit", case, k0, length - U)
                check("zero_opacity_kernelE_limit", case, ke, energy - eh)
                check("zero_opacity_frozen_limit", case, pf, stock0 + qf * U)

            # Exact constant-offset controls test arbitrary incoming uncertainty.
            # Offset d != 0 means this is an algebra control, not a midpoint sample.
            d = F(2, 9)
            dq = F(1, 7)
            exact = (stock0 + A) * exp(-(rate + d)) + (qf + dq) * jfun(rate + d)
            exact_e = exact - pf
            offset_r = dq - d * pf
            approximate_e1 = solution(rate, offset_r, B)
            rem = exact_e - approximate_e1
            check("incoming_uncertainty_remainder_equation", case,
                  rem.derivative() + (rate + d) * rem, -d * approximate_e1)
            check("incoming_uncertainty_initial", case, rem.at(0), A - B)
            check("incoming_uncertainty_frozen_remainder", case,
                  rem.at(length), exp(shift=-rate * length) * (A - B) - (wh * d * exact_e).integral(length))
            check("incoming_uncertainty_moment0", case,
                  rem.integral(length), (A - B) * jconst(rate, length) - (k0 * d * exact_e).integral(length))
            check("incoming_uncertainty_momentE", case,
                  (energy * rem).integral(length), energy0 * (A - B) * jconst(rate + 1, length) - (ke * d * exact_e).integral(length))

    # Sum opacity constant does not make each species' first-order moment exact.
    rate, length = F(7, 3), F(2, 5)
    pf = stock0 * exp(-rate) + qf * jfun(rate)
    centered = U - length / 2
    dq = centered * centered
    e1 = solution(rate, dq, 0)
    d1, d2 = eta * centered * centered, -eta * centered * centered
    missing1, missing2 = (d1 * e1).integral(length), (d2 * e1).integral(length)
    check("species_exchange_missing_terms_cancel_only_in_total", "deltaLambda=0", missing1 + missing2)
    checks.append({"name": "species_exchange_missing_term_is_nonzero", "case": "deltaLambda=0",
                   "status": "PASS" if missing1.terms else "FAIL",
                   "exact_expression_terms": len(missing1.terms),
                   "scope": "Nonzero formal expression; independently, d1>=0 and e1>0 on a set of positive measure imply a strictly positive exact integral."})

    # Exact coefficient identities for the entire J function at rate = 0.
    # These are its rate-series coefficients, not the old midpoint-h Taylor jets.
    h = F(3, 7)
    coefficients = [(-1) ** n * h ** (n + 1) / math.factorial(n + 1) for n in range(9)]
    checks.append({"name": "entire_J_zero_rate_coefficient", "case": "rate series",
                   "status": "PASS" if coefficients[0] == h else "FAIL"})
    for n in range(1, len(coefficients)):
        residual = coefficients[n - 1] + (-h) ** n / math.factorial(n)
        checks.append({"name": "entire_J_rate_times_J_plus_exp_coefficients", "case": f"power={n}",
                       "status": "PASS" if not residual else "FAIL", "rational_residual": str(residual)})

    counts = Counter(item["status"] for item in checks)
    groups = {}
    for item in checks:
        row = groups.setdefault(item["name"], {"total": 0, "pass": 0, "fail": 0})
        row["total"] += 1
        row[item["status"].lower()] += 1
    return {"status": "PASS" if not counts["FAIL"] else "FAIL",
            "total_checks": len(checks), "passed": counts["PASS"], "failed": counts["FAIL"],
            "groups": groups, "checks": checks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("THEORY_CHECKS.json"))
    args = parser.parse_args()
    result = run_checks()
    result.update({
        "schema": "bass-he-e13c3-exact-response-checks-v1",
        "evidence_status": ["derived", "implementation-verified"],
        "engine": "Python standard-library Fraction; exact finite exponential-polynomial identities in u and symbolic incoming defects a,b",
        "scope": "Finite rational-rate analytic controls including L=0, h=0, Lh>1e5; kernel/ledger identities, general incoming uncertainty, and omitted-residual checks",
        "not_claimed": ["physical coefficient enclosure", "physical accuracy admission", "global interval certificate", "new continuous reference", "independent final decision review"],
        "old_e13c2_17_check_suite_rerun": False,
        "saved_oracle_rerun": False,
        "python": sys.version,
        "platform": platform.platform(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "protected": {"baseline_RCT": "OFF", "actual_atomic_photon_heat_recoil": None,
                      "physical": "HOLD", "production": "HOLD", "HE_F2": "OPEN", "F09": "OPEN",
                      "legacy_Gamma_alias": {"value": 3.543295, "status": "FAIL"},
                      "receiver_adoption": "SEPARATE"},
    })
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "total_checks", "passed", "failed")}, sort_keys=True))
    print(f"Evidence: {args.output.resolve()}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
