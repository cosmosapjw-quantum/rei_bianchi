"""Third-level Cauchy diagnostic for original six native runs plus one ultra tier.

A three-tolerance goal difference is not a certified solution error or formal
Richardson order. Original source and archived runs remain immutable.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.path.insert(0,str(HERE.parent/"directional_tau_20261015"))
from native_goal_analysis import (CASE_Q,ZREL,extract_history,compare_native_levels,
                                  linearly_predicted_tau2)
from signed_prefix_tau import PREC,taucum
from directional_tau import directional_moments

def third_level(exp_old,exp_third,first,output):
    previous=json.loads(first.read_text())
    if previous["status"]!="EMPIRICAL_NATIVE_REFINEMENT_EXECUTED_NONAUTHORITATIVE":
        raise ValueError("Unexpected previous native result")
    frozen=json.loads((exp_third/"PLAN.json").read_text())
    data=json.loads((exp_third/"RUN_SUMMARY.json").read_text())
    if data["successes"]!=3 or len(data["receipts"])!=3:
        raise ValueError("Three additional native runs not all successful")
    if frozen["source_sha256"]!=previous["source_epoch_sha256"] or \
       frozen["binary_sha256"]!=previous["binary_sha256"]:
        raise ValueError("Third-tier source identity mismatched")
    receipts={r["case"]:r for r in data["receipts"]}
    loaded={};result_per={};level3={}
    for case in CASE_Q:
        original_meta=json.loads((exp_old/"RUN_SUMMARY.json").read_text())
        refined=next(r for r in original_meta["records"] if r["case"]==case and r["level"]=="refined")
        refined_dir=exp_old/"runs"/case/"refined"
        ultra_dir=exp_third/"runs"/case/"ultra"
        old_d,old_rec=extract_history(refined_dir,case,refined)
        ultra_d,ultra_rec=extract_history(ultra_dir,case,receipts[case])
        result_per[case]={
            "refined_to_ultra":compare_native_levels(old_d,ultra_d),
            "ultra_report":ultra_rec,
            "refined_report":old_rec
        }
        tau,_=taucum(ultra_d["time_s"],ultra_d["ne_proper_cm3"])
        inp={"a":ultra_d["a"],"t_s":ultra_d["time_s"],
             "ne_cm3":ultra_d["ne_proper_cm3"],"tau":tau}
        ang=directional_moments(inp,ultra_d["b"],z_targets=ZREL,angular_orders=(32,64))
        loaded[case]=ultra_d
        level3[case]={"history_sha256":ultra_rec["sha256"],
                      "tau_trap":format(tau[-1],".20g"),
                      "angular":ang}
    obs=[]
    for j,z in enumerate(ZREL):
        def v(case,key):
            return PREC(level3[case]["angular"][j]["selected"][key])
        base=v("ZERO","tau_sky_monopole")
        even=(v("SHEAR_HALF_PLUS","tau_sky_monopole")+
              v("SHEAR_HALF_MINUS","tau_sky_monopole"))/2-base
        odd=(v("SHEAR_HALF_PLUS","tau_legendre_a2")-
             v("SHEAR_HALF_MINUS","tau_legendre_a2"))/2
        pred=linearly_predicted_tau2(z,loaded["ZERO"],loaded["SHEAR_HALF_PLUS"],loaded["SHEAR_HALF_MINUS"])
        obs.append({
            "z_rel":z,
            "zero_tau_monopole":format(base,".20g"),
            "even_tau_monopole":format(even,".20g"),
            "odd_tau_quadrupole":format(odd,".20g"),
            "linear_prediction_odd_tau_quadrupole":format(pred["predicted_odd"],".20g"),
            "linear_analytic_relative_discrepancy":float(abs(odd-PREC(pred["predicted_odd"]))/
                                                              max(abs(odd),PREC("1e-40")))
        })
    differences=[]
    for j,z in enumerate(ZREL):
        old=previous["signed_observables_by_level"]["baseline"][j]
        mid=previous["signed_observables_by_level"]["refined"][j]
        fin=obs[j]
        v={"z_rel":z}
        for key in ("zero_tau_monopole","even_tau_monopole","odd_tau_quadrupole"):
            d12=PREC(mid[key])-PREC(old[key])
            d23=PREC(fin[key])-PREC(mid[key])
            v[key+"_delta_baseline_to_refined"]=format(d12,".20g")
            v[key+"_delta_refined_to_ultra"]=format(d23,".20g")
            v[key+"_abs_diff_attenuation_ratio"]=float(abs(d23)/max(abs(d12),PREC("1e-40")))
            v[key+"_ultra"]=fin[key]
            v[key+"_relative_ultra_difference"]=float(abs(d23)/max(abs(PREC(fin[key])),PREC("1e-40")))
        differences.append(v)
    metrics={}
    for case in CASE_Q:
        old=previous["paired_level_fields"][case]
        new=result_per[case]["refined_to_ultra"]
        metrics[case]={key:{
            "delta_level1_to_level2":old[key]["abs_diff_endpoint"],
            "delta_level2_to_level3":new[key]["abs_diff_endpoint"],
            "endpoint_difference_ratio":abs(new[key]["abs_diff_endpoint"])/
                                         max(abs(old[key]["abs_diff_endpoint"]),1e-300)}
            for key in ("x_HII","x_HeII","x_HeIII","b","ne_proper_cm3","time_s","temperature_K","J2_photon_u_eV_per_H")}
    output_data={
        "schema":"he18.axbi.three_native_tolerance_goal_cauchy.v1",
        "status":"THREE_EXPLORATORY_NATIVE_LEVELS_COMPLETED_NO_CERTIFIED_GLOBAL_ERROR",
        "binary_sha256":frozen["binary_sha256"],
        "source_epoch_sha256":frozen["source_sha256"],
        "tolerance_sequence":[1e-5,3e-6,1e-6],
        "zbar_emission_start":20.,"zbar_observer":19.99,
        "relative_redshift_targets":ZREL,
        "sampled_goal_difference_attenuation":differences,
        "per_case_state_endpoint_attentuation":metrics,
        "ultra_angular_results":level3,
        "original_level2_level3_readback":result_per,
        "constraints":"No power-law convergence order assumed. Three-level Cauchy ratio is not proof of true solution, model or interpolation accuracy.",
        "scientific_admission":"HOLD",
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(output_data,indent=2)+"\n")
    return output_data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-experiment",type=Path,required=True)
    p.add_argument("--third-experiment",type=Path,required=True)
    p.add_argument("--previous-analysis",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    summary=third_level(args.original_experiment,args.third_experiment,args.previous_analysis,args.out)
    print(json.dumps({
        "status":summary["status"],
        "sampled_goals":summary["sampled_goal_difference_attenuation"],
        "x_HII_endpoint":{k:v["x_HII"] for k,v in summary["per_case_state_endpoint_attentuation"].items()}
    },indent=2))
