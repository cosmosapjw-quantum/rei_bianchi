#!/usr/bin/env python3
"""Independent post-processing of completed Contract B raw files; no native run.

The audit_* and owner_* CSV fields are deliberately excluded from every
accounting calculation. Decimal(60) evaluates the printed binary64 records;
this does not recover the unprinted exact native trajectory.
"""
from collections import defaultdict
from decimal import Decimal, getcontext
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import argparse

getcontext().prec = 60
D = Decimal
ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--raw-dir", type=Path, default=ROOT / "execution_coupled")
parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent)
args = parser.parse_args()
RAW = args.raw_dir.resolve()
OUT = args.out_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
Y = D(".2454") / (D(4) * (1 - D(".2454")))
CHI = tuple(map(D, ("13.598434599702", "24.587389011", "54.41776")))
EV = D("1.602176634e-12")
KB = D("1.380649e-16")
H0 = D("67.4") * D("1e5") / D("3.0856775814913673e24")
ZERO = D(0)


def exact_float(value):
    """Round-trip CSV text to the recorded binary64 value, then expand exactly."""
    return D.from_float(float(value))


def native_hubble_float(a):
    # Actual owner arithmetic order; a.powi(3/4) written as products.
    a = float(a)
    a2 = a * a
    return (67.4 * 1e5 / 3.0856775814913673e24) * math.sqrt(
        0.315 / (a2 * a) + 9.2e-5 / (a2 * a2) + (1.0 - 0.315 - 9.2e-5))


def read(name):
    with (RAW / name).open() as f:
        records = list(csv.DictReader(f))
    return [{k: v if k == "kind" else D(v) for k, v in r.items()}
            for r in records]


def key(r):
    return r["kind"], int(r["m"])


def at(r):
    return {"kind": r["kind"], "m": int(r["m"]),
            "step": int(r.get("step", r["m"]))}


def sig(x):
    return {"decimal": str(x), "float": float(x)}


def energy_binding(r, prefix):
    x, y, z = [r[prefix + "_" + f] for f in ("HII", "HeII", "HeIII")]
    return CHI[0] * x + Y * (CHI[1] * y + (CHI[1] + CHI[2]) * z)


def electrons(r, prefix):
    return r[prefix + "_HII"] + Y * (r[prefix + "_HeII"] + 2 * r[prefix + "_HeIII"])


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), ZERO)


def formulas(r):
    p, c, rr = ([r[f"{prefix}_{j}"] for j in range(3)] for prefix in ("P", "C", "R"))
    net = [p[j] + c[j] - rr[j] for j in range(3)]
    capture = dot(CHI, rr) + CHI[1] * r["D"]
    rad = sum((r[f"CE_{j}"] for j in range(3)), ZERO) + sum((r[f"RRDR_{j}"] for j in range(4)), ZERO) + r["FF"]
    db = energy_binding(r, "final") - energy_binding(r, "initial")
    dw = r["final_w_eV_H"] - r["initial_w_eV_H"]
    ni = r["initial_active_N"] + r["initial_passive_N"]
    nf = r["final_active_N"] + r["final_passive_N"]
    ui = r["initial_active_U"] + r["initial_passive_U"]
    uf = r["final_active_U"] + r["final_passive_U"]
    dsn = r["source_N"] - r["initial_seed_N"]
    dsu = r["source_U"] - r["initial_seed_U"]
    xpred = r["initial_HII"] + net[0]
    ypred = r["initial_HeII"] + (net[1] - r["D"] - net[2]) / Y
    zpred = r["initial_HeIII"] + net[2] / Y
    wpred = r["initial_w_eV_H"] + r["photo_heat"] - dot(CHI, c) - rad + r["signed_CMB"] - r["gaswork"]
    epred = xpred + Y * (ypred + 2 * zpred)
    tpred = wpred * EV / (D("1.5") * KB * (1 + Y + epred))
    a = {
        "species_HII": r["final_HII"] - xpred,
        "species_HeII_per_H": Y * (r["final_HeII"] - ypred),
        "species_HeIII_per_H": Y * (r["final_HeIII"] - zpred),
        "electron_events": electrons(r, "final") - electrons(r, "initial") - sum(net, ZERO) + r["D"],
        "photo_binding": r["photo_binding"] - dot(CHI, p),
        "chemical_binding": db - dot(CHI, p) - dot(CHI, c) + capture,
        "thermal": dw - r["photo_heat"] + dot(CHI, c) + rad - r["signed_CMB"] + r["gaswork"],
        "escape": r["escape"] - capture - rad,
        "gas_binding_energy": dw + db + r["escape"] + r["gaswork"] - r["signed_CMB"] - r["photo_heat"] - r["photo_binding"],
        "photon_number": nf - ni + sum(p, ZERO) + r["boundary_N"] - dsn,
        "photon_energy": uf - ui + r["photonwork"] + r["boundary_U"] + r["photo_binding"] + r["photo_heat"] - dsu,
        "full_energy": dw + db + uf - ui + r["escape"] + r["gaswork"] + r["photonwork"] + r["boundary_U"] - dsu - r["signed_CMB"],
        "absorbed_number_ledger": r["absorbed_N"] - sum(p, ZERO),
        "seed_number_inventory": ni - r["initial_seed_N"],
        "seed_energy_inventory": ui - r["initial_seed_U"],
    }
    for prefix in ("initial", "final"):
        e = electrons(r, prefix)
        a[prefix + "_electron_eos"] = r[prefix + "_electrons_H"] - e
        a[prefix + "_binding_inventory"] = r[prefix + "_binding_eV_H"] - energy_binding(r, prefix)
        a[prefix + "_w_unit_conversion"] = r[prefix + "_w_erg_H"] / EV - r[prefix + "_w_eV_H"]
        a[prefix + "_thermal_eos_energy"] = D("1.5") * KB / EV * r[prefix + "_T_K"] * (1 + Y + e) - r[prefix + "_w_eV_H"]
    eos_correction = a["final_thermal_eos_energy"] - a["initial_thermal_eos_energy"]
    a["thermal_from_temperature_eos"] = a["thermal"] + eos_correction
    a["full_energy_from_temperature_eos"] = a["full_energy"] + eos_correction
    inferred = dict(zip(("final_HII", "final_HeII", "final_HeIII", "final_w_eV_H", "final_T_K"), (xpred, ypred, zpred, wpred, tpred)))
    return a, inferred


maxima = defaultdict(dict)


def record(group, name, value, row):
    old = maxima[group].get(name)
    if old is None or abs(value) > D(old["max_abs_decimal"]):
        maxima[group][name] = {"max_abs_decimal": str(abs(value)), "max_abs": float(abs(value)),
                                "signed_at_max": str(value), "at": at(row)}


rows = read("fixed_geometry.csv") + read("birth_histories.csv")
groups = defaultdict(list)
for row in rows:
    groups[key(row)].append(row)
    for k, v in formulas(row)[0].items():
        record("all", k, v, row)
        record(row["kind"], k, v, row)
for rs in groups.values():
    rs.sort(key=lambda r: int(r["step"]))

shape_errors = []
for (kind, m), rs in groups.items():
    if len(rs) != m or [int(r["step"]) for r in rs] != list(range(1, m + 1)):
        shape_errors.append([kind, m, "accepted step coverage"])
    if sum(int(r["is_final"]) for r in rs) != 1 or int(rs[-1]["is_final"]) != 1:
        shape_errors.append([kind, m, "final flag"])
    if any(r["steps"] != r["step"] or r["attempts"] != r["step"] or r["prefix_repeat"] != 0 for r in rs):
        shape_errors.append([kind, m, "counters"])

segment_map = {"dt_s": "total_time_s", "D": "D", "photoB": "photo_binding", "photoQ": "photo_heat",
               "DR": "RRDR_3", "FF": "FF", "CMB": "signed_CMB", "escape": "escape"}
for prefix in ("P", "C", "R", "CE"):
    segment_map.update({f"{prefix}{j}": f"{prefix}_{j}" for j in range(3)})
segment_map.update({f"RR{j}": f"RRDR_{j}" for j in range(3)})
segments = read("fixed_geometry.csv.segments.csv") + read("birth_histories.csv.segments.csv")
sgroups = defaultdict(list)
for r in segments:
    sgroups[key(r) + (int(r["step"]),)].append(r)
for (kind, m), rs in groups.items():
    cum = defaultdict(lambda: ZERO)
    for r in rs:
        ss = sorted(sgroups[(kind, m, int(r["step"]))], key=lambda v: v["segment"])
        expected = 1 if kind == "fixed_geometry" else 3
        if len(ss) != expected:
            shape_errors.append([kind, m, int(r["step"]), "segment count"])
        for s in ss:
            for f, target in segment_map.items():
                cum[target] += s[f]
        for target, value in cum.items():
            record("segment_reconstruction", target, value - r[target], r)
        if kind != "fixed_geometry":
            for j, s in enumerate(ss):
                record("segment_geometry", "a_mid", s["a_mid"] - (s["a_begin"] * s["a_end"]).sqrt(), r)
                h = H0 * (D(".315") / s["a_mid"]**3 + D(".000092") / s["a_mid"]**4 + 1 - D(".315") - D(".000092")).sqrt()
                exact_dt = (exact_float(s["a_end"]) / exact_float(s["a_begin"])).ln() / exact_float(native_hubble_float(s["a_mid"]))
                record("segment_geometry", "dt_relative_exact_float_endpoints_same_H", (exact_float(s["dt_s"]) - exact_dt) / exact_dt, r)
                record("segment_geometry", "H_float_vs_decimal_formula_relative", (exact_float(native_hubble_float(s["a_mid"])) - h) / h, r)
                if j and s["a_begin"] != ss[j-1]["a_end"]:
                    shape_errors.append([kind, m, int(r["step"]), "segment continuity"])
            if ss[-1]["a_end"] != r["final_a"]:
                shape_errors.append([kind, m, int(r["step"]), "segment endpoint"])

births = read("birth_histories.csv.births.csv")
bgroups = defaultdict(list)
for r in births:
    bgroups[key(r) + (int(r["step"]),)].append(r)
birth_zero_violation = 0
for (kind, m), rs in groups.items():
    bn, bu = ZERO, ZERO
    if kind == "fixed_geometry":
        continue
    for r in rs:
        bs = sorted(bgroups[(kind, m, int(r["step"]))], key=lambda v: v["node"])
        ss = sorted(sgroups[(kind, m, int(r["step"]))], key=lambda v: v["segment"])
        if len(bs) != 2:
            shape_errors.append([kind, m, int(r["step"]), "birth count"])
        for j, b in enumerate(bs):
            bn += b["added_N"]
            bu += b["added_U"]
            if b["proper_time_weight_s"] <= 0 or b["weight_dln_a"] <= 0:
                shape_errors.append([kind, m, int(r["step"]), "birth weight"])
            if b["a"] != ss[j]["a_end"]:
                shape_errors.append([kind, m, int(r["step"]), "birth chronological join"])
            if kind == "seeded_disabled_gl2" and (b["added_N"] != 0 or b["added_U"] != 0):
                birth_zero_violation += 1
            h = H0 * (D(".315") / b["a"]**3 + D(".000092") / b["a"]**4 + 1 - D(".315") - D(".000092")).sqrt()
            wt = b["weight_dln_a"] / h
            record("birth_geometry", "proper_weight_relative", (b["proper_time_weight_s"] - wt) / wt, r)
            c = (1 - 1 / D(3).sqrt()) / 2 if j == 0 else (1 + 1 / D(3).sqrt()) / 2
            expected_a = ss[0]["a_begin"] * (2 * b["weight_dln_a"] * c).exp()
            record("birth_geometry", "node_a", b["a"] - expected_a, r)
        record("birth_reconstruction", "source_N", bn + r["initial_seed_N"] - r["source_N"], r)
        record("birth_reconstruction", "source_U", bu + r["initial_seed_U"] - r["source_U"], r)

cells = read("fixed_geometry.csv.cells.csv") + read("birth_histories.csv.cells.csv")
cgroups = defaultdict(list)
negative_cells = 0
cone_violations = 0
for r in cells:
    cgroups[key(r)].append(r)
    if r["final_N"] < 0 or r["final_Uref"] < 0:
        negative_cells += 1
    if not r["lo"] * r["final_N"] <= r["final_Uref"] <= r["hi"] * r["final_N"]:
        cone_violations += 1
for k, cs in cgroups.items():
    r = groups[k][-1]
    if len(cs) != 128 or sorted(int(c["cell"]) for c in cs) != list(range(128)):
        shape_errors.append([*k, "cell coverage"])
    for prefix in ("initial", "final"):
        n = sum((c[prefix + "_N"] for c in cs), ZERO)
        uref = sum((c[prefix + "_Uref"] for c in cs), ZERO)
        scale = 1 if prefix == "initial" else r["initial_a"] / r["final_a"]
        record("cell_inventory", prefix + "_N", n - r[prefix + "_active_N"], r)
        record("cell_inventory", prefix + "_physical_U", uref * scale - r[prefix + "_active_U"], r)

channels = ["final_active_N", "final_active_U", "final_HII", "final_HeII", "final_HeIII", "final_w_eV_H", "final_T_K",
            "P_0", "P_1", "P_2", "photo_binding", "photo_heat", "signed_CMB", "source_N", "source_U"]
convergence = {}
decomposition = []
cell_convergence = {}
for kind in sorted({r["kind"] for r in rows}):
    levels = sorted(m for k, m in groups if k == kind)
    finals = [groups[(kind, m)][-1] for m in levels]
    ch = {}
    for field in channels:
        values = [r[field] for r in finals]
        diffs = [values[i] - values[i+1] for i in range(len(values)-1)]
        orders = [math.log2(float(abs(diffs[i] / diffs[i+1]))) if diffs[i] and diffs[i+1] else None for i in range(len(diffs)-1)]
        ch[field] = {"levels": levels, "values": [str(v) for v in values], "successive_signed_differences": [str(v) for v in diffs], "p_log2_abs_ratio": orders}
    convergence[kind] = ch
    for i in range(len(finals)-1):
        coarse, fine = finals[i:i+2]
        pc, pf = formulas(coarse)[1], formulas(fine)[1]
        for field in pc:
            observed = coarse[field] - fine[field]
            event_inferred = pc[field] - pf[field]
            defect = observed - event_inferred
            decomposition.append({"kind": kind, "coarse_m": levels[i], "fine_m": levels[i+1], "channel": field,
                                  "observed_difference": str(observed), "ledger_inferred_difference": str(event_inferred),
                                  "accounting_defect_difference": str(defect),
                                  "defect_fraction_of_observed_abs": float(abs(defect / observed)) if observed else None,
                                  "note": "ledger inference diagnoses output consistency; not an independent reference solution"})
    cc = {}
    for field in ("final_N", "final_Uref"):
        ds = []
        for mc, mf in zip(levels, levels[1:]):
            coarse = {int(c["cell"]): c for c in cgroups[(kind, mc)]}
            fine = {int(c["cell"]): c for c in cgroups[(kind, mf)]}
            ds.append(sum((abs(coarse[j][field] - fine[j][field]) for j in range(128)), ZERO))
        cc[field + "_L1"] = {"levels": levels, "differences": [str(d) for d in ds],
                              "p_log2_ratio": [math.log2(float(ds[i] / ds[i+1])) if ds[i+1] and ds[i] else None for i in range(len(ds)-1)]}
    cell_convergence[kind] = cc

clock_diagnosis = []
for (kind, m), rs in groups.items():
    if kind == "fixed_geometry":
        continue
    r = rs[-1]
    ss = [s for s in segments if key(s) == (kind, m)]
    a0, a1 = exact_float(r["initial_a"]), exact_float(r["final_a"])
    x = (a1 / a0).ln()
    def hubble(a):
        return H0 * (D(".315") / a**3 + D(".000092") / a**4 + 1 - D(".315") - D(".000092")).sqrt()
    ftime = lambda t: 1 / hubble(a0 * t.exp())
    simpson = x / 6 * (ftime(ZERO) + 4 * ftime(x / 2) + ftime(x))
    midpoint = sum(((exact_float(s["a_end"]) / exact_float(s["a_begin"])).ln() / exact_float(native_hubble_float(s["a_mid"])) for s in ss), ZERO)
    midpoint_exact_H = sum(((exact_float(s["a_end"]) / exact_float(s["a_begin"])).ln() / hubble(exact_float(s["a_mid"])) for s in ss), ZERO)
    actual = sum((exact_float(s["dt_s"]) for s in ss), ZERO)
    stable_matches = sum(float(s["dt_s"]) == math.log1p((float(s["a_end"]) - float(s["a_begin"])) / float(s["a_begin"])) / native_hubble_float(s["a_mid"]) for s in ss)
    old_matches = sum(float(s["dt_s"]) == math.log(float(s["a_end"]) / float(s["a_begin"])) / native_hubble_float(s["a_mid"]) for s in ss)
    clock_diagnosis.append({"kind": kind, "m": m,
        "printed_total_time_s": str(r["total_time_s"]),
        "decimal_sum_actual_segments_s": str(actual),
        "simpson_highprecision_endpoints_s": str(simpson),
        "midpoint_from_decimal_endpoints_s": str(midpoint),
        "endpoint_precision": "Decimal.from_float(float(csv_text)); reference uses same binary64 H formula",
        "midpoint_highprecision_H_s": str(midpoint_exact_H),
        "H_rounding_contribution_s": str(midpoint - midpoint_exact_H),
        "segments": len(ss), "recorded_dt_equal_stable_formula": stable_matches, "recorded_dt_equal_old_formula": old_matches,
        "actual_minus_midpoint_s": str(actual - midpoint),
        "midpoint_minus_simpson_s": str(midpoint - simpson),
        "actual_minus_simpson_s": str(actual - simpson),
        "approx_w_bias_from_clock_slope": str((r["final_w_eV_H"] - r["initial_w_eV_H"]) * (actual - simpson) / simpson)})

metadata = {}
for p in sorted(RAW.iterdir()):
    if p.suffix in (".csv", ".stdout", ".stderr", ".exit") or p.name in ("EXECUTION_RECEIPT.json", "SOURCE_RECEIPT.json", "INITIAL_SETTINGS.json") or p.name.endswith((".command.json", ".timing.json")):
        data = p.read_bytes()
        metadata[p.name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

result = {"schema": "rei.v15.independent_coupled_audit.1", "recorded_utc": datetime.now(timezone.utc).isoformat(),
          "reviewer": "/root/dropbox_v15_intake", "native_runs_started_by_reviewer": 0,
          "audit_method": "Decimal precision 60 over raw CSV numbers; no audit_* or owner_* values used. Clock checks expand exact binary64 endpoints/dt/H via Decimal.from_float after CSV roundtrip.",
          "raw_directory": str(RAW),
          "constants": {"Y": str(Y), "threshold_eV": [str(v) for v in CHI], "ev_erg": str(EV), "kb_erg_K": str(KB)},
          "counts": {"unique_histories": len(groups), "accepted_rows": len(rows), "segment_rows": len(segments), "birth_rows": len(births), "cell_rows": len(cells)},
          "accepted_dt_checks": {
              "fixed_segments": sum(s["kind"] == "fixed_geometry" for s in segments),
              "fixed_recorded_dt_equal_supplied_stage_dt": sum(float(s["dt_s"]) == 1.0 / (float(groups[key(s)][0]["k_ref20_s_inv"]) * int(s["m"])) for s in segments if s["kind"] == "fixed_geometry"),
              "birth_segments": sum(r["segments"] for r in clock_diagnosis),
              "birth_recorded_dt_equal_stable_formula": sum(r["recorded_dt_equal_stable_formula"] for r in clock_diagnosis)},
          "shape_errors": shape_errors, "disabled_nonzero_births": birth_zero_violation, "negative_final_cells": negative_cells,
          "strict_decimal_final_cone_violations": cone_violations,
          "observed_limits": {f: float(max(r[f] for r in rows)) for f in ("max_tau_stage1", "max_tau_stage2", "solver_max_residual", "quad_count_stage1", "quad_count_stage2", "quad_energy_stage1", "quad_energy_stage2", "boundary_N", "boundary_U", "final_passive_N", "final_passive_U")},
          "signed_cmb_range": [str(min(r["signed_CMB"] for r in rows)), str(max(r["signed_CMB"] for r in rows))],
          "maxima": dict(maxima), "convergence": convergence, "cell_convergence": cell_convergence,
          "clock_roundoff_diagnosis": clock_diagnosis,
          "gas_convergence_accounting_decomposition": decomposition, "raw_file_readback": metadata,
          "scope": "16 bounded native sandbox histories, no new NCP run; inventory audit includes actual zero boundary/passive fields; nonzero boundary flux not exercised"}
(OUT / "COUPLED_INDEPENDENT_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n")
(OUT / "COUPLED_CLOCK_ROUNDOFF_DIAGNOSIS.json").write_text(json.dumps({
    "method": "Post-process existing exact binary64 segment endpoints/dt via Decimal.from_float; Decimal60 log ratio with same binary64 H formula, plus independent high precision FLRW H/Simpson diagnostic, no native rerun",
    "simpson_scope": "Smooth analytic FLRW 1/H(log a), short actual endpoint interval; diagnostic not certified interval bound",
    "temperature_bias_scope": "Average-drift time sensitivity is a scale estimate, not a correction to the trajectory or a proof of the exact error cause",
    "rows": clock_diagnosis}, indent=2) + "\n")
with (OUT / "COUPLED_CONVERGENCE_DECOMPOSITION.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(decomposition[0]))
    writer.writeheader()
    writer.writerows(decomposition)
print(json.dumps({k: result[k] for k in ("counts", "shape_errors", "disabled_nonzero_births", "negative_final_cells", "strict_decimal_final_cone_violations", "observed_limits", "signed_cmb_range")}, indent=2))
print(json.dumps({"maxima_all": result["maxima"]["all"], "cell_inventory": result["maxima"]["cell_inventory"]}, indent=2))
for kind, ch in convergence.items():
    print(json.dumps({"kind": kind, "orders": {f: ch[f]["p_log2_abs_ratio"] for f in channels}, "cell_orders": cell_convergence[kind]}, indent=2))
