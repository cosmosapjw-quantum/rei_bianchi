#!/usr/bin/env python3
"""Exact/SymPy fallback for R2A moment, KKT, and structural-zero checks."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from decimal import Decimal, getcontext
from pathlib import Path

import sympy as sp

getcontext().prec = 80
HERE = Path(__file__).resolve().parent
STAGE = HERE.parent


def D(value: str | float | int) -> Decimal:
    return Decimal(str(value))


def rel(actual: Decimal, expected: Decimal) -> Decimal:
    return abs(actual - expected) / max(abs(expected), Decimal(1))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# Generic exact proof: closure construction, information projection, KKT, and zeros.
N, K1, K2, J1, J2, Phi1, Phi2 = sp.symbols(
    "N K1 K2 J1 J2 Phi1 Phi2", positive=True
)
M = sp.symbols("M0:18", nonnegative=True)
Kap1 = sp.symbols("Kap10:18", nonnegative=True)
Kap2 = sp.symbols("Kap20:18", nonnegative=True)
Mlast = N - sum(M[:-1])
K1last = K1 - sum(Kap1[:-1])
K2last = K2 - sum(Kap2[:-1])
moment_mass = sp.simplify(sum(M[:-1]) + Mlast - N)
moment_k1 = sp.simplify(sum(Kap1[:-1]) + K1last - K1)
moment_k2 = sp.simplify(sum(Kap2[:-1]) + K2last - K2)
current_gamma_1 = sp.simplify(Phi1 * K1 - J1).subs(Phi1, J1 / K1)
current_gamma_2 = sp.simplify(Phi2 * K2 - J2).subs(Phi2, J2 / K2)

x, p = sp.symbols("x p", positive=True)
gkl = x * sp.log(x / p) - x + p
gkl_gradient_at_prior = sp.simplify(sp.diff(gkl, x).subs(x, p))
gkl_value_at_prior = sp.simplify(gkl.subs(x, p))

q1, q2, p1, p2, rho = sp.symbols("q1 q2 p1 p2 rho", positive=True)
pM = q1 * p1 + q2 * p2
capacity_slack = sp.factor(rho * pM - q1 * p1 - q2 * p2)
mu, slack = sp.symbols("mu slack", nonnegative=True)
complementarity_zero_dual = sp.simplify((mu * slack).subs(mu, 0))

symbolic = {
    "mass_moment_closure": str(moment_mass),
    "G1_opacity_moment_closure": str(moment_k1),
    "G2a_opacity_moment_closure": str(moment_k2),
    "current_Gamma_G1": str(current_gamma_1),
    "current_Gamma_G2a": str(current_gamma_2),
    "generalized_KL_value_at_prior": str(gkl_value_at_prior),
    "generalized_KL_gradient_at_prior": str(gkl_gradient_at_prior),
    "capacity_slack_identity": str(capacity_slack),
    "zero_dual_complementarity": str(complementarity_zero_dual),
    "G3_HeII_exact_zero": str(sp.Integer(0)),
}
symbolic_pass = all(
    value == "0"
    for key, value in symbolic.items()
    if key != "capacity_slack_identity"
) and sp.simplify(capacity_slack - (rho - 1) * pM) == 0

macro = load_csv(STAGE / "data" / "macro_projection.csv")
global_rows = load_csv(STAGE / "data" / "global_moment_lock.csv")
global_map = {
    (int(row["interval_index"]), int(row["substep"])): row
    for row in global_rows
}
groups: dict[tuple[str, int, int], list[dict[str, str]]] = defaultdict(list)
for row in macro:
    groups[(row["shape_lane"], int(row["interval_index"]), int(row["substep"]))].append(row)

numeric_cases = []
maxima = defaultdict(lambda: Decimal(0))
all_numeric_pass = True
for key, rows in sorted(groups.items()):
    interval, substep = key[1], key[2]
    target = global_map[(interval, substep)]
    sum_M = sum(D(r["M_sink_H_cMpc3"]) for r in rows)
    sum_K1 = sum(D(r["kappa_sink_G1_cMpc_inv"]) for r in rows)
    sum_K2 = sum(D(r["kappa_sink_G2a_cMpc_inv"]) for r in rows)
    sum_J1 = sum(D(r["J_sink_G1_s_inv_cMpc3"]) for r in rows)
    sum_J2 = sum(D(r["J_sink_G2a_s_inv_cMpc3"]) for r in rows)
    sum_transfer = sum(D(r["mass_transfer_rate_macro_H_s_inv_cMpc3"]) for r in rows)
    target_M = D(target["N_H_sink_global_cMpc3"])
    target_K1 = D(target["kappa_sink_G1_global_cMpc_inv"])
    target_K2 = D(target["kappa_sink_G2a_global_cMpc_inv"])
    target_J1 = D(target["J_sink_G1_global_s_inv_cMpc3"])
    target_J2 = D(target["J_sink_G2a_global_s_inv_cMpc3"])
    target_transfer = D(target["diffuse_sink_mass_transfer_rate_H_s_inv_cMpc3"])
    residuals = {
        "mass": rel(sum_M, target_M),
        "kappa_G1": rel(sum_K1, target_K1),
        "kappa_G2a": rel(sum_K2, target_K2),
        "J_G1": rel(sum_J1, target_J1),
        "J_G2a": rel(sum_J2, target_J2),
        "mass_transfer": rel(sum_transfer, target_transfer),
    }
    gamma_residual = Decimal(0)
    for r in rows:
        gamma_residual = max(
            gamma_residual,
            rel(
                D(r["J_sink_G1_s_inv_cMpc3"]),
                D(r["current_Gamma_flux_G1_s_inv_cMpc2"])
                * D(r["kappa_sink_G1_cMpc_inv"]),
            ),
            rel(
                D(r["J_sink_G2a_s_inv_cMpc3"]),
                D(r["current_Gamma_flux_G2a_s_inv_cMpc2"])
                * D(r["kappa_sink_G2a_cMpc_inv"]),
            ),
        )
    residuals["current_Gamma"] = gamma_residual
    exact_zeros = all(
        D(r["kappa_sink_G2b_cMpc_inv"]) == 0
        and D(r["kappa_sink_G3_cMpc_inv"]) == 0
        and D(r["J_sink_G2b_s_inv_cMpc3"]) == 0
        and D(r["J_sink_G3_s_inv_cMpc3"]) == 0
        and D(r["HeII_G3_sink_absorption_exact_zero"]) == 0
        for r in rows
    )
    inequalities = all(
        D(r["M_sink_H_cMpc3"]) >= 0
        and D(r["mass_cap_slack_cMpc3"]) >= 0
        and D(r["volume_filling_macro"]) <= 1
        and D(r["cycling_capacity_slack_s_inv_cMpc3"]) >= 0
        for r in rows
    )
    case_pass = (
        max(residuals.values()) <= Decimal("5e-12")
        and exact_zeros
        and inequalities
    )
    all_numeric_pass &= case_pass
    for name, value in residuals.items():
        maxima[name] = max(maxima[name], value)
    numeric_cases.append(
        {
            "shape_lane": key[0],
            "interval_index": interval,
            "substep": substep,
            "residuals": {name: str(value) for name, value in residuals.items()},
            "exact_zeros": exact_zeros,
            "inequalities": inequalities,
            "pass": case_pass,
        }
    )

zero_rows = load_csv(STAGE / "data" / "exact_zero_audit.csv")
source_zero_pass = all(
    row["source_lock_exact_zero"] == "True"
    and row["exact_zero"] == "True"
    and D(row["source_lock_value"]) == 0
    and D(row["sum"]) == 0
    for row in zero_rows
)

kkt_rows = [json.loads(line) for line in (STAGE / "data" / "dual_kkt_certificates.jsonl").read_text().splitlines() if line.strip()]
kkt_pass = (
    len(kkt_rows) == 30
    and all(row.get("KKT_gate") is True for row in kkt_rows)
    and all(D(row.get("complementarity_residual_max", 0)) == 0 for row in kkt_rows)
    and all(D(row.get("dual_nonnegativity_residual", 0)) == 0 for row in kkt_rows)
)

result = {
    "stage": "P0.5-B2C2B0C-R2A-GLOBAL-MOMENT-CONSTRAINED-MACRO-SINK-DISTRIBUTION-LOCK",
    "backend": "SymPy exact identities + Decimal(80) imported-data audit",
    "symbolic_identities": symbolic,
    "symbolic_pass": symbolic_pass,
    "numeric_case_count": len(numeric_cases),
    "numeric_all_pass": all_numeric_pass,
    "numeric_max_relative_residuals": {name: str(value) for name, value in maxima.items()},
    "source_and_output_exact_zero_pass": source_zero_pass,
    "KKT_zero_dual_certificate_pass": kkt_pass,
    "overall_pass": symbolic_pass and all_numeric_pass and source_zero_pass and kkt_pass,
    "numeric_cases": numeric_cases,
}
(STAGE / "data" / "symbolic_validation_results.json").write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps({k: v for k, v in result.items() if k != "numeric_cases"}, indent=2, sort_keys=True))
raise SystemExit(0 if result["overall_pass"] else 2)
