#!/usr/bin/env python3
"""Reconstruct conditional full-interval omitted shear-stress response from saved AX08 rows.
No solver. Trapezoidal sampled diagnostic, NOT a rigorous dynamical bound.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
G_SI = 6.67430e-11                # m^3 kg^-1 s^-2
C_SI = 299792458.0               # m s^-1
COEFF = 8.0 * math.pi * G_SI / (3.0 * C_SI**2)
CEILING = 1e-4
PREFIX = "research/axbi_goal_20261014/runs/"
PATHS = {
    "ZERO": ROOT / (PREFIX + "flrw/32d11e733155/ZERO_composed_001/feedback.csv"),
    "SHEAR_HALF_PLUS": ROOT / (PREFIX + "paired/32d11e733155/SHEAR_HALF_PLUS_composed_002/feedback.csv"),
}

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def accumulate(path, case):
    source_cols = ("effective_radiation_DeltaP_J_m3", "ionizing_DeltaP_J_m3")
    summed = [0., 0.]
    compensated = [0., 0.]
    highest = {"abs_delta_s_over_H": -1., "t_s": None, "a": None, "delta_s_over_H": None}
    highest_extra = {"abs_ratio": -1., "t_s": None, "a": None, "ratio": None}
    prev = None
    n = 0
    endpoints = None
    with path.open(newline="") as source:
        for row in csv.DictReader(source):
            if row["case_id"] != case:
                raise ValueError("HOLD_CASE_ID:" + case)
            t, a, H = (float(row[k]) for k in ("time_s", "a", "H_per_s"))
            p = [float(row[k]) for k in source_cols]
            total = float(row["total_DeltaP_J_m3"])
            extra = float(row["extra_energy_ratio"])
            if not all(map(math.isfinite, (t,a,H,total,extra,*p))) or a <= 0 or H <= 0:
                raise ValueError("HOLD_NONFINITE_OR_UNPHYSICAL")
            if not math.isclose(sum(p), total, abs_tol=1e-25, rel_tol=1e-12):
                raise ValueError("HOLD_UNOWNED_PRESSURE")
            if prev is not None:
                old_t, old_a, old_p = prev
                if t <= old_t or a <= old_a:
                    raise ValueError("HOLD_CLOCK_OR_SCALE_ORDER")
                dt = t-old_t
                for j in (0,1):
                    area = .5 * (old_a**3 * old_p[j] + a**3 * p[j]) * dt
                    z = area - compensated[j]
                    s = summed[j] + z
                    compensated[j] = (s-summed[j])-z
                    summed[j] = s
            else:
                if abs(t) > 1e-4 or not math.isclose(a,1./21.,rel_tol=0,abs_tol=1e-16):
                    raise ValueError("HOLD_INITIAL_CLOCK")
            components = [COEFF*item/(a**3*H) for item in summed]
            result = sum(components)
            if abs(result) > highest["abs_delta_s_over_H"]:
                highest = {"abs_delta_s_over_H": abs(result),"t_s":t,"a":a,"delta_s_over_H":result}
            if abs(extra) > highest_extra["abs_ratio"]:
                highest_extra = {"abs_ratio":abs(extra),"t_s":t,"a":a,"ratio":extra}
            endpoints = (t, a, components, result, extra)
            prev = (t,a,p)
            n += 1
    if n != 312238 or endpoints is None or endpoints[1] != .2:
        raise ValueError("HOLD_INCOMPLETE_REPRESENTED_INTERVAL")
    return {
       "case":case,"n_rows":n,"source_feedback_path":str(path.relative_to(ROOT)),
       "source_feedback_sha256":digest(path),
       "endpoint":{"time_s":endpoints[0],"a":endpoints[1],
                    "effective_radiation_delta_s_over_H":endpoints[2][0],
                    "ionizing_delta_s_over_H":endpoints[2][1],
                    "total_delta_s_over_H":endpoints[3],
                    "extra_energy_ratio":endpoints[4]},
       "max_abs_delta_s_over_H":highest,
       "max_abs_extra_energy_ratio":highest_extra,
       "pressure_stress_policy_ceiling":CEILING,
       "measured_below_perturbative_ceiling":highest["abs_delta_s_over_H"]<CEILING and highest_extra["abs_ratio"]<CEILING
    }
if __name__ == "__main__":
    results = {case:accumulate(path,case) for case,path in PATHS.items()}
    receipt = {
        "schema":"rei.axbi.reconstructed_feedback.v1",
        "status":"SAMPLED_FULL_HISTORY_FEEDBACK_RECONSTRUCTION",
        "model_scope":"prescribed Bianchi I, initial isotropic effective Omega_r stress plus actual ionizing quadrupole",
        "method":"time-ordered composite trapezoid of a^3 pressure in SI, with compensated summation, divided by a^3 H",
        "coefficient_SI":COEFF,"G_SI":G_SI,"c_SI":C_SI,
        "numerical_quadrature_uncertainty":"NOT_QUANTIFIED",
        "feedback_on_dynamics":"NOT_APPLIED; perturbative omitted-stress diagnostic only",
        "scientific_admission":"NOT_ISSUED",
        "results":results
    }
    (HERE/"feedback_reconstruction.json").write_text(json.dumps(receipt,indent=2)+"\n")
    for case,item in results.items():
        print(case, "max_abs_delta_s_over_H",item["max_abs_delta_s_over_H"]["abs_delta_s_over_H"],
              "endpoint_delta_s_over_H",item["endpoint"]["total_delta_s_over_H"],
              "max_extra_energy_ratio",item["max_abs_extra_energy_ratio"]["abs_ratio"],
              "under_policy_ceiling",item["measured_below_perturbative_ceiling"])
