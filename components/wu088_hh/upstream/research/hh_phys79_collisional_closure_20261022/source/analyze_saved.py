"""Source-domain-bounded collision diagnostics on two immutable PHYS78 histories.

No IVP is integrated. All CI additions below are instantaneous operator probes
at unchanged old states. Invalid fit temperatures remain masked NaN, never zero.
D-CX's 43 k_B isotope energy shift is a new local ledger convention; it does not
retroactively alter the old isotope-blind PI/RR trajectory or its binding energy.
"""
from __future__ import annotations

import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import time

import numpy as np

import collisional
from phys78_bridge import atomic

UNIT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = UNIT / "inputs" / "phys78_selected"
DEFAULT_OUTPUT = UNIT / "analysis" / "saved_operator"
SCOPE = "CONDITIONAL_INSTANTANEOUS_OPERATOR_ON_UNCHANGED_PHYS78_SAVED_STATES"
EXPECTED = {
    "P013": {
        "filename": "ae604dcf96ddce8f9f970c7d2a4da22231a6bff4dc24d76b886dd602d870ca4b.npz",
        "sha256": "9101008f160908c7cabde566e20183f3f1cda1a5829d89844cd5ee2425605ee5",
        "uv_scale": 1.0,
    },
    "P030": {
        "filename": "e670cd4c365fe9cc13dfdcb0a1372a8c5dd58471c5eb29c9db00465b9a53821f.npz",
        "sha256": "1344faa08cc07f56606241e080d3c6482962ef5b4f9a7e7e13a09275519f31b8",
        "uv_scale": 2.0,
    },
}
ELEMENT_LABELS = ("H I", "He I", "He II", "Li I", "Li II", "Li III")
CI_MIN_EV = np.array([1., 1., 3., 1., 4., 5.])
NEUTRAL_ROWS = (0, 1, 3)
KB_EV_K = 1.380649e-23 / 1.602176634e-19
MYR_S = 365.25 * 86400. * 1e6


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_case(directory, case_id):
    """Hash and parse the same bytes, so a second path read cannot change input."""
    expected = EXPECTED[case_id]
    path = Path(directory) / expected["filename"]
    raw = path.read_bytes()
    if sha256(raw) != expected["sha256"]:
        raise ValueError("PHYS78_NPZ_IDENTITY_MISMATCH:" + case_id)
    with np.load(io.BytesIO(raw), allow_pickle=False) as f:
        data = {k: np.array(f[k], copy=True) for k in f.files}
    metadata_raw = path.with_suffix(".json").read_bytes()
    metadata = json.loads(metadata_raw)
    if metadata["case"]["id"] != case_id:
        raise ValueError("PHYS78_CASE_LABEL_MISMATCH")
    if metadata["binding"]["physical_case"]["uv_scale"] != expected["uv_scale"]:
        raise ValueError("PHYS78_PHYSICAL_INPUT_MISMATCH")
    scalar = ("x", "z", "T_K", "nH_cm3", "elapsed_seconds", "H_per_s", "xe")
    for k in scalar:
        if data[k].shape != (161,) or not np.isfinite(data[k]).all():
            raise ValueError("PHYS78_SCALAR_SHAPE_OR_FINITE:" + k)
    for k, shape in (("Y", (161, 21)), ("UV_mean_eV", (161, 3)),
                     ("UV_N_perH", (161, 3))):
        if data[k].shape != shape or not np.isfinite(data[k]).all():
            raise ValueError("PHYS78_ARRAY_SHAPE_OR_FINITE:" + k)
    if tuple(data["species_names"]) != tuple(atomic.SPECIES_NAMES):
        raise ValueError("PHYS78_SPECIES_ORDER_MISMATCH")
    if (np.any(data["Y"] < 0) or np.any(data["UV_N_perH"] <= 0)
            or np.any(data["T_K"] <= 0) or np.any(data["nH_cm3"] <= 0)):
        raise ValueError("PHYS78_PHYSICAL_DOMAIN_NO_CLIPPING")
    if not (np.all(np.diff(data["elapsed_seconds"]) > 0)
            and np.all(np.diff(data["z"]) < 0)):
        raise ValueError("PHYS78_CLOCK_ORDER")
    if not np.allclose(data["z"][[0, -1]], [20., 2.], rtol=0, atol=1e-12):
        raise ValueError("PHYS78_REDSHIFT_WINDOW")
    if np.max(np.abs(data["Y"] @ atomic.CHARGE - data["xe"])) > 2e-14:
        raise ValueError("PHYS78_ELECTRON_CENSUS_MISMATCH")
    identity = {"case_id": case_id, "npz_filename": path.name,
                "npz_bytes": len(raw), "npz_sha256": sha256(raw),
                "metadata_sha256": sha256(metadata_raw),
                "science_identity": path.stem,
                "old_source_manifest": metadata["binding"]["source"],
                "physical_case": metadata["binding"]["physical_case"]}
    return data, identity


def ratio(numerator, denominator, mask=None):
    a, b = np.broadcast_arrays(np.asarray(numerator, float), np.asarray(denominator, float))
    good = np.isfinite(a) & np.isfinite(b) & (b > 0)
    if mask is not None:
        good &= np.broadcast_to(np.asarray(mask, bool), a.shape)
    result = np.full(a.shape, np.nan)
    np.divide(a, b, out=result, where=good)
    return result


def extrema(values, data):
    v = np.asarray(values, float)
    finite = np.flatnonzero(np.isfinite(v))
    if not len(finite):
        return {"count": 0, "minimum": None, "maximum": None}
    i = int(finite[np.argmax(v[finite])])
    return {"count": int(len(finite)), "minimum": float(np.min(v[finite])),
            "maximum": float(v[i]), "maximum_epoch_index": i,
            "maximum_z": float(data["z"][i]),
            "maximum_T_K": float(data["T_K"][i])}


def analyze_case(data):
    n = len(data["T_K"])
    fit_mask = np.asarray(collisional.ci_domain_mask(data["T_K"]), dtype=bool)
    if fit_mask.shape != (n, 6):
        raise ValueError("CI_DOMAIN_MASK_SHAPE")
    expected_mask = ((data["T_K"][:, None] * KB_EV_K >= CI_MIN_EV[None, :])
                     & (data["T_K"][:, None] * KB_EV_K <= 20000.))
    if not np.array_equal(fit_mask, expected_mask):
        raise ValueError("CI_DOMAIN_CONTRACT_DISAGREEMENT")
    valid_neutral = np.all(fit_mask[:, NEUTRAL_ROWS], axis=1)
    prepared = atomic.prepare_network((18., 30., 60.))
    ci_network = collisional.CollisionNetwork(ci_rows=NEUTRAL_ROWS, d_cx=False)
    full_network = collisional.CollisionNetwork(ci_rows=NEUTRAL_ROWS, d_cx=True)
    lower, rows = np.asarray(prepared.lower), np.asarray(prepared.element_row)
    ci_k = np.full((n, 6), np.nan)
    ci_events = np.full((n, 6), np.nan)
    pi_events, rr_events = np.zeros((n, 6)), np.zeros((n, 6))
    pi_heat, rr_cooling = np.empty(n), np.empty(n)
    ci_cooling, ci_binding, ci_electron = (np.full(n, np.nan) for _ in range(3))
    full_local_residual = np.full(n, np.nan)
    d_kf, d_kr, d_raw_kf, d_raw_kr = (np.empty(n) for _ in range(4))
    d_forward, d_reverse, d_heat = (np.empty(n) for _ in range(3))
    d_pi, d_rr, d_balance = (np.empty(n) for _ in range(3))
    old_energy_residual = np.empty(n)
    d_lo = atomic.SPECIES_INDEX["D_I"]
    d_hi = atomic.SPECIES_INDEX["D_II"]
    h_lo = atomic.SPECIES_INDEX["H1_I"]
    h_hi = atomic.SPECIES_INDEX["H1_II"]
    d_transition = int(np.flatnonzero(lower == d_lo)[0])
    for i, temperature in enumerate(data["T_K"]):
        y, nh = data["Y"][i], float(data["nH_cm3"][i])
        point = prepared.rhs(float(temperature), nh, y, nh*data["UV_N_perH"][i],
                             photon_energy_eV=data["UV_mean_eV"][i])
        up = np.sum(point.photo_event_per_H_s, axis=1)
        pi_events[i] = np.bincount(rows, weights=up, minlength=6)
        rr_events[i] = np.bincount(rows, weights=point.rr_event_per_H_s, minlength=6)
        pi_heat[i] = point.photo_heat_eV_per_H_s
        rr_cooling[i] = point.rr_kinetic_cooling_eV_per_H_s
        old_energy_residual[i] = point.energy_ledger_residual_eV_per_H_s
        d_pi[i], d_rr[i] = up[d_transition], point.rr_event_per_H_s[d_transition]
        # Evaluate only source-admitted neutral rows; unsupported rows stay NaN.
        for row in NEUTRAL_ROWS:
            if fit_mask[i, row]:
                ci_k[i, row] = collisional.ci_rate(row, float(temperature))
                ci_events[i, row] = (point.electron_density_cm3 * ci_k[i, row]
                                     * float(y[lower[rows == row]].sum()))
        if valid_neutral[i]:
            ci = ci_network.rhs(float(temperature), nh, y)
            ci_cooling[i] = -ci.heat_eV_per_H_s
            ci_binding[i] = ci.binding_derivative_eV_per_H_s
            ci_electron[i] = ci.d_electron_per_H_dt
            full = full_network.rhs(float(temperature), nh, y)
            full_local_residual[i] = (full.heat_eV_per_H_s
                                     + full.binding_derivative_eV_per_H_s)
            if not np.isclose(ci_electron[i], np.nansum(ci_events[i]), rtol=2e-14, atol=0):
                raise ArithmeticError("CI_ELECTRON_EVENT_INDEPENDENT_RECONSTRUCTION")
        d_kf[i], d_kr[i] = collisional.d_cx_rates(float(temperature), closure="detailed_balance")
        d_raw_kf[i], d_raw_kr[i] = collisional.d_cx_rates(float(temperature), closure="raw_fit")
        d_forward[i] = nh*d_kf[i]*y[d_lo]*y[h_hi]
        d_reverse[i] = nh*d_kr[i]*y[d_hi]*y[h_lo]
        d_heat[i] = -43.*KB_EV_K*(d_forward[i]-d_reverse[i])
        d_balance[i] = (d_kf[i]/d_kr[i])/np.exp(-43./float(temperature)) - 1.
    arrays = {"x": data["x"], "z": data["z"], "T_K": data["T_K"],
              "elapsed_Myr": data["elapsed_seconds"]/MYR_S,
              "nH_cm3": data["nH_cm3"], "ne_cm3": data["nH_cm3"]*data["xe"],
              "fit_domain_mask": fit_mask, "neutral_CI_valid": valid_neutral,
              "CI_rate_cm3_s": ci_k, "CI_event_perH_s": ci_events,
              "PI_event_perH_s": pi_events, "RR_event_perH_s": rr_events,
              "CI_over_PI": ratio(ci_events, pi_events, fit_mask),
              "CI_over_RR": ratio(ci_events, rr_events, fit_mask),
              "PI_heat_eV_perH_s": pi_heat, "RR_kinetic_cooling_eV_perH_s": rr_cooling,
              "CI_threshold_cooling_eV_perH_s": ci_cooling,
              "CI_binding_gain_eV_perH_s": ci_binding,
              "CI_electron_perH_s": ci_electron,
              "CI_cooling_over_PI_heat": ratio(ci_cooling, pi_heat, valid_neutral),
              "CI_cooling_over_RR_kinetic": ratio(ci_cooling, rr_cooling, valid_neutral),
              "local_collision_energy_residual_eV_perH_s": full_local_residual,
              "old_PI_RR_energy_residual_eV_perH_s": old_energy_residual,
              "D_CX_forward_cm3_s": d_kf, "D_CX_reverse_DB_cm3_s": d_kr,
              "D_CX_forward_raw_cm3_s": d_raw_kf, "D_CX_reverse_raw_cm3_s": d_raw_kr,
              "D_CX_raw_ratio_over_DB": (d_raw_kf/d_raw_kr)/np.exp(-43./data["T_K"]),
              "D_CX_DB_residual": d_balance,
              "D_CX_forward_event_perH_s": d_forward,
              "D_CX_reverse_event_perH_s": d_reverse,
              "D_CX_heat_eV_perH_s": d_heat,
              "D_PI_event_perH_s": d_pi, "D_RR_event_perH_s": d_rr,
              "D_CX_forward_over_D_PI": ratio(d_forward, d_pi),
              "D_CX_reverse_over_D_RR": ratio(d_reverse, d_rr)}
    summary = {
        "saved_epochs": n, "T_min_K": float(np.min(data["T_K"])),
        "T_max_K": float(np.max(data["T_K"])),
        "neutral_CI_admitted_epochs": int(valid_neutral.sum()),
        "neutral_CI_excluded_epochs": int((~valid_neutral).sum()),
        "all_six_CI_rows_admitted_epochs": int(np.all(fit_mask, axis=1).sum()),
        "fit_domain_counts": {label: int(fit_mask[:, r].sum()) for r, label in enumerate(ELEMENT_LABELS)},
        "CI_over_PI": {ELEMENT_LABELS[r]: extrema(arrays["CI_over_PI"][:, r], data) for r in NEUTRAL_ROWS},
        "CI_over_RR": {ELEMENT_LABELS[r]: extrema(arrays["CI_over_RR"][:, r], data) for r in NEUTRAL_ROWS},
        "CI_cooling_over_PI_heat": extrema(arrays["CI_cooling_over_PI_heat"], data),
        "CI_cooling_over_RR_kinetic": extrema(arrays["CI_cooling_over_RR_kinetic"], data),
        "D_CX_raw_ratio_over_DB": extrema(arrays["D_CX_raw_ratio_over_DB"], data),
        "D_CX_forward_over_D_PI": extrema(arrays["D_CX_forward_over_D_PI"], data),
        "D_CX_reverse_over_D_RR": extrema(arrays["D_CX_reverse_over_D_RR"], data),
        "D_CX_DB_max_absolute_residual": float(np.max(np.abs(d_balance))),
        "local_collision_energy_max_absolute_residual_eV_perH_s": float(np.nanmax(np.abs(full_local_residual))),
        "old_PI_RR_energy_max_absolute_residual_eV_perH_s": float(np.max(np.abs(old_energy_residual))),
        "unsupported_rate_semantics": "NaN plus false validity mask; neither zero rate nor fitted extrapolation",
        "nonneutral_CI": "not evaluated: all saved temperatures are below corresponding author fit minima",
        "D_CX_energy_scope": "43 k_B isotope shift is local new collision accounting; old PI/RR binding was isotope-blind",
        "interpretation": SCOPE,
    }
    return arrays, summary


def write_csv(path, arrays):
    keys = [k for k, v in arrays.items() if v.ndim == 1]
    fields = keys + ["CI_over_PI_"+str(r) for r in NEUTRAL_ROWS]
    with Path(path).open("x", newline="") as f:
        w = csv.writer(f); w.writerow(fields)
        for i in range(len(arrays["z"])):
            w.writerow([arrays[k][i] for k in keys]
                       + [arrays["CI_over_PI"][i, r] for r in NEUTRAL_ROWS])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError("CREATE_ONLY_ANALYSIS_OUTPUT_ALREADY_EXISTS")
    args.output.mkdir(parents=True, exist_ok=True)
    wall, cpu = time.perf_counter(), time.process_time()
    source_paths = [Path(__file__).resolve(), Path(collisional.__file__).resolve(),
                    Path(atomic.__file__).resolve(), Path(__file__).with_name("phys78_bridge.py")]
    sources = {str(p.relative_to(UNIT)): sha256(p.read_bytes()) for p in source_paths}
    request = {"scope": SCOPE, "source_sha256": sources, "expected_inputs": EXPECTED,
               "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "new_ODE": 0, "NCP": 0, "threads": 1}
    (args.output/"REQUEST.json").write_text(json.dumps(request, indent=2)+"\n")
    summaries, identities = {}, {}
    try:
        for case_id in EXPECTED:
            data, identities[case_id] = read_case(args.input, case_id)
            arrays, summaries[case_id] = analyze_case(data)
            np.savez_compressed(args.output/(case_id+".npz"), **arrays)
            write_csv(args.output/(case_id+".csv"), arrays)
        outputs = {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p.read_bytes())}
                   for p in sorted(args.output.iterdir()) if p.is_file()}
        summary = {**request, "status": "COMPLETED_SCOPED_SAVED_OPERATOR_DIAGNOSTIC",
                   "input_identities": identities, "cases": summaries,
                   "total_saved_epochs": 322, "source_evaluations_PI_RR": 322,
                   "outputs": outputs, "wall_seconds": time.perf_counter()-wall,
                   "cpu_seconds": time.process_time()-cpu, "HH_R10": "OFF",
                   "production_admission": "NOT_ISSUED",
                   "changed_old_trajectory_files": 0,
                   "corrected_trajectory_or_species_off_causal_experiment": False}
        (args.output/"SUMMARY.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
        print(json.dumps({"status": summary["status"], "epochs": 322,
                          "new_ODE": 0, "cases": summaries}, allow_nan=False))
    except BaseException as exc:
        failure = {**request, "status": "FAILED", "error_type": type(exc).__name__,
                   "error": str(exc), "wall_seconds": time.perf_counter()-wall,
                   "cpu_seconds": time.process_time()-cpu,
                   "partial_cases": list(summaries), "new_ODE": 0}
        (args.output/"FAILURE.json").write_text(json.dumps(failure, indent=2)+"\n")
        raise


if __name__ == "__main__":
    main()
