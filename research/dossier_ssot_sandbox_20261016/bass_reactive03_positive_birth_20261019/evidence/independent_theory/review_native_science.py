#!/usr/bin/env python3
"""Independent, read-only analysis of the final BASS-REACTIVE-03 native matrix.

This program never modifies its input directory.  It validates metadata hashes,
derives age moments, and compares endpoint data.  It is an evidence review, not a
new integration of the evolving H/He/D equations.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import sys

NAMES = [
    "ap_n16_r2", "ap_n32_r1", "ap_n32_r2", "ap_n32_r4", "ap_n32_r8",
    "ap_n64_r2", "ap_n128_r2", "ap_n32_r2_plus", "ap_n32_r2_opacity8",
    "ap_n32_r2_spectrum", "off_gl2_n32", "off_gl4_n32", "ap_cx_worklimit",
]
TEXT_FIELDS = {"case", "split", "frozen", "birth_mode"}
OBS = ["photons_com3", "mean_age_s", "second_age_moment_s2", "DI", "q2", "T_K", "DII_m3"]
ENERGY_PARTS = ["photon_energy_com3", "gas_thermal_com3", "gas_binding_com3", "escaped_com3", "cmb_reservoir_com3"]
NONNEGATIVE = [
    "DII_m3", "photons_com3", "absorbed_com3", "HI", "HeI", "HeII", "DI",
    "source_count", "source_energy", "cohorts", "maxN", "maxE", "maxW",
    "RR", "CX_abs", "FF", "CMB_abs", "threshold_crossings",
    "survivor_age_com_s", "survivor_age2_com_s2", *ENERGY_PARTS,
]
CUMULATIVE = ["absorbed_com3", "HI", "HeI", "HeII", "DI", "source_count", "source_energy", "RR", "CX_abs", "FF", "CMB_abs"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(row):
    v = {k: float(value) for k, value in row.items() if k not in TEXT_FIELDS}
    v["mean_age_s"] = v["survivor_age_com_s"] / v["photons_com3"]
    v["second_age_moment_s2"] = v["survivor_age2_com_s2"] / v["photons_com3"]
    v["age_variance_s2"] = v["second_age_moment_s2"] - v["mean_age_s"] ** 2
    return v


def exact_text_ledgers(row):
    """80-digit arithmetic on printed component data; not on Rust residuals."""
    with localcontext() as ctx:
        ctx.prec = 80
        d = {k: Decimal(row[k]) for k in set(ENERGY_PARTS + [
            "initial_total_energy_com3", "source_energy", "geom_work",
            "photons_com3", "absorbed_com3", "source_count", "HI", "HeI", "HeII", "DI",
        ])}
        energy_now = sum((d[k] for k in ENERGY_PARTS), Decimal(0))
        energy_expected = d["initial_total_energy_com3"] + d["source_energy"] + d["geom_work"]
        er = energy_now - energy_expected
        nr = d["photons_com3"] + d["absorbed_com3"] - d["source_count"]
        sr = sum((d[k] for k in ["HI", "HeI", "HeII", "DI"]), Decimal(0)) - d["absorbed_com3"]
        return {
            "number_relative": float(abs(nr) / d["source_count"]),
            "energy_relative_total_scale": float(abs(er) / max(abs(energy_now), abs(energy_expected), abs(d["initial_total_energy_com3"]))),
            "energy_relative_source_scale": float(abs(er) / d["source_energy"]),
            "species_sum_relative_source_scale": float(abs(sr) / d["source_count"]),
        }


def seq_analysis(cases, names):
    result = {"cases": names, "observables": {}}
    for key in OBS:
        values = [cases[n]["endpoint"][key] for n in names]
        diffs = [y - x for x, y in zip(values, values[1:])]
        ratios = [math.log2(abs(x / y)) if x and y else None for x, y in zip(diffs, diffs[1:])]
        flips = [bool(x * y < 0) for x, y in zip(diffs, diffs[1:])]
        result["observables"][key] = {
            "values": values, "fine_minus_coarse": diffs,
            "log2_difference_magnitude_ratios": ratios,
            "adjacent_difference_sign_flips": flips,
            "last_relative_difference": diffs[-1] / values[-1] if values[-1] else None,
            "caution": "Magnitude ratios are diagnostics, not guaranteed error orders; sign flips prohibit a single monotone leading-error interpretation.",
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("native_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    native = args.native_dir.resolve()
    cases = {}
    snapshots = {}
    total_rows = 0
    binary_hashes = set()
    global_ledgers = {}
    for name in NAMES:
        jp, cp = native / (name + ".json"), native / (name + ".csv")
        metadata = json.loads(jp.read_text())
        snapshots[jp] = sha(jp)
        snapshots[cp] = sha(cp)
        assert metadata["name"] == name
        assert snapshots[cp] == metadata["csv_sha256"], (name, "CSV hash mismatch")
        with cp.open(newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            columns = reader.fieldnames
        assert len(rows) == metadata["rows"]
        binary_hashes.add(metadata["binary_sha256"])
        record = {
            "metadata_sha256": snapshots[jp], "csv_sha256": snapshots[cp],
            "binary_sha256": metadata["binary_sha256"],
            "status": metadata["status"], "failure_class": metadata["failure_class"],
            "exit_code": metadata["exit_code"], "rows": len(rows),
            "planned_rows": metadata["planned_rows"], "wall_s": metadata["wall_s"],
            "command": metadata["command"],
        }
        if name == "ap_cx_worklimit":
            assert len(rows) == 0 and metadata["exit_code"] == 2
            assert metadata["status"] == "RESOURCE_LIMIT_CX" and "Cx(WorkLimit)" in metadata["stderr"]
            assert metadata["final"] is None
            record["stderr"] = metadata["stderr"]
            record["classification"] = "CX work budget exhausted before first accepted step; no solution or convergence inference."
        else:
            assert len(columns) == 54, (name, "unexpected schema")
            assert metadata["status"] == "COMPLETED" and metadata["exit_code"] == 0
            assert len(rows) == metadata["planned_rows"]
            assert metadata["final"] == rows[-1]
            local_ledger = {}
            previous = None
            for index, row in enumerate(rows, 1):
                v = metrics(row)
                assert all(math.isfinite(x) for x in v.values()), (name, index, "nonfinite")
                assert v["step"] == index and v["nsteps"] == len(rows)
                assert v["time_s"] == v["t0"] + v["duration"] * index / len(rows)
                assert v["T_K"] > 0 and v["volume"] > 0 and v["photons_com3"] > 0
                assert all(v[k] >= 0 for k in NONNEGATIVE), (name, index, "negative observed quantity")
                elapsed = v["time_s"] - v["t0"]
                assert 0 <= v["mean_age_s"] <= elapsed
                assert v["age_variance_s2"] >= 0
                assert v["second_age_moment_s2"] <= elapsed * v["mean_age_s"] * (1 + 1e-12)
                assert -0.5 - 1e-14 <= v["q2"] <= 1 + 1e-14
                if previous:
                    assert all(v[k] >= previous[k] for k in CUMULATIVE), (name, index, "cumulative quantity decreased")
                previous = v
                for key, val in exact_text_ledgers(row).items():
                    local_ledger[key] = max(local_ledger.get(key, 0.0), val)
                    global_ledgers[key] = max(global_ledgers.get(key, 0.0), val)
            total_rows += len(rows)
            record["endpoint"] = {k: metrics(rows[-1])[k] for k in OBS + [
                "age_variance_s2", "source_count", "source_energy", "geom_work",
                "thermal_change_com3", "chemical_change_com3", "photo_energy_com3",
                "maxN", "maxE", "maxW", "threshold_crossings", "cohorts", *ENERGY_PARTS,
            ]}
            record["ledger_reconstruction_maxima"] = local_ledger
            record["threshold_crossing_diagnostics"] = {
                "semantics": "Per-macrostep transport diagnostic, not cumulative and not a count of unique physical photons.",
                "sum_over_steps": sum(int(r["threshold_crossings"]) for r in rows),
                "max_in_one_step": max(int(r["threshold_crossings"]) for r in rows),
                "final_step": int(rows[-1]["threshold_crossings"]),
            }
            record["observed_checks"] = "PASS: all 54 fields parse, numeric fields finite, positive T/volume, nonnegative exported populations/events, monotone cumulative quantities, physically supported first two age moments, energy-quadrupole range."
        cases[name] = record
    assert len(binary_hashes) == 1
    base = cases["ap_n32_r2"]["endpoint"]
    variants = ["ap_n32_r2_plus", "ap_n32_r2_opacity8", "ap_n32_r2_spectrum", "off_gl2_n32", "off_gl4_n32"]
    contrasts = {
        name: {key: (cases[name]["endpoint"][key] - base[key]) / base[key] for key in OBS}
        for name in variants
    }
    qminus = base["q2"]
    qplus = cases["ap_n32_r2_plus"]["endpoint"]["q2"]
    stale = []
    for path in sorted(native.glob("*.running.csv")):
        with path.open(newline="") as stream:
            n = len(list(csv.DictReader(stream)))
        stale.append({"file": path.name, "rows": n, "sha256": sha(path), "use": "EXCLUDED: temporary stream; authoritative completed CSV selected by metadata."})
    assert all(sha(p) == s for p, s in snapshots.items()), "Input changed during read-only review"
    result = {
        "review_status": "PASS_SCOPED_EVIDENCE_REVIEW",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "input_path": str(native),
        "method": {
            "role": "Independent read-only Python data analysis; no H/He/D rerun or source mutation.",
            "age_mean": "survivor_age_com_s / photons_com3",
            "age_second_moment": "survivor_age2_com_s2 / photons_com3",
            "q2": "sum(n*E*P2(mu_z))/sum(n*E), P2=(3*mu_z^2-1)/2; energy weighted, dimensionless.",
            "differences": "fine minus coarse; reported relative differences are comparisons, not absolute error estimates.",
            "formal_ratio": "log2(abs((v2-v1)/(v3-v2))); not an admitted global order.",
            "ledger": "80-digit Decimal on CSV component values, including final photon+thermal+binding+escaped+CMB minus initial+source+geometry work.",
            "limitation": "CSV exports DII but not every species population; unexported population positivity relies on solver checks/tests outside this review.",
        },
        "case_count": len(cases), "completed_case_count": 12, "accepted_macrosteps": total_rows,
        "resource_limit_cases": 1, "all_inputs_unchanged_during_review": True,
        "common_binary_sha256": next(iter(binary_hashes)),
        "global_ledger_reconstruction_maxima": global_ledgers,
        "cases": cases,
        "time_sequence": seq_analysis(cases, ["ap_n16_r2", "ap_n32_r2", "ap_n64_r2", "ap_n128_r2"]),
        "birth_sequence": seq_analysis(cases, ["ap_n32_r1", "ap_n32_r2", "ap_n32_r4", "ap_n32_r8"]),
        "contrasts_relative_to_ap_n32_r2": contrasts,
        "signed_shear_quadrupole": {
            "minus": qminus, "plus": qplus,
            "even_remainder": 0.5 * (qplus + qminus),
            "odd_component": 0.5 * (qminus - qplus),
            "relative_even_to_odd_magnitude": abs((qplus + qminus) / (qminus - qplus)),
            "claim": "This paired case recovers opposite quadrupole signs; one amplitude/grid pair does not establish complete BI-SIGNED or an exact nonlinear odd symmetry.",
        },
        "excluded_temporary_streams": stale,
        "admission": {
            "positive_AP_constant_problem": "ADMITTED_SCOPED by separate scalar/theory/frozen evidence, not inferred from native conservation.",
            "native_bounded_control_study": "COMPLETE: 12 accepted histories; tighter-CX attempt separately classified.",
            "native_birth_refinement": "CONTRACTING endpoint photon number, age moments, and q2 over r=1,2,4,8; no full distribution accuracy claim.",
            "native_temporal_photon_number": "CONTRACTING endpoint comparisons, magnitude ratios near one; no absolute error or universal second-order claim.",
            "native_temporal_age_and_q2": "NOT_ADMITTED: mean-age and q2 differences grow across latest pairs; second moment lacks stable contraction/order.",
            "DI_second_order": "NOT_ADMITTED: temporal triples disagree; birth DI difference changes sign at very small magnitude.",
            "spectral_convergence": "NOT_ADMITTED: one two-representation contrast, finite effect on number and age moments.",
            "full_age_distribution_and_angular_convergence": "NOT_ADMITTED: no complete distribution norm/native angular-grid hierarchy here.",
            "longspan_solution": "NOT_ADMITTED_PENDING_JOINT_TIME_BIRTH_AGE_SPECTRAL_CONVERGENCE",
            "universal_second_order_HHeD": "NOT_ADMITTED",
            "two_way_Einstein_feedback": "UNIMPLEMENTED; current geometry is one-way BASS donor.",
            "full_EoR": "HOLD; initial conditions remain regression controls.",
        },
        "next_science_node": {
            "goal": "Resolve time/birth-age interaction with a bounded crossed Nt x r hierarchy and actual cohort/group age diagnostics.",
            "proposal": "Compare a minimum 3-level temporal hierarchy at a finer fixed birth r and at least one cross r refinement; inspect threshold-aware spectral refinement separately; preserve signed-q2 and work-defect diagnostics.",
            "why": "N endpoint stability has improved while native mean age and q2 temporal differences do not yet contract. Finite moments do not establish age distribution convergence.",
        },
    }
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({k: result[k] for k in ["review_status", "completed_case_count", "accepted_macrosteps", "resource_limit_cases", "global_ledger_reconstruction_maxima"]}, indent=2))


if __name__ == "__main__":
    main()
