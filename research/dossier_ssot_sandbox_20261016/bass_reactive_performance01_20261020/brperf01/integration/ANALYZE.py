#!/usr/bin/env python3
"""Independent Python checks of native rate-table controls and paired timings.

Uses published CSV state values and explicit isotope/EOS/energy algebra. It
does not call Rust, reproduce its integrator, or infer accuracy from a ledger.
"""

from __future__ import annotations

import collections
import csv
import json
import math
from pathlib import Path
import statistics
import struct
import sys

SPECIES = [
    "N_neutron", "N_HI", "N_HII", "N_DI", "N_DII", "N_TI", "N_TII",
    "N_He3I", "N_He3II", "N_He3III", "N_He4I", "N_He4II", "N_He4III",
]
BARYON = [1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4]
CHARGE = [0, 0, 1, 0, 1, 0, 1, 0, 1, 2, 0, 1, 2]
FAMILIES = {
    "H": ["N_HI", "N_HII"], "D": ["N_DI", "N_DII"],
    "He4": ["N_He4I", "N_He4II", "N_He4III"],
}
EV_J = 1.602176634e-19
KB_J_K = 1.380649e-23
CHI_H, CHI_HE1, CHI_HE2 = 13.598434599702, 24.587389011, 54.41776
CHI_D = CHI_H + 0.0037
METRICS = ["temperature", "thermal", "binding", "escaped", "cmb_reservoir", "N_HII", "N_DII", "N_He4III"]


def rows(path: Path):
    with path.open(newline="") as stream:
        yield from csv.DictReader(stream)


def bits(value: float) -> bytes:
    return struct.pack(">d", value)


def binding(r):
    return EV_J * math.fsum([
        CHI_H * r["N_HII"], CHI_HE1 * r["N_He4II"],
        (CHI_HE1 + CHI_HE2) * r["N_He4III"], CHI_D * r["N_DII"],
    ])


def ratio(value: float, scale: float) -> float:
    return abs(value) / max(abs(scale), 1e-300)


def save_csv(path: Path, records: list[dict]) -> None:
    if not records:
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def analyze_science(directory: Path) -> dict:
    groups = collections.defaultdict(list)
    numeric = None
    for raw in rows(directory / "HISTORIES.csv"):
        record = {}
        for key, value in raw.items():
            record[key] = value if key in ("case", "backend", "status") else float(value)
        if numeric is None:
            numeric = [key for key, value in record.items() if isinstance(value, float)]
        groups[(record["case"], record["backend"], int(record["nsteps"]))].append(record)
    status = list(rows(directory / "HISTORY_STATUS.csv"))
    assert len(status) == len(groups)
    assert all(row["status"] == "COMPLETE" and int(row["accepted"]) == int(row["nsteps"]) for row in status)
    ledger = collections.defaultdict(float)
    population_min = math.inf
    final = {}
    for key, trajectory in groups.items():
        initial = trajectory[0]
        initial_binding = binding(initial)
        initial_energy = math.fsum([initial["thermal"], initial_binding, initial["escaped"], initial["cmb_reservoir"]])
        initial_baryons = math.fsum(initial[name] * a for name, a in zip(SPECIES, BARYON))
        initial_families = {name: math.fsum(initial[k] for k in members) for name, members in FAMILIES.items()}
        for record in trajectory:
            assert all(math.isfinite(record[field]) for field in numeric)
            populations = [record[name] for name in SPECIES]
            population_min = min(population_min, min(populations))
            assert all(math.isfinite(value) and value >= 0 for value in populations)
            baryons = math.fsum(n * a for n, a in zip(populations, BARYON))
            electrons = math.fsum(n * q for n, q in zip(populations, CHARGE))
            particles = math.fsum(populations) + electrons
            temperature = record["thermal"] / (1.5 * KB_J_K * particles)
            chemistry = binding(record)
            energy = math.fsum([record["thermal"], chemistry, record["escaped"], record["cmb_reservoir"]])
            checks = {
                "baryons": ratio(baryons - initial_baryons, initial_baryons),
                "EOS_temperature": ratio(temperature - record["temperature"], temperature),
                "binding_reconstruction": ratio(chemistry - record["binding"], chemistry),
                "energy_reconstruction": ratio(energy - record["total_energy"], energy),
                "total_energy_drift": ratio(energy - initial_energy, initial_energy),
                "thermal_budget": ratio(record["thermal"] - initial["thermal"] - record["thermal_budget"], initial["thermal"]),
                "chemical_budget": ratio(chemistry - initial_binding - record["chemical_budget"], initial_binding),
                "escape_budget": ratio(record["escaped"] - initial["escaped"] - record["escape_budget"], initial_energy),
                "cmb_budget": ratio(record["cmb_reservoir"] - initial["cmb_reservoir"] - record["cmb_budget"], initial_energy),
            }
            for name, members in FAMILIES.items():
                checks["nuclei_" + name] = ratio(math.fsum(record[k] for k in members) - initial_families[name], initial_families[name])
            for name, value in checks.items():
                ledger[name] = max(ledger[name], value)
            assert record["photo_energy"] == 0.0
            assert all(record[k] == 0.0 for k in ["photo_HI", "photo_HeI", "photo_HeII", "photo_DI"])
        final[key] = trajectory[-1]
    assert max(ledger.values()) < 2e-11, dict(ledger)

    parity = {"original_reused_direct": 0, "compact_scalar_simd": 0}
    for (case, mode, steps), trajectory in groups.items():
        expected_mode = {"reused_direct": "original_direct", "compact_pchip_simd": "compact_pchip"}.get(mode)
        if expected_mode is None:
            continue
        expected = groups[(case, expected_mode, steps)]
        assert len(expected) == len(trajectory)
        for left, right in zip(expected, trajectory):
            assert all(bits(left[field]) == bits(right[field]) for field in numeric), (case, mode, steps)
        parity["original_reused_direct" if mode == "reused_direct" else "compact_scalar_simd"] += 1

    differences = []
    for (case, mode, steps), trajectory in groups.items():
        if mode == "original_direct":
            continue
        baseline = groups[(case, "original_direct", steps)]
        assert len(trajectory) == len(baseline)
        initial = baseline[0]
        family_scale = {}
        for members in FAMILIES.values():
            scale = math.fsum(initial[name] for name in members)
            family_scale.update({name: scale for name in members})
        record = {"case": case, "backend": mode, "nsteps": steps}
        record["max_trajectory_population_family_scaled_error"] = max(
            abs(r[name] - b[name]) / family_scale[name]
            for r, b in zip(trajectory, baseline) for name in family_scale
        )
        for metric in METRICS:
            record[metric + "_final_abs_error"] = abs(trajectory[-1][metric] - baseline[-1][metric])
            scale = abs(baseline[-1][metric])
            record[metric + "_final_relative_error"] = ratio(trajectory[-1][metric] - baseline[-1][metric], scale)
        differences.append(record)
    save_csv(directory / "BACKEND_DIFFERENCES.csv", differences)

    convergence = []
    for case in sorted({key[0] for key in groups}):
        for mode in sorted({key[1] for key in groups}):
            for metric in METRICS:
                a, b, c = [final[(case, mode, n)][metric] for n in (48, 96, 192)]
                first, second = a - b, b - c
                resolved = min(abs(first), abs(second)) > 64 * sys.float_info.epsilon * max(abs(a), abs(b), abs(c))
                monotone = first * second > 0
                order = math.log2(abs(first / second)) if resolved and monotone else None
                convergence.append({"case": case, "backend": mode, "field": metric,
                    "value_48": a, "value_96": b, "value_192": c,
                    "delta_48_96": first, "delta_96_192": second,
                    "monotone_differences": monotone, "above_roundoff_threshold": resolved,
                    "formal_order": order,
                    "scope": "THREE_GRID_DIAGNOSTIC_NOT_UNIVERSAL_ORDER_PROOF"})
    save_csv(directory / "TIME_GRID_DIFFERENCES.csv", convergence)

    coefficient_maxima = {}
    point_ids = set()
    point_temperatures = []
    for row in rows(directory / "POINT_COEFFICIENTS.csv"):
        point_ids.add(int(row["point"]))
        point_temperatures.append(float(row["T_eos"]))
        key = row["backend"]
        assert all(math.isfinite(float(row[field])) for field in ("T_eos", "reference", "value", "relative_error"))
        error = abs(float(row["relative_error"]))
        if key not in coefficient_maxima or error > coefficient_maxima[key]["relative_error"]:
            coefficient_maxima[key] = {"relative_error": error, "temperature": float(row["T_eos"]), "channel": row["channel"]}
        if float(row["reference"]) == 0:
            assert float(row["value"]) == 0
        assert float(row["value"]) >= 0
    pointgroups = collections.defaultdict(list)
    for row in rows(directory / "POINT_RHS.csv"):
        pointgroups[(int(row["point"]), row["backend"])].append(row)
    rhs_maxima = collections.defaultdict(lambda: collections.defaultdict(float))
    point_parity = {"original_reused_direct_fields": 0, "compact_scalar_simd_fields": 0}
    for (point, mode), record in pointgroups.items():
        byfield = {int(row["field"]): row for row in record}
        assert set(byfield) == set(range(34))
        for row in record:
            assert all(math.isfinite(float(row[field])) for field in ("reference", "value", "absolute_error"))
            if mode == "reused_direct":
                assert bits(float(row["reference"])) == bits(float(row["value"]))
                point_parity["original_reused_direct_fields"] += 1
        if mode == "compact_pchip_simd":
            scalar = {int(row["field"]): row for row in pointgroups[(point, "compact_pchip")]}
            for field, row in byfield.items():
                assert bits(float(scalar[field]["value"])) == bits(float(row["value"]))
                point_parity["compact_scalar_simd_fields"] += 1
        for group, indices in {"population_rate": range(13), "event_rate": [*range(13,27),33], "energy_rate": range(27,33)}.items():
            scale = max(abs(float(byfield[i]["reference"])) for i in indices)
            absolute = max(abs(float(byfield[i]["absolute_error"])) for i in indices)
            rhs_maxima[mode][group] = max(rhs_maxima[mode][group], ratio(absolute,scale))
    influence = list(rows(directory / "CHANNEL_INFLUENCE.csv"))
    assert len(influence) == 15 and all(int(row["changed_rhs_fields"]) > 0 for row in influence)
    controls = list(rows(directory / "WORK_LIMIT_CONTROL.csv"))
    assert all(row["status"] == "CX_WORK_LIMIT" and int(row["accepted"]) == 0 for row in controls)
    compact_rows = [row for row in differences if row["backend"] == "compact_pchip"]
    result = {
        "status": "PASS", "scope": "FIXED_VOLUME_SOURCE_OFF_NATIVE_H_HE_D_CONTROL",
        "planned_histories": len(status), "completed_histories": sum(row["status"] == "COMPLETE" for row in status),
        "accepted_macrosteps": sum(int(row["accepted"]) for row in status),
        "all_history_statuses": dict(collections.Counter(row["status"] for row in status)),
        "bitwise_history_pairs": parity, "independent_python_max_relative_residuals": dict(ledger),
        "minimum_population": population_min, "zero_photon_source_and_events": True,
        "point_temperatures": len(point_ids), "point_temperature_range": [min(point_temperatures),max(point_temperatures)],
        "point_coefficient_maxima": coefficient_maxima,
        "point_rhs_group_scaled_maxima": dict(rhs_maxima),
        "point_rhs_bitwise_comparisons": point_parity,
        "all_15_coefficient_channels_influence_native_rhs_at_60000K": True,
        "forced_work_limit_controls": controls,
        "compact_max_trajectory_population_family_scaled_error": max(row["max_trajectory_population_family_scaled_error"] for row in compact_rows),
        "compact_max_final_temperature_relative_error": max(row["temperature_final_relative_error"] for row in compact_rows),
        "direct_Nt192_endpoints": [{"case": case, **{metric: final[(case,"original_direct",192)][metric] for metric in METRICS}} for case in sorted({key[0] for key in groups})],
        "claims_not_made": ["full_EoR", "BASS_photon_driver_integration", "universal_second_order", "table_error_global_supremum", "longspan_photon_convergence"],
    }
    (directory / "INDEPENDENT_ANALYSIS.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def analyze_timings(root: Path) -> dict:
    records = []
    setups = []
    for path in sorted(root.glob("session_*/RHS_TIMINGS.csv")):
        records.extend(list(rows(path)))
        for row in rows(path.parent / "SETUP.csv"):
            row["session"] = path.parent.name
            setups.append(row)
    assert records, "no timing records"
    paired = collections.defaultdict(list)
    controls = collections.defaultdict(list)
    for row in records:
        if row["comparison"] not in ("WARMUP", "AA_CONTROL"):
            paired[(row["session"],row["comparison"],row["pair"])].append(row)
        elif row["comparison"] == "AA_CONTROL":
            controls[(row["session"], row["pair"])].append(row)
    pairs = []
    for (session,comparison,pair), points in paired.items():
        assert len(points) == 4
        baseline = [float(row["seconds"])/int(row["iterations"]) for row in points if row["backend"]=="original_direct"]
        trial = [float(row["seconds"])/int(row["iterations"]) for row in points if row["backend"]==comparison]
        assert len(baseline)==len(trial)==2
        assert all(math.isfinite(value) and value > 0 for value in baseline + trial)
        if comparison == "reused_direct":
            assert len({row["checksum"] for row in points}) == 1
        b,t=statistics.mean(baseline),statistics.mean(trial)
        pairs.append({"session":session,"comparison":comparison,"pair":int(pair),"baseline_seconds_per_rhs":b,"trial_seconds_per_rhs":t,"speedup":b/t})
    save_csv(root/"PAIRED_RHS_TIMINGS.csv",pairs)
    summary={}
    for comparison in sorted({row["comparison"] for row in pairs}):
        relevant=[row for row in pairs if row["comparison"]==comparison]
        sessions=collections.defaultdict(list)
        for row in relevant:sessions[row["session"]].append(row["speedup"])
        per_session=[statistics.median(v) for v in sessions.values()]
        trial_ns=statistics.median(row["trial_seconds_per_rhs"] for row in relevant)*1e9
        baseline_ns=statistics.median(row["baseline_seconds_per_rhs"] for row in relevant)*1e9
        setup_key="compact_pchip" if comparison.startswith("compact") else comparison
        setup_samples=[float(row["setup_s"]) for row in setups if row["backend"]==setup_key]
        setup_s=statistics.median(setup_samples) if setup_samples else 0.0
        saved=(baseline_ns-trial_ns)*1e-9
        summary[comparison]={"processes":len(sessions),"ABBA_pairs":len(relevant),"median_process_speedup":statistics.median(per_session),
            "process_speedup_range":[min(per_session),max(per_session)],"median_baseline_ns_per_rhs":baseline_ns,"median_trial_ns_per_rhs":trial_ns,
            "median_setup_seconds":setup_s,"setup_break_even_rhs_calls":math.ceil(setup_s/saved) if saved>0 else None,
            "accuracy_relation":"BITWISE_DIRECT_PARITY" if comparison=="reused_direct" else "RATE_APPROXIMATION_QUANTIFIED_SEPARATELY"}
    aa_ratios = []
    for points in controls.values():
        assert len(points) == 2
        first, second = [float(row["seconds"]) / int(row["iterations"]) for row in points]
        aa_ratios.append(first / second)
    result={"status":"PASS","scope":"EXPLORATORY_SHARED_SANDBOX_ABBA_NATIVE_RHS","comparisons":summary,
        "AA_controls": {"paired_windows": len(aa_ratios), "median_ratio": statistics.median(aa_ratios), "ratio_range": [min(aa_ratios), max(aa_ratios)]},
        "inference_scope":"Measured process distributions; no claimed universal machine speedup or equal table approximation errors."}
    (root/"RHS_TIMING_ANALYSIS.json").write_text(json.dumps(result,indent=2)+"\n")
    return result


def main() -> None:
    if len(sys.argv)!=3:
        raise SystemExit("usage: ANALYZE.py science|bench DIRECTORY")
    result = analyze_science(Path(sys.argv[2])) if sys.argv[1]=="science" else analyze_timings(Path(sys.argv[2]))
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
