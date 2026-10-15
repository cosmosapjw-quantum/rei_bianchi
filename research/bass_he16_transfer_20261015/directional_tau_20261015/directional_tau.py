"""Direction-dependent redshift/Thomson-depth from stored normal-frame LRS Bianchi I histories.

Physical interpretation: a hypothetical normal observer at the *last shared prefix*
mean scale a_o=0.088736547..., NOT a z=0 CMB observer. The quantity z_rel is
photon energy redshift between an earlier event and this observer along the same
geodesic. No native ODE, anisotropic Thomson collision, or polarization claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

# Run directly as a script without requiring a package installation.
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))

# Earlier same research track; these functions validate original provenance caches.
from clock_decompose_signed import CASE_ORDER, EXPECTED_SOURCE_SHA, read_caches, path_for
from signed_prefix_tau import EXPECTED_Q, digest, PREC

KAPPA = PREC("6.6524587321e-29") * PREC("299792458") * PREC("1000000")
TARGET_ZREL = (0.20, 0.50, 0.75)
ANGULAR_N = (16, 32, 64, 128)
ROOT_ITERATIONS = 58


def source_b_history(path: Path, reference_a: np.ndarray) -> np.ndarray:
    """Read b, validate scale node parity. Separate SHA of original source is required."""
    out = np.empty(reference_a.size, dtype=np.float64)
    with path.open("r", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        for label in ("case_id", "q_ref", "a", "b"):
            if label not in header:
                raise ValueError(f"Missing physical source column {label}")
        ia, ib = header.index("a"), header.index("b")
        iq, ic = header.index("q_ref"), header.index("case_id")
        previous = None
        case = None
        for i, row in enumerate(reader):
            if not row:
                continue
            if i >= reference_a.size:
                raise ValueError("Source geometry has too many rows")
            if case is None:
                case = row[ic]
                if case not in EXPECTED_Q:
                    raise ValueError("Unknown q/case")
            if row[ic] != case or float(row[iq]) != EXPECTED_Q[case]:
                raise ValueError("Source case changed within geometry history")
            a = float(row[ia])
            if a != reference_a[i]:
                raise ValueError(f"Source scale-factor node parity mismatch at row {i}")
            b = float(row[ib])
            if not math.isfinite(b):
                raise ValueError(f"Nonfinite geometry at row {i}")
            out[i] = b
            previous = i
        if previous != reference_a.size - 1:
            raise ValueError("Source geometry incomplete")
    return out


def build_geometry(root: Path, baseline_cache: Path, geo_dir: Path) -> dict:
    """SHA-bound derived b arrays. Only parent-owned new files are written."""
    data, parent, _ = read_caches(baseline_cache)
    geo_dir.mkdir(parents=True, exist_ok=True)
    receipts = {}
    for case in CASE_ORDER:
        original = path_for(root, case)
        history = original / "history.csv"
        source_file = original / "source_identity.txt"
        h = digest(history)
        origin = parent["cases"][case]
        if h != origin["history_sha256"] or digest(source_file) != EXPECTED_SOURCE_SHA:
            raise ValueError(f"Original source provenance failed: {case}")
        b = source_b_history(history, data[case]["a"])
        output = geo_dir / (case + "_b.npz")
        np.savez_compressed(output, b=b,
                            history_sha256=np.array(h),
                            source_identity_sha256=np.array(EXPECTED_SOURCE_SHA))
        receipts[case] = {
            "history_sha256": h,
            "source_sha256": EXPECTED_SOURCE_SHA,
            "cache_file": output.name,
            "cache_sha256": digest(output),
            "rows": int(b.size),
            "b_min": float(np.min(b)), "b_max": float(np.max(b)),
        }
    record = {
        "schema": "he18.axbi.directional_geometry_cache.v1",
        "authority": "Original AXBI 200001-row cold source history CSVs",
        "physics": "b at each accepted mean-a step; normal-comoving LRS Bianchi I",
        "cases": receipts,
        "parent_cache_manifest_sha256": digest(baseline_cache / "MANIFEST.json"),
    }
    (geo_dir / "MANIFEST.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def read_geometry(geo_dir: Path, baseline_cache: Path, parent: dict) -> dict:
    manifest = json.loads((geo_dir / "MANIFEST.json").read_text())
    if digest(baseline_cache / "MANIFEST.json") != manifest["parent_cache_manifest_sha256"]:
        raise ValueError("Parent numerical cache identity changed")
    output = {}
    for case in CASE_ORDER:
        rec = manifest["cases"][case]
        if rec["history_sha256"] != parent["cases"][case]["history_sha256"]:
            raise ValueError(f"Source history mismatch for {case}")
        f = geo_dir / rec["cache_file"]
        if digest(f) != rec["cache_sha256"]:
            raise ValueError(f"Geometry derived cache mismatch for {case}")
        with np.load(f, allow_pickle=False) as z:
            if z["history_sha256"].item() != rec["history_sha256"] or \
               z["source_identity_sha256"].item() != EXPECTED_SOURCE_SHA:
                raise ValueError(f"Geometry source IDs mismatch for {case}")
            b = z["b"].copy()
        if b.size != rec["rows"]:
            raise ValueError("Wrong geometry history shape")
        output[case] = b
    return output


def _interpolate(x: np.ndarray, grid: np.ndarray, values: np.ndarray):
    """Vectorized indexed linear interpolation on a strictly increasing grid."""
    idx = np.searchsorted(grid, x, side="right") - 1
    idx = np.maximum(0, np.minimum(idx, len(grid) - 2))
    frac = (x - grid[idx]) / (grid[idx + 1] - grid[idx])
    return values[idx] + frac * (values[idx + 1] - values[idx]), idx, frac


def _log_z_relative(u, mu, loga, b):
    """Log(1+directional redshift) from emission loga=u to observer at last row.

    mu is the local direction cosine at observer. Original metric:
    a_perp=a*exp(-b), a_parallel=a*exp(2b).
    """
    b_u, _, _ = _interpolate(u, loga, b)
    db = b_u - b[-1]
    mu2 = mu * mu
    norm = (1 - mu2) * np.exp(2 * db) + mu2 * np.exp(-4 * db)
    return loga[-1] - u + .5 * np.log(norm)


def solve_directional_redshift(loga: np.ndarray, b: np.ndarray,
                               mu: np.ndarray, redshift: float,
                               niter: int = ROOT_ITERATIONS):
    """Batched monotone-bracketed root solver using only O(N_mu) temporaries."""
    loga = np.asarray(loga, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    mu = np.asarray(mu, dtype=np.float64)
    if loga.ndim != 1 or b.shape != loga.shape or mu.ndim != 1:
        raise ValueError("Input shape")
    if loga.size < 2 or np.any(~np.isfinite(loga)) or np.any(~np.isfinite(b)) \
       or np.any(np.diff(loga) <= 0) or np.any(~np.isfinite(mu)) or np.any(np.abs(mu) > 1):
        raise ValueError("Invalid expansion/anisotropy/direction")
    if not math.isfinite(redshift) or redshift < 0:
        raise ValueError("Invalid relative redshift")
    if niter < 10:
        raise ValueError("Insufficient bracketing iterations")
    slopes = np.diff(b) / np.diff(loga)
    max_slope = float(np.max(np.abs(slopes)))
    if 2 * max_slope >= 1:
        raise ValueError("Directional redshift monotonicity gate failed")
    target = math.log1p(redshift)
    lo = np.full(mu.shape, loga[0])
    hi = np.full(mu.shape, loga[-1])
    lowval = _log_z_relative(lo, mu, loga, b)
    highval = _log_z_relative(hi, mu, loga, b)
    if np.any(lowval < target - 1e-13) or np.any(highval > target + 1e-13):
        raise ValueError("Requested relative redshift outside history")
    for _ in range(niter):
        mid = 0.5 * lo + 0.5 * hi
        f = _log_z_relative(mid, mu, loga, b) - target
        lo = np.where(f > 0, mid, lo)
        hi = np.where(f <= 0, mid, hi)
    u = 0.5 * lo + 0.5 * hi
    residual = np.max(np.abs(_log_z_relative(u, mu, loga, b) - target))
    return u, {"iterations": niter, "max_abs_log_redshift_residual": float(residual),
               "max_abs_db_dln_a": max_slope,
               "strict_directional_monotonicity_interpolant": True}


def tau_between_source_and_observer(source: dict, b: np.ndarray,
                                     z_rel: float, mu: np.ndarray,
                                     niter: int = ROOT_ITERATIONS) -> tuple[np.ndarray, dict]:
    """Compute sampled-column tau(t_emit(mu,z_rel)->t_o) in dimensionless units."""
    a = source["a"]
    t = source["t_s"]
    ne = source["ne_cm3"]
    tau = source["tau"]
    if len(a) != len(b) or len(a) != len(t) or len(a) != len(ne) or len(a) != len(tau):
        raise ValueError("History shape mismatch")
    loga = np.log(a)
    u, info = solve_directional_redshift(loga, b, mu, z_rel, niter=niter)
    _, idx, frac = _interpolate(u, loga, b)
    emit_t = t[idx].astype(PREC) + frac.astype(PREC) * \
        (t[idx + 1].astype(PREC) - t[idx].astype(PREC))
    ne_emit = ne[idx].astype(PREC) + frac.astype(PREC) * \
        (ne[idx + 1].astype(PREC) - ne[idx].astype(PREC))
    delta_t = emit_t - t[idx].astype(PREC)
    tau_emit = tau[idx].astype(PREC) + KAPPA * delta_t * \
        (ne[idx].astype(PREC) + ne_emit) / 2
    column = tau[-1].astype(PREC) - tau_emit
    if np.any(column < -PREC("1e-16")):
        raise ValueError("Negative direction-integrated optical depth")
    if np.any(column > tau[-1] + PREC("1e-16")):
        raise ValueError("Direction-integrated tau exceeds entire history")
    info.update({
        "emission_mean_a_min": float(np.min(np.exp(u))),
        "emission_mean_a_max": float(np.max(np.exp(u))),
        "emission_proper_s_min": float(np.min(emit_t)),
        "emission_proper_s_max": float(np.max(emit_t)),
    })
    return np.maximum(column, PREC(0)), info


def directional_moments(source: dict, b: np.ndarray,
                        z_targets=TARGET_ZREL, angular_orders=ANGULAR_N):
    from numpy.polynomial.legendre import leggauss
    results = []
    for z in z_targets:
        convergence = []
        for n in angular_orders:
            mu, weights = leggauss(n)
            tau, info = tau_between_source_and_observer(source, b, z, mu)
            p2 = (3 * mu * mu - 1) / 2
            mono = np.dot(weights.astype(PREC), tau) / 2
            quadrupole = (PREC(5) / 2) * np.dot(weights.astype(PREC),
                                                 tau * p2.astype(PREC))
            convergence.append({
                "angular_nodes": n,
                "tau_sky_monopole": format(mono, ".20g"),
                "tau_legendre_a2": format(quadrupole, ".20g"),
                "max_abs_log_z_residual": info["max_abs_log_redshift_residual"],
            })
        mu_control = np.array([0, 1 / math.sqrt(3), 1], dtype=np.float64)
        tau_control, info = tau_between_source_and_observer(source, b, z, mu_control)
        results.append({
            "z_rel": z,
            "angular_convergence": convergence,
            "selected": convergence[-1],
            "mu_at_observer": [float(x) for x in mu_control],
            "tau_for_mu_0_magic_1": [format(v, ".20g") for v in tau_control],
            "monotonicity": info,
        })
    return results


def make_campaign(base_cache: Path, geometry_cache: Path, targets=TARGET_ZREL,
                  orders=ANGULAR_N, output: Path | None = None):
    data, parent, secs = read_caches(base_cache)
    geom = read_geometry(geometry_cache, base_cache, parent)
    case_results = {}
    times = {}
    for case in CASE_ORDER:
        start = perf_counter()
        moments = directional_moments(data[case], geom[case], targets, orders)
        times[case] = perf_counter() - start
        case_results[case] = {
            "case": case, "q_ref": EXPECTED_Q[case],
            "history_sha256": parent["cases"][case]["history_sha256"],
            "angular": moments,
        }
    differences = []
    for j, z in enumerate(targets):
        def v(case, name):
            return PREC(case_results[case]["angular"][j]["selected"][name])
        z0_mono = v("ZERO", "tau_sky_monopole")
        mono_h05_even = (v("SHEAR_HALF_PLUS", "tau_sky_monopole") +
                         v("SHEAR_HALF_MINUS", "tau_sky_monopole")) / 2 - z0_mono
        mono_h10_even = (v("SHEAR_PLUS", "tau_sky_monopole") +
                         v("SHEAR_MINUS", "tau_sky_monopole")) / 2 - z0_mono
        quad_h05_odd = (v("SHEAR_HALF_PLUS", "tau_legendre_a2") -
                        v("SHEAR_HALF_MINUS", "tau_legendre_a2")) / 2
        quad_h10_odd = (v("SHEAR_PLUS", "tau_legendre_a2") -
                        v("SHEAR_MINUS", "tau_legendre_a2")) / 2
        dif = {
            "z_rel": z,
            "zero_tau_monopole": format(z0_mono, ".20g"),
            "even_tau_monopole_q005": format(mono_h05_even, ".20g"),
            "even_tau_monopole_q010": format(mono_h10_even, ".20g"),
            "even_ratio_q010_q005": format(mono_h10_even / mono_h05_even, ".16g"),
            "odd_tau_a2_q005": format(quad_h05_odd, ".20g"),
            "odd_tau_a2_q010": format(quad_h10_odd, ".20g"),
            "odd_quadrupole_ratio_q010_q005": format(quad_h10_odd / quad_h05_odd, ".16g"),
        }
        differences.append(dif)
    result = {
        "schema": "he18.axbi.directional_tau.v1",
        "status": "SOURCE_SCOPED_NUMERICALLY_CHECKED_NOT_ODE_CERTIFIED",
        "geometry_convention": "ds2=-c2dt2+a2exp(-2b)(dx2+dy2)+a2exp(4b)dz2",
        "observer": "normal comoving observer at end of common signed prefix",
        "observer_mean_a": float(data["ZERO"]["a"][-1]),
        "observer_mean_zbar": float(1 / data["ZERO"]["a"][-1] - 1),
        "relative_directional_redshift_targets": list(targets),
        "redshift_formula": "(a_o/a)*sqrt((1-mu_o^2)exp(2(b-b_o))+mu_o^2 exp(-4(b-b_o)))",
        "opacity": "sigma_T*c*n_e(proper), with cm^-3 to m^-3 factor=1e6",
        "case_data": case_results,
        "signed_summary": differences,
        "benchmark_seconds": times,
        "parent_cache_sha256": digest(base_cache / "MANIFEST.json"),
        "geometry_cache_sha256": digest(geometry_cache / "MANIFEST.json"),
        "important_limitations": [
            "z_rel is between high-z emission and observer at zbar~10.269, not CMB observer at z=0",
            "quadrupole is Legendre optical-depth anisotropy at fixed redshift, not photon J2 or CMB polarization",
            "piecewise log(a) interpolation of b and proper-time source tau; no native ODE/global interpolation enclosure",
            "pure geometry and source ionization dependence are not separately causally identified",
            "directional redshift monotonicity gate concerns piecewise log(a) surrogate only",
        ],
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source-root", type=Path)
    p.add_argument("--base-cache", type=Path, required=True)
    p.add_argument("--geometry-cache", type=Path, required=True)
    p.add_argument("--build-geometry", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.build_geometry:
        if args.source_root is None:
            p.error("--source-root required when --build-geometry")
        build_geometry(args.source_root, args.base_cache, args.geometry_cache)
    res = make_campaign(args.base_cache, args.geometry_cache, output=args.out)
    print(json.dumps({"status": res["status"], "observer_a": res["observer_mean_a"],
                      "signed_summary": res["signed_summary"],
                      "case_seconds": res["benchmark_seconds"]}, indent=2))
