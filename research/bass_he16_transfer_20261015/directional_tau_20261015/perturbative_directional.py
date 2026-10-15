"""First-order directional tau quadrupole predicted independently from endpoint data.

For normal LRS BI:
delta log(a_e)=(1-3mu_o^2)*(b_e-b_o), hence a2_tau =
    2 (sigma_T c n_e/H)_at mean-emission (b_e-b_o) + O(b^2).
This is a local linearization at fixed observer-local directional redshift, with
ionization and proper clock held to the ZERO source for the derivative.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from clock_decompose_signed import read_caches
from directional_tau import read_geometry, KAPPA, PREC, TARGET_ZREL
from signed_prefix_tau import EXPECTED_Q


def predict(data: dict, b: dict, actual: dict):
    z=data["ZERO"]
    ao=PREC(z["a"][-1])
    u=np.log(z["a"])
    cases={}
    for target in TARGET_ZREL:
        abar=float(ao/PREC(1+target))
        j=int(np.searchsorted(z["a"],abar,side="right")-1)
        if j<0 or j>=len(u)-1:
            raise ValueError("Emission time outside ZERO history")
        ubar=np.log(abar)
        frac=(ubar-u[j])/(u[j+1]-u[j])
        ne=PREC(z["ne_cm3"][j])+PREC(frac)*PREC(z["ne_cm3"][j+1]-z["ne_cm3"][j])
        H=(PREC(u[j+1])-PREC(u[j]))/(PREC(z["t_s"][j+1])-PREC(z["t_s"][j]))
        kappa_over_H=KAPPA*ne/H
        one={"z_rel":target,"mean_emission_a":abar,
             "ZERO_ne_cm3":format(ne,".18g"),"ZERO_H_per_s":format(H,".18g"),
             "kappa_over_H":format(kappa_over_H,".18g"),
             "signed":{}}
        for q,neg,pos in ((.005,"SHEAR_HALF_MINUS","SHEAR_HALF_PLUS"),
                          (.01,"SHEAR_MINUS","SHEAR_PLUS")):
            diff=[]
            for case in (pos,neg):
                bq=np.interp(ubar,np.log(data[case]["a"]),b[case])
                diff.append(PREC(bq)-PREC(b[case][-1]))
            # each signed case's first-order coefficient a2=2 kappa/H Delta b.
            odd_pred=kappa_over_H*(diff[0]-diff[1])
            measured_row=next(v for v in actual["signed_summary"] if v["z_rel"]==target)
            measured=PREC(measured_row["odd_tau_a2_q005" if q==.005 else "odd_tau_a2_q010"])
            one["signed"][str(q)]={
                "odd_tau_a2_predicted_linear":format(odd_pred,".18g"),
                "odd_tau_a2_measured":format(measured,".18g"),
                "relative_linearization_discrepancy":float(abs(measured-odd_pred)/abs(measured)),
                "source_b_emission_minus_observer_plus":format(diff[0],".18g"),
                "source_b_emission_minus_observer_minus":format(diff[1],".18g"),
            }
        cases[str(target)]=one
    return {
        "schema":"he18.axbi.directional_tau_linear_analytic_check.v1",
        "scope":"source-scoped first-order formula, matched mean-a emission and normal observer",
        "status":"DERIVED_AND_NUMERICALLY_CHECKED_NOT_CERTIFIED_ODE",
        "cases":cases,
        "assumption":"frozen ZERO normal ne/H for linear redshift perturbation; angular coefficient a2 normalized as (5/2) integral P2(mu) tau dmu",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base-cache",type=Path,required=True)
    p.add_argument("--geometry-cache",type=Path,required=True)
    p.add_argument("--directional",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data,man,_=read_caches(args.base_cache)
    geom=read_geometry(args.geometry_cache,args.base_cache,man)
    report=predict(data,geom,json.loads(args.directional.read_text()))
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
