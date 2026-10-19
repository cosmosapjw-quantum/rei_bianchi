#!/usr/bin/env python3
"""Analyze saved bounded histories. Conservation is separate from accuracy."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math


FIELDS = ["photons_com3", "T_K", "DII_m3", "HI", "HeI", "HeII", "DI", "q2",
          "source_count", "source_energy", "geom_work", "mean_age_s", "second_age_s2",
          "photon_energy_com3", "gas_thermal_com3", "gas_binding_com3",
          "thermal_change_com3", "chemical_change_com3", "photo_energy_com3"]


def contrast(a, b):
    return {f: {"absolute": b[f] - a[f],
                "relative": (b[f] - a[f]) / a[f] if a[f] else None}
            for f in FIELDS}


def convergence(values):
    deltas = [b - a for a, b in zip(values, values[1:])]
    orders = []
    for d0, d1 in zip(deltas, deltas[1:]):
        orders.append(math.log2(abs(d0 / d1)) if d0 * d1 > 0 else None)
    return {"values": values, "successive_differences": deltas,
            "successive_relative_changes": [d / a if a else None for a, d in zip(values, deltas)],
            "formal_orders_same_sign_only": orders,
            "interpretation": "finite differences only; no exact evolving reference or universal order claim"}


def read_history(receipt_path):
    receipt = json.loads(receipt_path.read_text())
    path = receipt_path.with_suffix(".csv")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == receipt["csv_sha256"], path
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == receipt["rows"], path
    if not rows:
        assert receipt["name"] == "ap_cx_worklimit"
        assert receipt["status"] == "RESOURCE_LIMIT_CX"
        assert "Cx(WorkLimit)" in receipt["stderr"]
        return receipt, rows, None
    assert receipt["status"] == "COMPLETED"
    assert rows[-1] == receipt["final"]
    final = {k: float(v) for k, v in rows[-1].items()
             if k not in ("case", "split", "frozen", "birth_mode")}
    final["mean_age_s"] = final["survivor_age_com_s"] / final["photons_com3"]
    final["second_age_s2"] = final["survivor_age2_com_s2"] / final["photons_com3"]
    return receipt, rows, final


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    receipts = sorted((root / "evidence/native").glob("*.json"))
    assert len(receipts) == 13, len(receipts)
    finals, execution, histories = {}, {}, {}
    for path in receipts:
        receipt, rows, final = read_history(path)
        name = path.stem
        execution[name] = {k: receipt[k] for k in
                           ("status", "exit_code", "rows", "planned_rows", "failure_class", "wall_s", "csv_sha256")}
        if final is not None:
            finals[name] = final
            histories[name] = rows
    reference = finals["ap_n32_r2"]
    independent_axes = {
        "time_r2": {f: convergence([finals[f"ap_n{n}_r2"][f] for n in [16, 32, 64, 128]]) for f in FIELDS},
        "birth_n32": {f: convergence([finals[f"ap_n32_r{r}"][f] for r in [1, 2, 4, 8]]) for f in FIELDS},
        "spectrum_n32_r2": contrast(reference, finals["ap_n32_r2_spectrum"]),
        "opacity_n32_r2": contrast(reference, finals["ap_n32_r2_opacity8"]),
        "signed_geometry_n32_r2": contrast(reference, finals["ap_n32_r2_plus"]),
        "ap_vs_off_gl2_n32": contrast(finals["off_gl2_n32"], reference),
        "ap_vs_off_gl4_n32": contrast(finals["off_gl4_n32"], reference),
    }
    parity = {}
    for new, old in [("off_gl2_n32", "time32"), ("off_gl4_n32", "birth")]:
        path = root / f"evidence/parent_comparison/{old}.csv"
        with path.open() as handle:
            prior = list(csv.DictReader(handle))
        current = histories[new]
        operational = {"wall_s", "hits", "misses", "cache_size"}
        common = sorted(set(prior[0]) & set(current[0]) - operational)
        mismatches = [(i + 1, key, a[key], b[key]) for i, (a, b) in enumerate(zip(prior, current))
                      for key in common if a[key] != b[key]]
        parity[new] = {"rows": len(current), "parent_rows": len(prior),
                       "common_fields": common, "compared_cells": len(current) * len(common),
                       "mismatch_count": len(mismatches), "mismatches": mismatches[:20],
                       "operational_final_differences": {key: float(current[-1][key]) - float(prior[-1][key])
                                                          for key in operational if key in prior[0]},
                       "operational_note": "Two additional read-only thermal-energy observations add two cache hits. Timing and cache counters are excluded from scientific parity, and retained here.",
                       "status": "EXACT_TEXT_PARITY" if not mismatches and len(current) == len(prior) else "MISMATCH"}
        assert parity[new]["status"] == "EXACT_TEXT_PARITY", parity[new]
    with (root / "evidence/frozen/AP_FROZEN_FINAL.csv").open() as handle:
        frozen = list(csv.DictReader(handle))
    result = {
        "schema": "rei.bass.reactive03.science.v1",
        "status": "COMPLETE_SCOPED_POSITIVE_BIRTH_STUDY",
        "duration_s": 8e12, "planned_histories": 13,
        "completed_histories": len(finals),
        "completed_macrosteps": sum(len(rows) for rows in histories.values()),
        "execution": execution, "finals": finals, "independent_axes": independent_axes,
        "off_parity": parity, "frozen_cases": frozen,
        "native_reported_max_number_residual": max(x["maxN"] for x in finals.values()),
        "native_reported_max_energy_residual": max(x["maxE"] for x in finals.values()),
        "native_reported_max_work_quadrature_discrepancy": max(x["maxW"] for x in finals.values()),
        "claims": {
            "constant_source_opacity_survival": "EXACT_ANALYTIC_CONSTRUCTION_BINARY64_VERIFIED",
            "evolving_native_finite_grid_sensitivity": "MEASURED_INDEPENDENT_TIME_BIRTH_SPECTRAL_OPACITY_AXES",
            "entire_birth_age_distribution": "FINITE_COHORT_APPROXIMATION_NOT_EXACT",
            "longspan_solution": "NOT_ADMITTED_FULL_CONVERGENCE_INCOMPLETE",
            "universal_second_order": "NOT_ESTABLISHED",
            "angular_convergence": "NOT_TESTED_IN_THIS_UNIT",
            "two_way_Einstein_feedback": "NOT_IMPLEMENTED"
        },
    }
    target = root / "evidence/SCIENCE_RESULTS.json"
    target.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    columns = ["case"] + FIELDS + ["cohorts", "maxN", "maxE", "maxW"]
    with (root / "evidence/NATIVE_FINALS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for name, values in finals.items():
            writer.writerow({"case": name, **{f: f"{values[f]:.17e}" for f in columns[1:]}})
    print(json.dumps({"status": result["status"], "histories": len(finals),
                      "macrosteps": result["completed_macrosteps"],
                      "number": result["native_reported_max_number_residual"],
                      "energy": result["native_reported_max_energy_residual"],
                      "off_parity": {k: v["status"] for k, v in parity.items()}}, indent=2))


if __name__ == "__main__":
    main()
