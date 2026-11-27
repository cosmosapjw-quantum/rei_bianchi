"""Bounded HE27 source admission controls, independent of native evolution.

Compare the immutable HE25 fixed-grid source and HE26 positive cut donor with
physical birth-frame QUAD.  In QUAD only, sigma is scaled by 1e18 before
integration to prevent absolute-tolerance false agreement near 1e-18 cm2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import quad

PACKAGE = Path(__file__).resolve().parents[1]
RESEARCH = PACKAGE.parent
sys.path[:0] = [str(PACKAGE / "src"),
                str(RESEARCH / "he26_moving_cutoff_20261016" / "src"),
                str(RESEARCH / "he23_density_contract_20261016" / "src"),
                str(RESEARCH / "he25_proper_birth_20261016" / "analysis"),
                str(RESEARCH / "he25_proper_birth_20261016" / "src")]
from portable_cut_core import angular_cuts, children_of_cell, geometry
from he21_photo import BIND_EV, FIT_CUTS, X_END, shape, sigma_cm2
from source_moment_control import grid_only
from sourcecut import SourceCutModel

EXPECTED_DONOR_SHA = "ebb50445d968202c61cbb6dab5f02977c20b439592e2693a58cc716dea380c49"
EXPECTED_SOURCE_SHA = "3df86063f12e238ec41219343a016b3a5086d18ce973015c335ec8118d9a5b66"
EXPECTED_PHYSICS_SHA = "6df06662108635b525eea75b1ce2cdbcd91afe64a21ed0076977088c2fe5d63c"
SOURCE_MIN, SOURCE_MAX = 13.6, 100.0


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_pinned_sources():
    paths = {
        "he26_donor": RESEARCH / "he26_moving_cutoff_20261016" / "src" / "portable_cut_core.py",
        "he21_source": RESEARCH / "he23_density_contract_20261016" / "src" / "he21_photo.py",
        "he25_physics": RESEARCH / "he25_proper_birth_20261016" / "src" / "physics.py",
    }
    actual = {name: sha256(path) for name, path in paths.items()}
    expected = {"he26_donor": EXPECTED_DONOR_SHA,
                "he21_source": EXPECTED_SOURCE_SHA,
                "he25_physics": EXPECTED_PHYSICS_SHA}
    if actual != expected:
        raise RuntimeError(f"SOURCE_IDENTITY_MISMATCH actual={actual}")
    return actual


def birth_frame_reference():
    """Physical E quadrature, with every Verner kernel in 1e-18 cm2 units."""
    points = [SOURCE_MIN, *map(float, FIT_CUTS[1:]), SOURCE_MAX]

    def integrate(fn):
        return sum(quad(fn, left, right, epsabs=1e-11, epsrel=2e-13)[0]
                   for left, right in zip(points[:-1], points[1:]))

    raw_n = integrate(lambda e: float(shape(e)))
    raw_u = integrate(lambda e: float(shape(e)) * e)
    photo = []
    heat = []
    for species in range(3):
        def scaled_sigma(e):
            return float(sigma_cm2(e)[species]) * 1e18
        photo.append(integrate(lambda e: float(shape(e)) * scaled_sigma(e)) * 1e-18)
        heat.append(integrate(lambda e: float(shape(e)) * scaled_sigma(e)
                              * (e - BIND_EV[species])) * 1e-18)
    return {"raw_n": raw_n, "raw_u_ev": raw_u, "mean_ev": raw_u / raw_n,
            "photo_cm2": photo, "heat_ev_cm2": heat,
            "photo_mean_cm2": (np.array(photo) / raw_n).tolist(),
            "heat_mean_ev_cm2": (np.array(heat) / raw_n).tolist(),
            "quad_sigma_scale": 1e18}


def he25_panels(m, angles, q):
    """Transcribe only the immutable HE25 panel boundaries; no solver calls."""
    mus, mw = np.polynomial.legendre.leggauss(angles)
    for mu, weight in zip(mus, mw / 2):
        g, _ = geometry(X_END, q, float(mu))
        boundaries = sorted(set([13.6, 24.59, 54.42, 100.,
                                 13.6/g, 24.59/g, 54.42/g, 100./g]))
        for lo, hi in zip(boundaries[:-1], boundaries[1:]):
            parts = m if hi/lo > 1.01 else 1
            edges = np.geomspace(lo, hi, parts+1)
            for left, right in zip(edges[:-1], edges[1:]):
                yield float(mu), float(weight), float(left), float(right)


def he25_raw_moments(m, angles, q, x):
    model, _ = grid_only(m, q, angles)
    g = model.factor(x, model.mu0)
    e = model.Eref * g
    raw = model.weights * shape(e) * np.exp(-3*x)/g**2 * ((e >= 13.6) & (e <= 100.))
    sig = sigma_cm2(e)
    return {"raw_n": float(raw.sum()), "raw_u_ev": float(np.dot(raw, e)),
            "photo_cm2": np.sum(raw[:, None]*sig, axis=0).tolist(),
            "heat_ev_cm2": np.sum(raw[:, None]*sig*(e[:, None]-BIND_EV), axis=0).tolist(),
            "photon_modes": int(model.Eref.size)}


def donor_moments(m, angles, q, x, order=8):
    children = []
    parents = list(he25_panels(m, angles, q))
    for mu, weight, lo, hi in parents:
        children.extend(children_of_cell(lo, hi, x, q, mu, weight,
                       SOURCE_MIN, SOURCE_MAX, FIT_CUTS, BIND_EV,
                       shape, sigma_cm2, order=order))
    n = sum(child["n"] for child in children)
    u = sum(child["u_ev"] for child in children)
    photo = np.sum([child["photo_cm2"] for child in children], axis=0)
    heat = np.sum([child["heat_ev_cm2"] for child in children], axis=0)
    if not children or n <= 0 or not np.all(photo >= 0) or not np.all(heat >= 0):
        raise ArithmeticError("DONOR_NONPOSITIVE_MOMENTS")
    for child in children:
        if any(child["low_ev"] < c-4e-12 and child["high_ev"] > c+4e-12
               for c in (*FIT_CUTS, SOURCE_MAX)):
            raise ArithmeticError("DONOR_CHILD_STRADDLES_CUTOFF")
    return {"raw_n": n, "raw_u_ev": u, "mean_ev": u/n,
            "photo_cm2": photo.tolist(), "heat_ev_cm2": heat.tolist(),
            "children": len(children), "parents": len(parents),
            "all_positive": True, "no_cut_straddle": True}


def shell_cut_control(q, threshold, order=32, cut_order=8):
    """Manufactured delta-shell angular acceptance, not an EoR observable."""
    x = X_END
    target = .47
    g, _ = geometry(x, q, target)
    eref = threshold/g
    edges = angular_cuts(x, q, eref, [threshold])
    # The manufactured shell divides two nearly equal O(1) geometry terms;
    # its recovered angular root loses a few 1e-11 in binary64 cancellation.
    if len(edges) != 4 or abs(edges[1]+target) > 2e-10 or abs(edges[2]-target) > 2e-10:
        raise ArithmeticError("SHELL_CUT_PREIMAGE")

    def active(mu):
        gg, _ = geometry(x, q, mu)
        return float(eref*gg >= threshold)

    z, w = np.polynomial.legendre.leggauss(order)
    global_gl = float(np.dot(w, [active(float(mu)) for mu in z])/2)
    zc, wc = np.polynomial.legendre.leggauss(cut_order)
    split = sum(float(np.dot(wc, [active(float((left+right)/2+
                                      (right-left)*zz/2)) for zz in zc])
                      * (right-left)/4)
                for left, right in zip(edges[:-1], edges[1:]))
    # Compare the two quadratures to the analytic measure of the *computed*
    # preimage.  Comparing to the intended .47 target instead mixes in
    # cancellation error from solving the near-isotropic cutoff equation.
    root = edges[2]
    exact = 1-root if q > 0 else root
    return {"q": q, "fit_cut_ev": threshold, "preimages": list(edges),
            "exact": exact, "global_gl32": global_gl, "cut_gl8": split,
            "global_error": global_gl-exact, "cut_error": split-exact}


def evaluate():
    identities = check_pinned_sources()
    ref = birth_frame_reference()
    x = .37*X_END
    old = he25_raw_moments(4, 4, .005, x)
    new = donor_moments(4, 4, .005, x)
    shells = [shell_cut_control(q, float(c)) for q in (-.005, .005)
              for c in FIT_CUTS]
    integrated = []
    for q in (-.005, 0., .005):
        model = SourceCutModel(None, m=4, angles=4, q=q)
        t = .37*model.t_end
        source = model.source(t)
        report = model.last_source_moments
        donor = np.array(report["donor_raw"])
        admitted = np.array(report["admitted_raw"])
        integrated.append({"q": q, "m": 4, "angles": 4, "x": model.x(t),
                           "photon_modes": model.K,
                           "source_count_dt_per_H_s": float(source.sum()),
                           "expected_H_dN_dlnA": model.H(t)*model.source_per_x,
                           "min_source_dt_per_H_s": float(source.min()),
                           "donor_raw": donor.tolist(),
                           "admitted_raw": admitted.tolist(),
                           "max_relative_moment_defect": float(np.max(
                               np.abs(admitted-donor)/np.maximum(np.abs(donor), 1e-30))),
                           "threshold_bands": len(report["bands"])})
    identities["he27_opt_in_source"] = sha256(PACKAGE / "src" / "sourcecut.py")
    identities["he27_acceptance_analysis"] = sha256(__file__)
    return {"schema": "bass_he.he27.source_acceptance.v1",
            "scope": "source-only acceptance; no native evolution or EoR inference",
            "identities_sha256": identities,
            "physical_birth_quad": ref,
            "sample": {"q": .005, "m": 4, "angles": 4, "x_fraction": .37,
                       "he25_immutable": old, "he26_cut_donor": new},
            "opt_in_native_compatible_admission": integrated,
            "manufactured_shells": shells,
            "acceptance": {
                "old_raw_n_relative_error": old["raw_n"]/ref["raw_n"]-1,
                "cut_raw_n_relative_error": new["raw_n"]/ref["raw_n"]-1,
                "cut_mean_ev_error": new["mean_ev"]-ref["mean_ev"],
                "max_cut_photo_relative_error": max(abs(np.array(new["photo_cm2"])/
                                                       np.array(ref["photo_cm2"])-1)),
                "max_cut_heat_relative_error": max(abs(np.array(new["heat_ev_cm2"])/
                                                      np.array(ref["heat_ev_cm2"])-1)),
                "max_global_shell_error": max(abs(s["global_error"]) for s in shells),
                "max_cut_shell_error": max(abs(s["cut_error"]) for s in shells),
            }}


def bounded_campaign():
    """Finite 108-case source gate; returns the first failed case verbatim."""
    identity = check_pinned_sources()
    identity["he27_opt_in_source"] = sha256(PACKAGE / "src" / "sourcecut.py")
    identity["he27_acceptance_analysis"] = sha256(__file__)
    reference = birth_frame_reference()
    target = np.array([reference["raw_n"], reference["raw_u_ev"],
                       *reference["photo_cm2"], *reference["heat_ev_cm2"]])
    cases = []
    first_failure = None
    started = time.monotonic()
    for q in (-.005, 0., .005):
        if first_failure: break
        for m in (4, 8, 16):
            if first_failure: break
            for angles in (4, 8):
                if first_failure: break
                model = SourceCutModel(None, m=m, angles=angles, q=q)
                for fraction in (0., .1, .37, .5, .9, 1.):
                    record = {"q": q, "m": m, "angles": angles,
                              "proper_time_fraction": fraction,
                              "photon_modes": model.K}
                    try:
                        t = fraction*model.t_end
                        source = model.source(t)
                        moment = model.last_source_moments
                        donor = np.array(moment["donor_raw"])
                        admitted = np.array(moment["admitted_raw"])
                        record.update({"x": model.x(t),
                            "donor_raw": donor.tolist(),
                            "admitted_raw": admitted.tolist(),
                            "min_source_per_H_s": float(source.min()),
                            "source_number_per_H_s": float(source.sum()),
                            "source_expected_per_H_s": model.H(t)*model.source_per_x,
                            "raw_n_relative_error": float(donor[0]/target[0]-1),
                            "mean_energy_error_ev": float(donor[1]/donor[0]-reference["mean_ev"]),
                            "max_photo_relative_error": float(np.max(np.abs(donor[2:5]/target[2:5]-1))),
                            "max_heat_relative_error": float(np.max(np.abs(donor[5:]/target[5:]-1))),
                            "max_admission_relative_defect": float(np.max(
                                np.abs(admitted-donor)/np.maximum(np.abs(donor), 1e-30)))})
                        valid = (np.all(source >= 0) and
                                 abs(record["raw_n_relative_error"]) < 1e-13 and
                                 abs(record["mean_energy_error_ev"]) < 1e-11 and
                                 record["max_photo_relative_error"] < 2e-12 and
                                 record["max_heat_relative_error"] < 2e-12 and
                                 record["max_admission_relative_defect"] < 3e-13 and
                                 abs(record["source_number_per_H_s"]/
                                     record["source_expected_per_H_s"]-1) < 2e-15)
                        record["status"] = "PASS" if valid else "FAIL"
                    except Exception as exc:
                        record["status"] = "ERROR"
                        record["exception_type"] = type(exc).__name__
                        record["exception"] = str(exc)
                    cases.append(record)
                    if record["status"] != "PASS":
                        first_failure = record
                        break
                    if time.monotonic()-started > 60.:
                        first_failure = {"status": "TIME_CAP_60S", "last_case": record}
                        break
    return {"schema": "bass_he.he27.source_campaign.v1",
            "scope": "source admission only, no original Rust evolution",
            "identities_sha256": identity,
            "physical_birth_quad": reference,
            "expected_cases": 108,
            "executed_cases": len(cases),
            "passed_cases": sum(c["status"] == "PASS" for c in cases),
            "elapsed_s": time.monotonic()-started,
            "status": "PASS" if first_failure is None and len(cases) == 108 else "FAIL",
            "first_failure": first_failure,
            "cases": cases}


def atomic_create(path, result):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("x") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.link(temporary, path)
    temporary.unlink()
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--campaign", action="store_true")
    args = parser.parse_args()
    result = bounded_campaign() if args.campaign else evaluate()
    atomic_create(args.out, result)
    summary = ({k: result[k] for k in ("status", "executed_cases", "passed_cases", "elapsed_s")}
               if args.campaign else result["acceptance"])
    print(json.dumps({"out": str(args.out.resolve()), **summary}))
    if args.campaign and result["status"] != "PASS":
        raise SystemExit(1)
