#!/usr/bin/env python3
"""Original REI 26-event MPRK22 predictor: exact three-moment source sensitivity.

Scientific scope: conditional, source-locked, one nuclei-preserving point within the
frozen 46,080-node tick160 interval. Actual original 26-event flux enclosure supplies
the representative matrix A. The original photon source supplies exact common
global-moment derivatives. Neither an all-X source-correlated D_h certificate nor an
independent radiation transfer solution. Original owner/gates are READ ONLY.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py"
SOURCE_ARCHIVE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_BLOB="ca2676c84b3c93766c59aa3ef81740565226dad9"
N=46080
SRC_INDICES=(0,2,3)
DEST_INDICES=(1,3,4)
SPECIES=("HI","HeI","HeII")
KB=1.380649e-16
EV=1.602176634e-12
STRICT_LOCAL_ERROR=2e-4
STRICT_WIDTH=2e-3

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if not spec or not spec.loader:raise ImportError(str(path))
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as fd:
        for block in iter(lambda:fd.read(1048576),b""):h.update(block)
    return h.hexdigest()

def batch_solve(A,R):
    """Solve independent original 2x2 hydrogen and 3x3 helium blocks, with any RHS batch."""
    A=np.asarray(A,dtype=np.float64);R=np.asarray(R,dtype=np.float64)
    n=A.shape[0]
    if A.shape!=(n,5,5) or R.shape[0]!=n or R.shape[-1]!=5:
        raise ValueError("wrong original five-species population shape")
    if not np.isfinite(A).all() or not np.isfinite(R).all():
        raise ValueError("nonfinite stage block")
    Y=R.reshape(n,-1,5)
    Z=np.empty_like(Y)
    for left,right in ((0,2),(2,5)):
        sl=slice(left,right)
        Z[:,:,sl]=np.linalg.solve(A[:,sl,sl],Y[:,:,sl].transpose(0,2,1)).transpose(0,2,1)
    return Z.reshape(R.shape)

def photo_moment_derivatives(group_rates,group_shares):
    """Exact partials wrt LOG global source moments at fixed local numerator/current.

    group_rates: (4,n,3), actual original 26-event original photon owner;
    group_shares: (4,3), exact absorber fractions at this source site.
    """
    r=np.asarray(group_rates,float);p=np.asarray(group_shares,float)
    if r.ndim!=3 or r.shape[0]!=4 or r.shape[2]!=3 or p.shape!=(4,3):
        raise ValueError("wrong original photon source dimensions")
    if np.any(r<0) or np.any(p<0) or np.any(np.sum(p,axis=1)>1+1e-12):
        raise ValueError("invalid positive photons")
    first=-np.einsum("gns,gk->nsk",r,p)
    second=2*np.einsum("gns,gk,gl->nskl",r,p,p)
    for k in range(3):
        second[:,:,k,k]-=np.einsum("gns,g->ns",r,p[:,k])
    return first,second

def photo_matrix_derivatives(group_rates,group_shares,parent,dt):
    """dA/dlnS, d²A/dlnS² for exact ORIGINAL MPRK predictor population matrix."""
    parent=np.asarray(parent,float)
    if parent.shape!=(group_rates.shape[1],5) or np.any(parent<=0):raise ValueError("invalid positive parent")
    if not np.isfinite(dt) or dt<=0:raise ValueError("bad original physical time step")
    f,h=photo_moment_derivatives(group_rates,group_shares)
    n=len(parent);a1=np.zeros((n,3,5,5));a2=np.zeros((n,3,3,5,5))
    for s,(src,dest) in enumerate(zip(SRC_INDICES,DEST_INDICES)):
        dr=dt*f[:,s,:]/parent[:,src,None]
        d2r=dt*h[:,s,:,:]/parent[:,src,None,None]
        a1[:,:,src,src]+=dr;a1[:,:,dest,src]-=dr
        a2[:,:,:,src,src]+=d2r;a2[:,:,:,dest,src]-=d2r
    return a1,a2

def implicit_predictor_derivatives(A,parent,group_rates,group_shares,dt):
    """Exact conditional first and second derivatives of y_pred = A(lnS)^-1 parent."""
    base=batch_solve(A,parent)
    A1,A2=photo_matrix_derivatives(group_rates,group_shares,parent,dt)
    J=-batch_solve(A,np.einsum("nksj,nj->nks",A1,base))
    Hrhs=np.einsum("nklsj,nj->nkls",A2,base)
    Hrhs+=np.einsum("nksj,nlj->nkls",A1,J)
    Hrhs+=np.einsum("nlsj,nkj->nkls",A1,J)
    H=-batch_solve(A,Hrhs)
    if not np.isfinite(J).all() or not np.isfinite(H).all():raise ValueError("nonfinite MPRK sensitivity")
    if not np.allclose(H,H.transpose(0,2,1,3),rtol=3e-11,atol=0):
        raise ValueError("Hessian violates mixed-source symmetry")
    return base,J,H

def finite_source_matrix(A,parent,group_rates,group_shares,dt,deltas):
    """Exact original source denominator response for fixed local chemistry/p."""
    Anew=A.copy()
    denom=1+np.sum(group_shares*np.expm1(np.asarray(deltas,float))[None,:],axis=1)
    if np.any(denom<=0):raise ValueError("unphysical original source denominator")
    rdelta=np.einsum("gns,g->ns",group_rates,1/denom-1)
    for s,(src,dest) in enumerate(zip(SRC_INDICES,DEST_INDICES)):
        d=dt*rdelta[:,s]/parent[:,src]
        Anew[:,src,src]+=d;Anew[:,dest,src]-=d
    return Anew

def write_csv(out,cols):
    if not cols:raise ValueError("missing source model data")
    n=len(next(iter(cols.values())))
    path=out/"ORIGINAL_PREDICTOR_GLOBAL_MOMENT_JAC_HESS_46080.csv.gz"
    with path.open("wb") as f:
        with gzip.GzipFile(fileobj=f,mode="wb",filename="",mtime=0,compresslevel=6) as g:
            with io.TextIOWrapper(g,encoding="utf-8",newline="") as h:
                w=csv.writer(h);w.writerow(["node",*cols])
                for i in range(n):
                    w.writerow([i,*[format(float(cols[k][i]),".17g") for k in cols]])
    return path,sha(path)

def scientific_metrics(cols):
    stats={}
    for k,v in cols.items():
        if np.size(v)!=N or not np.isfinite(v).all():raise ValueError("original data column not 46080 valid")
        stats[k]={str(q):float(np.percentile(v,q)) for q in (0,5,50,95,100)}
    return stats

def actual_original_science(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    fb=load("rei_predictor_photon_source_original",repo/"research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py")
    src,mod,model,p0,p,frozen,t=fb.context(repo)
    if sha(repo/"stages"/fb.OLD/"local_results/first_interval_r2_blocked_minimum_step.tar.gz")!=SOURCE_ARCHIVE_SHA:
        raise ValueError("original frozen source archive has moved")
    if frozen["array_sha"]!=STATE_SHA:raise ValueError("original tick160 state mismatch")
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=fb.LANES[0])
    initial=np.asarray(base.inputs.state0.mutable_copy().values[:5].T,float)
    nh=initial[:,0]+initial[:,1];nhe=np.sum(initial[:,2:5],axis=1)
    temperature=np.exp(.5*(frozen["tl"]+frozen["th"]))
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*160/131072;dt=duration/131072
    box=mod._I(p)
    ev=mod.event_box(model,box,mod._I(temperature),t0)
    alo,ahi=mod._matrix_interval(ev.flux,box,dt)
    A=.5*(alo+ahi)
    ref=mod.population_step(box,ev.flux,box,dt,nh,nhe)
    if not ref.certified:raise ValueError("original predictor Krawczyk certificate failed")
    F=0.5*(ev.flux.lo+ev.flux.hi)
    forcing=model.forcing_bounds(t0,t0);z=fb.midpoint(forcing.z)
    coeff=fb.coefficients(model,mod,z)
    currents=np.asarray([fb.midpoint(x) for x in forcing.current],float)
    external=np.asarray([fb.midpoint(x) for x in forcing.external_subgrid],float)
    moments=np.asarray([np.sum(p[:,idx],dtype=np.longdouble) for idx in SRC_INDICES],float)
    lo=np.asarray([np.sum(frozen["lo"][:,idx],dtype=np.longdouble) for idx in SRC_INDICES],float)
    hi=np.asarray([np.sum(frozen["hi"][:,idx],dtype=np.longdouble) for idx in SRC_INDICES],float)
    if np.any(lo>moments) or np.any(hi<moments) or np.any(lo<=0):
        raise ValueError("original outer source moment enclosure invalid")
    group_rates=np.zeros((4,N,3));group_shares=np.zeros((4,3))
    groups=[]
    for g in range(4):
        ps,ext,den=fb.shares(moments,coeff[g],external[g])
        group_shares[g]=ps
        r=currents[g]*p[:,SRC_INDICES]*(coeff[g]/den)[None,:]
        if np.any(r<0) or not np.isfinite(r).all():raise ValueError("invalid real original photon rates")
        group_rates[g]=r
        conservation=float(np.max(abs(np.sum(r,axis=0)-currents[g]*ps)/
                                  np.maximum(1.,abs(currents[g]*ps))))
        if conservation>3e-12:raise ValueError("original source photon competition non-conservation")
        groups.append(dict(group=g,current_per_s=float(currents[g]),fractions=ps.tolist(),
                  external_fraction=float(ext),source_global_moments=moments.tolist(),
                  photon_rates_per_s=np.sum(r,axis=0).tolist(),max_photon_fraction_error=conservation,
                  group_source_resolved=bool(currents[g]>np.finfo(float).tiny)))
    pred,J,H=implicit_predictor_derivatives(A,p,group_rates,group_shares,dt)
    tol=1e-11*np.maximum(np.abs(p),np.abs(pred))
    if np.any(pred<ref.lower-tol) or np.any(pred>ref.upper+tol):
        raise ValueError("new predictor representative escapes original validated Krawczyk enclosure")
    for arr in (pred,J,H):
        if not np.isfinite(arr).all():raise ValueError("nonfinite genuine original source response")
    # Four exact nuclear invariants: states, all first and all second responses.
    for name,Q in (("first",J),("second",H)):
        if name=="first":
            hres=Q[:,:,:2].sum(axis=-1);heres=Q[:,:,2:5].sum(axis=-1)
            scale=np.max(np.abs(Q),axis=-1)
        else:
            hres=Q[:,:,:,:2].sum(axis=-1);heres=Q[:,:,:,2:5].sum(axis=-1)
            scale=np.max(np.abs(Q),axis=-1)
        if max(np.max(np.abs(hres)/np.maximum(scale,1e-200)),
               np.max(np.abs(heres)/np.maximum(scale,1e-200)))>4e-8:
            raise ValueError("nuclear conservation derivative violated")
    e0=(p[:,1]+p[:,3]+2*p[:,4])/nh
    ep=(pred[:,1]+pred[:,3]+2*pred[:,4])/nh
    j_e=(J[:,:,1]+J[:,:,3]+2*J[:,:,4])/nh[:,None]
    h_e=(H[:,:,:,1]+H[:,:,:,3]+2*H[:,:,:,4])/nh[:,None,None]
    ne=pred[:,1]+pred[:,3]+2*pred[:,4]
    thermal=1.5*1.380649e-16*temperature*(nh+nhe+ne)/nh
    dthermal=1.5*1.380649e-16*temperature[:,None]*j_e
    chi_h=float(mod.rim.CHI_H_EV);chi_he=float(mod.rim.CHI_HEI_EV)
    chi_he2=float(mod.rim.CHI_HEII_EV)
    u_binding=EV*(chi_h*pred[:,1]+chi_he*pred[:,3]+
                  (chi_he+chi_he2)*pred[:,4])/nh
    d_binding=EV*(chi_h*J[:,:,1]+chi_he*J[:,:,3]+(chi_he+chi_he2)*J[:,:,4])/nh[:,None]
    # Source moment outer bound; exact conditional source differences at five
    # selected points. These points are NOT an all-X/branch/reachable-set certificate.
    dlo=np.log(lo/moments);dhi=np.log(hi/moments)
    exact_cases={}
    stress=[("S_LO",dlo),("S_HI",dhi),("S_CROSS",np.array([dhi[0],dlo[1],dhi[2]])),
            ("S_LO_HALF",.5*dlo),("S_HI_HALF",.5*dhi)]
    for label,dvec in stress:
        new=finite_source_matrix(A,p,group_rates,group_shares,dt,dvec)
        exact=batch_solve(new,p)
        linear=np.einsum("nks,k->ns",J,dvec)
        quad=.5*np.einsum("nkls,k,l->ns",H,dvec,dvec)
        residual=exact-pred-linear-quad
        norm=nh[:,None]
        exact_cases[label]={
         "delta_log_moment":dvec.tolist(),
         "max_abs_fraction_exact_predictor_shift":float(np.max(abs(exact-pred)/norm)),
         "max_abs_fraction_linear_error":float(np.max(abs(exact-pred-linear)/norm)),
         "max_abs_fraction_second_order_error":float(np.max(abs(residual)/norm)),
         "max_abs_electron_per_H_shift":float(np.max(abs((exact[:,1]+exact[:,3]+2*exact[:,4])/nh-ep))),
         "predicted_populations_positive":bool(np.all(exact>0)),
         "nuclei_rel_error":float(max(np.max(abs(np.sum(exact[:,:2],axis=1)-nh)/nh),
                                       np.max(abs(np.sum(exact[:,2:5],axis=1)-nhe)/nhe)))
        }
        if not exact_cases[label]["predicted_populations_positive"] or exact_cases[label]["nuclei_rel_error"]>2e-11:
            raise ValueError("source stress violates positive MPRK predictor nuclear conservation")
    cols=dict(
      parent_xHII=p[:,1]/nh,
      parent_xHeII=p[:,3]/nhe,
      parent_xHeIII=p[:,4]/nhe,
      parent_T_K=temperature,
      one_tick_predictor_xHII=pred[:,1]/nh,
      one_tick_predictor_xHeII=pred[:,3]/nhe,
      one_tick_predictor_xHeIII=pred[:,4]/nhe,
      one_tick_predictor_xe=ep,
      one_tick_predictor_thermal_erg_H=thermal,
      one_tick_predictor_binding_erg_H=u_binding,
      one_tick_delta_xe=ep-e0
    )
    for k,name in enumerate(SPECIES):
        cols["d_predictor_xHII_dlnS_"+name]=J[:,k,1]/nh
        cols["d_predictor_xHeII_dlnS_"+name]=J[:,k,3]/nhe
        cols["d_predictor_xHeIII_dlnS_"+name]=J[:,k,4]/nhe
        cols["d_predictor_xe_dlnS_"+name]=j_e[:,k]
        cols["d_predictor_thermal_erg_H_dlnS_"+name]=dthermal[:,k]
        cols["d_predictor_binding_erg_H_dlnS_"+name]=d_binding[:,k]
    for k,name in enumerate(SPECIES):
        for l,other in enumerate(SPECIES):
            cols["d2_predictor_xe_dlnS_"+name+"_dlnS_"+other]=h_e[:,k,l]
    path,digest=write_csv(out,cols)
    stat=scientific_metrics(cols)
    report={
       "schema":"REI_IGM_ORIGINAL26_PREDICTOR_GLOBAL_SOURCE_JAC_HESS_V1",
       "status":"SOURCE_CONDITIONAL_ORIGINAL_MPRK_PREDICTOR_DERIVATIVES_NUMERICALLY_CHECKED",
       "original_source_archive_sha256":SOURCE_ARCHIVE_SHA,
       "original_tick160_array_sha256":STATE_SHA,
       "original_interval_discrete_map_blob":KERNEL_BLOB,
       "one_tick_time_s":dt,
       "original_accepted_tick":160,"total_ticks":131072,
       "physical_input_distinct_nodes":N,
       "new_physical_predictor_rows":N,"physical_model_columns":len(cols),
       "original_krawczyk_predictor_certified":True,
       "source_photon_group_owner_rows":groups,
       "original_global_moments":moments.tolist(),
       "original_global_moment_outer_lower":lo.tolist(),
       "original_global_moment_outer_upper":hi.tolist(),
       "source_log_moment_box_lower":dlo.tolist(),
       "source_log_moment_box_upper":dhi.tolist(),
       "absolute_max_dxe_dlnS":{SPECIES[k]:float(np.max(np.abs(j_e[:,k]))) for k in range(3)},
       "numerically_active_source_moments":{SPECIES[k]:bool(np.any(j_e[:,k]!=0)) for k in range(3)},
       "source_moment_fixed_local_numerator":True,
       "source_moment_perturbations_are_conditional_counterfactuals":True,
       "original_26event_other_events_frozen_in_matrix":True,
       "original_implicit_thermal_stage_derivative":"NOT_COMPUTED",
       "original_full_vs_two_half_entire_X_certificate":False,
       "original_next_tick_historical_logT_error":2.1245050576368385e-4,
       "original_local_error_gate":STRICT_LOCAL_ERROR,
       "original_state_width_gate":STRICT_WIDTH,
       "finite_source_outer_box_probe":exact_cases,
       "source_csv_file":path.name,"source_csv_sha256":digest,
       "nodewise_equal_node_quantiles":stat,
       "central_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
       "physical_fast_DAG":"4/7_REPORTED","canonical_delta":0,
       "whole_first_canonical_interval":"BLOCKED_MINIMUM_STEP",
       "production":"HOLD","merge":"HOLD","no_force_push":True,
       "native_subagent":"NOT_RUN","distinct_author":"NOT_RUN"
    }
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ORIGINAL26_PREDICTOR_PHYSICS",json.dumps({
        "node_rows":N,"columns":len(cols),"median_predictor_xe":stat["one_tick_predictor_xe"]["50"],
        "median_one_tick_delta_xe":stat["one_tick_delta_xe"]["50"],
        "max_abs_dxe_dlnS_HI":float(np.max(np.abs(j_e[:,0]))),
        "max_abs_dxe_dlnS_HeI":float(np.max(np.abs(j_e[:,1]))),
        "max_abs_dxe_dlnS_HeII":float(np.max(np.abs(j_e[:,2]))),
        "source_outer_moment_box":list(zip(dlo.tolist(),dhi.tolist())),
        "finite_cases":exact_cases,
        "csvsha256":digest,"central":"28/88","canonical_delta":0
    },sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    actual_original_science(args.repo,args.out)
