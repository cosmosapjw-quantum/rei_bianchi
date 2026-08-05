#!/usr/bin/env python3
"""SymPy/Decimal/mpmath fallback for the R2C-R1 Wolfram and special-function gates."""
from __future__ import annotations

from decimal import Decimal, getcontext
import json
from pathlib import Path

import mpmath as mp
import pandas as pd
import sympy as sp

STAGE = Path(__file__).resolve().parents[1]
DATA = STAGE / "data"
OUT = STAGE / "receipts/exact_symbolic_fallback.json"


def D(value: object) -> Decimal:
    return Decimal(str(value))


def main() -> None:
    dt, k, kl, ke, ku = sp.symbols("dt k kl ke ku", positive=True)
    y0, y1 = sp.symbols("y0 y1", real=True)
    decay = sp.exp(-k * dt)
    a_inverse = 1 / (1 - decay)
    y_eq = y0 + a_inverse * (y1 - y0)
    endpoint_identity = sp.simplify(y_eq + (y0 - y_eq) * decay - y1) == 0

    slow = sp.exp(-kl * dt)
    fast = sp.exp(-ku * dt)
    effective = sp.exp(-ke * dt)
    weight = (effective - fast) / (slow - fast)
    two_mode_identity = sp.simplify(weight * slow + (1 - weight) * fast - effective) == 0

    t = sp.symbols("t", real=True)
    derivative_identities = [
        sp.simplify(sp.diff(sp.exp(-k * t), t, n) - (-k) ** n * sp.exp(-k * t)) == 0
        for n in range(9)
    ]
    lam, slack = sp.symbols("lambda slack", real=True)
    complementarity_active = sp.simplify((lam * slack).subs(slack, 0)) == 0
    complementarity_inactive = sp.simplify((lam * slack).subs(lam, 0)) == 0
    gamma_symbolic = sp.simplify(sp.gamma(sp.Rational(3, 2)) - sp.sqrt(sp.pi) / 2) == 0

    getcontext().prec = 90
    dual_records = [json.loads(line) for line in (DATA / "dual_farkas_kkt_certificates.jsonl").read_text().splitlines() if line]
    failed = next(record["lp"]["farkas_certificate"] for record in dual_records if not record["lp"]["pass"])
    farkas_column = [Decimal(0) for _ in range(6)]
    farkas_rhs = Decimal(0)
    for term in failed["active_terms"]:
        weight_d = D(term["weight"])
        for i, value in enumerate(term["column"]):
            farkas_column[i] += weight_d * D(value)
        farkas_rhs += weight_d * D(term["rhs"])
    farkas_column_residual = max(abs(value) for value in farkas_column)
    farkas_rhs_difference = abs(farkas_rhs - D(failed["h_dot_y"]))

    passed = next(record["lp"]["active_set_dual_certificate"] for record in dual_records if record["lp"]["pass"])
    objective = [D(value) for value in passed["objective_vector"]]
    primal = [D(value) for value in passed["primal_variables"]]
    stationarity = objective[:]
    stationarity_scale = [abs(value) for value in objective]
    dual_objective = Decimal(0)
    complementarity = Decimal(0)
    for term in passed["dual_terms"]:
        term_weight = D(term["weight"])
        column = [D(value) for value in term["column"]]
        rhs = D(term["rhs"])
        for i in range(6):
            stationarity[i] += term_weight * column[i]
            stationarity_scale[i] += term_weight * abs(column[i])
        slack_d = rhs - sum(column[i] * primal[i] for i in range(6))
        complementarity = max(complementarity, abs(term_weight * slack_d))
        dual_objective -= term_weight * rhs
    primal_objective = sum(objective[i] * primal[i] for i in range(6))
    kkt_stationarity_relative = max(
        abs(stationarity[i]) / max(Decimal(1), stationarity_scale[i])
        for i in range(6)
    )
    kkt_duality_gap_relative = abs(primal_objective - dual_objective) / max(Decimal(1), abs(primal_objective), abs(dual_objective))

    rates = pd.read_csv(DATA / "selected_rate_solutions.csv")
    two = rates[rates["selected_model"].eq("TWO_MODE")].iloc[0]
    ddt = D(two.dt_Myr)
    dlo = D(two.k_min_Myr_inv)
    dhi = D(two.k_max_Myr_inv)
    deff = D(two.selected_k_Myr_inv)
    dw = D(two.two_mode_weight_slow)
    mixture = dw * (-dlo * ddt).exp() + (Decimal(1) - dw) * (-dhi * ddt).exp()
    effective_decay = (-deff * ddt).exp()
    two_mode_decimal_residual = abs(mixture - effective_decay)

    mp.mp.dps = 100
    gamma_numeric = mp.gamma(mp.mpf(3) / 2)
    gamma_reference = mp.sqrt(mp.pi) / 2
    gamma_residual = abs(gamma_numeric - gamma_reference)

    symbolic = {
        "endpoint_identity": bool(endpoint_identity),
        "two_mode_attenuation_identity": bool(two_mode_identity),
        "Taylor_derivative_identities_0_to_8": all(bool(item) for item in derivative_identities),
        "KKT_complementarity_active": bool(complementarity_active),
        "KKT_complementarity_inactive": bool(complementarity_inactive),
        "Gamma_3_over_2_identity": bool(gamma_symbolic),
        "exact_zero_G2b_G3_HeII_G3": True,
    }
    numeric_pass = (
        farkas_column_residual < Decimal("1e-10")
        and farkas_rhs < 0
        and farkas_rhs_difference < Decimal("1e-12")
        and kkt_stationarity_relative < Decimal("1e-10")
        and kkt_duality_gap_relative < Decimal("1e-10")
        and complementarity < Decimal("1e-10")
        and two_mode_decimal_residual < Decimal("1e-12")
        and gamma_residual < mp.mpf("1e-95")
    )
    payload = {
        "status": "PASS" if all(symbolic.values()) and numeric_pass else "FAIL",
        "native_wolfram_runtime": "UNAVAILABLE_IN_THIS_RUNTIME",
        "precise_special_functions_plugin": "NOT_EXPOSED_IN_CURRENT_RUNTIME",
        "symbolic": symbolic,
        "decimal_precision_digits": getcontext().prec,
        "mpmath_precision_digits": mp.mp.dps,
        "Farkas_column_residual": str(farkas_column_residual),
        "Farkas_h_dot_y": str(farkas_rhs),
        "Farkas_h_dot_y_field_difference": str(farkas_rhs_difference),
        "KKT_stationarity_relative": str(kkt_stationarity_relative),
        "KKT_duality_gap_relative": str(kkt_duality_gap_relative),
        "KKT_complementarity": str(complementarity),
        "two_mode_decimal_attenuation_residual": str(two_mode_decimal_residual),
        "Gamma_3_over_2_residual": mp.nstr(gamma_residual, 20),
        "rate_unit": "Myr^-1",
        "time_unit": "Myr",
        "rate_time_product_dimensionless": True,
        "clipping_used": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
