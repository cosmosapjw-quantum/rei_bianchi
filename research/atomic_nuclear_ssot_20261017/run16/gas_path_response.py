#!/usr/bin/env python3
"""RUN16: fixed-support survivor sensitivity to explicitly prescribed gas paths.

Only lightweight quadrature is performed. No native IVP is advanced. The
immutable RUN15 optical kernel and the original RUN13 source/inputs are read
with SHA guards. All path comparisons use ONE baseline core support, ONE
source measure and ONE common partition. Perturbed paths are diagnostics,
not reconstructed solutions of the coupled gas equations.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(key, "1")
sys.dont_write_bytecode = True

import numpy as np
import scipy
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

KERNEL_SHA = "f95c99ce30c886f9bff26744b00d6617b3a0f39661fec97c4cec1fb285f9d968"
COMPARE_SHA = "21d2f6ecdda9464467d57e2f97cd7946d3491471883913d6d2f89ff450ed3e76"
ARCHIVED_RESULT_SHA = "dccee4f8c3ab421c0abe280e4a138bbf1c767e3212e89cf4e76738bbf17b1079"
BASE_HEAD = "c875005e30d9de1ce7f426898e46fe912068412c"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_checked(path, expected, name):
    path = Path(path).resolve()
    if sha(path) != expected:
        raise ValueError("immutable dependency mismatch: " + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exp_remainder(x):
    """exp(-x)-1+x, without cancellation of the O(x) terms near zero."""
    x = np.asarray(x, dtype=float)
    if not np.isfinite(x).all() or np.any(x < -700):
        raise ValueError("finite exponential argument >= -700 required")
    out = np.empty_like(x)
    small = np.abs(x) < 0.01
    # Terms through x^10; the next relative contribution is < 6e-26 here.
    coeff = np.array([(-1.0)**k/math.factorial(k) for k in range(2, 11)])
    out[small] = x[small]**2*np.polynomial.polynomial.polyval(x[small], coeff)
    out[~small] = np.expm1(-x[~small])+x[~small]
    return out


def bump(z, knots):
    """C1, 0<=b<=1, b=b'=0 at every supplied knot, maximum one per panel."""
    z = np.asarray(z, dtype=float)
    knots = np.asarray(knots, dtype=float)
    if (knots.ndim != 1 or len(knots) < 2 or not np.all(np.diff(knots) > 0)
            or not np.isfinite(z).all() or np.any(z < knots[0]) or np.any(z > knots[-1])):
        raise ValueError("ordered knots and in-domain finite arguments required")
    j = np.clip(np.searchsorted(knots, z, side="right")-1, 0, len(knots)-2)
    u = (z-knots[j])/(knots[j+1]-knots[j])
    return 16*u*u*(1-u)*(1-u)


def moments(values, tau):
    total = float(values.sum())
    return {"S_com3": total, "uniform_relative_density_elasticity_magnitude":
            float(np.dot(values, tau)/total),
            "second_relative_density_derivative_over_S": float(np.dot(values, tau*tau)/total)}


def finite_response(values, delta):
    """Positive-measure finite change, derivative, and convex Taylor bounds."""
    values, delta = np.asarray(values), np.asarray(delta)
    if values.shape != delta.shape or np.any(values < 0) or not np.isfinite(values).all():
        raise ValueError("equal-shaped positive finite response measure required")
    linear = -float(np.dot(values, delta))
    actual = float(np.dot(values, np.expm1(-delta)))
    rem = float(np.dot(values, exp_remainder(delta)))
    rem_lo = 0.5*float(np.dot(values, np.exp(-np.maximum(delta, 0))*delta**2))
    rem_hi = 0.5*float(np.dot(values, np.exp(np.maximum(-delta, 0))*delta**2))
    total = float(values.sum())
    if not rem_lo*(1-3e-14) <= rem <= rem_hi*(1+3e-14):
        raise ValueError("convex exponential remainder bound failed")
    return {"delta_S_com3": actual, "relative_change_baseline_denominator": actual/total,
            "linear_delta_S_com3": linear, "convex_remainder_com3": rem,
            "remainder_lower_com3": rem_lo, "remainder_upper_com3": rem_hi,
            "quadratic_leading_com3": 0.5*float(np.dot(values, delta**2)),
            "stable_identity_absolute_residual_com3": actual-linear-rem,
            "min_delta_tau": float(delta.min()), "max_delta_tau": float(delta.max())}


def uniform_envelope(values, tau, epsilon):
    if not np.isfinite(epsilon) or not 0 <= epsilon < 1:
        raise ValueError("0 <= relative gas uncertainty < 1 required")
    total = float(values.sum())
    low_change = float(np.dot(values, np.expm1(-epsilon*tau)))
    high_change = float(np.dot(values, np.expm1(epsilon*tau)))
    return {"epsilon": epsilon, "core_lower_com3": total+low_change,
            "core_upper_com3": total+high_change,
            "relative_lower_change": low_change/total,
            "relative_upper_change": high_change/total}


class PathResponse:
    def __init__(self, run13_root, run15_root):
        self.root15 = Path(run15_root).resolve()
        kernel = self.root15/"postloss_diagnostic/postloss_fixed_gas_optical_response.py"
        comparator = self.root15/"source_recovery/theory/compare_gas_paths.py"
        self.k = load_checked(kernel, KERNEL_SHA, "run15_fixed_response")
        self.comp = load_checked(comparator, COMPARE_SHA, "run15_pchip_comparator")
        archived = self.root15/"postloss_diagnostic/FIXED_GAS_OPTICAL_RESPONSE.json"
        if sha(archived) != ARCHIVED_RESULT_SHA:
            raise ValueError("archived RUN15 numerical result differs")
        self.archived = json.loads(archived.read_text())
        self.base = self.k.FixedResponse(run13_root, "tight")
        self.standard = self.k.FixedResponse(run13_root, "standard")
        self.y0 = PchipInterpolator(self.base.zknots, self.base.gas_knots[:, 1], extrapolate=False)
        self.ys = PchipInterpolator(self.standard.zknots, self.standard.gas_knots[:, 1], extrapolate=False)
        self.knots = np.unique(np.r_[self.base.zknots, self.standard.zknots])
        self.time_knots = np.unique(np.r_[self.base.time_knots, self.standard.time_knots])
        self.regrid_t_on_s = PchipInterpolator(self.standard.zknots, self.y0(self.standard.zknots),
                                               extrapolate=False)
        self.regrid_s_on_t = PchipInterpolator(self.base.zknots, self.ys(self.base.zknots),
                                               extrapolate=False)
        self.enclosure = self.comp.compare_interpolants(self.y0, self.ys)

    def optical_fields(self, energies, rays, crossings, time_order):
        """Integrate positive baseline opacity and signed perturbations jointly."""
        node, weight = leggauss(time_order)
        n = len(energies)
        tau = np.zeros(n)
        fields = {name: np.zeros(n) for name in ("standard", "regrid_t_on_s", "regrid_s_on_t", "bump")}
        partial = np.zeros((len(self.knots)-1, n))
        evals = 0
        for a, b in zip(self.time_knots[:-1], self.time_knots[1:]):
            left = np.maximum(self.base.zbirth[rays], a)
            right = np.minimum(crossings, b)
            ids = np.flatnonzero(right > left)
            if not len(ids):
                continue
            span = right[ids]-left[ids]
            z = left[ids, None]+0.5*(node+1)*span[:, None]
            ratio, H, q = self.base.ratio(z, rays[ids, None])
            energy = energies[ids, None]*ratio
            sigma = self.base.native.sigma_native_formula(energy.ravel(), self.base.model.chi)[:, 0].reshape(z.shape)
            y = self.y0(z)
            kernel = self.k.C_M_S*self.base.dx/H*self.base.nh*np.exp(-3*self.base.dx*z)*sigma
            if (np.any(y <= 0) or np.any(kernel <= 0) or np.any(q <= 0)
                    or np.any(energy >= self.k.D_GATE) or not np.isfinite(kernel).all()):
                raise ValueError("positive D-inactive fixed-core contract failed")
            mass = 0.5*span[:, None]*weight*kernel
            dtau = np.sum(mass*y, axis=1)
            tau[ids] += dtau
            # Common gas knots also divide every native geometry/time panel.
            j = int(np.searchsorted(self.knots, 0.5*(a+b), side="right")-1)
            partial[j, ids] += dtau
            for label, path in (("standard", self.ys), ("regrid_t_on_s", self.regrid_t_on_s),
                                ("regrid_s_on_t", self.regrid_s_on_t)):
                fields[label][ids] += np.sum(mass*(path(z)-y), axis=1)
            fields["bump"][ids] += np.sum(mass*y*bump(z, self.knots), axis=1)
            evals += z.size
        if not np.allclose(partial.sum(axis=0), tau, rtol=3e-15, atol=1e-15):
            raise ValueError("time sensitivity partition fails additivity")
        return tau, fields, partial, evals

    def tail_upper(self, epsilon):
        """Original analytic H-only tail, weakened for n >= (1-eps)*n0."""
        if not 0 <= epsilon < 1:
            raise ValueError("tail relative uncertainty outside [0,1)")
        lam = (1-epsilon)*self.base.bounds["lambda_min_per_eV"]
        total = 0.0
        for ray in range(640):
            left, right = self.base.core_hi[ray], self.base.upper[ray]
            if right > left:
                total += self.base.weights_com3[ray]/self.base.source_norm*float(self.k.number_shape(self.k.H_FIT))*self.k.exponential_integral(
                    lam, left-self.k.H_FIT, right-self.k.H_FIT)
        return float(total)

    def calculate(self, energy_order, time_order):
        started = time.perf_counter()
        E, measure, ray, bins, panels = self.base.energy_rule(energy_order)
        crossing, root_receipt = self.base.crossings(E, ray)
        tau, fields, partial, evaluations = self.optical_fields(E, ray, crossing, time_order)
        values = measure*np.exp(-tau)
        total = float(values.sum())
        result = {"energy_order": energy_order, "time_order": time_order,
                  "energy_panels": panels, "energy_nodes": len(E), "time_evaluations": evaluations,
                  "crossing_receipt": root_receipt, "moments": moments(values, tau),
                  "binding_bins": {str(b): moments(values[bins == b], tau[bins == b]) for b in (0, 1)},
                  "standard_minus_tight_fixed_support": finite_response(values, fields["standard"])}
        sensitivity = partial @ values
        result["time_sensitivity"] = [{"left_z": float(a), "right_z": float(b),
                "minus_dS_d_relative_density_com3": float(v),
                "fraction_of_total_sensitivity": float(v/sensitivity.sum())}
                for a, b, v in zip(self.knots[:-1], self.knots[1:], sensitivity)]
        result["time_partition_sum_over_full_moment_minus1"] = float(sensitivity.sum()/np.dot(values, tau)-1)
        result["regrid_paths"] = {}
        for label in ("regrid_t_on_s", "regrid_s_on_t"):
            delta1 = fields[label]
            mid_values = values*np.exp(-delta1)
            first = finite_response(values, delta1)
            second = finite_response(mid_values, fields["standard"]-delta1)
            result["regrid_paths"][label] = {"tight_to_intermediate": first,
                    "intermediate_to_standard": second,
                    "telescope_residual_com3": first["delta_S_com3"]+second["delta_S_com3"]-
                        result["standard_minus_tight_fixed_support"]["delta_S_com3"]}
        result["knot_invisible_bump"] = {"definition": "Y_epsilon=Y_tight*(1+epsilon*16*u^2*(1-u)^2) on each common-knot panel",
                "zero_at_all_archived_knots": bool(np.all(bump(self.knots, self.knots) == 0)),
                "C1_at_knots_analytic": True,
                "directional_elasticity_magnitude": float(np.dot(values, fields["bump"])/total),
                "cases": [{"epsilon": eps, **finite_response(values, eps*fields["bump"])}
                            for eps in (-1e-4, -1e-6, 1e-6, 1e-4)]}
        eps_archive = self.enclosure["epsilon_abs_relative_upper"]
        result["conditional_uniform_gas_envelopes"] = []
        for eps in (1e-8, 1e-6, 1e-4, eps_archive):
            env = uniform_envelope(values, tau, eps)
            env["omitted_tail_upper_com3"] = self.tail_upper(eps)
            result["conditional_uniform_gas_envelopes"].append(env)
        # Diagnostic design targets, not user acceptance tolerances.
        result["conditional_gas_precision_targets"] = []
        for target in (1e-8, 1e-6):
            f = lambda eps: uniform_envelope(values, tau, eps)["relative_upper_change"]-target
            eps = brentq(f, 0.0, 1e-3, xtol=1e-20, rtol=1e-14)
            result["conditional_gas_precision_targets"].append({"example_relative_core_survivor_budget": target,
                "epsilon_saturating_quadrature_evaluated_envelope": eps,
                "interpretation": "conditional gas contribution only; not established gas error or total accuracy"})
        # Centered finite difference independently checks the analytic uniform derivative.
        result["directional_derivative_check"] = []
        for h in (1e-3, 1e-4, 1e-5):
            fd = (np.dot(values, np.expm1(-h*tau))-np.dot(values, np.expm1(h*tau)))/(2*h)
            exact = -np.dot(values, tau)
            bound = h*h/6*float(np.dot(values, np.exp(h*tau)*tau**3))
            result["directional_derivative_check"].append({"h": h, "centered_derivative_com3": float(fd),
                 "analytic_derivative_com3": float(exact), "absolute_gap_com3": float(abs(fd-exact)),
                 "analytic_centered_remainder_bound_com3": bound,
                 "within_bound_with_64eps_roundoff_allowance": bool(abs(fd-exact) <= bound+64*np.finfo(float).eps*abs(exact))})
        if not all(r["within_bound_with_64eps_roundoff_allowance"] for r in result["directional_derivative_check"]):
            raise ValueError("uniform derivative finite difference verification failed")
        result["wall_seconds"] = time.perf_counter()-started
        raw = {"energy_eV": E, "source_measure_com3": measure, "ray": ray, "binding_bin": bins,
               "crossing_z": crossing, "baseline_tau": tau, "common_gas_knots": self.knots,
               "time_interval_sensitivity_com3": sensitivity,
               **{"delta_tau_"+key: val for key, val in fields.items()}}
        return result, raw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run13-root", type=Path, required=True)
    p.add_argument("--run15-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    if args.output_dir.exists():
        p.error("output directory already exists; choose an unused add-only location")
    args.output_dir.mkdir(parents=True)
    start = time.perf_counter()
    calc = PathResponse(args.run13_root, args.run15_root)
    result = {"schema": "rei.run16.fixed_support_gas_path_response.v1",
        "status": "NUMERICALLY_CHECKED_CONDITIONAL_RESPONSE", "source_base_head": BASE_HEAD,
        "script_sha256": sha(__file__), "command": [sys.executable, *sys.argv],
        "environment": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                        "platform": platform.platform(), "native_IVP_runs": 0},
        "immutable_dependencies": {"run15_kernel_sha256": KERNEL_SHA,
             "run15_comparator_sha256": COMPARE_SHA, "run15_archived_result_sha256": ARCHIVED_RESULT_SHA},
        "inputs": {"tight": calc.base.identity(), "standard": calc.standard.identity()},
        "common_gas_knots": calc.knots.tolist(), "pchip_continuous_comparison": calc.enclosure,
        "scope": {"core_support": "fixed RUN15 tight core for every variation; no moving cutoff derivative",
            "source": "unchanged first-cell count, continuous BB50000K energy measure, finite160 births and GL8",
            "geometry": "original prescribed BASS121 SIGNED_MINUS; all other spectral cells untouched",
            "gas": "prescribed positive PCHIPs and explicitly labelled perturbation families",
            "units": "survivors comoving m^-3; neutral coordinate Y dimensionless; tau dimensionless",
            "not_established": ["true gas path enclosure", "core quadrature absolute error", "nonlinear continuum opacity feedback",
                "uniform m4", "angular continuum", "birth-time continuum", "whole donor domain", "full EoR",
                "Einstein feedback", "FLRW-CONV", "BI-SIGNED", "ISO-COUPLE full", "Li/Be nuclear T1-T8"],
            "floating_point_bounds": "analytic inequalities evaluated by binary64 quadrature and padded polynomial extrema; not directed rounding"},
        "runs": []}
    for energy_order, time_order in ((12, 24), (16, 24), (16, 32)):
        row, raw = calc.calculate(energy_order, time_order)
        result["runs"].append(row)
        print(json.dumps({"completed": [energy_order, time_order], "moments": row["moments"],
             "path_relative_delta": row["standard_minus_tight_fixed_support"]["relative_change_baseline_denominator"],
             "wall_seconds": row["wall_seconds"]}), flush=True)
    raw_path = args.output_dir/"RESPONSE_NODES_E16_T32.npz"
    np.savez_compressed(raw_path, **raw)
    result["raw_quadrature_nodes"] = {"file": raw_path.name, "bytes": raw_path.stat().st_size,
        "sha256": sha(raw_path), "arrays": {k: {"shape": list(v.shape), "dtype": str(v.dtype)} for k, v in raw.items()}}
    base_old = calc.archived["results"][3]["core_survivor_com3"]["all_below_H_fit"]
    std_old = calc.archived["results"][4]["core_survivor_com3"]["all_below_H_fit"]
    result["archived_RUN15_comparison"] = {"old_tight_core_com3": base_old, "old_standard_core_com3": std_old,
        "new_E12_T24_tight_relative_difference": result["runs"][0]["moments"]["S_com3"]/base_old-1,
        "interpretation": "baseline uses extra common time knots; new standard comparison fixes tight core support"}
    result["wall_seconds"] = time.perf_counter()-start
    path = args.output_dir/"GAS_PATH_RESPONSE.json"
    with path.open("x") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"output": str(path), "sha256": sha(path), "wall_seconds": result["wall_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
