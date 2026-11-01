#!/usr/bin/env python3
"""REI original 26-event H/He: physically conserving parent-direction predictor JVP.

NOT a rigorous all-X D_h enclosure or canonical first-interval acceptance.
Global source derivative is exact; full directional derivative is numerical at
source-owned 46,080-cell finite input curves with original MPRK population solve.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, importlib.util, io, json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "research/rei_igm_tick160_global_photon_20261101/photon_global_feedback.py"
PREDICTOR = ROOT / "research/rei_igm_original26_predictor_moment_20261101/predictor_moments.py"
SOURCE_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
N = 46080
MODES = (("HI_to_HII", 0, 1), ("HeI_to_HeII", 2, 3))
KB = 1.380649e-16
EV_ERG = 1.602176634e-12
TICK = 160
TOTAL = 131072
GATE = 2e-4
WIDTH = 2e-3

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def A_from_flux(flux, population, dt, identity=True):
    """Original positive production/destroy MPRK matrix at a source point."""
    F = np.asarray(flux, dtype=np.float64)
    P = np.asarray(population, dtype=np.float64)
    if F.shape != (N,5,5) or P.shape != (N,5) or np.any(P<=0):
        raise ValueError("Wrong original 46080x5 H/He state")
    if not np.isfinite(F).all() or np.any(F<0):
        raise ValueError("Bad original source-event flux")
    A = np.zeros((N,5,5), dtype=np.float64)
    if identity: A[:,np.arange(5),np.arange(5)] = 1.0
    for src in range(5):
        for dst in range(5):
            if dst == src: continue
            rate = dt*F[:,dst,src]/P[:,src]
            A[:,dst,src] -= rate
            A[:,src,src] += rate
    return A

def A_directional_from_flux(flux, dflux, parent, dparent, dt):
    """Directional derivative of original MPRK column-conservative A.

    Separate the actual flux response and variation of each Patankar denominator.
    This avoids cancellation of two nearly identical full MPRK matrices.
    """
    flux=np.asarray(flux,float);dflux=np.asarray(dflux,float)
    parent=np.asarray(parent,float);dparent=np.asarray(dparent,float)
    dA=np.zeros((N,5,5),float)
    for src in range(5):
        for dst in range(5):
            if dst==src:continue
            slope=dt*(dflux[:,dst,src]/parent[:,src] -
                      flux[:,dst,src]*dparent[:,src]/(parent[:,src]**2))
            dA[:,dst,src]-=slope
            dA[:,src,src]+=slope
    return dA

def source_point(fb,mod,model,p,temp,t,nh,nhe,dt):
    """Fresh ORIGINAL 26-event positive H/He flux, not surrogate RHS."""
    if np.any(p<=0) or np.any(temp<=0): raise ValueError("Nonpositive original state")
    parent=mod._I(p)
    ev=mod.event_box(model,parent,mod._I(temp),t)
    flux=0.5*(np.asarray(ev.flux.lo)+np.asarray(ev.flux.hi))
    A=A_from_flux(flux,p,dt)
    ref=mod.population_step(parent,ev.flux,parent,dt,nh,nhe)
    if not ref.certified: raise ValueError("Original population Krawczyk failed")
    return A, ev, ref

def physical_direction(p,low,high,src,dst,scale=0.20):
    """H- or He-conserving one-parameter candidate inside original marginal boxes."""
    if not 0<scale<1: raise ValueError("Perturbation scale")
    amp=scale*np.maximum(0.0,np.minimum.reduce([
         p[:,src]-low[:,src], high[:,src]-p[:,src],
         p[:,dst]-low[:,dst], high[:,dst]-p[:,dst]]))
    direction=np.zeros_like(p)
    direction[:,src]=-amp; direction[:,dst]=amp
    for a in (-1.,1.):
        q=p+a*direction
        roundoff=16*np.finfo(float).eps*np.maximum.reduce([abs(low),abs(high),abs(q)])
        if np.any(q<low-roundoff) or np.any(q>high+roundoff):
            raise ValueError("Original marginal source enclosure broken")
        if np.any(q<=0):raise ValueError("Nonpositive physical parent point")
    return direction,amp

def group_source(fb,model,mod,p,t):
    """Original 4-group photon source; return exact group flux and coefficients."""
    force=model.forcing_bounds(t,t)
    z=fb.midpoint(force.z)
    C=fb.coefficients(model,mod,z)
    current=np.array([fb.midpoint(x) for x in force.current])
    external=np.array([fb.midpoint(x) for x in force.external_subgrid])
    S=np.array([np.sum(p[:,k],dtype=np.longdouble) for k in (0,2,3)],float)
    group=np.zeros((4,N,3));shares=np.zeros((4,3));dens=np.zeros(4)
    for g in range(4):
        sh,ext,den=fb.shares(S,C[g],external[g])
        group[g]=current[g]*p[:,(0,2,3)]*(C[g]/den)[None,:]
        shares[g]=sh;dens[g]=den
    return group,shares,C,current,dens,S

def photon_directional_components(group,shares,C,current,dens,S,dp,excess_eV):
    """Exact original photo rate direct numerator + global moment denominator."""
    dS=np.array([np.sum(dp[:,k],dtype=np.longdouble) for k in (0,2,3)],float)
    direct=np.zeros((N,3));global_nonlocal=np.zeros((N,3))
    dH_direct=np.zeros(N);dH_global=np.zeros(N)
    for g in range(4):
        base=group[g]
        dr_direct=current[g]*dp[:,(0,2,3)]*(C[g]/dens[g])[None,:]
        ratio=float(np.dot(C[g],dS)/dens[g])
        dr_global=-base*ratio
        direct+=dr_direct;global_nonlocal+=dr_global
        dH_direct+=dr_direct@excess_eV[:,g]*EV_ERG
        dH_global+=dr_global@excess_eV[:,g]*EV_ERG
    return direct,global_nonlocal,dH_direct,dH_global,dS

def transfer_matrix_rate(f,p,dt):
    F=np.zeros((N,5,5))
    for s,(src,dst) in enumerate(((0,1),(2,3),(3,4))):
        F[:,dst,src]=f[:,s]
    return A_from_flux(F,p,dt,identity=False)

def charge(v,nh):
    return (v[:,1]+v[:,3]+2*v[:,4])/nh

def write_gz(out,cols):
    out.mkdir(parents=True,exist_ok=True)
    name="ORIGINAL_26EVENT_PHYSICAL_PARENT_JVP_46080.csv.gz"
    path=out/name
    with open(path,"wb") as f:
        with gzip.GzipFile(fileobj=f,filename="",mtime=0,compresslevel=6) as z:
            with io.TextIOWrapper(z,encoding="utf8",newline="") as h:
                w=csv.writer(h);w.writerow(["node",*cols])
                for i in range(N):
                    w.writerow([i,*[format(float(cols[k][i]),".17g") for k in cols]])
    return name,hashlib.sha256(path.read_bytes()).hexdigest()

def main(repo,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    fb=load("rei_phys_parent_fb",ORIGINAL)
    old=load("rei_phys_parent_predictor",PREDICTOR)
    src,mod,model,pinitial,p,frozen,t=fb.context(repo)
    if frozen["array_sha"]!=STATE_SHA:raise ValueError("Frozen original array identity")
    orig_archive=repo/"stages"/fb.OLD/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
    if fb.sha(orig_archive)!=SOURCE_SHA:raise ValueError("Original source archive identity")
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=fb.LANES[0])
    init=np.asarray(base.inputs.state0.mutable_copy().values[:5].T,float)
    nh=init[:,0]+init[:,1];nhe=np.sum(init[:,2:5],axis=1)
    T=np.exp(0.5*(frozen["tl"]+frozen["th"]))
    dt=float(base.forcing.duration_seconds(0))/TOTAL
    A,ev,ref=source_point(fb,mod,model,p,T,t,nh,nhe,dt)
    y=old.batch_solve(A,p)
    tol=128*np.finfo(float).eps*np.maximum(np.abs(y),np.abs(p))
    if np.any(y<ref.lower-tol) or np.any(y>ref.upper+tol):
        raise ValueError("Representative original MPRK predictor escapes Krawczyk")
    group,shares,C,current,dens,S=group_source(fb,model,mod,p,t)
    eps=np.array(model.excess_eV)
    cols={"T_K":T,"source_parent_xHII":p[:,1]/nh,"original_predictor_xe":charge(y,nh)}
    reports={}
    for label,srcidx,dstidx in MODES:
        d,amp=physical_direction(p,frozen["lo"],frozen["hi"],srcidx,dstidx)
        if np.count_nonzero(amp)<N//100: raise ValueError("No meaningful source-parent mode")
        pos=p+d; neg=p-d
        Aplus,evplus,refplus=source_point(fb,mod,model,pos,T,t,nh,nhe,dt)
        Aminus,evminus,refminus=source_point(fb,mod,model,neg,T,t,nh,nhe,dt)
        yp=old.batch_solve(Aplus,pos); ym=old.batch_solve(Aminus,neg)
        for q,r in ((yp,refplus),(ym,refminus)):
            tt=128*np.finfo(float).eps*np.maximum(abs(q),abs(p))
            if np.any(q<r.lower-tt) or np.any(q>r.upper+tt):
                raise ValueError("Original source Krawczyk rejects physical endpoint")
        F0=.5*(ev.flux.lo+ev.flux.hi)
        Fplus=.5*(evplus.flux.lo+evplus.flux.hi)
        Fminus=.5*(evminus.flux.lo+evminus.flux.hi)
        derivA=A_directional_from_flux(F0,.5*(Fplus-Fminus),p,d,dt)
        tangent=old.batch_solve(A,d-np.einsum("nij,nj->ni",derivA,y))
        finite=.5*(yp-ym)
        direct,glob,dheatdir,dheatglob,dS=photon_directional_components(
            group,shares,C,current,dens,S,d,eps)
        Ag=transfer_matrix_rate(glob,p,dt)
        glob_y=-old.batch_solve(A,np.einsum("nij,nj->ni",Ag,y))
        local_y=tangent-glob_y
        # Cross-check direct global photon piece vs PR345 formal independent ell_k derivatives.
        J=old.implicit_predictor_derivatives(A,p,group,shares,dt)[1]
        gcheck=np.einsum("nks,k->ns",J,dS/S)
        global_rel=float(np.max(abs(gcheck-glob_y))/max(np.max(abs(glob_y)),np.max(abs(gcheck)),1e-160))
        if global_rel>5e-8:
            raise ValueError("Original 3-moment-source JVP mismatch")
        norm=float(max(np.max(abs(finite)),np.max(abs(tangent)),1e-160))
        num_error=float(np.max(abs(finite-tangent))/norm)
        if not np.isfinite(num_error) or num_error>3e-4:
            raise ValueError("Full physically coupled source directional derivative check failed")
        for u in (tangent,finite,glob_y,local_y):
            if np.any(~np.isfinite(u)):raise ValueError("Nonfinite original scientific JVP")
            for sl in (slice(0,2),slice(2,5)):
                # Inspect physically normalized conservation, not residual/small
                # directional signal, which can be dominated by float cancellation.
                denom=nh if sl.start==0 else nhe
                residual_fraction=float(np.max(abs(u[:,sl].sum(axis=-1))/denom))
                if residual_fraction>1e-12:
                    raise ValueError(f"H/He nuclei violation: {residual_fraction:.6g}")
        td=charge(tangent,nh);fd=charge(finite,nh);gd=charge(glob_y,nh);ld=charge(local_y,nh)
        he=1.5*KB*T*td
        ch=float(mod.rim.CHI_H_EV);ca=float(mod.rim.CHI_HEI_EV);cb=float(mod.rim.CHI_HEII_EV)
        bind=EV_ERG*(ch*tangent[:,1]+ca*tangent[:,3]+(ca+cb)*tangent[:,4])/nh
        H0=(dheatdir+dheatglob)/nh;Hg=dheatglob/nh
        cols[f"{label}_amplitude_ion_per_H"]=amp/nh
        cols[f"{label}_dxe_total_coupled_MPRK"]=td
        cols[f"{label}_dxe_finite_original_source"]=fd
        cols[f"{label}_dxe_global_photon"]=gd
        cols[f"{label}_dxe_other_local_electron_OTS"]=ld
        cols[f"{label}_d_photoheat_erg_H_s"]=H0
        cols[f"{label}_d_photoheat_global_only_erg_H_s"]=Hg
        cols[f"{label}_d_thermal_energy_erg_H"]=he
        cols[f"{label}_d_binding_energy_erg_H"]=bind
        absden=np.maximum(abs(td),1e-15)
        cols[f"{label}_global_fraction_abs_with_floor"]=abs(gd)/absden
        reports[label]={
          "amplitude_max_fraction_per_H":float(np.max(amp/nh)),
          "number_nonzero_amplitude_nodes":int(np.count_nonzero(amp)),
          "delta_neutral_global_fraction":(dS/S).tolist(),
          "median_total_electron_response":float(np.median(td)),
          "median_global_photon_electron_response":float(np.median(gd)),
          "max_abs_total_electron_response":float(np.max(abs(td))),
          "max_abs_global_photon_electron_response":float(np.max(abs(gd))),
          "max_abs_local_other_electron_response":float(np.max(abs(ld))),
          "median_ratio_global_abs_to_total_floor_1e-15":float(np.median(abs(gd)/absden)),
          "max_global_source_jvp_relative_error":global_rel,
          "max_finite_difference_JVP_relative_error":num_error,
          "max_abs_primary_photoheat_response_erg_H_s":float(np.max(abs(H0))),
          "nuclei_invariants":True,
          "original_positive_Krawczyk_endpoints":True
        }
        print("ORIGINAL_PHYSICAL_PARENT_JVP",label,json.dumps(reports[label],sort_keys=True),flush=True)
    file,digest=write_gz(out,cols)
    if not all(v.shape==(N,) and np.isfinite(v).all() for v in cols.values()):
        raise ValueError("Invalid 46080-node source physical columns")
    result={
      "schema":"REI_IGM_ORIGINAL26_PHYSICALLY_CONSERVING_PARENT_PREDICTOR_JVP_V1",
      "science_status":"ORIGINAL_SOURCE_PHYSICALLY_CONSERVING_DIRECTIONAL_JVP_NUMERICALLY_CHECKED",
      "input_origin":"PR345 originally frozen 46080-node tick160 state and original 26-event Krawczyk",
      "parent_source_sha256":SOURCE_SHA,"parent_state_sha256":STATE_SHA,
      "original_source_interval_only":"160/131072 accepted; [160,161] remains blocked",
      "actual_source_node_rows":N,"scientific_output_columns":len(cols),
      "original_one_microstep_seconds":dt,
      "model_temperature":"original parent logT midpoint held fixed",
      "modes":reports,
      "source_photon_groups":[{"g":g,"photon_current_per_s":float(current[g]),"active_in_binary64":bool(current[g]>np.finfo(float).tiny)} for g in range(4)],
      "original_production_model":"UNMODIFIED_26_EVENT_H_HE_PHOTO_OTS_COLLISIONAL_RECOMBINATION",
      "physical_parent_assumption":"nuclei-conserving within marginal accepted source intervals, not proven full reachable history",
      "global_decomposition_scope":"exact photon denominator component + other local/numerator/electron/OTS finite directional response",
      "true_all_X_non_linear_interval_remainder":"NOT_CONSTRUCTED",
      "original_full_minus_two_half":"NOT_RUN",
      "original_logT_failed_gate":2.1245050576368385e-4,
      "unchanged_strict_gate":GATE,"unchanged_width_gate":WIDTH,
      "canonical_Central":"28/88_REPORTED","working":"33/88_REPORTED","physical_fast":"4/7_REPORTED","canonical_delta":0,
      "production":"HOLD","no_merge":True,"no_force_push":True,
      "science_csv":file,"science_csv_sha256":digest
    }
    (out/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PHYSICAL_PARENT_SCIENCE_FINAL",json.dumps({"rows":N,"columns":len(cols),"sha256":digest,"modes":list(reports),"original_gate":"BLOCKED","central":"28/88","canonical_delta":0}),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=ROOT)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    main(a.repo,a.out)
