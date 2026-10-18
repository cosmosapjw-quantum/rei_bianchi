#!/usr/bin/env python3
"""Compare frozen native Rust clock sweeps with V11's independent Radau RHS."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
V11 = HERE.parent / "v11"
sys.path.insert(0, str(V11 / "src"))
import ci_thermal_clock as v11  # noqa: E402


CASES = {"D1_X1E5": (1.0e-5, 1.0), "D1_X1E4": (1.0e-4, 1.0), "D5_X1E5": (1.0e-5, 5.0)}
MODES = (
    "owner_like_be",
    "ci_mid",
    "ce_mid",
    "ff_mid",
    "cmb_mid",
    "thermal_mid",
    "chemical_mid",
    "all_mid",
)
STEPS = (8, 16, 32, 64, 128, 256)


def load_rows(path):
    with Path(path).open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        expected = 46
        if len(reader.fieldnames or ()) != expected:
            raise ValueError(f"NATIVE_CSV_HEADER_COLUMNS:{len(reader.fieldnames or ())}")
        if any(len(row) != expected for row in rows):
            raise ValueError("NATIVE_CSV_ROW_WIDTH")
    return rows


def temperature_from_native_row(row):
    return float(row["T_K"])


def order_from_halving(coarse, fine):
    if coarse <= 0 or fine <= 0:
        return None
    return math.log(coarse / fine, 2.0)


def jacobian_spectrum(x, q, density_factor):
    y = np.zeros(21, dtype=float)
    y[:4] = q
    jac = np.empty((4, 4), dtype=float)
    for j in range(4):
        delta = 1.0e-6 * max(abs(q[j]), 1.0e-4)
        plus = y.copy()
        minus = y.copy()
        plus[j] += delta
        minus[j] -= delta
        fp = v11.rhs_continuous(x, plus, density_factor)[:4]
        fm = v11.rhs_continuous(x, minus, density_factor)[:4]
        jac[:, j] = (fp - fm) / (2.0 * delta)
    values = np.linalg.eigvals(jac)
    magnitudes = sorted(abs(v) for v in values if abs(v) > 1.0e-12)
    spectral_radius = max((abs(v) for v in values), default=0.0)
    ratio = magnitudes[-1] / magnitudes[0] if len(magnitudes) > 1 else 1.0
    return {"eigenvalues_per_X": [[float(z.real), float(z.imag)] for z in values],
            "spectral_radius_per_X": float(spectral_radius),
            "nonzero_spectral_ratio": float(ratio)}


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: analyze_native_sweep.py NATIVE_SWEEP.csv OUTPUT_DIR")
    source = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rows = load_rows(source)
    grouped = {}
    for row in rows:
        key = (row["case"], row["mode"], int(row["n"]))
        grouped.setdefault(key, []).append(row)
    expected_runs = len(CASES) * len(MODES) * len(STEPS)
    if len(grouped) != expected_runs:
        raise ValueError(f"NATIVE_RUN_COUNT:{len(grouped)} != {expected_runs}")

    references = {}
    for case, (x_end, density_factor) in CASES.items():
        sol = v11.reference(x_end=x_end, density_factor=density_factor, rtol=2e-12)
        references[case] = {
            "temperature_K": float(v11.temperature(sol.y[:4, -1])),
            "state": sol.y[:4, -1].tolist(),
            "nfev": int(sol.nfev),
            "njev": int(sol.njev),
            "nlu": int(sol.nlu),
            "success": bool(sol.success),
            "message": str(sol.message),
        }

    endpoints = []
    run_ledgers = []
    for case, (x_end, density_factor) in CASES.items():
        t_ref = references[case]["temperature_K"]
        for mode in MODES:
            by_n = {}
            for n in STEPS:
                run = grouped[(case, mode, n)]
                if len(run) != n or [int(r["step"]) for r in run] != list(range(1, n + 1)):
                    raise ValueError(f"NATIVE_STEP_COUNT:{case}:{mode}:{n}")
                final = run[-1]
                tf = temperature_from_native_row(final)
                by_n[n] = {"T_K": tf, "abs_error_Radau_K": abs(tf - t_ref), "final": final}
                endpoint = {"case": case, "mode": mode, "N": n, "x_end_actual": float(final["x"]),
                            "T_native_K": tf, "T_Radau_K": t_ref, "abs_error_Radau_K": abs(tf-t_ref),
                            "rhs_evaluations": int(float(final["rhs_evaluations"])),
                            "simulation_wall_s": float(final["elapsed_wall_s"]),
                            "max_newton_residual": max(float(r["newton_residual"]) for r in run),
                            "max_abs_energy_residual_eV_per_H": max(abs(float(r["total_energy_residual_eV_per_H"])) for r in run),
                            "max_abs_photon_residual_per_H": max(abs(float(r["photon_count_residual_per_H"])) for r in run),
                            "min_T_K": min(float(r["T_K"]) for r in run),
                            "min_HI_per_H": min(float(r["HI_per_H"]) for r in run),
                            "min_HII_per_H": min(float(r["HII_per_H"]) for r in run),
                            "min_HeI_per_H": min(float(r["HeI_per_H"]) for r in run),
                            "min_HeII_per_H": min(float(r["HeII_per_H"]) for r in run),
                            "min_HeIII_per_H": min(float(r["HeIII_per_H"]) for r in run)}
                endpoints.append(endpoint)

                sum_fields = [
                    "CI_HI_events_per_H", "CI_HeI_events_per_H", "CI_HeII_events_per_H",
                    "CI_HI_binding_eV_per_H", "CI_HeI_binding_eV_per_H", "CI_HeII_binding_eV_per_H",
                    "RR_HII_events_per_H", "RR_HeII_events_per_H", "RR_HeIII_events_per_H",
                    "DR_HeII_events_per_H", "RR_HII_cooling_eV_per_H", "RR_HeII_cooling_eV_per_H",
                    "RR_HeIII_cooling_eV_per_H", "DR_HeII_cooling_eV_per_H", "RRDR_binding_escape_eV_per_H",
                    "CE_HI_cooling_eV_per_H", "CE_HeI_cooling_eV_per_H", "CE_HeII_cooling_eV_per_H",
                    "freefree_cooling_eV_per_H", "CMB_signed_gas_input_eV_per_H",
                    "gas_adiabatic_work_eV_per_H_step",
                ]
                totals = {name: sum(float(r[name]) for r in run) for name in sum_fields}
                helium_abundance = float(run[-1]["nHe_proper_cm3"]) / float(run[-1]["nH_proper_cm3"])
                run_ledgers.append({"case": case, "mode": mode, "N": n, **totals,
                                    "H_nuclei_budget_residual_per_H": (
                                        float(final["HII_per_H"]) - 0.075 - totals["CI_HI_events_per_H"] + totals["RR_HII_events_per_H"]),
                                    "HeIII_budget_residual_per_H": (
                                        float(final["HeIII_per_H"]) - helium_abundance * 0.03 - totals["CI_HeII_events_per_H"] + totals["RR_HeIII_events_per_H"]),
                                    "HeII_budget_residual_per_H": (
                                        float(final["HeII_per_H"]) - helium_abundance * 0.12
                                        - totals["CI_HeI_events_per_H"] + totals["RR_HeII_events_per_H"]
                                        + totals["DR_HeII_events_per_H"] + totals["CI_HeII_events_per_H"]
                                        - totals["RR_HeIII_events_per_H"]),
                                    "electron_count_residual_per_H": (
                                        float(final["electrons_per_H"])
                                        - (0.075 + helium_abundance * (0.12 + 2.0 * 0.03))
                                        - totals["CI_HI_events_per_H"] + totals["RR_HII_events_per_H"]
                                        - totals["CI_HeI_events_per_H"] + totals["RR_HeII_events_per_H"]
                                        + totals["DR_HeII_events_per_H"] - totals["CI_HeII_events_per_H"]
                                        + totals["RR_HeIII_events_per_H"])} )

            for n in STEPS[:-1]:
                fine_n = n * 2
                order = order_from_halving(by_n[n]["abs_error_Radau_K"], by_n[fine_n]["abs_error_Radau_K"])
                selfdiff = abs(by_n[n]["T_K"] - by_n[fine_n]["T_K"])
                endpoints.append({"case": case, "mode": mode, "N": n, "radau_error_order_to_2N": order,
                                  "self_difference_K_to_2N": selfdiff})

    endpoint_file = out / "NATIVE_ENDPOINTS.csv"
    with endpoint_file.open("w", newline="") as f:
        fields = sorted({key for row in endpoints for key in row})
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(endpoints)
    ledger_file = out / "NATIVE_LEDGER_SUMMARY.csv"
    with ledger_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sorted({key for row in run_ledgers for key in row}))
        writer.writeheader()
        writer.writerows(run_ledgers)

    stiffness = {}
    initial = v11.initial_state()
    for case, (x_end, density_factor) in CASES.items():
        final = np.asarray(references[case]["state"], dtype=float)
        for n in (8, 128, 256):
            dx = x_end / n
            points = {}
            for label, x, q in (("initial", 0.0, initial), ("final", x_end, final)):
                spec = jacobian_spectrum(x, q, density_factor)
                spec["step_spectral_exposure"] = spec["spectral_radius_per_X"] * dx
                points[label] = spec
            stiffness[f"{case}:N{n}"] = points

    summary = {
        "schema": "rei.lrs.v12.native_analysis.1",
        "source_csv_sha256": __import__("hashlib").sha256(source.read_bytes()).hexdigest(),
        "python": sys.version,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "rows": len(rows),
        "native_runs": len(grouped),
        "cases": references,
        "stiffness_exposure": stiffness,
        "claim_scope": "frozen PR150 native source-free Case-A controlled clocks; not source-on cosmological validation",
        "python_regressions_or_old_144_case_matrix_rerun": False,
    }
    summary_path = out / "NATIVE_ANALYSIS.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"rows": len(rows), "runs": len(grouped), "references": references,
                      "analysis": str(summary_path), "endpoint_table": str(endpoint_file),
                      "ledger_table": str(ledger_file)}, indent=2))


if __name__ == "__main__":
    main()
