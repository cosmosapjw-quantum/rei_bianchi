#!/usr/bin/env python3
"""Exact rational source remainder + 46,080-node full-parent marginal envelopes.

Original REI 26-event _explicit_photo_fields only, inherited from PR #332.
The interval MPRK/SDIRK time-advance difference D_h is NOT certified here.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,sys
from pathlib import Path
import numpy as np

N=46080
G_ORIGINAL="research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py"
COLUMNS=(0,2,3)
SPECIES=("HI","HeI","HeII")
EV_ERG=1.602176634e-12

def quotient_remainder(u,r):
    if u < -1 or r <= -1:raise ValueError("nonpositive parent photo source")
    return (1+u)/(1+r)-1, u-r, -r*(u-r)/(1+r)

def max_quotient_remainder_factor(ulo,uhi,rlo,rhi):
    """Exact independent (u,r) rectangle sup |r*(u-r)/(1+r)|.

    r>-1 and u>=-1; actual shared source constraint is a subset, hence this
    box supremum is a conservative outer when physical correlations are lost.
    """
    ulo=np.asarray(ulo,dtype=float);uhi=np.asarray(uhi,dtype=float)
    if (np.any(ulo<-1-1e-12) or np.any(uhi<ulo) or
        not(-1<rlo<=rhi)):raise ValueError("invalid positive parent box")
    out=np.zeros_like(ulo)
    for u in (ulo,uhi):
        for r in (rlo,rhi):
            out=np.maximum(out,np.abs(r*(u-r)/(1+r)))
        rstar=np.clip(np.sqrt(np.maximum(0.,1+u))-1,rlo,rhi)
        out=np.maximum(out,np.abs(rstar*(u-rstar)/(1+rstar)))
    return out

def group_from_source(original,node,lo,hi,coeff,J,E):
    if node.shape!=(N,5) or lo.shape!=node.shape or hi.shape!=node.shape:
        raise ValueError("original node count/shape")
    S=np.sum(node[:,COLUMNS],axis=0,dtype=np.longdouble).astype(float)
    L=np.array([float(original.iv.sum_interval(original._I(lo[:,i],hi[:,i])).lo) for i in COLUMNS])
    U=np.array([float(original.iv.sum_interval(original._I(lo[:,i],hi[:,i])).hi) for i in COLUMNS])
    if np.any(S<L-2e-14*np.maximum(1,S)) or np.any(S>U+2e-14*np.maximum(1,S)):
        raise ValueError("original shared population moment escapes its interval")
    if np.any(coeff<0) or J<0 or E<0:raise ValueError("negative original source")
    D=float(E+np.dot(coeff,S))
    if D<=0 or not math.isfinite(D):raise ValueError("original photon denominator")
    p=coeff*S/D
    rlo=float(np.dot(np.asarray(p,np.longdouble),np.asarray(L/S-1,np.longdouble)))
    rhi=float(np.dot(np.asarray(p,np.longdouble),np.asarray(U/S-1,np.longdouble)))
    rlo=float(np.nextafter(np.nextafter(rlo,-np.inf),-np.inf))
    rhi=float(np.nextafter(np.nextafter(rhi,np.inf),np.inf))
    if not (-1<rlo<=0<=rhi):raise ValueError("original physical denominator box")
    rg=max(rlo*rlo/(1+rlo),rhi*rhi/(1+rhi))
    f0=[];bfull=[];bglobal=[]
    for k,idx in enumerate(COLUMNS):
        rate=(J*coeff[k]/D)*node[:,idx]
        u0=lo[:,idx]/node[:,idx]-1;u1=hi[:,idx]/node[:,idx]-1
        bound=rate*max_quotient_remainder_factor(u0,u1,rlo,rhi)
        if not (np.isfinite(rate).all() and np.isfinite(bound).all()):
            raise ValueError("nonfinite original physical source rate")
        f0.append(rate);bfull.append(bound);bglobal.append(rate*rg)
    detail={"S":S.tolist(),"S_lo":L.tolist(),"S_hi":U.tolist(),
            "r_lo":rlo,"r_hi":rhi,"baseline_absorption":p.tolist(),
            "J_per_s":float(J),"E_sink":float(E),
            "max_source_R_full_per_species": [float(np.max(v)) for v in bfull],
            "source_global_only_max_relative_R":rg}
    return detail,np.stack(f0,axis=1),np.stack(bfull,axis=1),np.stack(bglobal,axis=1)

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise ImportError(path)
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m)
    return m

def run(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    g=load("rei_original_332_photon",repo/G_ORIGINAL)
    src,mod,model,_,node,frozen,time=g.context(repo)
    if len(node)!=N or frozen["array_sha"]!=g.STATE_SHA:raise ValueError("source byte identity")
    lo,hi=frozen["lo"],frozen["hi"]
    forcing=model.forcing_bounds(time,time)
    C=g.coefficients(model,mod,g.midpoint(forcing.z))
    J=np.array([g.midpoint(q) for q in forcing.current])
    E=np.array([g.midpoint(q) for q in forcing.external_subgrid])
    rates=np.zeros((N,3));full=np.zeros((N,3));glob=np.zeros((N,3))
    heat=np.zeros(N);heatR=np.zeros(N);groups=[]
    for gi in range(4):
        detail,f,b,bg=group_from_source(mod,node,lo,hi,C[gi],J[gi],E[gi])
        detail["group"]=gi;groups.append(detail)
        rates+=f;full+=b;glob+=bg
        for k in range(3):
            excess=float(model.excess_eV[k,gi])*EV_ERG
            heat+=f[:,k]*excess;heatR+=b[:,k]*abs(excess)
    hstate=model.inputs.state0.mutable_copy() if False else None
    # Original conserved nuclei from original initial state, not generic 0.079 assumption.
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=g.LANES[0])
    orig=np.asarray(base.inputs.state0.mutable_copy().values[:5].T,float)
    H=orig[:,0]+orig[:,1];He=np.sum(orig[:,2:5],axis=1)
    if np.any(H<=0) or np.any(He<=0):raise ValueError("invalid original H/He nuclear abundance")
    T=np.exp(.5*(frozen["tl"]+frozen["th"]))
    cols={"node":np.arange(N),"T_K":T,"xHII":node[:,1]/H,"xHeII":node[:,3]/He}
    for k,name in enumerate(SPECIES):
        cols["original_photo_"+name+"_per_H_per_s"]=rates[:,k]/H
        cols["upper_global_only_R_"+name+"_per_H_per_s"]=glob[:,k]/H
        cols["upper_local_and_global_R_"+name+"_per_H_per_s"]=full[:,k]/H
        cols["max_ratio_source_R_"+name]=np.divide(full[:,k],rates[:,k],out=np.zeros(N),where=rates[:,k]>0)
    cols["original_photoheat_erg_per_H_s"]=heat/H
    cols["upper_photoheat_R_erg_per_H_s"]=heatR/H
    if not all(np.isfinite(v).all() for v in cols.values()):
        raise ValueError("new original source remainder nonfinite")
    output=out/"EXACT_ORIGINAL_PHOTON_REMAINDER_46080.csv.gz"
    with output.open("wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mode="wb",mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as ioout:
                w=csv.writer(ioout);w.writerow(cols.keys())
                for i in range(N):w.writerow([i if k=="node" else format(float(v[i]),".17g") for k,v in cols.items()])
    sha=hashlib.sha256(output.read_bytes()).hexdigest()
    quant={k:{str(q):float(np.percentile(v,q)) for q in (0,5,50,95,100)} for k,v in cols.items() if k!="node"}
    report={"schema":"REI_F05_TICK160_EXACT_PHOTON_SOURCE_REMAINDER_V1",
      "science":"exact original 3-global-moment 4-group photon *source* rational nonlinear remainder; NOT time integrator joint map",
      "original_archive_sha256":g.SOURCE_SHA,"original_state_array_sha256":g.STATE_SHA,
      "original_kernel_git_blob":g.KERNEL_BLOB,"original_source_owner_pr":332,
      "source_time_seconds":float(time),"group_rows":groups,
      "original_spatial_nodes":N,"new_derived_model_rows":N,"new_observations":0,
      "quantiles":quant,"csv":output.name,"csv_sha256":sha,
      "full_X_source_marginal_outer":"analytical independent rectangle u,r exact extremum, nominal original forcing midpoint, rounding not formal certificate",
      "whole_F05_step_Dh_certified":False,"first_full_interval":"BLOCKED_MINIMUM_STEP",
      "accepted_ticks":"160/131072","historical_failed_error":2.1245050576368385e-4,
      "original_strict_gate":2e-4,"canonical_DAG":"28/88","working_DAG":"33/88",
      "REI_fast":"4/7","REC_H5":"0/313","canonical_delta":0,
      "new_IVP":0,"production":"HOLD"}
    (out/"SCIENTIFIC_RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("PHYSICS",json.dumps({"nodes":N,"group_r":[[d["r_lo"],d["r_hi"]] for d in groups],
      "max_abs_source_remainder_ratio":{k:quant["max_ratio_source_R_"+k]["100"] for k in SPECIES},
      "photoheat_R_p95":quant["upper_photoheat_R_erg_per_H_s"]["95"],
      "csv_sha256":sha,"central_DAG":"28/88"},sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--repo",type=Path,required=True);ap.add_argument("--out",type=Path,required=True)
    x=ap.parse_args();run(x.repo,x.out)
