#!/usr/bin/env python3
"""SHA-provenant real AX08 minus full-history and clock decomposition.

Reuses tested PR119 ZERO/HALF_PLUS Python census/clock routines verbatim.
No solver or modified science input; scientific signal is not AX11-admitted.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"ax08_clock_census_20261015"))
import clock_census as cc

CASE="SHEAR_MINUS"
REL="research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001"
OLD="d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185"
NEW="4de69c1e68ebd395fe2d0b5580d901b9a82bde86cadbd11bdd07e5ad2042b4a1"
def require(predicate,reason):
    if not predicate:raise ValueError(reason)

def bind_minus(root):
    d=root/REL
    receipt=json.loads((d/"COMPOSITION_RECEIPT.json").read_text())
    case=json.loads((d/"COMPLETED_CASE_INPUT.json").read_text())
    require(receipt["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION",
            "HOLD_COMPOSITION_NOT_COMPLETE")
    require(receipt["scientific_admission"]=="NOT_ISSUED","HOLD_UNSUPPORTED_SCIENTIFIC_APPROVAL")
    require(case["id"]==CASE and case["clock_origin"]=="elapsed proper seconds since zbar20",
            "HOLD_CLOCK_OR_CASE")
    epochs=case["source_epochs"]
    require(epochs["predecessor"]==OLD and epochs["current"]==NEW
            and epochs["compatibility"]["relation"]=="REVIEWED_RESOURCE_ONLY",
            "HOLD_SCIENCE_SOURCE_EPOCHS")
    for name,n in (("history.csv",312238),("feedback.csv",312238),
                   ("abundances.csv",6*312238),("ledgers.csv",27*312238)):
        require(receipt["row_counts"][name]["composed_rows"]==n,
                "HOLD_CENSUS_ROWS:"+name)
    require(receipt["row_counts"]["history.csv"]["boundary_rows_removed"]==1,
            "HOLD_DUPLICATE_BOUNDARY")
    verified={}
    for role,name in (("history","history.csv"),("abundances","abundances.csv"),
                      ("config","config.cfg"),("source_identity","source_identity.txt"),
                      ("terminal","RETURN.txt")):
        record=case[role]
        path=root/record["path"]
        require(path.resolve()==(d/name).resolve(),"HOLD_EXTERNAL_SCIENCE_FILE")
        sha=cc.digest(path)
        require(sha==record["sha256"]==receipt["output_sha256"][name],
                "HOLD_CHANGED_COMPLETED_BYTES:"+name)
        verified[role]={"path":record["path"],"sha256":sha}
    require(verified["source_identity"]["sha256"]==NEW,"HOLD_COMPILED_SOURCE_EPOCH")
    return verified,receipt

def analyze(root,census=True,nodes=4097):
    m,_=bind_minus(root)
    known=cc.bindings(root)
    zero,_=cc.history(Path(known["ZERO"]["history"]["path"]))
    plus,_=cc.history(Path(known["SHEAR_HALF_PLUS"]["history"]["path"]))
    minus,read_s=cc.history(root/m["history"]["path"])
    count=cc.census(root/m["abundances"]["path"],minus,CASE) if census else None
    comparisons={}
    curves={}
    for key,candidate in (("SHEAR_MINUS",minus),("SHEAR_HALF_PLUS",plus)):
        r,a,data,mask,_,_=cc.compare(zero,candidate,nodes)
        r["scope"]="ZERO vs "+key+" full completed represented history; source-scoped"
        comparisons[key]=r
        curves[key]={"a":a,"data":data}
    a=np.exp(np.linspace(np.log(zero[0,1]),np.log(zero[-1,1]),nodes))
    a[0]=zero[0,1];a[-1]=zero[-1,1]
    mixed={}
    for label,col in (("x_HII",4),("x_HeII",6),("temperature_K",10),("J2_photon_u_eV_per_H",11)):
        z=np.interp(a,zero[:,1],zero[:,col])
        d=np.interp(a,minus[:,1],minus[:,col])-z
        p=np.interp(a,plus[:,1],plus[:,col])-z
        factor=-2 if label=="J2_photon_u_eV_per_H" else 4
        peak=int(np.argmax(abs(d)))
        defect=float(np.max(abs(d-factor*p)))
        amp=max(float(np.max(abs(d))),1e-300)
        mixed[label]={"physics_assumed_leading_parity":"q" if factor==-2 else "q_squared",
            "expected_unequal_amplitude_factor":factor,
            "maximum_abs_minus_response":float(np.max(abs(d))),
            "maximum_abs_plus_half_response":float(np.max(abs(p))),
            "fixed_a_peak_zbar":float(1/a[peak]-1),
            "ratio_at_common_minus_peak":float(d[peak]/p[peak]) if p[peak] else None,
            "max_abs_scaling_residual":defect,
            "relative_scaling_residual":defect/amp,
            "scientific_error":"UNKNOWN_NO_AX11"}
    result={
      "schema":"rei.axbi.minus_full_clock_census.v1",
      "status":"COMPLETED_MINUS_SAVED_HISTORY_EXPLORATORY_PHYSICS",
      "source":"PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1",
      "physics_clock":"elapsed proper time since common zbar20; fixed a and fixed t distinct",
      "source_relation":"REVIEWED_RESOURCE_ONLY",
      "full_case_sha256":m,
      "reference_case_sha256":{k:{r:x["sha256"] for r,x in v.items()} for k,v in known.items()},
      "actual_minus_rows":312238,"minus_read_s":read_s,
      "minus_census":count,
      "matched_ln_a_points":nodes,
      "comparisons":comparisons,
      "unequal_sign_amplitude_exploration":mixed,
      "AX11_error":"NOT_MEASURED","scientific_admission":"NOT_ISSUED"}
    return result,zero,minus,plus,curves

def write_plots(result,Z,M,P,curves,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out.mkdir(parents=True,exist_ok=False)
    (out/"MINUS_SCIENCE_RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    fig,ax=plt.subplots(3,1,figsize=(10,9),constrained_layout=True)
    for data,label in ((Z,"ZERO"),(M,"-0.01"),(P,"+0.005")):
        loc=np.linspace(0,len(data)-1,2300,dtype=int)
        for a,j in zip(ax,(4,6,10)):
            a.plot(data[loc,2],data[loc,j],label=label)
    for a,t in zip(ax,("x_HII","x_HeII","Gas temperature [K]")):
        a.set_ylabel(t);a.set_xlabel("Mean redshift");a.invert_xaxis();a.grid(alpha=.25);a.legend(fontsize=8)
    fig.suptitle("AX08 actual complete histories (conditional MD14, numerical error unknown)")
    fig.savefig(out/"three_complete_HHe_Tgas.png",dpi=165);plt.close(fig)
    cur=curves["SHEAR_MINUS"]
    a=cur["a"]
    fig,ax=plt.subplots(3,2,figsize=(11,9),constrained_layout=True)
    for panel,(name,(fixed_time,fixed_scale,clock)) in zip(ax.flat,cur["data"].items()):
        panel.plot(1/a-1,fixed_time,label="fixed proper time")
        panel.plot(1/a-1,fixed_scale,label="fixed mean scale",linestyle="--")
        panel.plot(1/a-1,clock,label="FLRW clock drift",linestyle=":")
        panel.invert_xaxis();panel.set_title(name);panel.set_xlabel("Mean redshift")
        panel.grid(alpha=.25);panel.legend(fontsize=7)
    fig.suptitle("AX08 q=-0.01 versus FLRW: exact algebraic clock split, no AX11 bound")
    fig.savefig(out/"minus_clock_decomposition.png",dpi=155);plt.close(fig)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--no-census",action="store_true")
    args=ap.parse_args()
    result,Z,M,P,curves=analyze(args.owner_root,not args.no_census)
    write_plots(result,Z,M,P,curves,args.output)
    m=result["comparisons"]["SHEAR_MINUS"]["observables"]
    print(json.dumps({"status":result["status"],"census_rows":result["minus_census"]["rows"] if result["minus_census"] else None,
      "x_HII_max_fixed_scale":m["x_HII"]["max_abs_delta_fixed_scale"],
      "x_HII_max_fixed_time":m["x_HII"]["max_abs_delta_fixed_proper_time"],
      "Tgas_max_fixed_scale":m["temperature_K"]["max_abs_delta_fixed_scale"],
      "Tgas_max_fixed_time":m["temperature_K"]["max_abs_delta_fixed_proper_time"]},indent=2))
if __name__=="__main__":
    main()
