#!/usr/bin/env python3
"""Original REI 26-event H/He global-photon competition at frozen tick160.

The original model's _explicit_photo_fields shares one group denominator over
46,080 spatial nodes. The only global population coordinates entering each
photon-source evaluation are the THREE neutral-species sums HI, HeI, HeII.
No first-interval IVP, no complete nonlinear D_h enclosure or production switch.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,sys
from pathlib import Path
import numpy as np

SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_BLOB="ca2676c84b3c93766c59aa3ef81740565226dad9"
N=46080
L=160;NT=131072
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR","SCRIPT_SELF_SHIELDING_AUDITOR")
OLD="Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY"
PRED="Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK"
PREV="research/rei_igm_original_26event_tick160_20261101/source_26events.py"
INDICES=(0,2,3)
NAMES=("HI","HeI","HeII")

def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise ImportError(str(path))
    m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def midpoint(x):
    if hasattr(x,"lo"):return float(0.5*(np.asarray(x.lo)+np.asarray(x.hi)))
    return float(x)

def shares(source_moments, coefficients, ext):
    """p_s=C_s*S_s/(external+sum_s C_s*S_s)."""
    source_moments=np.asarray(source_moments,dtype=float)
    coefficients=np.asarray(coefficients,dtype=float)
    if source_moments.shape!=(3,) or coefficients.shape!=(3,):
        raise ValueError("wrong three-species moment/coefficient shape")
    if np.any(source_moments<0) or np.any(coefficients<0) or ext<0:
        raise ValueError("negative population/cross-section/external sink")
    a=source_moments*coefficients
    den=float(ext+np.sum(a))
    if not math.isfinite(den) or den<=0:raise ValueError("no absorbers/sink")
    p=a/den;pe=ext/den
    if not np.isfinite(p).all() or abs(float(np.sum(p)+pe)-1)>2e-14:
        raise ValueError("photon not normalized")
    return p,pe,den

def logmoment_jacobian(p):
    p=np.asarray(p,dtype=float)
    if p.shape!=(3,) or not np.isfinite(p).all() or np.any(p<0) or np.sum(p)>1+1e-12:
        raise ValueError("invalid channel probabilities")
    return np.diag(p)-np.outer(p,p)

def positive_outward_weight(coeff,scale,moment,upper=False):
    """Preserve exact structural channel zeros under outward IEEE-754 rounding."""
    c=np.asarray(coeff,dtype=float)
    a=c*scale*np.asarray(moment,dtype=float)
    direction=np.inf if upper else -np.inf
    widened=np.nextafter(a,direction)
    return np.where(c==0.0,0.0,np.maximum(0.0,widened))

def exact_interval_fraction(a_lo,a_hi,e_lo,e_hi):
    """Monotone, self-dependent fraction bounds for independent positive moment boxes."""
    a_lo=np.asarray(a_lo,dtype=float);a_hi=np.asarray(a_hi,dtype=float)
    if a_lo.shape!=(3,) or a_hi.shape!=(3,) or np.any(a_lo<0) or np.any(a_hi<a_lo):
        raise ValueError("negative or inverted source-moment box")
    if e_lo<0 or e_hi<e_lo:raise ValueError("inverted external sink")
    low=[];high=[]
    for s in range(3):
        dlo=a_lo[s]+np.sum(np.delete(a_hi,s))+e_hi
        dhi=a_hi[s]+np.sum(np.delete(a_lo,s))+e_lo
        if dlo<=0 or dhi<=0:raise ValueError("undefined photon fraction")
        low.append(max(0,float(np.nextafter(a_lo[s]/dlo,-np.inf))))
        high.append(min(1,float(np.nextafter(a_hi[s]/dhi,np.inf))))
    return np.asarray(low),np.asarray(high)

def exact_fraction_line_integral(s0,s1,c,e):
    """Numerical check of the exact analytic Jacobian via a linear source-moment path."""
    s0=np.asarray(s0,float);s1=np.asarray(s1,float)
    nodes,weights=np.polynomial.legendre.leggauss(32)
    delta=np.zeros(3);ds=s1-s0
    for x,w in zip(nodes,weights):
        s=s0+(x+1)*0.5*ds
        p,_,den=shares(s,c,e)
        # dp/dlambda = C_s ΔS_s/D - p_s sum_t C_t ΔS_t/D
        dp=(c*ds-p*np.dot(c,ds))/den
        delta+=0.5*w*dp
    a,_,_=shares(s0,c,e);b,_,_=shares(s1,c,e)
    return float(np.max(np.abs(delta-(b-a)))),delta

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def write_gz(path,columns):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as out:
        with gzip.GzipFile(fileobj=out,mode="wb",filename="",mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf8",newline="") as fd:
                wr=csv.writer(fd);wr.writerow(["node",*columns])
                n=len(next(iter(columns.values())))
                for i in range(n):
                    wr.writerow([i,*[format(float(v[i]),".17g") for v in columns.values()]])
    return sha(path)

def context(repo):
    old=repo/"stages"/OLD
    guard=load("rei_global_guard",old/"analysis/jax_import_guard.py")
    if not guard.install_if_missing():raise RuntimeError("original JAX import guard failed")
    source=load("rei_global_previous_source",repo/PREV)
    archive=old/"local_results/first_interval_r2_blocked_minimum_step.tar.gz"
    if sha(archive)!=SOURCE_SHA:raise ValueError("original source archive identity")
    states=source.archived_tick160(archive)
    if set(states)!=set(LANES) or {v["array_sha"] for v in states.values()}!={STATE_SHA}:
        raise ValueError("original three-lane tick160 state mismatch")
    mod=load("rei_global_source_map",repo/"stages"/PRED/"analysis/interval_discrete_map.py")
    model=mod.rim.ReducedIntervalModel.from_repo(repo)
    base=mod.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=LANES[0])
    start=base.inputs.state0.mutable_copy()
    pop0=np.asarray(start.values[:5].T,dtype=float)
    nh=pop0[:,0]+pop0[:,1];nhe=np.sum(pop0[:,2:5],axis=1)
    frozen=states[LANES[0]]
    pop1=source.representative(frozen["lo"],frozen["hi"],nh,nhe)
    if np.any(pop1<frozen["lo"]-1e-14) or np.any(pop1>frozen["hi"]+1e-14):
        raise ValueError("sample escapes original interval")
    t160=float(base.forcing.duration_seconds(0))*L/NT
    return source,mod,model,pop0,pop1,frozen,t160

def coefficients(model,mod,z):
    """Exactly reproduce original _explicit_photo_fields owner/YHe conventions."""
    scale=mod.rim.NH0_CM3*(1+z)**2*mod.rim.MPC_CM
    c=np.zeros((4,3),dtype=float)
    den=(model.n_h_total,model.n_he_total,model.n_h_total)
    for g in range(4):
        for s in range(3):
            owner=(1,2,3)[s]
            if bool(model.inputs.owner_support[owner,g]):
                v=float(model.inputs.sigma_cm2[s,g]) * scale
                if s>0:v*=mod.rim.YHE
                c[g,s]=v/den[s]
    if np.any(c<0) or not np.isfinite(c).all():raise ValueError("bad original source cross sections")
    return c

def original_source_interval(model,mod,p,forcing):
    pops=tuple(mod._I(p[:,j]) for j in range(5))
    ph,pe,pe2,heat=model._explicit_photo_fields(pops,forcing)
    return [mod.iv.sum_interval(x) for x in (ph,pe,pe2,heat)]

def do_case(mod,model,kind,p,plo,phi,t):
    forcing=model.forcing_bounds(t,t)
    z=midpoint(forcing.z)
    cm=coefficients(model,mod,z)
    jm=np.asarray([midpoint(x) for x in forcing.current],float)
    em=np.asarray([midpoint(x) for x in forcing.external_subgrid],float)
    sources=np.asarray([np.sum(p[:,j],dtype=np.longdouble) for j in INDICES],float)
    s_bounds=[mod.iv.sum_interval(mod._I(plo[:,j],phi[:,j])) for j in INDICES]
    slo=np.asarray([float(x.lo) for x in s_bounds]);shi=np.asarray([float(x.hi) for x in s_bounds])
    if np.any(sources<slo-1e-10*np.maximum(1,sources)) or np.any(sources>shi+1e-10*np.maximum(1,sources)):
        raise ValueError("population moment source box failed")
    zlo,zhi=float(forcing.z.lo),float(forcing.z.hi)
    rscale=(mod.rim.NH0_CM3*mod.rim.MPC_CM)
    scale_ratio_lo=((1+zlo)/(1+z))**2;scale_ratio_hi=((1+zhi)/(1+z))**2
    point_flux=np.zeros((len(p),3));local_deriv=np.zeros((len(p),3,3))
    rows=[];group_eps=np.zeros(4)
    for g in range(4):
        vec=cm[g];ev=em[g];pg,pe,den=shares(sources,vec,ev)
        obs=jm[g]
        W=logmoment_jacobian(pg)
        eig=np.linalg.eigvalsh(W)
        if eig[0]<-2e-13:raise ValueError("source photon susceptibility not PSD")
        det_expected=pe*float(np.prod(pg))
        if abs(np.linalg.det(W)-det_expected)>1e-12:raise ValueError("source determinant identity")
        lower_a=positive_outward_weight(vec,scale_ratio_lo,slo,upper=False)
        upper_a=positive_outward_weight(vec,scale_ratio_hi,shi,upper=True)
        lfrac,hfrac=exact_interval_fraction(lower_a,upper_a,float(forcing.external_subgrid[g].lo),float(forcing.external_subgrid[g].hi))
        if np.any(pg<lfrac-1e-12) or np.any(pg>hfrac+1e-12):
            raise ValueError("point photo distribution not enclosed")
        # Point conditional node source and its three GLOBAL-moment feedback columns.
        source_g=p[:,INDICES]*(obs*vec/den)[None,:]
        point_flux+=source_g
        local_deriv-=source_g[:,:,None]*pg[None,None,:]
        rows.append({"case":kind,"group":g,"time_s":t,"z_mean":z,
            "current_photons_per_s":float(obs),"external_fraction":float(pe),
            "source_sum_HI":float(sources[0]),"source_sum_HeI":float(sources[1]),"source_sum_HeII":float(sources[2]),
            "species_fraction":pg.tolist(),"species_fraction_lower":lfrac.tolist(),
            "species_fraction_upper":hfrac.tolist(),
            "absorbed_photons_per_s":(obs*pg).tolist(),
            "external_photons_per_s":float(obs*pe),
            "d_fraction_d_lnS":W.tolist(),"eigenvalues":eig.tolist(),
            "susceptibility_det":float(np.linalg.det(W)),
            "source_normalization_error":float(abs(float(np.sum(pg))+pe-1.0))})
        group_eps[g]=float(obs*pe)
    # Exact original source operator interval must enclose our point competitor sum.
    original=original_source_interval(model,mod,p,forcing)
    totals=np.sum(point_flux,axis=0)
    for s in range(3):
        bound=original[s];value=totals[s];tol=1e-9*max(1e-60,abs(value))
        if value<float(bound.lo)-tol or value>float(bound.hi)+tol:
            raise ValueError(f"source owner mismatch {NAMES[s]}: {value} not in [{bound.lo},{bound.hi}]")
    heat_total=0.0
    for row in rows:
        g=row["group"]
        heat_total+=sum(row["absorbed_photons_per_s"][s]*float(model.excess_eV[s,g])*mod.rim.EV_ERG for s in range(3))
    if not (float(original[3].lo)-1e-9*max(1e-60,abs(heat_total))<=heat_total<=float(original[3].hi)+1e-9*max(1e-60,abs(heat_total))):
        raise ValueError("original photoheat source ownership mismatch")
    summary={"case":kind,"time_s":float(t),"z":z,
        "photon_current_per_s":float(np.sum(jm)),
        "photo_species_photons_per_s":totals.tolist(),
        "external_subgrid_photons_per_s":float(np.sum(group_eps)),
        "source_photoheat_erg_per_s":float(heat_total),
        "max_photon_normalization_error":max(x["source_normalization_error"] for x in rows),
        "exact_source_operator_inclusion":True,"frozen_original_nodal_input":True}
    return rows,summary,point_flux,local_deriv,sources,cm,em

def main(repo,out):
    repo=repo.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    source,mod,model,p0,p1,frozen,t=context(repo)
    cases=[("initial_at_t0",p0,p0,p0,0.0),
           ("initial_at_tick160",p0,p0,p0,t),
           ("accepted_at_tick160",p1,frozen["lo"],frozen["hi"],t)]
    group_rows=[];summary=[];calcs={}
    for name,p,lo,hi,when in cases:
        r,s,point,deriv,mom,c,e=do_case(mod,model,name,p,lo,hi,when)
        group_rows.extend(r);summary.append(s);calcs[name]=(point,deriv,mom,c,e)
    initial=calcs["initial_at_tick160"];accept=calcs["accepted_at_tick160"]
    counterfactual=[]
    for gi in range(4):
        err,delta=exact_fraction_line_integral(initial[2],accept[2],initial[3][gi],initial[4][gi])
        p0g,_,_=shares(initial[2],initial[3][gi],initial[4][gi])
        p1g,_,_=shares(accept[2],accept[3][gi],accept[4][gi])
        if err>5e-13:raise ValueError("exact same-clock photon response integral mismatch")
        counterfactual.append({"group":gi,"delta_photon_absorption_fraction":(p1g-p0g).tolist(),
            "same_clock_jacobian_path_error":err,"source_current_held_fixed":True})
    p=accept[0];d=accept[1]
    cols={}
    for s,name in enumerate(NAMES):
        cols[f"original_photo_{name}_events_per_s"]=p[:,s]
    for s,name in enumerate(NAMES):
        for t,den in enumerate(NAMES):
            cols[f"d_photo_{name}_d_ln_global_{den}_events_per_s"]=d[:,s,t]
    cols["source_tick160_xHII"]=p1[:,1]/(p1[:,0]+p1[:,1])
    cols["source_tick160_T_K"]=np.exp(0.5*(frozen["tl"]+frozen["th"]))
    csvpath=out/"ORIGINAL_26EVENT_GLOBAL_PHOTON_JACOBIAN_46080.csv.gz"
    csvsha=write_gz(csvpath,cols)
    percentiles={k:{str(q):float(np.percentile(v,q)) for q in (0,5,50,95,100)} for k,v in cols.items()}
    report={"schema":"REI_IGM_TICK160_THREE_MOMENT_GLOBAL_PHOTON_FEEDBACK_V1",
        "original_archive_sha256":SOURCE_SHA,"state_array_sha256":STATE_SHA,
        "original_kernel_git_blob":KERNEL_BLOB,
        "science":"Original 26-event source original _explicit_photo_fields, H/He photon-sharing, exact low-rank global moment Jacobian; NOT a map derivative",
        "source_conditioned_models":3,"source_group_rows":len(group_rows),
        "unique_original_physical_nodes":N,"new_model_node_rows":N,
        "independent_observations":0,"new_cosmological_ivps":0,
        "group_rows":group_rows,"snapshots":summary,
        "same_clock_material_counterfactual":counterfactual,
        "nodewise_derivative_csv":csvpath.name,"nodewise_csv_sha256":csvsha,
        "nodewise_column_quantiles_equal_node":percentiles,
        "physical_population_interpretation":"tick160 is a nuclei-conserving representative of accepted source box, not unique dynamical physical parent",
        "original_model_global_coupling":"three species SUMS inside four group photon denominators; cannot treat 46080 source cells independently",
        "global_rank":"rank<=3 at EACH individual source evaluation site, not a proof about full multi-stage D_h Jacobian",
        "no_joint_full_half_enclosure":True,
        "original_160_161_local_error":2.1245050576368385e-4,
        "locked_gate":2e-4,
        "canonical_dag_reported":"28/88","working_dag_reported":"33/88","physical_fast_reported":"4/7","canonical_delta":0,
        "first_canonical_interval":"BLOCKED","production":"HOLD","no_merge":True,"no_force_push":True}
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("PHYSICAL_GLOBAL_PHOTON_RESULT",json.dumps({"groups":len(group_rows),"unique_nodes":N,
        "snapshots":summary,"same_clock_counterfactual":counterfactual,
        "nodewise_sha256":csvsha,"central":"28/88","delta":0},sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    a.add_argument("--out",type=Path,required=True)
    v=a.parse_args();main(v.repo,v.out)
