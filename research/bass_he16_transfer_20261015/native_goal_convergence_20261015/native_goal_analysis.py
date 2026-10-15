"""Read-only AXBI native ZERO/±0.005 short-prefix convergence diagnosis.

Requires six original pinned Rust runs and source identities. Does not infer a
true-error bound, Richardson order, posterior probability, or scientific admission.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
sys.path.insert(0,str(PARENT))
sys.path.insert(0,str(PARENT/"directional_tau_20261015"))
from signed_prefix_tau import taucum, PREC
from directional_tau import directional_moments


CASE_Q={"ZERO":0.0,"SHEAR_HALF_MINUS":-0.005,"SHEAR_HALF_PLUS":0.005}
LEVELS=("baseline","refined")
ZREL=(0.00010,0.00025,0.00040)
SOURCE_SHA="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
BINARY_SHA="32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca"
HE_TO_H=1227/15092
FIELDS=("time_s","a","zbar","b","H_per_s","x_HII","x_HeII","x_HeIII",
        "nH_proper_cm3","ne_proper_cm3","temperature_K","J2_photon_u_eV_per_H")


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(2**20),b""):
            h.update(chunk)
    return h.hexdigest()


def extract_history(run_dir,case,receipt):
    if receipt["status"]!="EXIT_ZERO":
        raise ValueError("Native execution did not finish successfully")
    rec=receipt["result"]
    native=rec["native_return"]
    if native["status"]!="COMPLETE_REPRESENTED_INTERVAL" or native["scientific_admission"]!="NOT_ISSUED":
        raise ValueError("Unexpected science run status/admission")
    if receipt["binary_sha256"]!=BINARY_SHA or rec["source_identity_sha256"]!=SOURCE_SHA:
        raise ValueError("Frozen binary/source identity mismatch")
    if sha(run_dir/"source_identity.txt")!=SOURCE_SHA or sha(run_dir/"config.cfg")!=receipt["config_sha256"]:
        raise ValueError("Native source/config bytes differ from sealed plan")
    path=run_dir/"history.csv"
    if sha(path)!=rec["history_sha256"]:
        raise ValueError("Original native output hash changed")
    data={f:[] for f in FIELDS}
    with path.open("r",newline="") as f:
        reader=csv.DictReader(f)
        if not all(key in reader.fieldnames for key in FIELDS) or \
           "case_id" not in reader.fieldnames or "q_ref" not in reader.fieldnames:
            raise ValueError("Unexpected native history fields")
        for row in reader:
            if row["case_id"]!=case or float(row["q_ref"])!=CASE_Q[case]:
                raise ValueError("Case q identity changed in output")
            for name in FIELDS:
                data[name].append(float(row[name]))
    d={key:np.asarray(values,dtype=np.float64) for key,values in data.items()}
    n=len(d["a"])
    if n!=rec["rows"] or n<3 or not all(x.shape==(n,) and np.isfinite(x).all() for x in d.values()):
        raise ValueError("Native source output missing or nonfinite")
    if np.any(np.diff(d["a"])<=0) or np.any(np.diff(d["time_s"])<=0):
        raise ValueError("Native proper clock and mean-scale not monotone")
    if d["x_HII"].min()<0 or d["x_HII"].max()>1 or d["x_HeII"].min()<0 or \
       d["x_HeIII"].min()<0 or np.any(d["x_HeII"]+d["x_HeIII"]>1):
        raise ValueError("Species composition simplex violated")
    nec=d["nH_proper_cm3"]*(d["x_HII"]+HE_TO_H*(d["x_HeII"]+2*d["x_HeIII"]))
    scale=np.maximum(d["nH_proper_cm3"],1e-300)
    max_census=float(np.max(abs(nec-d["ne_proper_cm3"])/scale))
    if max_census>2e-12:
        raise ValueError("Electron census mismatch in actual native run")
    k=d["nH_proper_cm3"]*d["a"]**3
    max_h_conservation=float(np.max(abs(k/k[0]-1)))
    if max_h_conservation>1e-11:
        raise ValueError("Hydrogen number evolution violates expected homogeneous dilution")
    return d,{
        "rows":n,"sha256":rec["history_sha256"],
        "source_epoch_sha256":rec["source_identity_sha256"],
        "electron_census_max_relative_to_nH":max_census,
        "hydrogen_dilution_max_relative":max_h_conservation,
        "tau_last":None,
    }


def interpolate(a,x,field):
    return np.interp(x,a,field)


def compare_native_levels(coarse,fine):
    if coarse["a"][0]!=fine["a"][0] or coarse["a"][-1]!=fine["a"][-1]:
        raise ValueError("Different target mean-scale endpoints")
    u=np.linspace(np.log(coarse["a"][0]),np.log(coarse["a"][-1]),101)
    ag=np.exp(u)
    names=("time_s","b","H_per_s","x_HII","x_HeII","x_HeIII","nH_proper_cm3",
           "ne_proper_cm3","temperature_K","J2_photon_u_eV_per_H")
    matches={}
    for name in names:
        ref=interpolate(coarse["a"],ag,coarse[name])
        target=interpolate(fine["a"],ag,fine[name])
        delta=target-ref
        matches[name]={
            "abs_diff_endpoint":float(fine[name][-1]-coarse[name][-1]),
            "abs_diff_max_101_lna_samples":float(np.max(abs(delta))),
            "relative_max_to_max_signal":float(np.max(abs(delta))/
              max(np.max(abs(ref)),np.max(abs(target)),1e-300))
        }
    return matches


def linearly_predicted_tau2(z_rel,zero,positive,negative):
    a_observer=zero["a"][-1]
    emit=a_observer/(1.+z_rel)
    if emit<zero["a"][0]:
        raise ValueError("Uncontained reference redshift")
    ne0=np.interp(emit,zero["a"],zero["ne_proper_cm3"])
    H0=np.interp(emit,zero["a"],zero["H_per_s"])
    sigma_c=float(np.longdouble("6.6524587321e-29")*
                  np.longdouble("299792458")*np.longdouble(1000000))
    def expr(d):
        delta=np.interp(emit,d["a"],d["b"])-d["b"][-1]
        return 2*sigma_c*(ne0/H0)*delta
    return {"predicted_plus":expr(positive),"predicted_minus":expr(negative),
            "predicted_odd":(expr(positive)-expr(negative))/2,
            "reference_ne_cm3":ne0,"reference_H_s_inv":H0,"reference_mean_a":emit}


def original_prefix_replay(baseline,original_path,original_sha):
    if sha(original_path)!=original_sha:
        raise ValueError("Original science source CSV changed")
    longest=0
    first_mismatch=None
    with original_path.open("rb") as f1, baseline.open("rb") as f2:
        while True:
            current=f2.readline()
            if not current:break
            orig=f1.readline()
            if current!=orig:
                first_mismatch=longest
                break
            longest+=1
    return {"matching_initial_csv_lines_including_header":longest,
            "first_mismatch_line_zero_index":first_mismatch,
            "original_sha256":original_sha,
            "baseline_sha256":sha(baseline)}


def analyze(exp,original_root,expected_source_hashes,output):
    plan=json.loads((exp/"PLAN.json").read_text())
    run_manifest=json.loads((exp/"RUN_SUMMARY.json").read_text())
    if run_manifest["successful"]!=6 or len(run_manifest["records"])!=6:
        raise ValueError("Six finished native runs not available")
    if plan["source_frozen_binary_sha256"]!=BINARY_SHA or \
       plan["original_source_identity_sha256"]!=SOURCE_SHA:
        raise ValueError("Native source epoch/compiled executable changed")
    records={(r["case"],r["level"]):r for r in run_manifest["records"]}
    datasets={}; reports={}; per_case={}
    for case in CASE_Q:
        for level in LEVELS:
            d,rec=extract_history(exp/"runs"/case/level,case,records[(case,level)])
            tau,_=taucum(d["time_s"],d["ne_proper_cm3"])
            rec["tau_last"]=format(tau[-1],".20g")
            source={"a":d["a"],"t_s":d["time_s"],"ne_cm3":d["ne_proper_cm3"],"tau":tau}
            angular=directional_moments(source,d["b"],z_targets=ZREL,angular_orders=(32,64))
            datasets[(case,level)]=(d,source)
            reports[(case,level)]={"case":case,"level":level,"n":rec,"observer_a":float(d["a"][-1]),
                                   "observer_zbar":float(d["zbar"][-1]),"angular":angular}
        coarse=datasets[(case,"baseline")][0]
        refined=datasets[(case,"refined")][0]
        per_case[case]=compare_native_levels(coarse,refined)
    paired={}
    for level in LEVELS:
        def moment(case,index,key):
            return PREC(reports[(case,level)]["angular"][index]["selected"][key])
        scalar=[]
        for j,z in enumerate(ZREL):
            zerom=moment("ZERO",j,"tau_sky_monopole")
            evenm=(moment("SHEAR_HALF_MINUS",j,"tau_sky_monopole")+
                   moment("SHEAR_HALF_PLUS",j,"tau_sky_monopole"))/2-zerom
            oddq=(moment("SHEAR_HALF_PLUS",j,"tau_legendre_a2")-
                  moment("SHEAR_HALF_MINUS",j,"tau_legendre_a2"))/2
            pred=linearly_predicted_tau2(z,datasets[("ZERO",level)][0],
                datasets[("SHEAR_HALF_PLUS",level)][0],datasets[("SHEAR_HALF_MINUS",level)][0])
            scalar.append({
                "z_relative_to_zbar19p99_observer":z,
                "zero_tau_monopole":format(zerom,".20g"),
                "even_tau_monopole":format(evenm,".20g"),
                "odd_tau_quadrupole":format(oddq,".20g"),
                "linear_analytic_odd_prediction":format(pred["predicted_odd"],".20g"),
                "linear_analytic_odd_rel_error":float(abs(oddq-PREC(pred["predicted_odd"]))/
                                                       max(abs(oddq),PREC("1e-40"))),
                "reference_mean_emission_a":pred["reference_mean_a"],
            })
        paired[level]=scalar
    goal_level_diff=[]
    for i,z in enumerate(ZREL):
        a=paired["baseline"][i]
        b=paired["refined"][i]
        row={"z_rel":z}
        for name in ("zero_tau_monopole","even_tau_monopole","odd_tau_quadrupole"):
            x=PREC(a[name]);y=PREC(b[name])
            row[name+"_difference_refined_minus_baseline"]=format(y-x,".20g")
            row[name+"_relative_to_refined"]=float(abs(y-x)/max(abs(y),PREC("1e-40")))
        goal_level_diff.append(row)
    control={}
    for case in CASE_Q:
        kind="flrw" if case=="ZERO" else "paired"
        original=original_root/kind/"32d11e733155"/case/"history.csv"
        baseline=exp/"runs"/case/"baseline"/"history.csv"
        control[case]=original_prefix_replay(baseline,original,expected_source_hashes[case])
    result={
        "schema":"he18.axbi.native_goal_convergence.v1",
        "status":"EMPIRICAL_NATIVE_REFINEMENT_EXECUTED_NONAUTHORITATIVE",
        "binary_sha256":BINARY_SHA,"source_epoch_sha256":SOURCE_SHA,
        "probe_end_zbar":19.99,
        "local_targets":{"baseline":1e-5,"refined":3e-6},
        "cases":CASE_Q,
        "source_results":{f"{case}_{level}":reports[(case,level)] for case in CASE_Q for level in LEVELS},
        "paired_level_fields":per_case,
        "signed_observables_by_level":paired,
        "signed_goal_refinement_difference":goal_level_diff,
        "original_baseline_prefix_identity":control,
        "limit":"Two-tolerance observed differences do not certify true global errors or asymptotic order; no physical source/microphysics/model-error bound",
        "publication_admission":"HOLD",
        "native_subagents":"NOT_RUN"
    }
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n")
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--experiment",type=Path,required=True)
    p.add_argument("--original-root",type=Path,required=True)
    p.add_argument("--original-prefix-receipt",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    obj=json.loads(args.original_prefix_receipt.read_text())
    expected={k:v["history_sha256"] for k,v in obj["cases"].items() if k in CASE_Q}
    result=analyze(args.experiment,args.original_root,expected,args.out)
    print(json.dumps({
        "status":result["status"],
        "goal_differences":result["signed_goal_refinement_difference"],
        "coarse_fine_case_xHII":[[name,r["x_HII"]["abs_diff_endpoint"]] for name,r in result["paired_level_fields"].items()],
        "original_baseline_control":result["original_baseline_prefix_identity"]
    },indent=2))


if __name__=="__main__":
    main()
