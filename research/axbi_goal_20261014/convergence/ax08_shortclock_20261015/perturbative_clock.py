#!/usr/bin/env python3
"""Exact signed-q perturbative physical clock oracle on frozen AX08 backgrounds.

Uses analytic H_FLRW(a), shear source from AX03 lock; no source ODE rerun.
Even proper-time and odd b expansion, with positive alternating-series
remainder and actual completed ZERO/+half/-q saved endpoints.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
from actual_clock_gl4 import load_one
from shortstep import Background,Family

HERE=Path(__file__).resolve().parent
QCASES=("ZERO","SHEAR_HALF_PLUS","SHEAR_MINUS")
AREF=1/21
def physical_coefficients(order=16,n_panel=128):
    bg=Background(Family(0.0))
    nodes,w=np.polynomial.legendre.leggauss(order)
    steps=np.arange(n_panel,dtype=np.float64)
    x=bg.xmax*(steps[:,None]+0.5*(nodes[None,:]+1))/n_panel
    ww=w[None,:]*(bg.xmax/(2*n_panel))
    a=bg.aref*np.exp(x)
    f=bg.h_flrw(a)
    lamb=bg.href*(bg.aref/a)**3/f
    if not (np.isfinite(lamb).all() and np.max(lamb)<=1+1e-13):
        raise RuntimeError("HOLD_LAMBDA_SOURCE_POSITIVITY")
    mean=lambda v:float(np.sum(ww*v))
    coef={
        "t2_s":-mean(lamb**2/f)/2,
        "t4_s":3*mean(lamb**4/f)/8,
        "t6_s":-5*mean(lamb**6/f)/16,
        "t8_remainder_integral_positive_s":35*mean(lamb**8/f)/128,
        "b1":mean(lamb),
        "b3":-mean(lamb**3)/2,
        "b5":3*mean(lamb**5)/8,
        "b7":-5*mean(lamb**7)/16,
        "b9_remainder_integral_positive":35*mean(lamb**9)/128,
        "t_iso_GL_s":mean(1/f),
        "max_lambda":float(np.max(lamb)),
        "physical_source_Href_s":bg.href,
        "absolute_GL_quadrature_order":order,
        "panels":n_panel
    }
    return coef

def prediction(c,q):
    q=float(q)
    dt=q**2*c["t2_s"]+q**4*c["t4_s"]+q**6*c["t6_s"]
    db=q*c["b1"]+q**3*c["b3"]+q**5*c["b5"]+q**7*c["b7"]
    # Alternating series for (1+u)^(-1/2) and u>=0; q² λ² <=1e-4.
    terr=q**8*c["t8_remainder_integral_positive_s"]
    berr=abs(q)**9*c["b9_remainder_integral_positive"]
    return {"clock_shift_s_taylor6":dt,
            "b_shift_taylor7":db,
            "analytic_clock_taylor_remainder_bound_s":terr,
            "analytic_b_taylor_remainder_bound":berr}

def actual(owner):
    coef=physical_coefficients()
    coeff_hi=physical_coefficients(32)
    independent={k:abs(coef[k]-coeff_hi[k]) for k in coef if k not in ("absolute_GL_quadrature_order","panels")}
    arrays={}
    for key in QCASES:
        arr,meta=load_one(owner,key)
        arrays[key]=(arr,meta)
    t0=arrays["ZERO"][0][-1,0]
    r=[]
    for key in QCASES:
        arr,meta=arrays[key]
        q=meta["q_ref"]
        p=prediction(coef,q)
        observed_t=float(arr[-1,0]-t0)
        observed_b=float(arr[-1,2])
        terr=observed_t-p["clock_shift_s_taylor6"]
        berr=observed_b-p["b_shift_taylor7"]
        r.append({
          "case":key,"q_ref":q,"stored_last_a":float(arr[-1,1]),
          "actual_saved_t_shift_s":observed_t,
          "actual_saved_b":observed_b,
          **p,
          "observed_minus_taylor_clock_s":terr,
          "observed_minus_taylor_b":berr,
          "relative_observed_clock_residual_to_effect":abs(terr)/max(abs(observed_t),1e-300),
          "observed_source_saved_vs_analytic_tolerance":"Includes source tables/finite precision; not solely Taylor remainder."
        })
    # The first omitted term is a conditional physical Taylor bound; saved
    # accumulated clock discrepancies are NOT covered by this truncated-series bound.
    # Scale analytic truncation against its physical signed clock effect;
    # a 0.01-second absolute arbitrary threshold is not a source error policy.
    if any(x["analytic_clock_taylor_remainder_bound_s"] >
           1e-10*abs(x["clock_shift_s_taylor6"])
           for x in r if x["q_ref"]!=0.0):
        raise ValueError("HOLD_EXCESS_Q_TAYLOR_RELATIVE_REMAINDER")
    result={
      "schema":"rei.axbi.signed_shear_perturbative_clock_coefficients.v1",
      "status":"EXACT_PARITY_AND_PHYSICAL_BACKGROUND_NUMERIC_ORACLE_COMPUTED",
      "geometry":"non-tilted density-fixed H=sqrt(F²+s²), s=q H_FLRW(aref)*(aref/a)^3",
      "expansion":"1/H=F^-1*(1-0.5 q² λ²+0.375 q^4 λ^4-0.3125 q^6 λ^6+...); db/dx=q λ*(1-0.5 q² λ²+0.375 q^4 λ^4-0.3125 q^6 λ^6+...)",
      "coefficient_units":"t_i in seconds, b_i dimensionless",
      "positive_alternating_remainder_condition":"0<=q² λ² <= 1e-4, valid for studied q_ref <=0.01 and these source x",
      "coefficients":coef,
      "GL16_vs_GL32_coefficient_absolute_differences":independent,
      "saved_case_endpoint_samples":r,
      "source_only_not_coupled_evolution":True,
      "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/perturbative_clock.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",type=Path,required=True)
    args=p.parse_args()
    x=actual(args.owner_root)
    print(json.dumps({"coeff":x["coefficients"],"observed":x["saved_case_endpoint_samples"]},indent=2))
