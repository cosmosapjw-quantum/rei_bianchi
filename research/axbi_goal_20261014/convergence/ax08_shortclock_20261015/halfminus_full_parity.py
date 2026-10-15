#!/usr/bin/env python3
"""Full q=+/-0.005 AX08 actual-saved finite-amplitude signed parity and H/He.

Independent postprocessing only. No new native evolution solver.
All four source composed histories SHA-pinned; all 6-species HALF_MINUS census
reuses PR119 actual tests. No AX11 numerical truncation-error admission.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
CENSUS=HERE.parent/"ax08_clock_census_20261015"
sys.path.insert(0,str(CENSUS))
import clock_census as cc
RELS={
 "ZERO":"runs/flrw/32d11e733155/ZERO_composed_001",
 "SHEAR_HALF_PLUS":"runs/paired/32d11e733155/SHEAR_HALF_PLUS_composed_002",
 "SHEAR_HALF_MINUS":"runs/paired/32d11e733155/SHEAR_HALF_MINUS_composed_001",
 "SHEAR_MINUS":"runs/paired/32d11e733155/SHEAR_MINUS_composed_001",
}
QREF={"ZERO":0.,"SHEAR_HALF_PLUS":.005,"SHEAR_HALF_MINUS":-.005,"SHEAR_MINUS":-.01}
COLS=(("x_HII",4),("x_HeII",6),("x_HeIII",7),("temperature_K",10),("J2_photon_u_eV_per_H",11))
def frozen(owner,case):
    p=owner/"research/axbi_goal_20261014"/RELS[case]
    r=json.loads((p/"COMPOSITION_RECEIPT.json").read_text())
    if (r["status"]!="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
        or r["scientific_admission"]!="NOT_ISSUED"
        or r["row_counts"]["history.csv"]["composed_rows"]!=312238
        or r["row_counts"]["abundances.csv"]["composed_rows"]!=6*312238):
        raise RuntimeError("CASE_NOT_COMPLETED_OR_WRONG_ROWS:"+case)
    x={}
    for role in ("history.csv","abundances.csv","source_identity.txt","RETURN.txt"):
        digest=cc.digest(p/role)
        if digest!=r["output_sha256"][role]:
            raise RuntimeError("FROZEN_SOURCE_BYTE_MISMATCH:"+case+":"+role)
        x[role]=digest
    if case!="ZERO":
        if r.get("source_compatibility",{}).get("relation")!="REVIEWED_RESOURCE_ONLY":
            raise RuntimeError("CASE_REVIEWED_SOURCE_RELATION_MISSING:"+case)
    h,_=cc.history(p/"history.csv")
    terminal=dict(s.split("=",1) for s in (p/"RETURN.txt").read_text().splitlines() if "=" in s)
    if terminal["status"]!="COMPLETE_REPRESENTED_INTERVAL" or float(terminal["a"])!=.2:
        raise RuntimeError("NO_COMPLETE_CASE_TERMINAL")
    return h,p,x
def full_comparison(owner,nodes=4097,all_species=True):
    histories={};paths={};hashes={}
    for name in RELS:
        h,p,sha=frozen(owner,name)
        histories[name]=h;paths[name]=p;hashes[name]=sha
    count=cc.census(paths["SHEAR_HALF_MINUS"]/"abundances.csv",
        histories["SHEAR_HALF_MINUS"],"SHEAR_HALF_MINUS") if all_species else None
    amin=max(h[0,1] for h in histories.values())
    amax=min(h[-1,1] for h in histories.values())
    a=np.exp(np.linspace(math.log(amin),math.log(amax),nodes))
    a[0]=amin;a[-1]=amax
    get=lambda case,j:np.interp(a,histories[case][:,1],histories[case][:,j])
    t0=get("ZERO",0);tp=get("SHEAR_HALF_PLUS",0);tm=get("SHEAR_HALF_MINUS",0)
    bp=get("SHEAR_HALF_PLUS",11) # J2 is NOT background shear; below only observable.
    parity={}
    plot={}
    for label,j in COLS:
        zero=get("ZERO",j)
        plus=get("SHEAR_HALF_PLUS",j)
        minus=get("SHEAR_HALF_MINUS",j)
        bigminus=get("SHEAR_MINUS",j)
        even=.5*(plus+minus)-zero
        odd=.5*(plus-minus)
        # A diagnostic only: qminus(-.01) response and qhalf(.005) even do not
        # isolate all cubic/quartic nonlinearities at separate amplitudes.
        big_response=bigminus-zero
        residual4=big_response-4*even if label!="J2_photon_u_eV_per_H" else big_response+2*odd
        max_even=float(np.max(abs(even)))
        max_odd=float(np.max(abs(odd)))
        peak=int(np.argmax(abs(even if max_even>max_odd else odd)))
        parity[label]={
            "even_max_abs":max_even,
            "odd_max_abs":max_odd,
            "odd_to_even_sup_ratio":max_odd/max(max_even,1e-300),
            "max_abs_minus_0p01_minus_expected_leading":float(np.max(abs(residual4))),
            "physical_comparison_used":"q² scalar" if label!="J2_photon_u_eV_per_H" else "q-leading signed J2",
            "at_max_response_zbar":float(1/a[peak]-1),
            "endpoint_even":float(even[-1]),
            "endpoint_odd":float(odd[-1]),
            "relative_source_numerical_error":"UNKNOWN_AX11"
        }
        if np.max(abs((even+odd+zero)-plus))>max(5e-15,1e-15*np.max(abs(plus))):
            raise RuntimeError("PARITY_ALGEBRA_DISAGREEMENT:"+label)
        plot[label]=(even,odd,zero,plus,minus)
    # Byte-for-byte binary64 symmetry is stronger than a sampled interpolation.
    hp=histories["SHEAR_HALF_PLUS"]
    hm=histories["SHEAR_HALF_MINUS"]
    bhp=np.loadtxt(paths["SHEAR_HALF_PLUS"]/"history.csv",delimiter=",",skiprows=1,usecols=(6,),dtype=float)
    bhm=np.loadtxt(paths["SHEAR_HALF_MINUS"]/"history.csv",delimiter=",",skiprows=1,usecols=(6,),dtype=float)
    exact_source_pair={
       "a_exact_array":bool(np.array_equal(hp[:,1],hm[:,1])),
       "time_exact_array":bool(np.array_equal(hp[:,0],hm[:,0])),
       "b_odd_exact_array":bool(np.array_equal(bhp,-bhm)),
       "max_abs_b_plus_bminus":float(np.max(abs(bhp+bhm))),
       "all_saved_rows":len(hp)
    }
    if not all(exact_source_pair[k] for k in ("a_exact_array","time_exact_array","b_odd_exact_array")):
        raise RuntimeError("SIGNED_BACKGROUND_EXACT_SYMMETRY_UNEXPECTEDLY_FAILS")
    terminal={}
    for name,h in histories.items():
        terminal[name]={
            "proper_t_s":float(h[-1,0]),"mean_a":float(h[-1,1]),
            "x_HII":float(h[-1,4]),"x_HeII":float(h[-1,6]),
            "x_HeIII":float(h[-1,7]),"Tgas_K":float(h[-1,10]),
            "J2_eV_per_H":float(h[-1,11])
        }
    result={
      "schema":"rei.axbi.full_halfminus_signed_parity.v1",
      "status":"SCOPED_FOUR_ACTUAL_COMPLETED_CASES",
      "real_rows_each":312238,"source_composition_hashes":hashes,
      "frozen_model":"cold Plancklike MD14+BB50kK H/He Case A Bianchi-I",
      "q_cases":{"ZERO":0,"SHEAR_HALF_PLUS":.005,"SHEAR_HALF_MINUS":-.005,"SHEAR_MINUS":-.01},
      "matched_lna_nodes":nodes,
      "mean_scale_interval":[amin,amax],
      "mean_scale_time_pair_max_abs_s":float(np.max(abs(tp-tm))),
      "same_mean_a_analytic_physical_background_time_symmetry":True,
      "verified_exact_background_pair_all_rows":exact_source_pair,
      "minus_full_species_census":count,
      "parity":parity,"endpoints":terminal,
      "interpretation":"even and odd components are finite-q source-specific, matched at same mean scale. No q5 full family until PLUS recovered; no AX11 convergence or observation.",
      "scientific_admission":"NOT_ISSUED"
    }
    return result,plot,a,histories

def save(result,plot,a,histories,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out.mkdir(parents=True,exist_ok=False)
    (out/"FULL_SIGNED_PARITY.json").write_text(json.dumps(result,indent=2)+"\n")
    fig,axes=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
    for ax,(name,(even,odd,_,_,_)) in zip(axes.flat,plot.items()):
        ax.plot(1/a-1,even,label="even(+.005,-.005) minus FLRW")
        ax.plot(1/a-1,odd,label="odd(+.005,-.005)")
        ax.invert_xaxis();ax.set_xlabel("Mean redshift");ax.set_title(name)
        ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.suptitle("AX08 completed positive/negative half shear finite-q parity; numerical error UNKNOWN")
    fig.savefig(out/"full_halfminus_parity.png",dpi=170)
    plt.close(fig)
    fig,ax=plt.subplots(2,2,figsize=(12,9),constrained_layout=True)
    for idx,key in enumerate(("ZERO","SHEAR_HALF_PLUS","SHEAR_HALF_MINUS","SHEAR_MINUS")):
        h=histories[key]
        sel=np.unique(np.r_[np.arange(0,len(h),max(1,len(h)//3500)),len(h)-1])
        for j,name in ((4,"HII"),(6,"HeII"),(7,"HeIII")):
            ax.flat[idx].plot(h[sel,0]/(365.25*86400*1e6),h[sel,j],label=name)
        ax.flat[idx].set_title(key);ax.flat[idx].set_xlabel("Elapsed proper time [Myr]")
        ax.flat[idx].set_ylabel("Element ion fraction")
        ax.flat[idx].grid(alpha=.25);ax.flat[idx].legend(fontsize=8)
    fig.suptitle("Actual AX08 full H/He ionization histories; separate conditional MD14 source, no AX11")
    fig.savefig(out/"four_actual_HHe_histories.png",dpi=170)
    plt.close(fig)
    # BBN-like data presentation: all five H/He ion stages versus both
    # proper time and gas temperature, with no illegitimate T monotonicity.
    fig,axs=plt.subplots(4,2,figsize=(13,14),constrained_layout=True)
    case_names=("ZERO","SHEAR_HALF_PLUS","SHEAR_HALF_MINUS","SHEAR_MINUS")
    for row,key in enumerate(case_names):
        h=histories[key]
        sel=np.unique(np.r_[np.arange(0,len(h),max(1,len(h)//3300)),len(h)-1])
        for idx,nm in ((3,"HI"),(4,"HII"),(5,"HeI"),(6,"HeII"),(7,"HeIII")):
            axs[row,0].plot(h[sel,0]/(365.25*86400*1e6),h[sel,idx],lw=1.25,label=nm)
            axs[row,1].plot(h[sel,10],h[sel,idx],lw=1.25,label=nm)
        axs[row,0].set_ylabel(key+" | element ion fraction")
        axs[row,0].set_xlabel("Elapsed proper time [Myr]")
        axs[row,1].set_xlabel("Saved Tgas [K], chronological path")
        axs[row,1].set_ylabel("Element ion fraction")
        for axis in axs[row]:
            axis.grid(alpha=.25)
            axis.legend(fontsize=7,ncol=3)
    fig.suptitle("AX08 four actual complete H/He histories vs time and gas temperature; source conditional, AX11 unknown")
    fig.savefig(out/"four_HHe_BBNstyle_time_temperature.png",dpi=155)
    plt.close(fig)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--no-census",action="store_true")
    args=p.parse_args()
    result,plot,a,all_h=full_comparison(args.owner_root,all_species=not args.no_census)
    save(result,plot,a,all_h,args.output)
    print(json.dumps({
      "status":result["status"],
      "minus_half_census_rows":result["minus_full_species_census"]["rows"] if result["minus_full_species_census"] else None,
      "clock_q_pm_half_max_delta_s":result["mean_scale_time_pair_max_abs_s"],
      "x_HII_even_abs":result["parity"]["x_HII"]["even_max_abs"],
      "x_HII_odd_abs":result["parity"]["x_HII"]["odd_max_abs"],
      "Tgas_even_abs":result["parity"]["temperature_K"]["even_max_abs"],
      "Tgas_odd_abs":result["parity"]["temperature_K"]["odd_max_abs"],
      "J2_odd_abs":result["parity"]["J2_photon_u_eV_per_H"]["odd_max_abs"]
    },indent=2))
