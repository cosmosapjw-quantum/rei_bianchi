#!/usr/bin/env python3
"""Actual AX08 free-streamed photon-number and energy quadrupole invariant.

Separate local-current-angle GL64 quadrature and stable expm1 cancellation.
The original AX08 driver and all stored science files remain unchanged.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

RUNS={
  "ZERO":"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001",
  "SHEAR_HALF_PLUS":"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002",
}
H0=67.4e3/3.0856775814913673e22
G_SI=6.67430e-11
C_SI=299792458.0
OM_R=9.2e-5
PREF=3*H0*H0*C_SI*C_SI*OM_R/(8*math.pi*G_SI)
NROWS=312238

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as file:
        for part in iter(lambda:file.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def bound_case(owner,case):
    directory=owner/RUNS[case]
    receipt=json.loads((directory/"COMPOSITION_RECEIPT.json").read_text())
    if receipt.get("status")!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION":
        raise RuntimeError("HOLD_NOT_COMPOSED")
    hashes={}
    for name in ("history.csv","feedback.csv"):
        digest=sha(directory/name)
        if digest!=receipt["output_sha256"].get(name):
            raise RuntimeError("HOLD_FROZEN_SCIENCE_FILE_IDENTITY:"+name)
        hashes[name]=digest
    history=np.loadtxt(directory/"history.csv",delimiter=",",skiprows=1,
                       usecols=(3,4,6),dtype=np.float64,ndmin=2)
    feedback=np.loadtxt(directory/"feedback.csv",delimiter=",",skiprows=1,
                        usecols=(1,2,6),dtype=np.float64,ndmin=2)
    if history.shape!=(NROWS,3) or feedback.shape!=(NROWS,3):
        raise RuntimeError("HOLD_INCOMPLETE_OR_BAD_SAVED_HISTORY")
    t,a,b=history.T
    tf,af,correction=feedback.T
    if not (np.array_equal(t,tf) and np.array_equal(a,af)):
        raise RuntimeError("HOLD_TIME_OR_SCALE_MISMATCH")
    if not (np.all(np.isfinite(history)) and np.all(np.isfinite(feedback))
            and a[0]==1/21 and a[-1]==.2 and t[0]==0
            and np.all(np.diff(t)>0) and np.all(np.diff(a)>0)):
        raise RuntimeError("HOLD_SCIENCE_CLOCK_DOMAIN")
    return a,b,correction,hashes

def check(a,b,corr,nmu):
    x,w=np.polynomial.legendre.leggauss(nmu)
    w=w/2.
    mu2=x*x
    max_number=0.
    max_energy=0.
    max_series=0.
    max_b=0.
    idx_energy=-1
    endpoint_energy=0.
    endpoint_pred=0.
    for j in range(0,len(a),2048):
        s=slice(j,min(len(a),j+2048))
        bb=b[s,None]
        # Stable around exact isotropy.
        pert=(1-mu2[None,:])*np.expm1(-2*bb)+mu2[None,:]*np.expm1(4*bb)
        ell=np.log1p(pert)
        number_change=np.sum(np.expm1(-1.5*ell)*w[None,:],axis=1)
        energy_change=np.sum(np.expm1(-2*ell)*w[None,:],axis=1)
        observed_change=corr[s]/(PREF/a[s]**4)
        error=abs(observed_change-energy_change)
        local=int(np.argmax(error))
        if float(error[local])>max_energy:
            max_energy=float(error[local])
            idx_energy=j+local
        max_number=max(max_number,float(np.max(abs(number_change))))
        max_b=max(max_b,float(np.max(abs(b[s]))))
        series=8*b[s]**2/5-16*b[s]**3/21
        max_series=max(max_series,float(np.max(abs(energy_change-series))))
        endpoint_energy=float(energy_change[-1])
        endpoint_pred=float(observed_change[-1])
    return {"max_abs_photon_number_ratio_minus_one":max_number,
            "max_abs_energy_ratio_difference":max_energy,
            "max_abs_b":max_b,
            "max_abs_energy_series_cubic_remainder":max_series,
            "energy_witness_row":idx_energy,
            "endpoint_gl_energy_correction_over_rho_iso":endpoint_energy,
            "endpoint_saved_energy_correction_over_rho_iso":endpoint_pred,
            "pass_photon_number":max_number<1e-12,
            "pass_saved_energy":max_energy<1e-10}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner-root",required=True,type=Path)
    ap.add_argument("--order",default=64,type=int)
    args=ap.parse_args()
    if args.order not in (32,64,128):
        raise SystemExit("order must be 32/64/128")
    results={}
    for case in RUNS:
        a,b,corr,h=bound_case(args.owner_root,case)
        results[case]={"inputs_sha256":h,"actual_rows":len(a),**check(a,b,corr,args.order)}
    data={"schema":"rei.axbi.phase_space_number_energy_v1",
          "scope":"initially isotropic collisionless massless background radiation",
          "geometry":"a_perp=a exp(-b), a_parallel=a exp(2b), metric (-,+,+,+)",
          "theory_number":"(1/2) Integral[-1,1] D(mu,b)^(-3/2) dmu == 1 exactly",
          "theory_energy":"rho/rho_iso=1+8b^2/5-16b^3/21+O(b^4)",
          "D":"(1-mu^2)exp(-2b)+mu^2 exp(4b)",
          "quadrature":"local-direction GL"+str(args.order)+", stable expm1/log1p",
          "source_model_change":"NONE","owner_science_start_count":0,
          "result_status":"NUMERICALLY_CHECKED" if all(z["pass_photon_number"] and z["pass_saved_energy"] for z in results.values()) else "HOLD_MISMATCH",
          "scientific_admission":"NOT_ISSUED",
          "results":results}
    out=Path(__file__).resolve().parent/"number_energy_invariant_result.json"
    out.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({k:{"max_number_error":v["max_abs_photon_number_ratio_minus_one"],
          "max_energy_error":v["max_abs_energy_ratio_difference"],
          "max_series_remainder":v["max_abs_energy_series_cubic_remainder"]}
          for k,v in results.items()},indent=2))
    if data["result_status"]!="NUMERICALLY_CHECKED":
        raise SystemExit(2)
if __name__=="__main__":
    main()
