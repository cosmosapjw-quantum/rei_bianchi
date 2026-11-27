"""Exact-in-constant-T collision-clock reduction for seven-initial-channel GL2022 SQM.

Produces **conditional** finite-temperature, finite-volume, forward-only model
results under a declared nuclear-spin-rate policy. No physical caloric Q,
reverse-rate, or production integration is issued.
"""
from __future__ import annotations
from decimal import Decimal
import json
import math
from pathlib import Path
from scipy.integrate import quad
from scipy.optimize import brentq
from .native_atlas import (FINAL,INITIAL,TEMPS,SourceContractError,verify_source,parse_printed,
                         cell_issue,PDF_SHA)


def coefficients(source:dict,T:int,chosen_initial:tuple[int,...],spin:bool)->tuple[list[list[float]],list[float]]:
    tokens=verify_source(source)
    if T==15 or T not in TEMPS or any(j not in INITIAL for j in chosen_initial):
        raise SourceContractError("unsupported temperature/HD initial J or 15K censored")
    rates=[]
    for j in chosen_initial:
        vec=[]
        for jp in FINAL:
            token=tokens[jp][j][TEMPS.index(T)]
            if cell_issue(j,jp,T,token)!="POSITIVE_PRINTED_NOMINAL":
                raise SourceContractError(f"source cell not qualified: T={T} J={j} Jp={jp} token={token}")
            q=parse_printed(token)
            if q is None:raise SourceContractError("unqualified printed-zero channel")
            if spin:q*=Decimal(3)/4 if jp%2 else Decimal(1)/4
            vec.append(float(q*Decimal("1e-6")))
        rates.append(vec)
    K=[sum(row) for row in rates]
    if min(K)<=0:raise SourceContractError("invalid total effective rate")
    return rates,K


def step(source:dict,*,T:int,duration_s:float,proton_m3:float,
         HD_by_J_m3:dict[int,float], H2_by_J_m3:list[float],Dplus_m3:float,
         spin:bool)->dict:
    """One exact constant-temperature stage (scalar quadrature/root, no state truncation)."""
    if not math.isfinite(duration_s) or duration_s<=0:raise ValueError("positive duration required")
    chosen=tuple(sorted(HD_by_J_m3))
    if not chosen or any(j not in INITIAL for j in chosen):raise ValueError("source J outside 0..6")
    y0=[float(HD_by_J_m3[j]) for j in chosen]
    p0=float(proton_m3)
    if not all(math.isfinite(x) and x>0 for x in y0+[p0]):raise ValueError("positive populations required")
    if p0<=sum(y0):raise ValueError("positive-proton reserve required for scalar clock quadrature")
    if len(H2_by_J_m3)!=len(FINAL) or any(not math.isfinite(x) or x<0 for x in H2_by_J_m3):
        raise ValueError("bad H2 populations")
    if not math.isfinite(Dplus_m3) or Dplus_m3<0:raise ValueError("bad D+ population")
    q,K=coefficients(source,T,chosen,spin)

    def residual_protons(u):
        return p0-sum(n*(-math.expm1(-kk*u)) for n,kk in zip(y0,K))
    def time_at_u(u):
        t,err=quad(lambda s:1.0/residual_protons(s),0.0,u,epsabs=1e-6,epsrel=3e-13,limit=100)
        return t
    max_u=p0*duration_s
    if time_at_u(max_u)<duration_s-1e-6:raise RuntimeError("scalar root bracket failed")
    u=brentq(lambda x:time_at_u(x)-duration_s,0.,max_u,rtol=9e-16,xtol=1e-3,maxiter=120)
    y=[n*math.exp(-kk*u) for n,kk in zip(y0,K)]
    extent=[a-b for a,b in zip(y0,y)]
    p1=p0-sum(extent)
    prod=[sum(extent[i]*q[i][jp]/K[i] for i in range(len(chosen))) for jp in FINAL]
    h2new=[float(x)+prod[jp] for jp,x in enumerate(H2_by_J_m3)]
    d1=Dplus_m3+sum(extent)
    if p1<=0 or any(x<0 for x in y):raise SourceContractError("negative or zero state")
    return {"T_K":T,"duration_s":duration_s,"spin_policy":"Eq6_7_spin_weighted" if spin else "raw_SQM",
            "collision_clock_m-3_s":u,"initial_proton_m3":p0,"final_proton_m3":p1,
            "initial_HD_J_m3":{str(j):a for j,a in zip(chosen,y0)},
            "final_HD_J_m3":{str(j):a for j,a in zip(chosen,y)},
            "final_H2_Jprime_m3":h2new,"final_Dplus_m3":d1,
            "stage_extent_m3":sum(extent),"per_initial_J_extent_m3":{str(j):v for j,v in zip(chosen,extent)},
            "K_J_m3_s":{str(j):k for j,k in zip(chosen,K)}}


def run_experiment(source:dict,*, schedule:tuple[tuple[int,float],...], spin:bool,
                   proton_initial_m3:float=1_300_000., initial_HD:dict[int,float]|None=None)->dict:
    initial_HD={2:600_000.,4:400_000.} if initial_HD is None else initial_HD
    verify_source(source)
    if not schedule:raise ValueError("nonempty schedule required")
    hd={int(k):float(v) for k,v in initial_HD.items()}
    p=float(proton_initial_m3);d=0.;z=[0.]*10
    records=[]
    for T,seconds in schedule:
        record=step(source,T=T,duration_s=float(seconds),proton_m3=p,HD_by_J_m3=hd,H2_by_J_m3=z,Dplus_m3=d,spin=spin)
        p=record["final_proton_m3"];d=record["final_Dplus_m3"]
        hd={int(k):float(v) for k,v in record["final_HD_J_m3"].items()}
        z=record["final_H2_Jprime_m3"]
        records.append(record)
    total_y0=sum(initial_HD.values())
    total_y=sum(hd.values())
    total_z=sum(z)
    # H+/HD -> D+/H2 conserves H and D nuclear numbers, charge and particle count.
    inv={
      "H_initial":proton_initial_m3+total_y0,"H_final":p+total_y+2*total_z,
      "D_initial":total_y0,"D_final":total_y+d,
      "charge_initial":proton_initial_m3,"charge_final":p+d,
      "particle_initial":proton_initial_m3+total_y0,"particle_final":p+total_y+d+total_z}
    max_res=max(abs(inv[k+"_initial"]-inv[k+"_final"]) for k in ("H","D","charge","particle"))
    if max_res>1e-4:raise SourceContractError("conservation residual too large")
    return {"schema":"wu.r26.multi_HD_forward_only_source_kinetic.v1",
        "model":"SYNTHETIC_INITIAL_POPULATIONS_EXTERNAL_FIXED_VOLUME_T_NO_REVERSE_NO_LEVEL_MIXING",
        "physics_input":"PUBLISHED_GL2022_COMPUTED_SQM_700_CELL_GRID",
        "source_original_pdf_sha256":PDF_SHA,
        "spin_policy":"Eq6_7_spin_weighted" if spin else "raw_SQM",
        "initial_proton_m3":proton_initial_m3,"initial_HD_J_m3":{str(j):v for j,v in initial_HD.items()},
        "segments":records,"final_proton_m3":p,"final_HD_J_m3":{str(j):v for j,v in hd.items()},
        "final_Dplus_m3":d,"final_H2_Jprime_m3":z,"total_extent_m3":d,
        "ortho_Jprime_m3":sum(z[j] for j in FINAL if j%2),
        "para_Jprime_m3":sum(z[j] for j in FINAL if j%2==0),
        "conservation":inv,"max_conservation_abs_m3":max_res,
        "physical_Q":None,"PES_native_threshold":None,"source_uncertainty":None,"owner_ACK":None,
        "HH_R10":"OFF","production":"NOT_ISSUED","L4":False,"full_A":None,"canonical_DAG":"34/49_UNCHANGED"}


def two_order_study(source:dict,spin:bool)->dict:
    a=run_experiment(source,schedule=((105,5e9),(255,5e9)),spin=spin)
    b=run_experiment(source,schedule=((255,5e9),(105,5e9)),spin=spin)
    return {"schema":"wu.r26.order_memory_comparison.v1","policy":a["spin_policy"],
         "source_pdf_sha256":PDF_SHA,"forward":a,"reversed":b,
         "delta_forward_minus_reverse_extent_m3":a["total_extent_m3"]-b["total_extent_m3"],
         "delta_forward_minus_reverse_H2_by_Jprime_m3":[x-y for x,y in zip(a["final_H2_Jprime_m3"],b["final_H2_Jprime_m3"])],
         "physical_Q":None,"PES_native_threshold":None,"owner_ACK":None,
         "production":"NOT_ISSUED","L4":False,"canonical_DAG":"34/49_UNCHANGED"}

if __name__=="__main__":
    import argparse
    pa=argparse.ArgumentParser();pa.add_argument("--source",type=Path,required=True)
    pa.add_argument("--output",type=Path,required=True)
    ar=pa.parse_args();src=json.loads(ar.source.read_text())
    out={"schema":"wu.r26.two_spin_policy_report.v1", "raw":two_order_study(src,False),
         "eq_spin":two_order_study(src,True),"physical_Q":None,"production":"NOT_ISSUED","canonical_DAG":"34/49_UNCHANGED"}
    from .native_atlas import save_exclusive
    save_exclusive(ar.output,out)
    for policy in ("raw","eq_spin"):
        z=out[policy]
        print(policy,"FwdExtent",z["forward"]["total_extent_m3"],"RevExtent",z["reversed"]["total_extent_m3"],"delta",z["delta_forward_minus_reverse_extent_m3"])
