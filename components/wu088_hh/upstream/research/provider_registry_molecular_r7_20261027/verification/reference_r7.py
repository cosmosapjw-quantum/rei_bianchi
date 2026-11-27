#!/usr/bin/env python3
"""Independent R7 numerical corroboration; no production/reused science imports.

The caller supplies a frozen primary JSON, its SHA256, this fixed input, and a
new output path.  This entry point is intended for the single authorized R7
reference run.  It does not fetch sources, rerun R6, or infer physical inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(value: Any) -> Fraction:
    """Read declared exact inputs without silently rounding/renormalizing."""
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"Expected exact integer/rational string, got {type(value).__name__}")
    return Fraction(value)


def exact_vector(value: Any, n: int | None = None) -> list[Fraction]:
    if not isinstance(value, list) or (n is not None and len(value) != n):
        raise ValueError("Vector dimension mismatch")
    return [rational(x) for x in value]


def exact_matrix(value: Any, n: int, m: int) -> list[list[Fraction]]:
    if not isinstance(value, list) or len(value) != n:
        raise ValueError("Matrix dimension mismatch")
    return [exact_vector(row, m) for row in value]


def array(value: Any) -> np.ndarray:
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return np.array([[float(rational(x)) for x in row] for row in value], dtype=float)
        return np.array([float(rational(x)) for x in value], dtype=float)
    raise ValueError("Expected list for numeric reference array")


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def required(obj: dict, *names: str) -> Any:
    """Explicit schema aliases only; absent scientific data are errors."""
    for name in names:
        if name in obj:
            return obj[name]
    raise ValueError("Required field absent: " + "/".join(names))


def exact_numbers_equal(left: Any, right: Any) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(exact_numbers_equal(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(exact_numbers_equal(a, b) for a, b in zip(left, right))
    return rational(left) == rational(right)


def frozen_primary_input(config: dict, primary: dict) -> dict:
    identity = config["primary_input_identity"]
    path = (Path(config["_input_directory"])/identity["path_relative_to_this_input"]).resolve()
    if sha256(path) != identity["sha256"]:
        raise ValueError("Frozen primary input SHA256 mismatch")
    fixed = json.loads(path.read_text())
    for collection, required_ids in (("affine_cases", identity["required_affine_ids"]), ("hd_cases", identity["required_HD_ids"])):
        actual = required(primary, collection)
        by_id = {str(x["id"]): x for x in actual}
        if len(by_id) != len(actual) or set(by_id) != set(required_ids):
            raise ValueError(f"Missing/extra/duplicate frozen {collection} IDs")
        for expected in fixed[collection]:
            saved = by_id[expected["id"]]
            if collection == "hd_cases" and len(required(saved, "blocks")) != expected["blocks"]:
                raise ValueError("Frozen HD block count changed")
            saved = saved.get("fixture", saved.get("inputs", saved))
            keys = ("B", "g", "H", "rho", "w0") if collection == "affine_cases" else (
                "K", "pi", "alpha", "kf", "destruction", "coarse_kf_offset", "H", "rho",
                "initial_fine", "initial_coarse", "density_box", "q_norm_upper", "branch_distance_upper", "coarse_scalar_defect_upper")
            for key in keys:
                if not exact_numbers_equal(required(saved, key), expected[key]):
                    raise ValueError(f"Frozen exact input value changed: {collection}/{expected['id']}/{key}")
    return fixed


class Recorder:
    def __init__(self, input_data: dict, result: dict, output_file: Any):
        self.config = input_data
        self.result = result
        self.output_file = output_file
        self.checks: list[dict] = result["checks"]

    def check(self, name: str, condition: Any, **evidence: Any) -> None:
        self.checks.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "evidence": serial(evidence)})

    def upper(self, name: str, reference: Any, upper: Any, *, trajectory: bool = False) -> None:
        ref, bound = np.asarray(reference, dtype=float), np.asarray(upper, dtype=float)
        if ref.shape != bound.shape or not np.all(np.isfinite(ref)) or not np.all(np.isfinite(bound)):
            raise ValueError(f"Nonfinite/shape mismatch in {name}")
        tol = self.config["comparison_tolerances"]
        prefix = "trajectory_bound" if trajectory else "matrix"
        allowance = float(tol[prefix + "_absolute"]) + float(tol[prefix + "_relative"]) * np.abs(ref)
        excess = ref - bound
        self.check(name, np.all(excess <= allowance), max_reference_minus_upper=float(np.max(excess)),
                   max_allowed_excess=float(np.max(allowance)), max_positive_violation_after_allowance=float(np.max(np.maximum(excess-allowance, 0))),
                   max_upper_slack=float(np.max(bound-ref)))

    def close(self, name: str, actual: Any, expected: Any, *, atol: float | None = None) -> None:
        actual, expected = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
        tol = self.config["comparison_tolerances"]
        if actual.shape != expected.shape:
            raise ValueError(f"Shape mismatch in {name}")
        absolute = float(tol["matrix_absolute"] if atol is None else atol)
        allowance = absolute + float(tol["matrix_relative"]) * np.abs(expected)
        error = np.abs(actual-expected)
        self.check(name, np.all(np.isfinite(actual)) and np.all(error <= allowance),
                   max_absolute_error=float(np.max(error)), max_allowed_error=float(np.max(allowance)))

    def flush(self) -> None:
        self.result["check_count"] = len(self.checks)
        self.result["failure_count"] = sum(x["status"] == "FAIL" for x in self.checks)
        self.output_file.seek(0)
        json.dump(serial(self.result), self.output_file, ensure_ascii=False, indent=2, allow_nan=False)
        self.output_file.write("\n")
        self.output_file.truncate()
        self.output_file.flush()
        os.fsync(self.output_file.fileno())


def augmented_reference(B: np.ndarray, g: np.ndarray, duration: float) -> tuple[np.ndarray, np.ndarray]:
    M = np.zeros((3, 3), dtype=float)
    M[:2, :2], M[:2, 2] = B, g
    W = expm(duration*M)
    return W[:2, :2], W[:2, 2]


def block_inputs(case: dict) -> tuple[np.ndarray, np.ndarray, float, float, np.ndarray]:
    data = case.get("certificate", case.get("inputs", case))
    Bq = exact_matrix(required(data, "B"), 2, 2)
    gq = exact_vector(required(data, "g"), 2)
    wq = exact_vector(required(data, "w0"), 2)
    Hq, rhoq = rational(required(data, "H")), rational(required(data, "rho"))
    if not (Bq[0][0] >= 0 and Bq[0][1] >= 0 and Bq[1][0] >= 0):
        raise ValueError("R7 comparison domain requires a,b,c nonnegative")
    if Hq <= 0 or not 0 <= rhoq <= 1 or min(gq+wq) < 0:
        raise ValueError("Invalid H/rho/nonnegative comparison input")
    return np.array(Bq, dtype=float), np.array(gq, dtype=float), float(Hq), float(rhoq), np.array(wq, dtype=float)


def block_output(case: dict) -> dict:
    return case.get("certificate", case.get("result", case.get("output", case)))


def inspect_block(rec: Recorder, case: dict, label: str, *, require_clocks: bool = False) -> dict:
    B, g, H, rho, w0 = block_inputs(case)
    out = block_output(case)
    W, q = augmented_reference(B, g, H)
    T = W.copy()
    T[0, 0] -= 1-rho
    endpoint = T @ w0 + q
    savedW = array(required(out, "W_upper", "exp_BH_upper", "exp_BH_entrywise_upper"))
    savedT = array(required(out, "T", "T_upper", "T_entrywise_upper"))
    savedq = array(required(out, "q", "q_upper", "q_entrywise_upper"))
    saved_endpoint = array(required(out, "w_next_upper"))
    rec.upper(label+": exp(BH) enclosure", W, savedW)
    rec.upper(label+": causal T enclosure", T, savedT)
    rec.upper(label+": forcing integral enclosure", q, savedq)
    rec.upper(label+": endpoint enclosure", endpoint, saved_endpoint)
    rec.check(label+": positive matrices", min(float(np.min(savedT)), float(np.min(savedq)), float(np.min(saved_endpoint))) >= 0)
    causal_saved = savedW.copy()
    causal_saved[0, 0] -= 1-rho
    rec.close(label+": only initial residual receives rho", savedT, causal_saved)
    rec.close(label+": saved endpoint arithmetic", saved_endpoint, savedT @ w0 + savedq)
    interior = case.get("interior", out.get("interior", []))
    if "queries" in case:
        interior = [{"u": required(point, "t"), "w_upper": required(point, "bound")} for point in case["queries"]]
    if require_clocks and len(interior) not in rec.config["solver"]["primary_pointwise_clocks_per_block_allowed"]:
        raise ValueError(f"{label}: expected fixed 5/33/65 primary pointwise clocks")
    point_records = []
    for point in interior:
        u = float(rational(required(point, "u")))
        if not 0 <= u <= H*(1+1e-14):
            raise ValueError("Interior query outside declared block")
        Wu, qu = augmented_reference(B, g, u)
        vu = Wu @ w0 + qu
        pu = point.get("result", point.get("output", point))
        rec.upper(label+f": interior u={u:.16g}", vu, array(required(pu, "w_upper")))
        if "W_upper" in pu:
            rec.upper(label+f": interior matrix u={u:.16g}", Wu, array(pu["W_upper"]))
        if "q" in pu:
            rec.upper(label+f": interior integral u={u:.16g}", qu, array(pu["q"]))
        point_records.append({"u": u, "comparison_reference": vu, "production_upper": array(pu["w_upper"])})
    if require_clocks:
        clocks = [p["u"] for p in point_records]
        rec.close(label+": fixed equally spaced clocks", clocks, np.linspace(0, H, len(clocks)))
    return {"id": label, "B": B, "g": g, "H": H, "rho": rho, "w0": w0,
            "W_reference": W, "T_reference": T, "q_reference": q, "endpoint_reference": endpoint,
            "production_endpoint_upper": saved_endpoint, "points": point_records}


def classify_analytic(B: np.ndarray) -> str:
    if np.count_nonzero(B) == 0:
        return "zero"
    if B[0, 0] == B[1, 0] == B[1, 1] == 0 and B[0, 1] > 0:
        return "nilpotent"
    if B[0, 1] == B[1, 0] == 0 and B[1, 1] < 0:
        return "diagonal_negative_d"
    if B[0, 1] > 0 and B[1, 0] > 0 and B[1, 1] < 0:
        return "coupled_negative_d"
    return "other"


def analytic_controls(rec: Recorder, cases: list[dict]) -> list[dict]:
    seen, records = set(), []
    for i, case in enumerate(cases):
        label = "affine:"+str(case.get("id", case.get("case_id", i)))
        r = inspect_block(rec, case, label)
        B, g, H = r["B"], r["g"], r["H"]
        kind = classify_analytic(B)
        seen.add(kind)
        analyticW = analyticq = None
        if kind == "zero":
            analyticW, analyticq = np.eye(2), H*g
        elif kind == "nilpotent":
            analyticW, analyticq = np.eye(2)+H*B, H*g+(H*H/2)*(B@g)
        elif kind == "diagonal_negative_d":
            diag = np.diag(B)
            analyticW = np.diag(np.exp(H*diag))
            analyticq = np.array([g[j]*(H if diag[j] == 0 else math.expm1(H*diag[j])/diag[j]) for j in range(2)])
        if analyticW is not None:
            rec.close(label+": independent closed-form W", r["W_reference"], analyticW)
            rec.close(label+": independent closed-form integral", r["q_reference"], analyticq)
            r["analytic_W"], r["analytic_q"] = analyticW, analyticq
        r["analytic_class"] = kind
        records.append(r)
    required_controls = set(rec.config["required_matrix_controls"])
    rec.check("All required affine analytic/control classes covered", required_controls <= seen,
              required=sorted(required_controls), observed=sorted(seen))
    return records


def invariant_exact(state: list[Fraction], *, fine: bool) -> tuple[Fraction, Fraction, Fraction]:
    u, v, w = state[:3]
    X = sum(state[3:]) if fine else state[3]
    return 2*u+w+X, v+X, v+w


def hd_input(case: dict, defaults: dict) -> dict:
    f = {**defaults, **case.get("fixture", case.get("inputs", case))}
    piq = exact_vector(required(f, "pi"))
    n = len(piq)
    if n not in (2, 9) or min(piq) <= 0 or sum(piq) != 1:
        raise ValueError("HD fixture requires 2/9 states and exact strictly positive fixed simplex pi")
    alphaq = exact_vector(required(f, "alpha"), n)
    dq = exact_vector(required(f, "destruction", "d"), n)
    Kq = exact_matrix(required(f, "K"), n, n)
    fineq = exact_vector(required(f, "initial_fine", "fine_initial", "z0", "fine0"), n+3)
    coarseq = exact_vector(required(f, "initial_coarse", "coarse_initial", "ybar0", "coarse0"), 4)
    kfq = rational(required(f, "kf"))
    offsetq = rational(required(f, "coarse_kf_offset"))
    defectq = rational(required(f, "coarse_scalar_defect_upper"))
    if sum(alphaq) != 1 or min(alphaq+dq+fineq+coarseq+[kfq, kfq+offsetq, defectq]) < 0:
        raise ValueError("Invalid explicit alpha, destruction, rate or initial state")
    for j in range(n):
        if sum(Kq[i][j] for i in range(n)) != 0:
            raise ValueError("Nominal K must have exact zero column sums")
        if any(Kq[i][j] < 0 for i in range(n) if i != j):
            raise ValueError("Nominal K must be Metzler")
    Ifine, Icoarse = invariant_exact(fineq, fine=True), invariant_exact(coarseq, fine=False)
    if Ifine != Icoarse:
        raise ValueError("Initial H/D/charge invariants differ; scalar eta theorem does not apply")
    box = required(f, "density_box", "box")
    boxq = {key: exact_vector(required(box, key), 2) for key in ("u", "v", "w", "X")}
    if any(lo < 0 or lo > hi for lo, hi in boxq.values()):
        raise ValueError("Invalid whole-block density box")
    q_exact = [sum(Kq[i][j]*piq[j] for j in range(n)) for i in range(n)]
    if sum(abs(x) for x in q_exact) > rational(required(f, "q_norm_upper")):
        raise ValueError("Declared q bound does not cover exact fixed-lift K*pi")
    if sum(abs(alphaq[i]-piq[i]) for i in range(n)) > rational(required(f, "branch_distance_upper")):
        raise ValueError("Declared branch distance does not cover explicit alpha-pi")
    if abs(offsetq)*boxq["u"][1]*boxq["v"][1] > defectq:
        raise ValueError("Declared coarse source defect does not cover the full density box")
    if not isinstance(required(f, "positive_box_evidence"), str) or not f["positive_box_evidence"].strip():
        raise ValueError("Whole-block box proof/provenance is required")
    return {"raw": f, "n": n, "piq": piq, "Kq": Kq, "invariants_exact": Ifine,
            "K": np.array(Kq, dtype=float), "pi": np.array(piq, dtype=float),
            "alpha": np.array(alphaq, dtype=float), "d": np.array(dq, dtype=float),
            "kf": float(kfq), "coarse_kf_offset": float(offsetq), "coarse_scalar_defect_upper": float(defectq),
            "fine0": np.array(fineq, dtype=float), "coarse0": np.array(coarseq, dtype=float),
            "box": {key: np.array(bounds, dtype=float) for key, bounds in boxq.items()}}


def fine_rhs(_: float, z: np.ndarray, K: np.ndarray, alpha: np.ndarray, kf: float, destruction: np.ndarray) -> np.ndarray:
    """Independent direct event propensities, not a residual/bound equation."""
    u, v, w = z[:3]
    hd = z[3:]
    formation = kf*u*v*alpha
    destruction_events = w*destruction*hd
    net = formation-destruction_events
    total = float(np.sum(net))
    return np.concatenate((np.array([-total, -total, total]), K@hd+net))


def coarse_rhs(_: float, y: np.ndarray, kf: float, mean_d: float) -> np.ndarray:
    u, v, w, X = y
    net = kf*u*v-mean_d*w*X
    return np.array([-net, -net, net, net])


def invariant_values(states: np.ndarray, *, fine: bool) -> np.ndarray:
    u, v, w = states[:, 0], states[:, 1], states[:, 2]
    X = np.sum(states[:, 3:], axis=1) if fine else states[:, 3]
    return np.column_stack((2*u+w+X, v+X, v+w))


def nominal_binding(rec: Recorder, f: dict, blocks: list[dict], label: str) -> dict:
    """Bind the reused nominal certificate; never recompute old R6 science."""
    if f["n"] == 2:
        gamma = float(f["Kq"][0][1]+f["Kq"][1][0])
        for j, block in enumerate(blocks):
            _, _, H, rho, _ = block_inputs(block)
            rec.upper(label+f": exact two-state nominal contraction block{j}", np.array([math.exp(-gamma*H)]), np.array([rho]))
        return {"kind": "new mathematical two-state fixture", "zero_sum_decay_gamma": gamma,
                "rho_reference": "exp(-(K01+K10)*H)", "physical_consumer_admitted": False}
    source = rec.config["native_reference_source"]
    path = (Path(rec.config["_input_directory"])/source["path_relative_to_this_input"]).resolve()
    source_sha = sha256(path)
    if source_sha != source["sha256"]:
        raise ValueError("Saved native R6 evidence differs from pinned identity")
    saved = json.loads(path.read_text())
    lo, hi = saved["graph"]["K_lo"], saved["graph"]["K_hi"]
    if any(not rational(lo[i][j]) <= f["Kq"][i][j] <= rational(hi[i][j]) for i in range(9) for j in range(9)):
        raise ValueError("Native fixture K is outside the reused saved interval generator family")
    reuse = required(f["raw"], "reuse")
    if reuse["sha256"] != source_sha or reuse["rho_and_H_reused_without_R6_execution"] is not True:
        raise ValueError("Native reuse provenance does not bind unchanged saved H/rho")
    matched = []
    for block in blocks:
        data = block.get("certificate", block.get("inputs", block))
        H, rho = rational(required(data, "H")), rational(required(data, "rho"))
        identities = [x["id"] for x in saved["graph"]["blocks"] if rational(x["H"]) == H and rational(x["rho_upper"]) == rho]
        if len(identities) != 1:
            raise ValueError("Native H/rho does not bind one exact reused R6 source block")
        if identities[0] != reuse["graph_block_id"]:
            raise ValueError("Native source block ID disagrees with exact H/rho identity")
        matched.append(identities[0])
    rec.check(label+": exact saved native nominal certificate binding", True, source_sha256=source_sha,
              block_ids=matched, K_family="K_lo <= K <= K_hi with exact zero column sums", clock=saved["graph"]["clock"])
    return {"kind": "reused saved native excitation family", "source_path": str(path), "source_sha256": source_sha,
            "block_ids": matched, "inherited_generator_clock": saved["graph"]["clock"],
            "declared_fixture_clock": required(f["raw"], "clock"), "time_unit": required(f["raw"], "time_unit"),
            "R6_scientific_reexecution": False,
            "destruction_and_formation_role": "new declared synthetic fixture; GL2022 consumer unbound"}


def independent_hd(rec: Recorder, case: dict, index: int) -> dict:
    label = "HD:"+str(case.get("id", case.get("case_id", index)))
    f = hd_input(case, rec.config["_primary_metadata_defaults"])
    blocks = required(case, "blocks")
    if len(blocks) not in rec.config["solver"]["blocks_allowed"]:
        raise ValueError("HD fixture must use fixed 3/4 blocks")
    binding = nominal_binding(rec, f, blocks, label)
    inspected = [inspect_block(rec, b, f"{label}:block{j}", require_clocks=True) for j, b in enumerate(blocks)]
    durations = [x["H"] for x in inspected]
    boundaries = np.concatenate(([0.0], np.cumsum(durations)))
    clock_count = int(rec.config["solver"]["saved_ODE_clocks_per_block"])
    if clock_count not in (33, 65):
        raise ValueError("Fixed independent ODE clocks must be 33 or65 per block")
    local_clocks = [np.linspace(0, b["H"], clock_count) for b in inspected]
    times = np.concatenate([boundaries[j]+c if j == 0 else boundaries[j]+c[1:] for j, c in enumerate(local_clocks)])
    settings = rec.config["solver"]
    fine = solve_ivp(lambda t, z: fine_rhs(t, z, f["K"], f["alpha"], f["kf"], f["d"]),
                     (0.0, float(boundaries[-1])), f["fine0"], method=settings["method"],
                     rtol=settings["rtol"], atol=settings["atol"], t_eval=times)
    coarse = solve_ivp(lambda t, y: coarse_rhs(t, y, f["kf"]+f["coarse_kf_offset"], float(f["d"]@f["pi"])),
                       (0.0, float(boundaries[-1])), f["coarse0"], method=settings["method"],
                       rtol=settings["rtol"], atol=settings["atol"], t_eval=times)
    rec.check(label+": independent solvers completed", fine.success and coarse.success,
              fine_status=fine.status, coarse_status=coarse.status, fine_message=fine.message, coarse_message=coarse.message)
    if not fine.success or not coarse.success or fine.y.shape[1] != len(times) or coarse.y.shape[1] != len(times):
        raise ValueError("Independent ODE failed; partial solver result cannot validate complete clocks")
    z, ybar = fine.y.T, coarse.y.T
    X = np.sum(z[:, 3:], axis=1)
    aggregated = np.column_stack((z[:, :3], X))
    r = z[:, 3:]-X[:, None]*f["pi"][None, :]
    eta = X-ybar[:, 3]
    errors = np.column_stack((np.sum(np.abs(r), axis=1), np.abs(eta)))
    defect = f["coarse_kf_offset"]*ybar[:, 0]*ybar[:, 1]
    rec.upper(label+": actual scalar coarse source defect", np.abs(defect),
              np.full(len(times), f["coarse_scalar_defect_upper"]), trajectory=True)
    invariants = np.array(f["invariants_exact"], dtype=float)
    invfine, invcoarse = invariant_values(z, fine=True), invariant_values(ybar, fine=False)
    inv_allowance = float(rec.config["comparison_tolerances"]["conservation_absolute"])
    rec.check(label+": conserved fine H/D/charge", np.max(np.abs(invfine-invariants)) <= inv_allowance,
              max_absolute_drift=float(np.max(np.abs(invfine-invariants))), expected=invariants)
    rec.check(label+": conserved coarse H/D/charge", np.max(np.abs(invcoarse-invariants)) <= inv_allowance,
              max_absolute_drift=float(np.max(np.abs(invcoarse-invariants))), expected=invariants)
    identity_tol = float(rec.config["comparison_tolerances"]["identity_absolute"])
    rec.close(label+": coarse error direction s*eta", aggregated-ybar, eta[:, None]*np.array([-1., -1., 1., 1.]), atol=identity_tol)
    rec.close(label+": coarse l1 observable equals4E", np.sum(np.abs(aggregated-ybar), axis=1), 4*errors[:, 1], atol=identity_tol)
    rec.close(label+": residual has zero HD sum", np.sum(r, axis=1), np.zeros(len(times)), atol=identity_tol)
    fine_derivatives = np.array([fine_rhs(float(t), state, f["K"], f["alpha"], f["kf"], f["d"]) for t, state in zip(times, z)])
    coarse_derivatives = np.array([coarse_rhs(float(t), state, f["kf"]+f["coarse_kf_offset"], float(f["d"]@f["pi"])) for t, state in zip(times, ybar)])
    eta_direct = np.sum(fine_derivatives[:, 3:], axis=1)-coarse_derivatives[:, 3]
    Um = (z[:, 0]+z[:, 1]+ybar[:, 0]+ybar[:, 1])/2
    Wm = (z[:, 2]+X+ybar[:, 2]+ybar[:, 3])/2
    dbar = float(f["d"]@f["pi"])
    eta_identity = -(f["kf"]*Um+dbar*Wm)*eta-z[:, 2]*(r@f["d"])-defect
    rec.close(label+": scalar eta differential identity with source defect", eta_direct, eta_identity, atol=identity_tol)
    r_direct = fine_derivatives[:, 3:]-np.sum(fine_derivatives[:, 3:], axis=1)[:, None]*f["pi"]
    q0 = f["K"]@f["pi"]
    QD = np.diag(f["d"])-np.outer(f["pi"], f["d"])
    vD = f["d"]*f["pi"]-f["pi"]*dbar
    r_identity = r@f["K"].T-z[:, 2, None]*(r@QD.T)+X[:, None]*q0
    r_identity += (f["kf"]*z[:, 0]*z[:, 1])[:, None]*(f["alpha"]-f["pi"])
    r_identity -= (z[:, 2]*X)[:, None]*vD
    rec.close(label+": residual differential identity from direct event RHS", r_direct, r_identity, atol=identity_tol)
    positivity_allowance = float(rec.config["comparison_tolerances"]["positivity_absolute"])
    rec.check(label+": nonnegative fine/coarse samples", min(float(np.min(z)), float(np.min(ybar))) >= -positivity_allowance,
              min_fine=float(np.min(z)), min_coarse=float(np.min(ybar)))
    for j, key in enumerate(("u", "v", "w", "X")):
        values = np.concatenate((aggregated[:, j], ybar[:, j]))
        lo, hi = f["box"][key]
        rec.check(label+f": declared {key} box at saved clocks", np.min(values) >= lo-positivity_allowance and np.max(values) <= hi+positivity_allowance,
                  lower=float(lo), upper=float(hi), observed_min=float(np.min(values)), observed_max=float(np.max(values)),
                  scope="sample corroboration; whole-interval box follows separately declared invariant/loss proof")
    cursor = 0
    block_summaries = []
    for j, (raw, checked) in enumerate(zip(blocks, inspected)):
        count = clock_count
        indices = np.arange(cursor, cursor+count)
        actual = errors[indices]
        point_indices = np.array([round(p["u"]/checked["H"]*(count-1)) for p in checked["points"]], dtype=int)
        rec.close(label+f": block{j} primary clocks align with independent clocks", local_clocks[j][point_indices], [p["u"] for p in checked["points"]])
        saved = np.array([p["production_upper"] for p in checked["points"]])
        rec.upper(label+f": block{j} actual R/E at primary interior clocks", actual[point_indices], saved, trajectory=True)
        dense_comparison = []
        for u in local_clocks[j]:
            Wu, qu = augmented_reference(checked["B"], checked["g"], float(u))
            dense_comparison.append(Wu@checked["w0"]+qu)
        dense_comparison = np.array(dense_comparison)
        rec.upper(label+f": block{j} actual R/E versus independent pointwise comparison at65clocks", actual, dense_comparison, trajectory=True)
        rec.upper(label+f": block{j} actual endpoint R/E", actual[-1], checked["production_endpoint_upper"], trajectory=True)
        rec.upper(label+f": block{j} start error enclosed by w0", actual[0], checked["w0"], trajectory=True)
        out = block_output(raw)
        whole = array(required(out, "whole_block_upper"))
        rec.upper(label+f": block{j} constant whole-block enclosure at65clocks", actual, np.broadcast_to(whole, actual.shape), trajectory=True)
        if j:
            rec.upper(label+f": block{j} propagated certified initial error", inspected[j-1]["production_endpoint_upper"], checked["w0"])
        block_summaries.append({"index": j, "t0": boundaries[j], "H": checked["H"], "rho": checked["rho"],
                                "saved_clock_indices": indices, "actual_endpoint": actual[-1],
                                "production_endpoint_upper": checked["production_endpoint_upper"],
                                "primary_pointwise_clock_indices": point_indices, "production_pointwise_upper": saved,
                                "independent_pointwise_comparison_at_saved_clocks": dense_comparison,
                                "production_whole_block_upper": whole})
        cursor += count-1
    return {"id": label, "states": f["n"], "scope": required(f["raw"], "source_scope", "scope"),
            "physical_consumer_admitted": False, "invariants_exact": f["invariants_exact"],
            "solver": {"method": settings["method"], "rtol": settings["rtol"], "atol": settings["atol"],
                       "fine_nfev": fine.nfev, "coarse_nfev": coarse.nfev},
            "clock": required(f["raw"], "clock"), "times": times, "fine_states": z, "coarse_states": ybar,
            "R_E": errors, "actual_coarse_scalar_defect": defect, "fine_invariants": invfine, "coarse_invariants": invcoarse, "blocks": block_summaries,
            "nominal_certificate": binding}


def late_forcing(rec: Recorder, primary: dict) -> dict:
    control = rec.config["late_forcing_control"]
    gamma, H, epsilon, J = [float(rational(control[k])) for k in ("gamma", "H", "epsilon", "J")]
    if gamma <= 0 or not 0 < epsilon <= H or J <= 0:
        raise ValueError("Invalid fixed late-forcing control")
    rho = math.exp(-gamma*H)
    exact = J*(-math.expm1(-gamma*epsilon))/(gamma*epsilon)
    correct, wrong = J, rho*J
    rec.check("late forcing: causal upper covers exact residual", exact <= correct, exact=exact, causal_upper=correct)
    rec.check("late forcing: rho applied to all forcing is violated", exact > wrong, exact=exact, wrong_upper=wrong, strict_gap=exact-wrong)
    saved = primary.get("late_forcing")
    primary_control = None
    if saved is not None and all(k in saved for k in ("gamma", "H", "epsilon", "J")):
        pgamma, pH, peps, pJ = [float(rational(saved[k])) for k in ("gamma", "H", "epsilon", "J")]
        if pgamma <= 0 or not 0 < peps <= pH or pJ <= 0:
            raise ValueError("Invalid primary late-forcing control")
        pexact = pJ*(-math.expm1(-pgamma*peps))/(pgamma*peps)
        pwrong = math.exp(-pgamma*pH)*pJ
        rec.check("primary late forcing: same causal mechanism independently verified", pwrong < pexact <= pJ,
                  exact=pexact, correct_upper=pJ, wrong_upper=pwrong)
        primary_control = {"gamma": pgamma, "H": pH, "epsilon": peps, "J": pJ,
                           "independent_exact_endpoint_R": pexact, "independent_wrong_upper": pwrong}
    return {"gamma": gamma, "H": H, "epsilon": epsilon, "J": J, "rho": rho, "exact_endpoint_R": exact,
            "correct_forcing_upper": correct, "wrong_forcing_upper": wrong,
            "primary_control_independently_checked": primary_control,
            "counterexample_scope": "Incorrect causal update only; not a physical impossibility theorem"}


def cpu_limit_signal(signum: int, frame: Any) -> None:
    raise RuntimeError("Declared R7 independent-reference CPU limit reached")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("REFERENCE_INPUT.json"))
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--primary-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    started_utc = utc()
    config = json.loads(args.input.read_text())
    config["_input_directory"] = str(args.input.resolve().parent)
    actual_primary_sha = sha256(args.primary)
    if actual_primary_sha != args.primary_sha256:
        raise ValueError("Primary artifact SHA256 differs from frozen command binding")
    if args.output.exists():
        raise FileExistsError("Preserve first reference result: output already exists")
    result = {"schema": "WU_R7_INDEPENDENT_REFERENCE_RESULT_V1", "run_id": "R7_REFERENCE_01", "status": "RUNNING",
              "started_utc": started_utc, "command": sys.argv, "contract_id": config["contract_id"],
              "input_sha256": sha256(args.input), "script_sha256": sha256(Path(__file__)),
              "primary_path": str(args.primary.resolve()), "primary_sha256": actual_primary_sha,
              "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "platform": platform.platform()},
              "budget": {"new_reference_run_number": 1, "CPU_limit_s": config["execution"]["CPU_limit_s"], "old_science_replay": 0,
                         "old_R6_remaining": [0, 0, 0], "old_PHYS91_remaining": [0, 0, 0], "global_remaining": None},
              "checks": [], "affine_cases": [], "hd_cases": [],
              "scientific_role": "Independent binary64 corroboration of the general R7 proof and saved exact-production bounds",
              "physical_consumer_admitted": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        rec = Recorder(config, result, output)
        rec.flush()
        try:
            signal.signal(signal.SIGXCPU, cpu_limit_signal)
            limit = int(config["execution"]["CPU_limit_s"])
            resource.setrlimit(resource.RLIMIT_CPU, (limit, limit+1))
            primary = json.loads(args.primary.read_text())
            fixed = frozen_primary_input(config, primary)
            config["_primary_metadata_defaults"] = fixed["metadata_defaults"]
            result["frozen_primary_input_sha256"] = config["primary_input_identity"]["sha256"]
            affine = required(primary, "affine_cases", "matrix_controls")
            hd = required(primary, "hd_cases", "hd_fixtures")
            result["affine_cases"] = analytic_controls(rec, affine)
            rec.flush()
            sizes = []
            for i, case in enumerate(hd):
                result["hd_cases"].append(independent_hd(rec, case, i))
                sizes.append(result["hd_cases"][-1]["states"])
                rec.flush()
            rec.check("Required new two-state HD fixture covered", 2 in sizes, observed_state_counts=sizes)
            rec.check("At most one native nine-state HD fixture", sizes.count(9) <= 1, observed_state_counts=sizes)
            result["late_forcing"] = late_forcing(rec, primary)
            result["status"] = "PASS" if all(c["status"] == "PASS" for c in rec.checks) else "FAIL"
        except BaseException as exc:
            result["status"] = "FAIL"
            result["first_exception"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        finally:
            total_process_cpu = time.process_time()
            elapsed_cpu = total_process_cpu-start_cpu
            elapsed_wall = time.perf_counter()-start_wall
            result["finished_utc"] = utc()
            result["actual_process_CPU_s"] = total_process_cpu
            result["main_entry_CPU_s"] = elapsed_cpu
            result["CPU_includes_Python_and_library_imports"] = True
            result["actual_wall_s"] = elapsed_wall
            result["CPU_allowance_satisfied"] = total_process_cpu <= float(config["execution"]["CPU_limit_s"])
            if not result["CPU_allowance_satisfied"]:
                result["status"] = "FAIL"
            rec.flush()
    print(json.dumps({"status": result["status"], "output": str(args.output), "checks": result["check_count"],
                      "failures": result["failure_count"], "CPU_s": result["actual_process_CPU_s"], "wall_s": result["actual_wall_s"]}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
