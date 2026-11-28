#!/usr/bin/env python3
"""Independent exact scalar witnesses for the PHYS69 mathematical review.

This imports no PHYS69 or PHYS68 solver and performs no Coulomb evaluation,
radial quadrature, historical test, or native integration. Universal claims
are proved in INDEPENDENT_REVIEW.md; these are reproducible scalar witnesses.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def exact(value: F) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def display(value: F) -> str:
    with localcontext() as ctx:
        ctx.prec = 45
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def tail_sum(cutoff: int) -> F:
    x, a = F(1, 100), cutoff + 2
    return x ** (cutoff + 1) * (
        F(a * a, 1) / (1 - x)
        + 2 * a * x / (1 - x) ** 2
        + x * (1 + x) / (1 - x) ** 3
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    previous = repo / "research/hh_phys68_20261019/profiles/run_l28_t65_completed/CERTIFICATE.json"
    raw = previous.read_bytes()
    expected = "ddaae206009a276def281af5526851ceb717baf2e0de5f8472552a9db340de9a"
    assert hashlib.sha256(raw).hexdigest() == expected
    cert = json.loads(raw)
    gamma_record = cert["analytic_radial_cutoff"]["gamma"]
    gamma = F(int(gamma_record["numerator_hex"], 16), int(gamma_record["denominator_hex"], 16))
    assert gamma == 5929
    x = F(41, 20)
    term, partial = F(1), F(1)
    for n in range(1, 17):
        term *= x / n
        partial += term
    tail = (term * x / 17) / (1 - x / 18)
    exponential_upper = partial + tail
    assert exponential_upper < 8
    # 49*j^2 - 378*j - 3591 at j=t+20: all coefficients positive.
    shifted = [49 * 20**2 - 378 * 20 - 3591, 2 * 49 * 20 - 378, 49]
    assert shifted == [8449, 1582, 49]
    j, k = 20, F(7, 10)
    a, r = (j - 1) / k, (j + 1) / k
    angular = j * (j + 1)
    nu_a = k * k + 2 / a - angular / (a * a)
    nu_r = k * k + 2 / r - angular / (r * r)
    assert a >= 27 and nu_a == -F(7 * j + 91, 100 * (j - 1)**2)
    assert nu_r == F(189, 100 * (j + 1)) and 0 < nu_r < k * k
    assert r < F(angular, 2) and k * k + F(1, angular) < F(1, 2)
    exponent_at_20 = 2 + F(14 * j + 182, 49 * (j - 1)**2)
    assert exponent_at_20 < F(41, 20)
    m = F(1, 4 * 10**19)
    prefactor = gamma * F(800, 189)**2 * (4 * m / 9)**2 * 10**43 / 16
    angular_bounds = []
    for cutoff in [28, 35, 36, 64]:
        s = tail_sum(cutoff)
        finite = sum(F((mode + 1)**2, 100**mode) for mode in range(cutoff + 1, cutoff + 65))
        assert s == finite + tail_sum(cutoff + 64)
        bound = prefactor * s
        angular_bounds.append({"ell": 21, "p": 20, "cutoff": cutoff,
                               "external_ratio_product_bound": exact(gamma),
                               "bound_exact": exact(bound),
                               "decimal_display_nearest_not_an_outward_bound": display(bound)})
    output = {
        "schema": "WU088_HH_PHYS69_INDEPENDENT_EXACT_WITNESSES_V1",
        "status": "PASS_EXACT_SCALAR_CHECKS",
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "old_certificate_sha256": expected,
        "exp_41_over_20_upper": exact(exponential_upper),
        "exp_upper_is_strictly_below_8": True,
        "all_j_exponent_inequality_polynomial_in_j_minus_20": shifted,
        "polynomial_coefficients_strictly_positive": True,
        "j20_anchor": {"a": exact(a), "R": exact(r), "nu_a": exact(nu_a),
                       "nu_R": exact(nu_r), "transfer_exponent": exact(exponent_at_20)},
        "geometric_sum_crosschecks": {"cutoffs": [28, 35, 36, 64],
                                     "explicit_terms_each": 64,
                                     "exact_finite_sum_plus_analytic_remainder_match": True},
        "excluded_second_born_bounds": angular_bounds,
        "scope": "Scalar arithmetic and source identity only; universal proof is in INDEPENDENT_REVIEW.md.",
        "solver_imports": 0, "Coulomb_function_evaluations": 0,
        "radial_integrations": 0, "historical_suites_rerun": 0,
        "HH_R10": "OFF"
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": output["status"], "angular_bounds": [
        {"L": row["cutoff"], "display": row["decimal_display_nearest_not_an_outward_bound"]}
        for row in angular_bounds], "output": str(args.out)}))


if __name__ == "__main__":
    main()
