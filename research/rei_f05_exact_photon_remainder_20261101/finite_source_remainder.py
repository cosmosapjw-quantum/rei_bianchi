#!/usr/bin/env python3
"""Exact finite-state nonlocal photo-source Taylor remainder on original REI tick160.

The ORIGINAL 26-event _explicit_photo_fields owner is evaluated with its
original photons, cross sections, external sink and four group frequencies.
Only the global H I, He I and He II photon competition is differentiated.
No thermal OTS/26-event full-step Jacobian, no new IVP or canonical admission.
"""
from __future__ import annotations
import sys,math,csv,gzip,io,hashlib,json,argparse
from pathlib import Path
from decimal import Decimal, localcontext
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/rei_igm_tick160_global_photon_20261101"))
import photon_global_feedback as gp

N=46080
SPECIES=("HI","HeI","HeII")
IDS=(0,2,3)
ORIGINAL_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STRICT=2e-4
K_B=1.380649e-16
def D(x):return Decimal.from_float(float(x))
def exact_sum(x):
    total=Decimal(0)
    for v in np.asarray(x).reshape(-1):total+=D(v)
    return total
def outward_positive(a):
    if a<0:raise ValueError("negative exact remainder majorant")
    if a==0:return 0.0
    y=float(a)
    if not math.isfinite(y):raise OverflowError("rem bound not representable")
    return float(np.nextafter(y,np.inf))
def finite_remainder_exact(x0,dx,j,c,e,totals0,deltas):
    """One source-site cell: exact identity at fixed forcing, all binary64 input as reals."""
    with localcontext() as ctx:
        ctx.prec=100
        J,C,E=D(j),D(c),D(e)
        s0=[D(v) for v in totals0];sd=[D(v) for v in deltas]
        d0=E+sum((C0*S for C0,S in zip([D(z) for z in totals0[3:]],s0)),Decimal(0)) if False else None
        raise RuntimeError("Use source_site() for common multi-species owner")

def algebraic_remainder(x0,dx,v,k):
    """Exact rational identity (1+v)>0: f−f0−f'δ=k(x0 v²−δx v)/(1+v)."""
    if 1+v<=0:raise ValueError("nonpositive owner denominator")
    return k*(x0*v*v-dx*v)/(1+v)

def parent_sample(base,lo,hi,init):
    """One H/He nuclei-preserving feasible path inside marginal original box."""
    out=np.array(base,copy=True);nh=init[:,0]+init[:,1];nhe=np.sum(init[:,2:5],axis=1)
    dh=np.minimum(hi[:,1]-base[:,1],base[:,0]-lo[:,0])
    de=np.minimum(hi[:,2]-base[:,2],base[:,3]-lo[:,3])
    dh=np.maximum(0.0,dh);de=np.maximum(0.0,de)
    out[:,1]=base[:,1]+0.5*dh;out[:,0]=nh-out[:,1]
    out[:,2]=base[:,2]+0.5*de;out[:,3]=nhe-out[:,2]-out[:,4]
    tolerance=256*np.finfo(float).eps*np.maximum(1.,np.max(np.abs(hi),axis=1))
    if np.any(out<lo-tolerance[:,None]) or np.any(out>hi+tolerance[:,None]) or np.any(out<=0):
        raise ValueError("sample not in physical parent hull")
    return out

def majorant(k,x0,dxmax,vmax,dmin_ratio):
    if dmin_ratio<=0 or vmax<0 or k<0:raise ValueError("invalid positive source quantities")
    return k*(x0*vmax*vmax+dxmax*vmax)/dmin_ratio

def run(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    if not (repo/"research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py").exists():
        raise ValueError("missing original photon-source owner")
    source,mod,model,init,base,frozen,t=gp.context(repo)
    low=np.asarray(frozen["lo"],float);high=np.asarray(frozen["hi"],float)
    if base.shape!=(N,5) or low.shape!=base.shape or high.shape!=base.shape:raise ValueError("original 46k identity")
    sample=parent_sample(base,low,high,init)
    forcing=model.forcing_bounds(t,t);z=gp.midpoint(forcing.z)
    c=gp.coefficients(model,mod,z)
    js=np.asarray([gp.midpoint(x) for x in forcing.current],float)
    ext=np.asarray([gp.midpoint(x) for x in forcing.external_subgrid],float)
    with localcontext() as ctx:
        ctx.prec=100
        S0=[exact_sum(base[:,j]) for j in IDS]
        Slo=[exact_sum(low[:,j]) for j in IDS]
        Shi=[exact_sum(high[:,j]) for j in IDS]
        Sa=[exact_sum(sample[:,j]) for j in IDS]
        for tix in range(3):
            if not(Slo[tix]<=S0[tix]<=Shi[tix] and Slo[tix]<=Sa[tix]<=Shi[tix]):
                raise ValueError("original sample moments outside rectangle")
    dims=N; columns={}
    for s,name in enumerate(SPECIES):
        for key in ("baseline_photo_events_s","sample_photo_events_s","first_order_delta_events_s","finite_remainder_events_s","parent_box_remainder_bound_events_s"):
            columns[name+"_"+key]=np.zeros(dims,float)
    columns["photoheat_finite_remainder_erg_s"]=np.zeros(dims,float)
    columns["photoheat_parent_box_bound_erg_s"]=np.zeros(dims,float)
    columns["temperature_K_source_state"]=np.exp(.5*(frozen["tl"]+frozen["th"]))
    summaries=[];max_majorant_ratio=0.;source_flux_delta=0.
    for g in range(4):
        with localcontext() as ctx:
            ctx.prec=100
            cg=[D(v) for v in c[g]];E=D(ext[g]);J=D(js[g])
            den0=E+sum((cg[s]*S0[s] for s in range(3)),Decimal(0))
            denlo=E+sum((cg[s]*Slo[s] for s in range(3)),Decimal(0))
            denhi=E+sum((cg[s]*Shi[s] for s in range(3)),Decimal(0))
            dena=E+sum((cg[s]*Sa[s] for s in range(3)),Decimal(0))
            if min(den0,denlo,denhi,dena)<=0:raise ValueError("source denominator zero")
            vmin=(denlo-den0)/den0;vmaxsigned=(denhi-den0)/den0
            vamax=(dena-den0)/den0
            vabs=max(abs(vmin),abs(vmaxsigned));dmin_ratio=denlo/den0
            group_bound=Decimal(0);group_flux0=Decimal(0);group_sample=Decimal(0)
            for s,name in enumerate(SPECIES):
                f0=columns[name+"_baseline_photo_events_s"]
                fa=columns[name+"_sample_photo_events_s"]
                lin=columns[name+"_first_order_delta_events_s"]
                rr=columns[name+"_finite_remainder_events_s"]
                bb=columns[name+"_parent_box_remainder_bound_events_s"]
                K=J*cg[s]/den0
                if K==0:
                    continue
                gain=D(float(model.excess_eV[s,g]))*D(mod.rim.EV_ERG)
                for i in range(N):
                    x=D(base[i,IDS[s]]);da=D(sample[i,IDS[s]])-x
                    delta_max=max(abs(D(low[i,IDS[s]])-x),abs(D(high[i,IDS[s]])-x))
                    base_src=K*x
                    sample_src=J*cg[s]*(x+da)/dena
                    lin_src=K*(da-x*vamax)
                    exact_r=algebraic_remainder(x,da,vamax,K)
                    independent_r=sample_src-base_src-lin_src
                    if abs(exact_r-independent_r)>D("5e-75")*max(Decimal(1),abs(sample_src)):
                        raise ValueError("finite-source identity not closed")
                    bound=majorant(K,x,delta_max,vabs,dmin_ratio)
                    if abs(exact_r)>bound:
                        raise ValueError("original full-box source remainder bound failed")
                    f0[i]+=float(base_src);fa[i]+=float(sample_src);lin[i]+=float(lin_src)
                    rr[i]+=float(exact_r);bb[i]+=outward_positive(bound)
                    columns["photoheat_finite_remainder_erg_s"][i]+=float(exact_r*gain)
                    columns["photoheat_parent_box_bound_erg_s"][i]+=outward_positive(bound*abs(gain))
                group_bound+=K*(max(S0)*vabs*vabs+max(Shi[tix]-Slo[tix] for tix in range(3))*vabs)/dmin_ratio
                group_flux0+=J*cg[s]*S0[s]/den0
                group_sample+=J*cg[s]*Sa[s]/dena
            summaries.append(dict(group=g,original_current_photons_s=float(J),
                 source_occupancy=[float(cg[s]*S0[s]/den0) for s in range(3)],
                 external_occupancy=float(E/den0),
                 min_global_denominator_ratio=float(dmin_ratio),
                 global_v_interval=[float(vmin),float(vmaxsigned)],
                 global_v_sample=float(vamax),global_v_abs_bound=float(vabs),
                 baseline_absorbed_s=float(group_flux0),
                 sample_absorbed_s=float(group_sample),
                 sample_source_physics_only=True))
    # Direct original 26-event provider must enclose both frozen state representatives.
    for label,pop in (("baseline",base),("sample",sample)):
        owners=gp.original_source_interval(model,mod,pop,forcing)
        for s,name in enumerate(SPECIES):
            actual=float(np.sum(columns[name+("_baseline_photo_events_s" if label=="baseline" else "_sample_photo_events_s")],dtype=np.longdouble))
            tol=1e-8*max(abs(actual),1e-200)
            if not(float(owners[s].lo)-tol<=actual<=float(owners[s].hi)+tol):
                raise ValueError("parent ORIGINAL _explicit_photo_fields mismatch "+name)
    for name in SPECIES:
        a=columns[name+"_baseline_photo_events_s"];b=columns[name+"_sample_photo_events_s"]
        l=columns[name+"_first_order_delta_events_s"];r=columns[name+"_finite_remainder_events_s"]
        bound=columns[name+"_parent_box_remainder_bound_events_s"]
        # float summation cannot certify sub-ulp tiny remainder, so one-sided tolerance on this diagnostic only
        if np.any(np.abs(r)>bound*(1+1e-13)+1e-300):raise ValueError("numeric bound check")
        phys=max(float(np.max(np.abs(a))),1e-200)
        source_flux_delta=max(source_flux_delta,float(np.max(np.abs(b-a))))
        max_majorant_ratio=max(max_majorant_ratio,float(np.max(bound))/phys)
    outpath=out/"ORIGINAL_SOURCE_FINITE_REMAINDER_46080.csv.gz"
    csv_sha=gp.write_gz(outpath,columns)
    doc=dict(schema="REI_ORIGINAL_TICK160_GLOBAL_PHOTON_TAYLOR_SOURCE_REMAINDER_V1",
        original_sha=ORIGINAL_SHA,state_sha=gp.STATE_SHA,parent_pr=332,
        unique_physical_nodes=N,physical_source_group_count=4,
        new_source_conditioned_rows=N,new_measured_rows=0,new_cosmological_ivps=0,
        precise_claim="Exact finite source operator Taylor identity; positive mathematically uniform bound on original full rectangular tick160 parent for fixed binary64 owner J_g,E_g,c_sg at t160",
        excluded="All-X joint MPRK22/SDIRK2 full-vs-twohalf D_h, original forcing uncertainty, temperature feedback, photo-recombination OTS, Bianchi directional transport",
        source_groups=summaries,nonlinear_remainder_bound_peak_over_source_peak=max_majorant_ratio,
        source_sample_max_delta_events_s=source_flux_delta,
        source_analytic_code_tested=True,
        first_canonical_interval="BLOCKED_MINIMUM_STEP",historical_logT_error=2.1245050576368385e-4,
        strict_gate=STRICT,central="28/88_REPORTED",working="33/88_REPORTED",fast="4/7_REPORTED",canonical_delta=0,
        output_csv=outpath.name,output_csv_sha256=csv_sha)
    (out/"RESULT.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print("REI_SOURCE_TAYLOR_REAL_PHYSICS",json.dumps({k:doc[k] for k in ("unique_physical_nodes","source_groups","nonlinear_remainder_bound_peak_over_source_peak","output_csv_sha256","central","canonical_delta")},sort_keys=True),flush=True)
    return doc

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--repo",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    run(x.repo,x.output)
