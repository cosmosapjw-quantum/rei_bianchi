"""Signed-pair correlated-versus-uncorrelated native error counterfactual.

This is a diagnostic, not independent physical source perturbation or an ODE bound.
Both q=+/-0.005 solver histories must be source-identity compatible and have the
same accepted-step a,t grids within each tolerance level.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np

PARENT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PARENT))
sys.path.insert(0,str(PARENT/"directional_tau_20261015"))
from native_goal_analysis import extract_history
from signed_prefix_tau import taucum,PREC
from directional_tau import directional_moments

PAIRS=("SHEAR_HALF_PLUS","SHEAR_HALF_MINUS")
ZREL=(0.0001,0.00025,0.0004)


def load(experiment,level):
    all_receipts=json.loads((experiment/"RUN_SUMMARY.json").read_text())
    records=all_receipts.get("records",all_receipts.get("receipts"))
    bycase={r["case"]:r for r in records}
    return {case:extract_history(experiment/"runs"/case/level,case,bycase[case])[0]
            for case in PAIRS}


def odd_j2_tau(dplus,dminus,z):
    def goal(d):
        tau,_=taucum(d["time_s"],d["ne_proper_cm3"])
        source={"a":d["a"],"t_s":d["time_s"],
                "ne_cm3":d["ne_proper_cm3"],"tau":tau}
        return PREC(directional_moments(source,d["b"],z_targets=(z,),angular_orders=(64,))
                    [0]["selected"]["tau_legendre_a2"])
    return (goal(dplus)-goal(dminus))/2


def check_pair_grid(d):
    a=d[PAIRS[0]];b=d[PAIRS[1]]
    err={}
    for field in ("a","time_s"):
        err[field+"_abs_max"]=float(np.max(abs(a[field]-b[field])))
        if err[field+"_abs_max"]!=0:
            raise ValueError("Signed pair does not share exact mean-a/proper-time history")
    return err


def analyze(exp_refined,exp_ultra):
    refined=load(exp_refined,"refined")
    ultra=load(exp_ultra,"ultra")
    parity={"refined":check_pair_grid(refined),"ultra":check_pair_grid(ultra)}
    a_ref=refined[PAIRS[0]]["a"]
    a_ultra=ultra[PAIRS[0]]["a"]
    changes={case:np.interp(a_ref,a_ultra,ultra[case]["ne_proper_cm3"])
             -refined[case]["ne_proper_cm3"] for case in PAIRS}
    even=(changes[PAIRS[0]]+changes[PAIRS[1]])/2
    odd=(changes[PAIRS[0]]-changes[PAIRS[1]])/2
    nh=refined[PAIRS[0]]["nH_proper_cm3"]
    masks={
       "max_abs_delta_ne_even_cm3":float(np.max(abs(even))),
       "max_abs_delta_ne_odd_cm3":float(np.max(abs(odd))),
       "max_abs_delta_ne_even_over_nH":float(np.max(abs(even)/nh)),
       "max_abs_delta_ne_odd_over_nH":float(np.max(abs(odd)/nh)),
       "max_abs_odd_to_even_ratio":float(np.max(abs(odd))/max(np.max(abs(even)),1e-300))
    }
    revised_both={}
    revised_plus={}
    for case in PAIRS:
        d=refined[case]
        revised_both[case]={**d,"ne_proper_cm3":d["ne_proper_cm3"]+even}
        revised_plus[case]={**d,"ne_proper_cm3":d["ne_proper_cm3"]+
                            (even if case==PAIRS[0] else 0.)}
    rows=[]
    for z in ZREL:
        native_ref=odd_j2_tau(refined[PAIRS[0]],refined[PAIRS[1]],z)
        native_ultra=odd_j2_tau(ultra[PAIRS[0]],ultra[PAIRS[1]],z)
        common=odd_j2_tau(revised_both[PAIRS[0]],revised_both[PAIRS[1]],z)-native_ref
        plus_only=odd_j2_tau(revised_plus[PAIRS[0]],revised_plus[PAIRS[1]],z)-native_ref
        native_delta=native_ultra-native_ref
        rows.append({
            "z_rel":z,"odd_native_refined":format(native_ref,".20g"),
            "odd_native_ultra":format(native_ultra,".20g"),
            "observed_native_goal_change":format(native_delta,".20g"),
            "even_ne_error_applied_to_both_signed_histories_change":format(common,".20g"),
            "same_ne_error_applied_to_plus_only_change":format(plus_only,".20g"),
            "correlated_common_error_suppression_ratio":float(abs(common)/max(abs(plus_only),PREC("1e-40"))),
            "fraction_of_native_change_predicted_by_frozen_geometry_common_ne":float(common/native_delta)
                      if abs(native_delta)>PREC("1e-40") else None
        })
    return {
        "schema":"he18.axbi.native_signed_error_correlation.v1",
        "status":"NUMERICAL_COUNTERFACTUAL_NOT_SOURCE_ODE_ERROR_CERTIFICATE",
        "target_refined":3e-6,"target_ultra":1e-6,
        "native_case_source_hashes":{case:{
            "refined":refined[case]["ne_proper_cm3"].size,
            "ultra":ultra[case]["ne_proper_cm3"].size} for case in PAIRS},
        "exact_signed_grid_parity":parity,
        "native_electron_error_common_odd":masks,
        "counterfactual":rows,
        "caveat":"This counterfactual freezes background geometry and clock; plus-only perturbation breaks signed source symmetry. Not a causal physical decomposition or true-error estimate."
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--refined",type=Path,required=True)
    p.add_argument("--ultra",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    r=analyze(args.refined,args.ultra)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
