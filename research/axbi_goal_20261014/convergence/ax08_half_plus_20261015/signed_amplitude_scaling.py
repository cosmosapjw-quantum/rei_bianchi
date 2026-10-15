#!/usr/bin/env python3
"""Two-amplitude signed response checks on the actual 200k-step AX08 prefix.

This tests small-q scaling consistency, NOT evolution/time-energy-angle
convergence; it does not deliver a certified shear-response detection.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
DEF=HERE/"signed_prefix_parity.py"
A0=1/21

def module(owner):
    spec=importlib.util.spec_from_file_location("ax08_prefix_parity",DEF)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.ROOT=owner
    m.BASE=owner/"research/axbi_goal_20261014/runs"
    return m

def actual(owner):
    m=module(owner)
    cases={k:m.load_case(k,v) for k,v in m.REL.items()}
    if len({x["files"]["source_identity_sha256"] for x in cases.values()})!=1:
        raise RuntimeError("HOLD_UNMATCHED_IMMUTABLE_SOURCE")
    final=min(v["last_a"] for v in cases.values())
    grid=np.exp(np.linspace(math.log(A0),math.log(final),501))
    grid[0]=A0;grid[-1]=final
    values={}
    for case,data in cases.items():
        a=data["arr"][:,0]
        if a[0]>A0 or a[-1]<final:
            raise RuntimeError("HOLD_COMMON_LOG_A_EXTRAPOLATION")
        values[case]=[np.interp(grid,a,data["arr"][:,j]) for j in (1,2,3)]
    output={}
    h=.01
    for j,name in enumerate(m.COLUMNS[1:]):
        o0=values["ZERO"][j]
        p=values["SHEAR_PLUS"][j]; neg=values["SHEAR_MINUS"][j]
        hp=values["SHEAR_HALF_PLUS"][j]; hm=values["SHEAR_HALF_MINUS"][j]
        even=(p+neg)*.5-o0
        evenhalf=(hp+hm)*.5-o0
        odd=(p-neg)*.5
        oddhalf=(hp-hm)*.5
        def witness(a,scale):
            k=int(np.argmax(abs(a)))
            return {"signed_at_max":float(a[k]),"abs_max":float(abs(a[k])),
                    "scale":scale,"zbar_at_max":float(1/grid[k]-1),
                    "ln_a_at_max":float(math.log(grid[k])),"sample":k}
        # Pointwise even q²/odd q finite-amplitude deviation.
        q4=even-4*evenhalf
        q3=odd-2*oddhalf
        even_scale=1.0 - (np.max(abs(q4))/max(np.max(abs(even)),1e-300))
        odd_scale=1.0 - (np.max(abs(q3))/max(np.max(abs(odd)),1e-300))
        imax=int(np.argmax(abs(even)))
        jmax=int(np.argmax(abs(odd)))
        output[name]={
          "big_even":witness(even,h),"half_even":witness(evenhalf,h/2),
          "big_odd":witness(odd,h),"half_odd":witness(oddhalf,h/2),
          "even_pointwise_max_abs_Eq_minus_4_Ehalf":float(np.max(abs(q4))),
          "odd_pointwise_max_abs_Oq_minus_2_Ohalf":float(np.max(abs(q3))),
          "relative_even_scaling_defect":float(1-even_scale),
          "relative_odd_scaling_defect":float(1-odd_scale),
          "even_ratio_at_big_peak":float(even[imax]/evenhalf[imax]) if evenhalf[imax]!=0 else None,
          "odd_ratio_at_big_peak":float(odd[jmax]/oddhalf[jmax]) if oddhalf[jmax]!=0 else None,
          "even_C2_at_peak":float((16*evenhalf[imax]-even[imax])/(3*h*h)),
          "odd_C1_at_peak":float((8*oddhalf[jmax]-odd[jmax])/(3*h)),
          "roundoff_warning": "Ratios near zero especially odd scalar may be numerical roundoff, not an observable scaling law."
        }
    return {
      "schema":"rei.axbi.signed_amplitude_scaling.v1",
      "status":"EXECUTED_SCOPED_REAL_PREFIX_AMPLITUDE_CHECK",
      "representation":"200001 accepted history rows per 5 real cases; 501 common log(a) points",
      "q_ref":[0,-h/2,h/2,-h,h],
      "even_formula":"E(h)=C2 h²+C4 h⁴+O(h⁶), coefficients are only formal within numerical uncertainty",
      "odd_formula":"O(h)=C1 h+C3 h³+O(h⁵), coefficients are only formal within numerical uncertainty",
      "signed_q_error":"UNKNOWN_NOSCIRUNTIME_REFINEMENT","claim_status":"EXPLORATORY_NOT_RESOLVED",
      "source_identities":{k:v["files"] for k,v in cases.items()},
      "observables":output,
      "scientific_admission":"NOT_ISSUED"
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--owner-root",type=Path,required=True)
    args=parser.parse_args()
    data=actual(args.owner_root)
    (HERE/"signed_amplitude_scaling_result.json").write_text(json.dumps(data,indent=2)+"\n")
    for key,val in data["observables"].items():
        print(key,"even_ratio_at_peak",val["even_ratio_at_big_peak"],
              "even_q4_relative",val["relative_even_scaling_defect"],
              "odd_ratio_at_peak",val["odd_ratio_at_big_peak"],
              "odd_q3_relative",val["relative_odd_scaling_defect"])
