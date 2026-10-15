"""Conditional a-posteriori sensitivity budget for directional Thomson-depth quadrupoles.

Assumptions: normal-comoving non-tilted LRS Bianchi I, exact mean a(t), t(a),
nH(t), sigma_T, and the sampled piecewise-linear surrogate for b(ln a),
ne(ln a). Perturbations satisfy sup|delta b|<=eps_b at ALL ln a including
observer, and sup|delta x_HII|, sup|delta x_HeII|, sup|delta x_HeIII| <=
eps_x at ALL proper times for each signed case. The original source ODE is NOT
certified; this tool derives sufficient budgets conditional on those hypotheses.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path
from time import perf_counter
import numpy as np

PARENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PARENT))
from clock_decompose_signed import CASE_ORDER, read_caches, EXPECTED_SOURCE_SHA
from goal_error_budget import integral_nh, F_HE
from directional_tau import read_geometry

KAPPA = np.longdouble("6.6524587321e-29") * np.longdouble("299792458") * np.longdouble("1000000")
QUAD_L1 = np.longdouble(10) / (np.longdouble(3) * np.sqrt(np.longdouble(3)))
H = (("0.005", "SHEAR_HALF_PLUS", "SHEAR_HALF_MINUS"),
     ("0.01", "SHEAR_PLUS", "SHEAR_MINUS"))


def maxima_chunked(a, t, ne, b, chunk=16384):
    """Piecewise exact (for affine t and ne vs ln a) bounds using O(chunk) scratch."""
    if chunk < 2:
        raise ValueError("chunk must be >=2")
    a = np.asarray(a)
    t = np.asarray(t)
    ne = np.asarray(ne)
    b = np.asarray(b)
    n = a.size
    if n < 2 or any(x.shape != (n,) for x in (t, ne, b)):
        raise ValueError("Inconsistent input histories")
    L = np.longdouble(0)
    M = np.longdouble(0)
    for left in range(0, n - 1, chunk):
        right = min(left+chunk, n-1)
        sl = slice(left,right+1)
        ua = np.log(a[sl].astype(np.longdouble))
        dt = np.diff(t[sl].astype(np.longdouble))
        du = np.diff(ua)
        ne_slice = ne[sl].astype(np.longdouble)
        db = np.diff(b[sl].astype(np.longdouble))
        if np.any(~np.isfinite(ua)) or np.any(~np.isfinite(dt)) or \
           np.any(~np.isfinite(ne_slice)) or np.any(~np.isfinite(db)) or \
           np.any(du <= 0) or np.any(dt <= 0) or np.any(ne_slice < 0):
            raise ValueError("Invalid proper-time, log scale, geometry or electron density")
        L = max(L, KAPPA * np.max((dt/du) *
                                np.maximum(ne_slice[:-1],ne_slice[1:])))
        M = max(M, np.max(np.abs(db/du)))
    if 2*M >= 1:
        raise ValueError("No inverse-log-redshift stability margin")
    return L, M, np.longdouble(1)-2*M


def maxima_vectorized(a, t, ne, b):
    """Independent full-array O(N) scratch reference for numerical parity tests."""
    a=np.asarray(a,dtype=np.longdouble)
    t=np.asarray(t,dtype=np.longdouble)
    ne=np.asarray(ne,dtype=np.longdouble)
    b=np.asarray(b,dtype=np.longdouble)
    du=np.diff(np.log(a))
    dt=np.diff(t)
    return (KAPPA*np.max((dt/du)*np.maximum(ne[:-1],ne[1:])),
            np.max(abs(np.diff(b)/du)))


def per_case_bounds(a, t, ne, b, chunk=16384):
    L,M,m = maxima_chunked(a,t,ne,b,chunk)
    # From |delta b(u)|<=eps_b both at emission and observer,
    # |delta log redshift|<=4eps_b, and root |delta u|<=4eps_b/m.
    geom = np.longdouble(4)*L/m
    # Ion fractions uniform absolute errors, fixed nH(a), t(a).
    frac = (np.longdouble(1)+3*F_HE)*integral_nh(t,a)
    return {
        "max_abs_b_slope_dln_a": format(M,".21g"),
        "minimum_absolute_redshift_dlog_a": format(m,".21g"),
        "max_abs_d_tau_dln_a": format(L,".21g"),
        "geometry_bound_coefficient_per_sup_abs_b_error": format(geom,".21g"),
        "gas_fraction_bound_coefficient_per_sup_abs_species_error": format(frac,".21g"),
        "interpretation":"|delta tau_direction| <= G eps_b + X eps_x at a common observer and fixed mean a(t),t(a)",
    }


def _p(x):
    return np.longdouble(x)


def directional_redshift_domain_margin(a, b, z_rel):
    """At earliest node, least redshift over observer mu in [0,1]."""
    da = _p(b[0])-_p(b[-1])
    min_g = np.log(_p(a[-1])/_p(a[0]))+min(da,-2*da)
    return min_g-np.log1p(_p(z_rel))


def campaign_error_budget(baseline_cache, geometry_cache, direction_result, relative_goal=0.1):
    if not math.isfinite(float(relative_goal)) or not 0 < relative_goal < 1:
        raise ValueError("relative_goal must be in (0,1)")
    records, manifest, cache_secs=read_caches(baseline_cache)
    bmap=read_geometry(geometry_cache,baseline_cache,manifest)
    props={}
    timings={}
    for case in CASE_ORDER:
        t0=perf_counter()
        dat=records[case]
        props[case]=per_case_bounds(dat["a"],dat["t_s"],dat["ne_cm3"],bmap[case])
        timings[case]=perf_counter()-t0
    output = {
        "schema":"he18.axbi.directional_tau2_conditional_goal_budget.v1",
        "status":"DERIVED_AND_NUMERICALLY_CHECKED_CONDITIONAL_NOT_SOURCE_ODE_CERTIFIED",
        "observer_mean_a":direction_result["observer_mean_a"],
        "goal_relative_fraction":relative_goal,
        "epsilon_b_definition":"uniform |delta b| on the entire prefix INCLUDING b_observer, fixed normal-frame observer direction",
        "epsilon_x_definition":"uniform absolute |delta x_HII|,|delta x_HeII|,|delta x_HeIII| on entire prefix",
        "held_fixed":"a(t), t(a), nH(a), constants, normal electron congruence and continuous piecewise-linear source surrogate",
        "analytic_bound":"|delta O_tau2(q)| <= C_b eps_b + C_x eps_x, C_b=(10/(3sqrt(3)))/2 *(4L_plus/m_plus+4L_minus/m_minus), C_x=(10/(3sqrt(3)))/2*(X_plus+X_minus); m_q=1-2 max|db_q/d ln a|, L_q=max|d tau_q/d ln a|, X_q=(1+3fHe)*sigmaTc integral nH_q dt",
        "quad_L1_factor":format(QUAD_L1,".19g"),
        "history_sha256":{c:v["history_sha256"] for c,v in manifest["cases"].items()},
        "source_identity_sha256":EXPECTED_SOURCE_SHA,
        "case_coefficients":props,
        "derived_sampled_directional":[],
        "elapsed_s":timings,
        "cache_read_s":cache_secs,
        "critical_limitations":[
            "These are sufficient conditional budgets, not proof that source errors satisfy them",
            "No separate control of errors in a(t), t(a), H(t), nH, microphysics, radiation transport or native global solver error",
            "Numerical quadrature, interpolation and floating-point error not included in this analytic source perturbation bound",
            "Direction-dependent redshift is relative to early observer at zbar about 10.269, not the present CMB observer",
        ],
    }
    cases=direction_result["case_data"]
    for row in direction_result["signed_summary"]:
        z=float(row["z_rel"])
        mcheck={}
        for case in CASE_ORDER:
            dat=records[case]
            mm=directional_redshift_domain_margin(dat["a"],bmap[case],z)
            if mm<=0:
                raise ValueError("No positive redshift bracketing domain")
            mcheck[case]=mm
        for q,plus,minus in H:
            gq=(_p(props[plus]["geometry_bound_coefficient_per_sup_abs_b_error"]) +
                _p(props[minus]["geometry_bound_coefficient_per_sup_abs_b_error"]))*QUAD_L1/2
            xq=(_p(props[plus]["gas_fraction_bound_coefficient_per_sup_abs_species_error"]) +
                _p(props[minus]["gas_fraction_bound_coefficient_per_sup_abs_species_error"]))*QUAD_L1/2
            value=abs(_p(row["odd_tau_a2_q005" if q=="0.005" else "odd_tau_a2_q010"]))
            if value <= 0:
                raise ValueError("Cannot set relative accuracy of zero quadrupole")
            bmax=_p(relative_goal)*value/gq
            xmax=_p(relative_goal)*value/xq
            if 4*bmax >= min(mcheck.values()):
                raise ValueError("Permissible geometry perturbation would cross redshift domain")
            output["derived_sampled_directional"].append({
                "z_rel":z,
                "q_abs":q,
                "abs_odd_tau2":format(value,".20g"),
                "sensitivity_coeff_geometry":format(gq,".20g"),
                "sensitivity_coeff_ion_fractions":format(xq,".20g"),
                "max_uniform_b_error_if_only_geometry_for_10percent":format(bmax,".20g"),
                "max_uniform_ion_fraction_error_if_only_species_for_10percent":format(xmax,".20g"),
                "minimum_end_redshift_log_margin":format(min(mcheck.values()),".20g"),
                "condition_for_joint_budget":"C_b*eps_b + C_x*eps_x <= goal_relative_fraction*abs(odd_tau2)",
            })
    return output


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-cache",type=Path,required=True)
    p.add_argument("--geometry-cache",type=Path,required=True)
    p.add_argument("--direction-result",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=json.loads(args.direction_result.read_text())
    result=campaign_error_budget(args.base_cache,args.geometry_cache,data)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result["derived_sampled_directional"],indent=2))

if __name__=="__main__":
    main()
