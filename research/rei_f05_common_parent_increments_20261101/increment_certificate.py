#!/usr/bin/env python3
"""Original F05 [160,161] common-parent step-increment enclosures.

Crucial algebraic construction:
  A y_out = y_in, A=I+B  => A(delta y) = -B*y_in.
  log(T_out/T_in) = log1p(delta U/U_in)-log1p(delta Ne/Npart_in).
The actual original source-locked 26event run_step and unchanged three physical
lanes supply each F_h and G2(G1) stage. No source substitution or tolerance changes.

A correlated-increment bound can be conservative for true shared physical
histories even though native cross-output boxes are independent. The inherited
Krawczyk solver uses float64 and does not constitute MPFI-formal proof.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np

N=46080
SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
LOCAL_GATE=2e-4
PUBLIC_GATE=2e-3
ORIGINAL_FAIL=2.1245050576368385e-4
LANES=("LOCAL_NEUTRAL_HAZARD_PRIMARY","RECOMBINATION_WEIGHTED_AUDITOR",
       "SCRIPT_SELF_SHIELDING_AUDITOR")
CHANNELS=("x_HII","x_HeII","x_HeIII","log_T")


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()


def interval_upper(q):
    return np.maximum(abs(np.asarray(q.lo)),abs(np.asarray(q.hi)))


def zero_contained(q):
    return (np.asarray(q.lo)<=0.0)&(np.asarray(q.hi)>=0.0)


def original_matrix_delta_rhs(m,lower,upper,parent):
    """Outward interval of -(A-I)p for the exact ORIGINAL positive MPRK blocks."""
    lo=np.asarray(lower,float);hi=np.asarray(upper,float)
    Plo=np.asarray(parent.lo,float);Phi=np.asarray(parent.hi,float)
    if lo.shape!=hi.shape or lo.ndim!=3 or lo.shape[1]!=lo.shape[2]:
        raise ValueError("INVALID_NATIVE_MPRK_MATRIX")
    n,k,_=lo.shape
    if Plo.shape!=(n,k) or Phi.shape!=Plo.shape:
        raise ValueError("INVALID_NATIVE_MPRK_PARENT")
    if np.any(lo>hi) or np.any(Plo>Phi) or np.any(~np.isfinite(lo)):
        raise ValueError("NONFINITE_OR_INVERTED_NATIVE_SOURCE")
    # Matrix interval entries include identity + rate. The exact identity is
    # subtracted from the SAME enclosure, not a separate state interval.
    # IEEE 754 subtraction of 1.0 from a finite binary64 number in [0.5,2)
    # is exact by Sterbenz's lemma; outward expand in either case.
    Blo=np.nextafter(lo-np.eye(k)[None,:,:],-np.inf)
    Bhi=np.nextafter(hi-np.eye(k)[None,:,:],np.inf)
    outlo=np.empty((n,k));outhi=np.empty((n,k))
    for i in range(k):
        summ=m._I(np.zeros(n))
        for j in range(k):
            a=m._I(Blo[:,i,j],Bhi[:,i,j])
            b=m._I(Plo[:,j],Phi[:,j])
            summ=summ+a*b
        neg=-summ
        outlo[:,i]=neg.lo
        outhi[:,i]=neg.hi
    return outlo,outhi


def krawczyk_increment(m,parent,flux,den,dt,nh,nhe):
    """Two validated linear systems for original H(2), He(3) FINAL corrector."""
    A_lo,A_hi=m._matrix_interval(flux,den,dt)
    lo=np.empty_like(parent.lo);hi=np.empty_like(parent.hi)
    stats=[]
    for sl in (slice(0,2),slice(2,5)):
        P=m._I(parent.lo[:,sl],parent.hi[:,sl])
        blo,bhi=original_matrix_delta_rhs(m,A_lo[:,sl,sl],A_hi[:,sl,sl],P)
        cert=m.cert.linear_interval_krawczyk(A_lo[:,sl,sl],A_hi[:,sl,sl],blo,bhi)
        passed=int(np.count_nonzero(cert.certified))
        stats.append({"block": "H" if sl.start==0 else "He",
                      "certified_nodes":passed,"nodes":N,
                      "max_row_sum":float(np.max(cert.row_sum_bound)),
                      "max_radius":float(np.max(cert.krawczyk_radius))})
        if passed!=N:
            raise ArithmeticError(f"ORIGINAL_{sl.start}_INCREMENT_KRAWCZYK_FAILURE:{N-passed}")
        lo[:,sl]=np.nextafter(cert.center-cert.krawczyk_radius,-np.inf)
        hi[:,sl]=np.nextafter(cert.center+cert.krawczyk_radius,np.inf)
    dp=m._I(lo,hi)
    nucleiH=m._I(dp.lo[:,0],dp.hi[:,0])+m._I(dp.lo[:,1],dp.hi[:,1])
    nucleiHe=(m._I(dp.lo[:,2],dp.hi[:,2])+m._I(dp.lo[:,3],dp.hi[:,3])
              +m._I(dp.lo[:,4],dp.hi[:,4]))
    if not np.all(zero_contained(nucleiH)&zero_contained(nucleiHe)):
        raise ValueError("ORIGINAL_H_HE_NUCLEI_INCREMENT_NOT_ZERO_ENCLOSED")
    return dp,stats


def incremental_thermochemical_state(m,parentpop,parentlog,dp,Rgamma,Rfinal,dt,nh,nhe):
    """Common-parent log T increment, with exact conservation of nucleus totals."""
    if np.any(np.asarray(nh)<=0) or np.any(np.asarray(nhe)<=0):
        raise ValueError("NONPOSITIVE_ORIGINAL_H_HE_NUCLEI")
    if dt<=0:raise ValueError("NONPOSITIVE_ORIGINAL_STEP_DURATION")
    g=float(m.sdirk.GAMMA)
    ne=(m._I(parentpop.lo[:,1],parentpop.hi[:,1])
        +m._I(parentpop.lo[:,3],parentpop.hi[:,3])
        +2*m._I(parentpop.lo[:,4],parentpop.hi[:,4]))
    n0=m._I(nh+nhe)+ne
    dne=(m._I(dp.lo[:,1],dp.hi[:,1])
         +m._I(dp.lo[:,3],dp.hi[:,3])
         +2*m._I(dp.lo[:,4],dp.hi[:,4]))
    # Underlying original native kinetic U=3/2 k_B T * N_particles
    U0=1.5*m.KB*n0*m.iv.exp(parentlog)
    dU=dt*((1-g)*Rgamma+g*Rfinal)
    thermal=1+dU/U0
    material=1+dne/n0
    if np.any(np.asarray(thermal.lo)<=0) or np.any(np.asarray(material.lo)<=0):
        raise ArithmeticError("LOG_T_INCREMENT_POSITIVITY_NOT_CERTIFIED")
    dz=m.iv.log(thermal)-m.iv.log(material)
    deriv={
      "x_HII":m._I(dp.lo[:,1],dp.hi[:,1])/m._I(nh),
      "x_HeII":m._I(dp.lo[:,3],dp.hi[:,3])/m._I(nhe),
      "x_HeIII":m._I(dp.lo[:,4],dp.hi[:,4])/m._I(nhe),
      "log_T":dz,
    }
    if any(np.any(~np.isfinite(v.lo)) or np.any(~np.isfinite(v.hi)) for v in deriv.values()):
        raise ArithmeticError("INCREMENT_NOT_FINITE")
    return deriv,{"thermal_log_ratio_max_upper":float(np.max(interval_upper(m.iv.log(thermal)))),
                  "electron_log_ratio_max_upper":float(np.max(interval_upper(m.iv.log(material)))),
                  "logT_increment_max_upper":float(np.max(interval_upper(dz)))}


def original_map(m,model,base,label,pop,logt,t0,t1,nh,nhe):
    saved_pop=m.population_step
    saved_root=m.thermal_root
    pops=[];roots=[]
    def traced_pop(parent,flux,den,dt,total_h,total_he):
        q=saved_pop(parent,flux,den,dt,total_h,total_he)
        pops.append((parent,flux,den,dt,q))
        return q
    def traced_root(*args,**kwargs):
        q=saved_root(*args,**kwargs)
        roots.append(q)
        return q
    try:
        m.population_step=traced_pop
        m.thermal_root=traced_root
        step=m.run_step(model,base,parent_pop=pop,parent_logt=logt,
                        t0=t0,t1=t1,total_h=nh,total_he=nhe)
    finally:
        m.population_step=saved_pop
        m.thermal_root=saved_root
    receipt={"name":label,"status":step.classification,"native_certified":bool(step.certified),
             "original_population_solves":len(pops),"original_root_calls":len(roots),
             "original_table_event_count":int(sum(bool(e.any_event) for e in step.table_events)),
             "original_native_diagnostics":step.diagnostics}
    if not step.certified:
        return step,None,receipt
    if len(pops)!=3 or len(roots)<3 or not all(r.certified for r in roots[-2:]):
        raise ArithmeticError("ORIGINAL_NATIVE_CORRECTOR_ROOT_MISSING")
    corrector=pops[-1]
    # Original MPRK correction is A(p,flux,den,dt) p_out=p_in.
    if corrector[0] is not pop:
        raise ArithmeticError("CORRECTOR_PARENT_IDENTITY_NOT_SAME")
    dp,stats=krawczyk_increment(m,*corrector[:4],nh,nhe)
    receipt["increment_krawczyk_blocks"]=stats
    delta,extra=incremental_thermochemical_state(m,pop,logt,dp,
                roots[-2].rhs,roots[-1].rhs,float(t1-t0),nh,nhe)
    receipt.update(extra)
    # Numerical cross-inclusion is a necessary consistency check, not
    # evidence of tightness or a formal roundoff certificate.
    z_overlap=(pop.lo[:,1]+dp.lo[:,1]<=step.population.hi[:,1]) & (
               pop.hi[:,1]+dp.hi[:,1]>=step.population.lo[:,1])
    if not np.all(z_overlap):
        raise ArithmeticError("COMMON_PARENT_INCREMENT_DISJOINT_FROM_NATIVE_MPRK")
    newlog=pop.lo[:,1]  # no need to materialize full high-dimensional images
    del newlog
    znew=logt+delta["log_T"]
    if np.any((znew.lo>step.log_temperature.hi)|(znew.hi<step.log_temperature.lo)):
        raise ArithmeticError("COMMON_PARENT_THERMAL_INCREMENT_DISJOINT_FROM_NATIVE_ROOT")
    receipt["x_HII_consistency_overlap_nodes"]=int(np.count_nonzero(z_overlap))
    receipt["logT_consistency_overlap_nodes"]=N
    return step,delta,receipt



def original_set_ledger_with_totals(m,model,second,mid,stop,nh,nhe):
    pop=second.population
    ledgers={
      "H_nuclei":(float(np.min((pop.lo[:,0]+pop.lo[:,1])-nh)),
                  float(np.max((pop.hi[:,0]+pop.hi[:,1])-nh))),
      "He_nuclei":(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-nhe)),
                   float(np.max(np.sum(pop.hi[:,2:5],axis=1)-nhe)))
    }
    for prefix,event,pbox,clock in (
        ("stage",second.stage_event,second.population,
           mid+m.sdirk.GAMMA*(stop-mid)),
        ("final",second.final_event,second.population,stop)):
        ledgers[prefix+"_photon_identity"]=(
            float(np.min(event.photon_identity.lo)),
            float(np.max(event.photon_identity.hi)))
        total=event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
        ledgers[prefix+"_total_energy"]=(float(np.min(total.lo)),float(np.max(total.hi)))
        for g,residual in enumerate(m.group_photon_residuals(model,pbox,clock)):
            ledgers[f"{prefix}_group_{g}_photon"]=(
                float(np.asarray(residual.lo)),float(np.asarray(residual.hi)))
    audit=m.primitive.audit_set_ledgers(ledgers)
    return {"passed":bool(audit.all_include_zero),"failed_ledgers":list(audit.failed),
            "evaluated_ledgers":len(ledgers),
            "first_failed_witnesses":[(k,ledgers[k]) for k in audit.failed[:5]]}

def to_csv(path,cols):
    if any(np.asarray(v).shape!=(N,) or not np.isfinite(v).all() for v in cols.values()):
        raise ValueError("CORRELATION_AWARE_DATA_INVALID")
    with path.open("wb") as stream:
        with gzip.GzipFile(fileobj=stream,filename="",mode="wb",mtime=0,compresslevel=6) as gz:
            with io.TextIOWrapper(gz,encoding="utf-8",newline="") as h:
                w=csv.writer(h);w.writerow(["node",*cols])
                for i in range(N):
                    w.writerow([i,*[format(float(v[i]),".17g") for v in cols.values()]])
    return sha(path)


def run(repo:Path,lane:str,out:Path):
    if lane not in LANES:raise ValueError("INVALID_ORIGINAL_LANE")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    report={"schema":"REI_26EVENT_TICK160_COMMON_PARENT_INCREMENT_ENCLOSURE_V1",
            "original_parent_pr":347,
            "original_parent_head":"6a0f0a9e70d3f4f1dac5be00ddd1c6153f5ade85",
            "frozen_original_archive_sha256":SOURCE_SHA,
            "original_state_array_sha256":STATE_SHA,
            "original_26event_kernel_sha256":KERNEL_SHA,
            "original_accepted_tick":"160/131072",
            "original_nodes":N,"original_shape_lane":lane,
            "original_local_error_gate":LOCAL_GATE,
            "original_public_width_gate":PUBLIC_GATE,
            "original_failed_independent_logT_upper":ORIGINAL_FAIL,
            "full_allX_jacobian_hessian_certificate":False,
            "production":"HOLD","no_merge":True,"no_tolerance_relaxation":True,
            "auto_next_node":False,
            "canonical_delta":0,"central_dag":"28/88_REPORTED",
            "working_dag":"33/88_REPORTED","fast_dag":"4/7_REPORTED",
            "steps":{}}
    def checkpoint():
        (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    checkpoint()
    edge=load("rei_f05_original_edge",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    stage=repo/edge.REL_STAGE
    worker=load("rei_f05_original_worker",stage/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    if sha(worker.KERNEL_PATH)!=KERNEL_SHA:raise ValueError("FROZEN_ORIGINAL_KERNEL_DRIFT")
    decoded,source=edge.source_state(stage,lane,worker.state_io)
    if source["archive_sha256"]!=SOURCE_SHA or source["accepted_array_sha256"]!=STATE_SHA:
        raise ValueError("ORIGINAL_SOURCE_AUTHORITY_DRIFT")
    base,initial,initial_log,nh,nhe=worker._context(m,lane)
    if len(nh)!=N:raise ValueError("SOURCE_NODE_NUMBER_DRIFT")
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    duration=float(base.forcing.duration_seconds(0))
    start=duration*160/131072;stop=duration*161/131072;mid=(start+stop)/2
    P=m._I(decoded.population_lower,decoded.population_upper)
    Z=m._I(decoded.log_temperature_lower,decoded.log_temperature_upper)
    maps={};deltas={}
    prev=None
    for label,pt,zt,a,b in (("full",P,Z,start,stop),("half1",P,Z,start,mid),
                            ("half2",None,None,mid,stop)):
        if label=="half2":
            if "half1" not in maps:break
            pt=maps["half1"].population
            zt=maps["half1"].log_temperature
        try:
            step,delta,receipt=original_map(m,model,base,label,pt,zt,a,b,nh,nhe)
        except Exception as exc:
            report["steps"][label]={"status":"INCREMENT_CONSTRUCTION_FAILURE",
                                    "kind":type(exc).__name__,"message":str(exc)}
            report["status"]="INCREMENT_CONSTRUCTION_BLOCKED"
            checkpoint()
            raise
        report["steps"][label]=receipt
        checkpoint()
        if not step.certified:
            report["status"]="ORIGINAL_NATIVE_MAP_FAILED"
            checkpoint()
            break
        maps[label]=step;deltas[label]=delta
    if len(deltas)!=3:
        print(json.dumps({"status":report.get("status"),"canonical_delta":0}),flush=True)
        return report
    cols={"source_tick160_parent_lnT_center":0.5*(Z.lo+Z.hi)}
    outputs={}
    allpass=True
    for name in CHANNELS:
        full=deltas["full"][name]
        half=deltas["half1"][name]+deltas["half2"][name]
        D=full-half
        bound=interval_upper(D)
        accepted=bool(np.all(bound<LOCAL_GATE))
        allpass&=accepted
        outputs[name]={"maximum_original_full_increment_upper":float(np.max(interval_upper(full))),
                       "maximum_original_twohalf_increment_upper":float(np.max(interval_upper(half))),
                       "max_correlated_increment_defect_upper":float(np.max(bound)),
                       "p95_correlated_increment_defect_upper":float(np.percentile(bound,95)),
                       "nodes_below_unchanged_2eMinus4":int(np.count_nonzero(bound<LOCAL_GATE)),
                       "all_nodes_below_original_gate":accepted}
        cols[f"{name}_original_full_increment_lower"]=full.lo
        cols[f"{name}_original_full_increment_upper"]=full.hi
        cols[f"{name}_original_twohalf_increment_lower"]=half.lo
        cols[f"{name}_original_twohalf_increment_upper"]=half.hi
        cols[f"{name}_joint_input_cancelled_defect_lower"]=D.lo
        cols[f"{name}_joint_input_cancelled_defect_upper"]=D.hi
        cols[f"{name}_joint_input_cancelled_defect_abs_upper"]=bound
    final=maps["half2"]
    sf=maps["full"]
    max_width=max(
         float(np.max(final.log_temperature.hi-final.log_temperature.lo)),
         float(np.max(sf.log_temperature.hi-sf.log_temperature.lo)),
         *[float(np.max(v)) for v in (
             (final.population.hi[:,1]-final.population.lo[:,1])/nh,
             (final.population.hi[:,3]-final.population.lo[:,3])/nhe,
             (final.population.hi[:,4]-final.population.lo[:,4])/nhe)]
    )
    report["original_output_max_public_width"]=max_width
    report["increment_defect_coordinates"]=outputs
    report["all_original_4_channel_local_defects_below_gate"]=bool(allpass)
    report["original_public_width_pass"]=max_width<PUBLIC_GATE
    report["original_native_table_event_pass"]=all(
         report["steps"][k]["original_table_event_count"]==0
         for k in ("full","half1","half2"))
    historic=np.maximum(abs(sf.log_temperature.lo-final.log_temperature.hi),
                       abs(sf.log_temperature.hi-final.log_temperature.lo))
    report["historical_crossbox_logT_check"]=float(np.max(historic))
    report["original_set_ledgers"]=original_set_ledger_with_totals(
         m,model,maps["half2"],mid,stop,nh,nhe)
    report["original_set_ledger_pass"]=report["original_set_ledgers"]["passed"]
    if not report["original_set_ledger_pass"]:
        report["status"]="ORIGINAL_SET_LEDGER_EXCLUDES_ZERO_NO_PROMOTION"
    report["source_derived_model_rows"]=N
    path=out/"REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz"
    report["csv_file"]=path.name
    report["csv_sha256"]=to_csv(path,cols)
    report["csv_columns"]=len(cols)+1
    report["status"]=("SCOPED_SOURCE_REAL_F05_INCREMENT_GATE_CANDIDATE_PASS"
        if allpass and max_width<PUBLIC_GATE and report["original_native_table_event_pass"]
            and report["original_set_ledger_pass"]
        else "SCOPED_SOURCE_REAL_F05_INCREMENT_BOUND_ABOVE_GATE")
    # This script NEVER calls production history code, never accepts tick161
    # or changes original canonical DAG, even when its separate scope passes.
    report["original_first_canonical_interval"]="BLOCKED_UNTIL_ORIGINAL_OWNER_ADMISSION"
    checkpoint()
    print(json.dumps({"lane":lane,"status":report["status"],
          "original_nodes":N,"max_logT_increment_bound":outputs["log_T"]["max_correlated_increment_defect_upper"],
          "original_independent_crossbox_logT":report["historical_crossbox_logT_check"],
          "max_width":max_width,
          "four_channel_candidate_gate":allpass,
          "canonical_delta":0,"csv_sha256":report["csv_sha256"]},sort_keys=True),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--lane",choices=LANES,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.repo.resolve(),a.lane,a.out)
