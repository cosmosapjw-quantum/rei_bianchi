"""New, bounded HE34 reduction implementation checks; no background IVP replay.

Run with Python.  Evidence is atomically saved, including failed attempts.
The eight existing independent synthetic Radau controls are reused unchanged.
"""

from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile
import time
import traceback

import numpy as np
import scipy
from scipy.linalg import expm


UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "src"))
import certified_relaxation as reduction


def _assert_close(actual, expected, atol=3.0e-13, rtol=3.0e-13):
    assert np.allclose(actual, expected, atol=atol, rtol=rtol), (actual, expected)


def _expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("invalid input was not rejected with ValueError")


def check_package_interface_and_dense():
    N = np.array([0.0, 0.2, 0.5])
    S = np.array([0.08, -0.03, 0.02])
    sol = reduction.solve_reduced(N, S, 1.0e4)
    assert isinstance(sol, reduction.ReducedSolution)
    assert sol.certified and sol.certificate_valid and sol.approximation_valid
    assert sol.quadrature_converged and sol.interval_count == 2
    assert len(sol.intervals) == 2
    assert all(a.shape == N.shape and not a.flags.writeable for a in (
        sol.N, sol.S, sol.r, sol.u, sol.ratio_error_bound, sol.logp_error_bound))
    at_knots = sol.evaluate(N)
    assert np.array_equal(at_knots.r, sol.r)
    assert np.array_equal(at_knots.u, sol.u)
    assert np.array_equal(at_knots.ratio_error_bound, sol.ratio_error_bound)
    points = np.array([[0.0, 0.1], [0.2, 0.5]])
    dense = sol.evaluate(points)
    assert dense.r.shape == points.shape and np.all(np.isfinite(dense.u))
    assert float(sol.evaluate(0.0).r) == 0.0
    assert np.all(dense.ratio_error_bound <= sol.max_ratio_error_bound)
    assert np.all(dense.logp_error_bound <= sol.final_logp_error_bound)
    assert np.all(dense.omitted_layer_tail_bound >= 0.0)
    # Mutating caller-owned inputs cannot change the defined source control.
    N[1], S[1] = 0.3, 100.0
    assert sol.N[1] == 0.2 and sol.S[1] == -0.03
    return {"intervals": sol.interval_count, "status": sol.status,
            "max_ratio_bound": sol.max_ratio_error_bound,
            "final_logp_bound": sol.final_logp_error_bound,
            "quadrature_error_estimate": sol.quadrature_error_estimate,
            "omitted_layer_tail_bound": sol.omitted_layer_tail_bound}


def check_constant_source_against_eigenpressure_expm():
    """Independent full two-eigenpressure matrix, not a Riccati replay."""
    cases = []
    max_r_error = max_u_error = 0.0
    for chi, s, r0 in [(7.0, 0.0, 0.4), (10.0, 0.1, 0.0),
                        (10.0, -0.3, 0.0), (7.0, 0.2, -0.5),
                        (7.0, -0.2, 1.0), (20.0, -0.4, 0.7)]:
        N = np.array([0.0, 0.02, 0.15, 0.7])
        sol = reduction.solve_reduced(N, np.full_like(N, s), chi, r0=r0)
        # Z=(X,Y)*exp(5N)/p0.  This matrix follows directly from the
        # eigenpressure balance law before forming r=q/p.
        matrix = np.array([[2.0*s-chi/3.0, chi/3.0],
                           [2.0*chi/3.0, -4.0*s-2.0*chi/3.0]])
        initial = np.array([1.0-r0, 1.0+2.0*r0])
        query = np.unique(np.concatenate((N, [0.004, 0.09, 0.4])))
        dense = sol.evaluate(query)
        rref, uref = [], []
        for t in query:
            z = expm(float(t) * matrix) @ initial
            total = 2.0*z[0] + z[1]
            rref.append((z[1]-z[0]) / total)
            uref.append(math.log(total / 3.0))
        re = float(np.max(np.abs(dense.r-np.array(rref))))
        ue = float(np.max(np.abs(dense.u-np.array(uref))))
        max_r_error, max_u_error = max(max_r_error, re), max(max_u_error, ue)
        _assert_close(dense.r, rref)
        _assert_close(dense.u, uref)
        assert sol.certified and sol.certificate_valid
        assert np.all(sol.ratio_error_bound == 0.0)
        assert np.all(sol.logp_error_bound == 0.0)
        assert sol.quadrature_error_estimate == 0.0 and sol.omitted_layer_tail_bound == 0.0
        assert all(rec.pressure_method == "constant_source_closed_form" for rec in sol.intervals)
        cases.append({"chi": chi, "S": s, "r0": r0,
                      "max_ratio_error": re, "max_logp_error": ue})
    return {"reference": "scipy.linalg.expm of independent full eigenpressure matrix",
            "cases": cases, "max_ratio_error": max_r_error, "max_logp_error": max_u_error}


def check_invalid_inputs():
    valid = {"N_knots": [0.0, 1.0], "S_knots": [0.1, 0.2], "chi": 10.0}
    changes = [
        {"N_knots": [0.0]}, {"S_knots": [0.1]},
        {"N_knots": [1.0, 2.0]}, {"N_knots": [0.0, 0.0]},
        {"N_knots": [0.0, -1.0]}, {"N_knots": [[0.0, 1.0]]},
        {"N_knots": [0.0, math.inf]}, {"S_knots": [0.1, math.nan]},
        {"S_knots": [0.1, 0.2j]}, {"chi": 0.0}, {"chi": -1.0},
        {"chi": math.inf}, {"chi": True}, {"chi": [10.0]},
        {"r0": -0.500001}, {"r0": 1.000001}, {"r0": math.nan},
        {"tol_ratio": 0.0}, {"tol_logp": -1.0}, {"tol_logp": math.nan},
    ]
    for change in changes:
        params = {**valid, **change}
        _expect_value_error(lambda params=params: reduction.solve_reduced(**params))
    sol = reduction.solve_reduced(**valid)
    for points in [[-1.0], [1.1], [math.nan], [1j]]:
        _expect_value_error(lambda points=points: sol.evaluate(points))
    return {"rejected_solver_inputs": len(changes), "rejected_dense_inputs": 4,
            "policy": "ValueError for malformed inputs; no clipping"}


def check_unavailable_and_excessive_certificates():
    noncontractive = reduction.solve_reduced([0.0, 1.0], [1.0, 1.0], 6.0)
    assert not noncontractive.certified and not noncontractive.certificate_valid
    assert noncontractive.approximation_valid and np.all(np.isfinite(noncontractive.u))
    assert any("kappa_" in reason for reason in noncontractive.certificate_failures)
    assert math.isinf(noncontractive.final_logp_error_bound)

    cone = reduction.solve_reduced([0.0, 1.0e-8], [0.1, -0.1], 10.0, r0=1.0)
    assert not cone.certified and not cone.certificate_valid
    assert cone.approximation_valid
    assert any("cone_not_proved" in reason for reason in cone.certificate_failures)
    assert cone.r[-1] > 1.0  # A useful explicit rejected approximation, not clipping.

    denominator = reduction.solve_reduced([0.0, 1.0], [1.0, 1.0], 1.0e-300, r0=1.0)
    assert not denominator.certified
    assert any("denominator_" in reason for reason in denominator.certificate_failures)
    assert denominator.approximation_valid

    pole = reduction.solve_reduced([0.0, 100.0], [1.0, 1.0], 1.0e-300, r0=1.0)
    assert not pole.certified and not pole.approximation_valid
    assert pole.r[0] == 1.0 and math.isnan(pole.r[-1])

    bound = reduction.solve_reduced([0.0, 1.0], [0.1, 0.2], 10.0,
                                    tol_ratio=1.0e-12, tol_logp=1.0e-12)
    assert bound.certificate_valid and not bound.certified
    assert bound.approximation_valid and np.all(np.isfinite(bound.r))
    assert "ratio_tolerance_not_met" in bound.certificate_failures
    assert "logp_tolerance_not_met" in bound.certificate_failures
    return {"noncontractive": noncontractive.certificate_failures,
            "cone": cone.certificate_failures, "denominator": denominator.certificate_failures,
            "unrepresentable_denominator": pole.certificate_failures,
            "bound_not_met": {"status": bound.status, "failures": bound.certificate_failures,
                              "max_ratio_bound": bound.max_ratio_error_bound,
                              "final_logp_bound": bound.final_logp_error_bound}}


def check_small_kappa_h_and_pressure_cancellation():
    errors = []
    with localcontext() as ctx:
        ctx.prec = 90
        for kappa, h in [(1.0e-12, 1.0e-8), (1.0, 1.0e-16), (1.0e8, 1.0e-18),
                         (1.0, 1.0e-4), (1.0, 1.0e-3), (2.0, 0.1), (1.0, 40.0)]:
            kd, hd = Decimal.from_float(kappa), Decimal.from_float(h)
            ed = (-kd*hd).exp()
            m0d = (1-ed)/kd
            hm0d = hd-m0d
            m1d = hm0d/kd
            observed = reduction._relaxation_integrals(kappa, h)
            reference = tuple(map(float, (ed, m0d, hm0d, m1d)))
            relative = [abs(a-b)/abs(b) if b else abs(a-b) for a, b in zip(observed, reference)]
            assert max(relative) < 3.0e-12, (kappa, h, observed, reference, relative)
            errors.append({"kappa": kappa, "h": h, "max_relative_error": max(relative)})
        # Direct high-precision constant-source formula checks the tiny net
        # pressure increment when its O(h) root and layer terms cancel.
        chi, s, h = 2.0, 0.1, 1.0e-12
        cd, sd, hd = map(Decimal.from_float, (chi, s, h))
        dd = (cd*cd+4*cd*sd+36*sd*sd).sqrt()
        bd = -4*sd/(cd+2*sd+dd)
        cc = 4*sd*(-bd)/dd
        expected = -4*sd*bd*hd + (1+cc*((-dd*hd).exp()-1)).ln()
        sol = reduction.solve_reduced([0.0, h], [s, s], chi)
        pressure_relative = abs(sol.u[-1]-float(expected))/abs(float(expected))
        assert pressure_relative < 2.0e-13, (sol.u[-1], str(expected))
        assert sol.certified
    return {"reference": "standard-library Decimal, 90 digits", "moment_checks": errors,
            "tiny_constant_logp": float(sol.u[-1]), "tiny_constant_logp_relative_error": pressure_relative}


def check_large_chi_h_rescaled_layer():
    chi, h, sa, sb, r0 = 1.0e8, 1.0e6, 0.1, -0.2, 0.2
    sol = reduction.solve_reduced([0.0, h], [sa, sb], chi, r0=r0)
    assert sol.certified and sol.quadrature_converged
    rec = sol.intervals[0]
    assert rec.D0*h > 1.0e13 and 48.0 <= rec.layer_x_cap < rec.D0*h
    assert rec.layer_pressure_increment != 0.0 and rec.omitted_layer_tail_bound > 0.0
    # Independent absolutely convergent Laplace-moment expansion on [0,inf).
    # Here |c/(1-c)| < 1e-8: 12 terms give a negligible geometric remainder.
    t = rec.c/(1.0-rec.c)
    assert abs(t) < 1.0e-8
    slope = (sb-sa)/h
    moment_sum = math.fsum(((-t)**k)*(sa/(k+1)+(slope/rec.D0)/(k+1)**2)
                           for k in range(12))
    reference = (-4.0*rec.delta0/rec.D0)/(1.0-rec.c)*moment_sum
    layer_error = abs(rec.layer_pressure_increment-reference)
    assert layer_error <= rec.quadrature_error_estimate + rec.omitted_layer_tail_bound + 1.0e-23
    assert layer_error < 1.0e-22
    # This would differ by O(1e-9) if the initial layer were missed by
    # quadrature on the unresolved original-N domain.
    assert abs(reference) > 1.0e-10
    return {"chi_h": chi*h, "layer_x_cap": rec.layer_x_cap,
            "layer_increment": rec.layer_pressure_increment, "layer_reference": reference,
            "layer_absolute_error": layer_error,
            "quadrature_error_estimate": rec.quadrature_error_estimate,
            "analytic_omitted_layer_tail_bound": rec.omitted_layer_tail_bound,
            "quadrature_evaluations": rec.quadrature_evaluations}


def check_scaled_root_and_unavailable_numeric_range():
    # The S^2 expression would overflow, but all actual outputs are finite.
    chi, s, h, r0 = 1.0e200, -1.0e199, 1.0e-200, 0.3
    sol = reduction.solve_reduced([0.0, h], [s, s], chi, r0=r0)
    small_matrix = np.array([[2.0*(s*h)-(chi*h)/3.0, (chi*h)/3.0],
                             [2.0*(chi*h)/3.0, -4.0*(s*h)-2.0*(chi*h)/3.0]])
    z = expm(small_matrix) @ np.array([1.0-r0, 1.0+2.0*r0])
    total = 2.0*z[0]+z[1]
    rref, uref = (z[1]-z[0])/total, math.log(total/3.0)
    _assert_close(sol.r[-1], rref)
    _assert_close(sol.u[-1], uref)
    assert sol.certified
    unavailable = reduction.solve_reduced([0.0, 1.0], [1.0e308, 1.0e308], 1.0e308)
    assert not unavailable.approximation_valid and not unavailable.certified
    assert "binary64 range" in " ".join(unavailable.certificate_failures)
    return {"scaled_constant_ratio_error": abs(sol.r[-1]-rref),
            "scaled_constant_logp_error": abs(sol.u[-1]-uref),
            "explicit_numeric_range_failure": unavailable.certificate_failures}


def check_exact_zero_residual_with_huge_finite_interval():
    h = 1.0e160
    sol = reduction.solve_reduced([0.0, h], [0.0, 0.0], 1.0e-200, r0=0.4)
    assert sol.certified and np.all(sol.ratio_error_bound == 0.0)
    assert np.all(sol.logp_error_bound == 0.0) and np.all(sol.u == 0.0)
    dense = sol.evaluate(h/2.0)
    assert float(dense.ratio_error_bound) == 0.0 and float(dense.logp_error_bound) == 0.0
    observed = reduction._max_t_exp(1.0e308, 1.0, 2.0)
    with localcontext() as ctx:
        ctx.prec = 90
        expected = float(1/(2*Decimal.from_float(1.0e308)*Decimal(1).exp()))
    assert observed > 0.0 and abs(observed-expected) <= 2.0*float(np.nextafter(0.0, 1.0))
    return {"h": h, "kappa_h": sol.chi*h, "status": sol.status,
            "two_rate_exponential_maximum": observed,
            "two_rate_exponential_maximum_reference": expected}


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    destination = UNIT / "evidence" / "REDUCTION_UNIT_CHECKS.json"
    existing = json.loads(destination.read_text()) if destination.exists() else {}
    attempts = existing.get("attempts", [])
    started = time.perf_counter()
    attempt = {"started_utc": datetime.now(timezone.utc).isoformat(),
               "source_sha256": _sha(UNIT/"src"/"certified_relaxation.py"),
               "checks_sha256": _sha(Path(__file__)), "checks": []}
    checks = [check_package_interface_and_dense, check_constant_source_against_eigenpressure_expm,
              check_invalid_inputs, check_unavailable_and_excessive_certificates,
              check_small_kappa_h_and_pressure_cancellation, check_large_chi_h_rescaled_layer,
              check_scaled_root_and_unavailable_numeric_range,
              check_exact_zero_residual_with_huge_finite_interval]
    status = "pass_scoped"
    for check in checks:
        before = time.perf_counter()
        try:
            detail = check()
            attempt["checks"].append({"name": check.__name__, "status": "pass", "detail": detail,
                                      "wall_seconds": time.perf_counter()-before})
            print(f"PASS {check.__name__}", flush=True)
        except Exception as exc:
            status = "failed"
            attempt["checks"].append({"name": check.__name__, "status": "failed",
                                      "exception": repr(exc), "traceback": traceback.format_exc(),
                                      "wall_seconds": time.perf_counter()-before})
            print(f"FAIL {check.__name__}: {exc}", flush=True)
            break
    attempt["status"] = status
    attempt["wall_seconds"] = time.perf_counter()-started
    attempts.append(attempt)
    reused = Path("/tmp/he34_reduction_theory/CONTROL_RESULTS.json")
    evidence = {"schema": "he34.certified_relaxation_unit_checks.v1", "status": status,
                "scope": "New implementation interface, constant-source matrix oracle, edge regimes, and invalid inputs only",
                "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                "existing_independent_controls": {"path": str(reused), "sha256": _sha(reused),
                    "run_count": 8, "replayed": False} if reused.exists() else {"replayed": False},
                "old_HE32_IVPs_replayed": 0, "HE32_background_comparisons_run_here": 0,
                "qualification": "Analytic continuum approximation certificate only; binary64 evaluation, numerical quadrature estimates, analytic tail evaluation and finite oracle checks are not an outward-rounded machine proof.",
                "attempts": attempts}
    _atomic_json(destination, evidence)
    print(json.dumps({"status": status, "attempts": len(attempts), "evidence": str(destination)}), flush=True)
    return 0 if status == "pass_scoped" else 1


if __name__ == "__main__":
    raise SystemExit(main())
