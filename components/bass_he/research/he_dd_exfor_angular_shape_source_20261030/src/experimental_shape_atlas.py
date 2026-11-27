#!/usr/bin/env python3
"""Source-observed 4He(gamma,dd) angular shape descriptors.

This code computes *only* dimensionless source-data contrasts and conditional
weighted fits from the original, pinned IAEA EXFOR M0475.x4. Neither the
unmeasured exclusive reaction event-rate normalization nor the Fermi gamma
spectrum/target rest frame is supplied or inferred.
"""
from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
from collections import defaultdict
import argparse
import csv
import hashlib
import io
import json
import math

import numpy as np
from scipy.stats import chi2

EXPECTED_SHA256 = "b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f"
EXPECTED_SOURCE_GIT_BLOB = "c49433293921dbb012d7f1b0387745732a598efa"
ENERGIES = (213, 258, 330)
ANGLES = (46, 61, 73, 87)
SOURCE_COMMIT = "939a14d7bba1ddce51975cb5e8711ce96b3b0871"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parse_original(source: Path):
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256 or git_blob(raw) != EXPECTED_SOURCE_GIT_BLOB:
        raise ValueError("SOURCE_IDENTITY_MISMATCH")
    data = raw.decode("ascii")
    sec = data.split("SUBENT        M0475002", 1)[1].split("ENDSUBENT", 1)[0]
    if "REACTION   (2-HE-4(G,D)1-H-2,,DA)" not in sec or "NB/SR      NB/SR" not in sec:
        raise ValueError("UNQUALIFIED_OR_NON_DA_SOURCE")
    table = sec.split("MEV        ADEG       NB/SR      NB/SR", 1)[1].split("ENDDATA", 1)[0]
    records = []
    for line in table.splitlines():
        parts = line.split()
        if len(parts) == 4:
            try:
                en = Q(parts[0]); theta = Q(parts[1]); value = Q(parts[2]); err = Q(parts[3])
            except (ValueError, ZeroDivisionError):
                continue
            if value <= 0 or err < 0:
                raise ValueError("NEGATIVE_OBSERVATION")
            records.append({"E_gamma_MeV": int(en), "theta_CM_deg": int(theta),
                            "DA_nb_per_srCM": value, "ERR_S_nb_per_srCM": err})
    if [(r["E_gamma_MeV"], r["theta_CM_deg"]) for r in records] != [(e, a) for e in ENERGIES for a in ANGLES]:
        raise ValueError("EXPECTED_MEASURED_GRID_MISSING")
    # The source SIG subentry is NOT the same experiment coordinate grid.
    sig = data.split("SUBENT        M0475003", 1)[1].split("ENDSUBENT", 1)[0]
    if "(2-HE-4(G,D)1-H-2,,SIG)" not in sig or "  330." in sig:
        raise ValueError("UNQUALIFIED_SIG_STATUS")
    return records


def rational_string(q: Q) -> str:
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def contrast(a: dict, b: dict, dimension: str):
    # b-a divided by b+a. Reported ERR-S Cartesian box is NOT a confidence set.
    av, ae = a["DA_nb_per_srCM"], a["ERR_S_nb_per_srCM"]
    bv, be = b["DA_nb_per_srCM"], b["ERR_S_nb_per_srCM"]
    if min(av-ae, bv-be) <= 0:
        raise ValueError("ERR_S_BOX_CROSSES_ZERO")
    c = (bv-av)/(bv+av)
    lo = ((bv-be)-(av+ae))/((bv-be)+(av+ae))
    hi = ((bv+be)-(av-ae))/((bv+be)+(av-ae))
    ua = abs(-2*bv/(av+bv)**2 * ae)
    ub = abs(2*av/(av+bv)**2 * be)
    return {"dimension": dimension,
            "a": [a["E_gamma_MeV"], a["theta_CM_deg"]],
            "b": [b["E_gamma_MeV"], b["theta_CM_deg"]],
            "contrast_exact": rational_string(c),
            "contrast": float(c),
            "ERR_S_box_min_exact": rational_string(lo),
            "ERR_S_box_max_exact": rational_string(hi),
            "ERR_S_box_min": float(lo), "ERR_S_box_max": float(hi),
            "delta_sigma_independent_ONLY": math.hypot(float(ua), float(ub)),
            "delta_sigma_covariance_unknown_min": float(abs(ua-ub)),
            "delta_sigma_covariance_unknown_max": float(ua+ub),
            "status": "MEASURED_POINT_CONTRAST_WITH_ERROR_BOX_NOT_JOINT_CI"}


def fit_models(rows: list[dict]):
    en = rows[0]["E_gamma_MeV"]
    theta = np.radians([r["theta_CM_deg"] for r in rows]); cs2 = np.cos(theta)**2; sin2 = 1-cs2
    data = np.array([float(r["DA_nb_per_srCM"]) for r in rows])
    error = np.array([float(r["ERR_S_nb_per_srCM"]) for r in rows])
    bases = {"constant": np.ones((4,1)),
             "sin_squared": sin2[:,None],
             "even_quartic": np.column_stack([sin2, sin2*cs2])}
    fits=[]
    for name, design in bases.items():
        w=1/error**2
        param=np.linalg.solve(design.T@(w[:,None]*design),design.T@(w*data))
        pred=design@param
        stat=float(np.sum(((pred-data)/error)**2)); dof=len(rows)-len(param)
        fits.append({"E_gamma_MeV": en,"model":name,"model_basis":
                     ["1"] if name=="constant" else (["sin²θ"] if name=="sin_squared" else ["sin²θ","sin²θ cos²θ"]),
                     "parameters_nb_per_srCM":param.tolist(),"chi_squared_conditional_independent_ERR_S":stat,
                     "dof":dof,"pvalue_conditional_Gaussian_independent":float(chi2.sf(stat,dof)),
                     "predicted_nb_per_srCM_at_measured_angles":pred.tolist(),
                     "out_of_measured_angle_support_extrapolation": name!="constant",
                     "not_detector_corrected":True})
    return fits


def build(source:Path) -> dict:
    rows=parse_original(source)
    grouped=defaultdict(list)
    for r in rows: grouped[r["E_gamma_MeV"]].append(r)
    output={"schema":"BASS_HE_EXFOR_M0475_EMPIRICAL_ANGULAR_SHAPES_V1",
            "source":{"repository":"IAEA-NDS/exfor_master","commit":SOURCE_COMMIT,
                      "path":"exforall/M04/M0475.x4","sha256":EXPECTED_SHA256,
                      "git_blob":EXPECTED_SOURCE_GIT_BLOB,"subentry":"M0475002","value_units":"nb/sr_CM",
                      "pointwise_error":"ERR-S only, correlation unknown"},
            "original_measured_rows":[{"E_gamma_MeV":r["E_gamma_MeV"],
                   "theta_CM_deg":r["theta_CM_deg"],"DA_nb_per_srCM_exact":rational_string(r["DA_nb_per_srCM"]),
                   "ERR_S_nb_per_srCM_exact":rational_string(r["ERR_S_nb_per_srCM"])} for r in rows],
            "pairwise_shape_contrasts":[], "statistical_fit_diagnostics":[],
            "admissibility":{"R_event":None,"heat_rate":None,"kappa":None,"L4":False,
                              "production":"HOLD","independent_R6_C9":"NOT_RUN",
                              "source_angular_covariance":None,"source_detector_angle_acceptance":None,
                              "source_efficiency_calibration":None,"source_330_total_SIG":None,
                              "central_DAG":"28/88","HE_physical_DAG":"14/18",
                              "PR119_angular_DAG":"2/3_UNCHANGED",
                              "new_shape_source_scoped":"1/1", "physical_delta":0}}
    for en in ENERGIES:
        a=grouped[en];output["statistical_fit_diagnostics"].extend(fit_models(a))
        for i in range(4):
            for j in range(i+1,4): output["pairwise_shape_contrasts"].append(contrast(a[i],a[j],"WITHIN_ENERGY_ANGLE_PAIR"))
    for angle in ANGLES:
        a=[next(z for z in grouped[en] if z["theta_CM_deg"]==angle) for en in ENERGIES]
        for i in range(3):
            for j in range(i+1,3):output["pairwise_shape_contrasts"].append(contrast(a[i],a[j],"FIXED_ANGLE_ENERGY_PAIR"))
    assert len(output["pairwise_shape_contrasts"])==30
    assert len(output["statistical_fit_diagnostics"])==9
    return output


def generate(root:Path):
    obj=build(root/"sources/M0475.x4")
    output=root/"results";output.mkdir(parents=True,exist_ok=True)
    (output/"SOURCE_ANGULAR_SHAPES.json").write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    with (output/"MEASURED_30_SHAPE_CONTRASTS.csv").open("w",newline="") as fo:
        keys=["dimension","a","b","contrast_exact","contrast","ERR_S_box_min","ERR_S_box_max","delta_sigma_independent_ONLY","delta_sigma_covariance_unknown_min","delta_sigma_covariance_unknown_max"]
        writer=csv.DictWriter(fo,fieldnames=keys,lineterminator="\n");writer.writeheader()
        for z in obj["pairwise_shape_contrasts"]:writer.writerow({k:json.dumps(z[k]) if k in ["a","b"] else z[k] for k in keys})
    with (output/"SOURCE_9_SHAPE_MODEL_FITS.csv").open("w",newline="") as fo:
        writer=csv.DictWriter(fo,fieldnames=["E_gamma_MeV","model","parameters_nb_per_srCM","chi_squared_conditional_independent_ERR_S","dof","pvalue_conditional_Gaussian_independent"],lineterminator="\n");writer.writeheader()
        for z in obj["statistical_fit_diagnostics"]:
            writer.writerow({k:json.dumps(z[k]) if k=="parameters_nb_per_srCM" else z[k] for k in writer.fieldnames})
    return obj

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parent.parent)
    ns=ap.parse_args();result=generate(ns.root)
    print("source observations",len(result["original_measured_rows"]),"exact contrasts",len(result["pairwise_shape_contrasts"]),"conditional fits",len(result["statistical_fit_diagnostics"]))
