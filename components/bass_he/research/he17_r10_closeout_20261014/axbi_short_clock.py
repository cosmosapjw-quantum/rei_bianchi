#!/usr/bin/env python3
"""Read-only local proper-time increment for the pinned AXBI background.

Scientific domain: Planck-like, prescribed non-tilted LRS Bianchi I,
A_REF=1/21 to A_END=1/5, physical-density-fixed or same-H control.

The analytic quadrature truncation bound concerns the EXACT-REAL f=1/H and
exact-real endpoints/evaluations only. Float input formation, log1p, exp,
hypot, and binary64 summation are explicitly UNBOUNDED in this witness.
It must not be installed into a native solver without new parity and interval
error checks; no backend/driver/physics/acceptance mutation is performed here.
"""
from __future__ import annotations
import math

H0_S = 67.4 * 1e5 / 3.0856775814913673e24
OMEGA_M = 0.315
OMEGA_R = 9.2e-5
OMEGA_L = 1 - OMEGA_M - OMEGA_R
A_REF = 1.0 / 21.0
A_END = 0.2


def _hubble(a: float, q_ref: float, family: str) -> float:
    e = OMEGA_M / a**3 + OMEGA_R / a**4 + OMEGA_L
    hf = H0_S * math.sqrt(e)
    if family == "SameHDiagnostic":
        return hf
    eref = OMEGA_M / A_REF**3 + OMEGA_R / A_REF**4 + OMEGA_L
    s = q_ref * H0_S * math.sqrt(eref) * (A_REF/a)**3
    return math.hypot(hf, s)


def truncation_relative_ceiling(delta_log_a: float) -> float:
    """Bound Simpson's exact-real RELATIVE error using only positive weights.

    f(x)=1/H(e^x), H/H0=sqrt(sum_{n=0,3,4,6} c_n exp(-n*x)).
    For c_n>=0, |f''''/f|<=30537 and f(x1)/f(x0)<=exp(3h).
    This bound does not include floating-point evaluation errors.
    """
    h=float(delta_log_a)
    if not math.isfinite(h) or h<0 or h>math.log(A_END/A_REF):
        raise ValueError("DELTA_LOG_A_OUTSIDE_PINNED_SOURCE_DOMAIN")
    return (30537.0/2880.0)*h**4*math.exp(3*h)


def short_increment(a0: float,a1: float,q_ref:float,family:str="PhysicalDensityFixed") -> dict:
    """Compute small-cell Simpson diagnostic using stable log1p of ACTUAL endpoints.

    This is a candidate+diagnostic, not an accepted replacement for Driver.dt.
    """
    a0=float(a0);a1=float(a1);q_ref=float(q_ref)
    if any(not math.isfinite(v) for v in (a0,a1,q_ref)):
        raise ValueError("NONFINITE_INPUT")
    if not (A_REF<=a0<a1<=A_END):
        raise ValueError("PINNED_SCALE_DOMAIN_OR_ORDER")
    if q_ref not in (0.0,0.005,-0.005,0.01,-0.01):
        raise ValueError("UNREVIEWED_SHEAR_PARAMETER")
    if family not in ("PhysicalDensityFixed","SameHDiagnostic"):
        raise ValueError("UNKNOWN_BACKGROUND_FAMILY")
    # Sterbenz subtraction is exact for nearby binary64 inputs; note that the
    # inputs themselves may carry separate source/clock errors.
    h=math.log1p((a1-a0)/a0)
    amid=a0*math.exp(0.5*h)
    f0=1.0/_hubble(a0,q_ref,family)
    fm=1.0/_hubble(amid,q_ref,family)
    f1=1.0/_hubble(a1,q_ref,family)
    dt=(h/6.0)*math.fsum((f0,4.0*fm,f1))
    if not (dt>0 and math.isfinite(dt)):
        raise ValueError("CLOCK_INCREMENT_INVALID")
    return {
        "status":"FLOAT_PILOT_WITH_ANALYTIC_TRUNCATION_BOUND_ONLY",
        "dt_s":dt,"model":family,"q_ref":q_ref,
        "a0_binary64":a0.hex(),"a1_binary64":a1.hex(),
        "delta_log_a_float":h,
        "analytic_exact_real_relative_truncation_ceiling":truncation_relative_ceiling(h),
        "binary64_eval_error_bound":None,
        "native_driver_parity":None,
        "true_trajectory_error_bound":None,
        "source_RHS_ODE_calls":0,
        "number_H_evaluations":3,
    }
