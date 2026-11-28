"""Independent direct angular/radial checks for the new H1 gain derivation.

No existing HE suite/IVP is imported or rerun. Units in the angular toy are
dimensionless with I=1; radial controls use x=I/(k_B T). This is not a new
physical calibration. Output is create-once, with atomic replacement+fsync.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import time

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.special import exp1


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "CHECKS.json"
I = 1.0
KB_EV = 1.380649e-23 / 1.602176634e-19


def sphere(nmu=6, nphi=12):
    mu, wm = leggauss(nmu)
    phi = np.arange(nphi) * (2*math.pi/nphi)
    x = np.sqrt(1-mu[:, None]**2)*np.cos(phi)[None, :]
    y = np.sqrt(1-mu[:, None]**2)*np.sin(phi)[None, :]
    z = np.broadcast_to(mu[:, None], x.shape)
    vec = np.stack((x, y, z), axis=-1).reshape(-1, 3)
    weights = np.broadcast_to(wm[:, None]/(2*nphi), x.shape).ravel().copy()
    return vec, weights


def relative_norm(a, b, floor=1.0):
    return float(np.linalg.norm(np.asarray(a)-np.asarray(b)) /
                 max(np.linalg.norm(np.asarray(b)), floor))


def source_cdf_energy(E, z):
    # Upsilon=CDF^{-1}(z); z is uniform on [0,1].
    transfer = I*E/(E-z*(E-I))
    return E-transfer, transfer-I


def direct_angular_case(theta, law):
    inc, wi = sphere()
    outlocal, wo = sphere(5, 12)
    outmu = outlocal[:, 2]
    p2 = (3*outmu*outmu-1)/2
    basis1 = np.cross(np.array([0., 0., 1.]), inc)
    basis1 /= np.linalg.norm(basis1, axis=1)[:, None]
    basis2 = np.cross(inc, basis1)
    outgoing = (outlocal[None, :, 0, None]*basis1[:, None, :]
                + outlocal[None, :, 1, None]*basis2[:, None, :]
                + outmu[None, :, None]*inc[:, None, :])
    # Direct Cartesian tensor nodes; no P2 tensor identity used here.
    outerout = np.einsum("nqi,nqj->nqij", outgoing, outgoing)
    outerin = np.einsum("ni,nj->nij", inc, inc)
    epi, ewi = leggauss(64)
    energy = I+(epi+1)*3.0
    we = ewi*3.0
    uz, uw = leggauss(24)
    uz, uw = (uz+1)/2, uw/2
    ne, nh = 2.3, 1.4
    pi = np.array([[.2, .11, -.04], [.11, -.07, .03], [-.04, .03, -.13]])
    incident_pi = np.einsum("nij,ij->n", outerin, pi)
    base = np.zeros((3, 3))
    linear = np.zeros((3, 3))
    ngain = qgain = alpha = beta = gamma = edmoment = 0.0
    max_norm_defect = max_energy_defect = 0.0
    d_values = []
    for E, w in zip(energy, we):
        # Positive manufactured radial K; no previous source/IVP reused.
        K = (E-I)**2/(1+E)**3
        radial = w*2*math.sqrt(E)/(math.sqrt(math.pi)*theta**1.5)*math.exp(-E/theta)*K
        gain = np.zeros((len(inc), 3, 3))
        gain_count = 0.0
        energy_sum = 0.0
        D_analytic = 0.0
        e1, e2 = source_cdf_energy(E, uz)
        for first, second, wshare in zip(e1, e2, uw):
            for epsilon in (first, second):
                # Each toy angular marginal is nonnegative. For the selected
                # published isotropic model the coefficient is exactly zero.
                aval = 0.0 if law == "isotropic" else -.8+2.5*(epsilon/(E-I))/(1+.2*(E-I))
                prob = wo*(1+aval*p2)
                assert np.min(prob) >= 0
                gain += wshare*2*epsilon*np.einsum("q,nqij->nij", prob, outerout)
                gain_count += wshare*float(np.sum(prob))
                energy_sum += wshare*epsilon*float(np.sum(prob))
                D_analytic += wshare*epsilon*aval/5
        max_norm_defect = max(max_norm_defect, abs(gain_count-2))
        max_energy_defect = max(max_energy_defect, abs(energy_sum-(E-I)))
        combined = gain-2*E*outerin
        base += ne*nh*radial*np.einsum("n,nij->ij", wi, combined)
        linear += ne*nh*radial*np.einsum("n,nij->ij", wi*(E/(ne*theta**2))*incident_pi, combined)
        ngain += ne*nh*radial*gain_count
        qgain += ne*nh*radial*energy_sum
        alpha += radial
        beta += radial*E
        gamma += radial*E*E
        edmoment += radial*E*D_analytic
        d_values.append((D_analytic+(E-I)/2, E-I-D_analytic))
    Qnet = -ne*nh*I*alpha
    nu = 4*nh*(gamma-edmoment)/(15*theta**2)
    expected_base = (2*Qnet/3)*np.eye(3)
    expected_linear = -nu*pi
    lower = 4*nh*I*beta/(15*theta**2)
    upper = 2*nh*(3*gamma-I*beta)/(15*theta**2)
    res = {
        "theta_over_I": theta,
        "law": law,
        "baseline_tensor_residual": relative_norm(base, expected_base),
        "STF_derivative_residual": relative_norm(linear, expected_linear),
        "linear_trace_abs": abs(float(np.trace(linear))),
        "net_heat_residual": abs(float(np.trace(base))/2-Qnet),
        "outgoing_number_residual": abs(ngain-2*ne*nh*alpha),
        "outgoing_energy_residual": abs(qgain-ne*nh*(beta-I*alpha)),
        "max_event_normalization_defect": max_norm_defect,
        "max_event_energy_defect": max_energy_defect,
        "minimum_D_bound_slack": float(np.min(d_values)),
        "nu": nu,
        "nu_bound": [lower, upper],
        "moment_alpha_beta_gamma": [alpha, beta, gamma],
        "incident_sphere_nodes": len(inc),
        "outgoing_marginal_nodes": len(wo),
        "energy_nodes": len(energy),
        "sharing_CDF_nodes": len(uz),
        "joint_sampling": "not_needed_for_additive_one_particle_moments",
    }
    assert res["baseline_tensor_residual"] < 1e-12
    assert res["STF_derivative_residual"] < 1e-12
    assert res["max_event_normalization_defect"] < 1e-13
    assert res["max_event_energy_defect"] < 1e-12
    assert lower <= nu <= upper
    return res


def radial_case(T):
    x = 13.6/(KB_EV*T)
    # Direct positive scaled radial integrals after E=I+theta*t.
    integ = []
    errors = []
    for j in range(4):
        value, err = quad(lambda t: t*(x+t)**(j-1)*math.exp(-t),
                          0, math.inf, epsabs=2e-13, epsrel=2e-13)
        integ.append(value)
        errors.append(err)
    F = 1-x*math.exp(x)*float(exp1(x))
    expected = [F, 1, x+2, x*x+4*x+6]
    discrepancy = [abs(a-b)/abs(a) for a,b in zip(integ, expected)]
    assert max(discrepancy) < 3e-12
    assert 1/(x+2) <= integ[0] <= 1/(x+1)
    # Stable conditional mean and gamma/beta checks use positive integral F.
    mean_over_theta = 1/integ[0]
    assert x+1 <= mean_over_theta <= x+2
    return {
        "T_K": T, "x": x, "positive_radial_integrals": integ,
        "special_function_and_polynomial_expected": expected,
        "relative_discrepancy": discrepancy, "adaptive_error_estimates": errors,
        "F_bounds": [1/(x+2), 1/(x+1)],
        "mean_energy_over_theta": mean_over_theta,
    }


def source_sharing_case(E):
    p = lambda transfer: I*E/((E-I)*transfer*transfer)
    vals = [quad(p, I, E, epsabs=1e-13, epsrel=1e-13)[0],
            quad(lambda tr: p(tr)*((E-tr)+(tr-I)), I, E,
                 epsabs=1e-13, epsrel=1e-13)[0]]
    assert abs(vals[0]-1) < 1e-12
    assert abs(vals[1]-(E-I)) < 1e-12
    return {"E_over_I": E, "normalization": vals[0], "outgoing_energy_sum_over_I": vals[1]}


def main():
    if OUT.exists():
        raise SystemExit("CHECKS.json exists; unchanged independent controls must be reused")
    start = time.perf_counter()
    report = {
        "schema": "he37.independent_gain_controls.v1",
        "status": "RUNNING",
        "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": platform.python_version(), "numpy": np.__version__,
        "scope": "new_gain_derivation_only; no_IVP; no_old_suite_replay",
        "angular_cases": [], "radial_cases": [], "sharing_cases": [],
    }
    try:
        for theta in (.7, 3.0):
            for law in ("isotropic", "positive_P2_manufactured"):
                report["angular_cases"].append(direct_angular_case(theta, law))
        for T in (2000.0, 20000.0, 200000.0):
            report["radial_cases"].append(radial_case(T))
        for E in (1.001, 2.0, 5.0, 50.0):
            report["sharing_cases"].append(source_sharing_case(E))
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        report["elapsed_s"] = time.perf_counter()-start
        report["maxrss_KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        pending = OUT.with_suffix(".tmp")
        with open(pending, "x") as handle:
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, OUT)
    print(json.dumps({"status": report["status"], "output": str(OUT),
                      "angular_cases": len(report["angular_cases"]),
                      "radial_cases": len(report["radial_cases"]),
                      "sharing_cases": len(report["sharing_cases"]),
                      "elapsed_s": report["elapsed_s"]}, indent=2))


if __name__ == "__main__":
    main()
