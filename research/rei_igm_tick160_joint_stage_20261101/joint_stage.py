#!/usr/bin/env python3
"""Real original-26-event all-X tick160 stage-source and thermal-root bound inputs.

This is a constructive stage-certificate input, NOT a whole D_h interval
Jacobian/remainder, and it cannot promote tick161 or change the locked gates.
The original interval integrator and frozen accepted source are never edited.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

N = 46080
SOURCE_SHA = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA = "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
LANES = ("LOCAL_NEUTRAL_HAZARD_PRIMARY", "RECOMBINATION_WEIGHTED_AUDITOR",
         "SCRIPT_SELF_SHIELDING_AUDITOR")
NEUTRAL = (0, 2, 3)
GATE = 2e-4
WIDTH = 2e-3
OLD_FAILURE = 2.1245050576368385e-4


def load(name: str, path: Path):
    s = importlib.util.spec_from_file_location(name, path)
    if s is None or s.loader is None:
        raise ImportError(str(path))
    v = importlib.util.module_from_spec(s)
    sys.modules[s.name] = v
    s.loader.exec_module(v)
    return v


def rational_rate_jvp(n, dn, c, dglobal, current, external):
    """EXACT directional derivative of original group J*c*n/(E+c·S).

    n,dn: (nodes,3). c: (3,). dglobal = sum_nodes(dn).
    The local numerator term is mandatory, not just denominator-only response.
    """
    n = np.asarray(n, float)
    dn = np.asarray(dn, float)
    c = np.asarray(c, float)
    if n.ndim != 2 or n.shape[1] != 3 or dn.shape != n.shape:
        raise ValueError("three neutral populations per original node")
    if c.shape != (3,) or np.asarray(dglobal).shape != (3,):
        raise ValueError("exactly three shared moments")
    if np.any(c < 0) or current < 0 or external < 0:
        raise ValueError("negative original photon coefficient")
    S = np.sum(n, axis=0, dtype=np.longdouble).astype(float)
    D = external + float(np.dot(c, S))
    if D <= 0 or not math.isfinite(D):
        raise ValueError("positive photon denominator required")
    return (current * c / D)[None, :] * (
        dn - n * (float(np.dot(c, dglobal)) / D)
    )


def rational_remainder_bound(n0, low, high, c, current, external):
    """Real-arithmetic analytical rectangular outer bound, fixed forcing.

    Float implementation is a *numeric* bound estimate, not MPFI/CRlibm
    verification. Global moments are shared within this ONE source evaluation.
    """
    n0, low, high = (np.asarray(q, float) for q in (n0, low, high))
    c = np.asarray(c, float)
    if n0.shape != low.shape or high.shape != low.shape or low.shape[1] != 3:
        raise ValueError("invalid population source-site box")
    # Reconstructing conserved H/He complements may change the last few
    # binary64 bits; reject a genuinely exterior point but outward-widen by
    # those ulps instead of silently clipping the physical original parent.
    scale = np.maximum.reduce([abs(low), abs(n0), abs(high),
                               np.full(low.shape, 1e-40)])
    tol = 64*np.finfo(float).eps*scale
    if (np.any(low < 0) or np.any(low > n0+tol)
            or np.any(n0 > high+tol)):
        raise ValueError("invalid point inside source-site box")
    low=np.minimum(low,n0)
    high=np.maximum(high,n0)
    if c.shape != (3,) or np.any(c < 0) or current < 0 or external < 0:
        raise ValueError("negative source group")
    S0 = np.sum(n0, axis=0, dtype=np.longdouble).astype(float)
    Sl = np.sum(low, axis=0, dtype=np.longdouble).astype(float)
    Sh = np.sum(high, axis=0, dtype=np.longdouble).astype(float)
    D0 = external + float(c @ S0)
    Dl = external + float(c @ Sl)
    Dh = external + float(c @ Sh)
    if not (0 < Dl <= D0 <= Dh) or not all(map(math.isfinite, (Dl, D0, Dh))):
        raise ValueError("NONPOSITIVE_OR_UNORDERED_GLOBAL_DENOMINATOR")
    rho = max(abs((Dl-D0)/D0), abs((Dh-D0)/D0))
    ratio = max(abs((Dl-D0)/Dl), abs((Dh-D0)/Dh))
    delta_n = np.maximum(abs(low-n0), abs(high-n0))
    lin = (current*c/D0)[None, :] * (delta_n+n0*rho)
    rem = lin * ratio
    return rem, {"denominator_lower":Dl,"denominator_center":D0,
                 "denominator_upper":Dh,"maximum_relative_denominator_move":rho,
                 "maximum_exact_nonlinear_factor":ratio}


def source_site(m, model, pop, temp, t, site, h, nh, nhe, ev):
    """Original 46080-node uncertain stage input, not a point-parent probe."""
    from numpy import finfo
    p0 = np.asarray(pop.lo)
    p1 = np.asarray(pop.hi)
    if p0.shape != (N,5) or np.asarray(temp.lo).shape != (N,):
        raise ValueError("ORIGINAL_SOURCE_NODE_SHAPE")
    # Preserve H and He nuclei of every ORIGINAL node in the expansion point.
    point = 0.5*p0+0.5*p1
    point[:,0] = nh-point[:,1]
    point[:,2] = nhe-point[:,3]-point[:,4]
    tol=64*np.finfo(float).eps*np.maximum.reduce(
        [abs(p0),abs(p1),np.broadcast_to(nh[:,None],p0.shape),
         np.broadcast_to(nhe[:,None],p0.shape)])
    if np.any(point <= 0) or np.any(point < p0-tol) or np.any(point > p1+tol):
        raise ValueError("NOT_A_NUCLEI_CONSERVING_INTERVAL_REPRESENTATIVE")
    force = model.forcing_bounds(float(t), float(t))
    z = float((np.asarray(force.z.lo)+np.asarray(force.z.hi))/2)
    scale = m.rim.NH0_CM3*(1+z)**2*m.rim.MPC_CM
    den = (model.n_h_total, model.n_he_total, model.n_h_total)
    rates = np.zeros((N,3))
    heat = np.zeros(N)
    heat_rem = np.zeros(N)
    groups = []
    for g in range(4):
        c = np.zeros(3)
        for s in range(3):
            owner=(1,2,3)[s]
            if bool(model.inputs.owner_support[owner,g]):
                c[s]=float(model.inputs.sigma_cm2[s,g])*scale
                if s>0:c[s]*=m.rim.YHE
                c[s]/=den[s]
        current = float((force.current[g].lo+force.current[g].hi)/2)
        ext = float((force.external_subgrid[g].lo+force.external_subgrid[g].hi)/2)
        if current <= finfo(float).tiny:
            groups.append({"group":g,"status":"UNRESOLVED_SUBNORMAL_OR_ZERO_CURRENT",
                           "original_current_photons_s":current})
            continue
        rem, diag = rational_remainder_bound(
            point[:,NEUTRAL],p0[:,NEUTRAL],p1[:,NEUTRAL],c,current,ext
        )
        S = np.sum(point[:,NEUTRAL],axis=0,dtype=np.longdouble).astype(float)
        source = point[:,NEUTRAL]*(current*c/(ext+float(c@S)))[None,:]
        rates += source
        excess = np.asarray(model.excess_eV[:,g],float)
        heat += np.sum(source*excess[None,:],axis=1)*m.rim.EV_ERG
        heat_rem += np.sum(rem*abs(excess)[None,:],axis=1)*m.rim.EV_ERG
        groups.append({"group":g,"status":"SOURCE_BOX_NUMERIC_ESTIMATE",
                       "original_current_photons_s":current,
                       "group_photoevents_s":np.sum(source,axis=0).tolist(),
                       "max_node_group_photoevents_remainder_s":float(np.max(rem)),
                       **diag})
    # Independent exact-owner crosscheck. Parent box must contain every point.
    pops = tuple(m._I(p0[:,j],p1[:,j]) for j in range(5))
    original = model._explicit_photo_fields(pops,force)
    inclusion = []
    for j in range(3):
        ob = m.iv.sum_interval(original[j])
        v = float(np.sum(rates[:,j],dtype=np.longdouble))
        tol = 2e-8*max(abs(v),1e-70)
        inclusion.append(bool(float(ob.lo)-tol <= v <= float(ob.hi)+tol))
    ob = m.iv.sum_interval(original[3])
    v = float(np.sum(heat,dtype=np.longdouble))
    inclusion.append(bool(float(ob.lo)-2e-8*max(abs(v),1e-70)
                          <= v <= float(ob.hi)+2e-8*max(abs(v),1e-70)))
    if not all(inclusion):
        raise ValueError("ORIGINAL_PHOTON_AND_HEAT_OWNER_INTERVAL_INCLUSION_FAILED")
    thermal = {"status":"NO_ROOT_AT_PARENT_SITE"}
    if site != "parent":
        # This is the original frozen-photoheat partial thermal root derivative.
        # Coupling from photoheat(T) in the OUTER root iteration is not included.
        weighted = (h if site=="predictor" else h*m.sdirk.GAMMA)
        ctx = m.thermal_context(pop,force.volume_cm3,ev.photo_heat,force.hubble_s_inv)
        logt = m._I(np.log(temp.lo),np.log(temp.hi))
        d = m.thermal_root_derivative(ctx,logt,weighted)
        denom = ctx.ecoef*temp
        thermal = {
            "status":"FROZEN_HEAT_PARTIAL_ONLY_NOT_COUPLED_ROOT_CERTIFICATE",
            "original_partial_derivative_min_erg":float(np.min(d.lo)),
            "positive_partial_derivative_all_nodes":bool(np.all(d.lo>0)),
            "dimensionless_min_partial_derivative_ratio":
                float(np.min(d.lo/denom.hi)),
        }
    data = {
        "node_xHII_center":point[:,1]/nh,
        "node_T_center_K":0.5*(temp.lo+temp.hi),
        "primary_photoheat_center_erg_H_s":heat/nh,
        "source_population_only_heat_remainder_estimate_erg_H_s":heat_rem/nh
    }
    result = {"site":site,"source_time_seconds":float(t),
              "unique_original_nodes":N,"original_source_group_count":4,
              "active_groups":sum(g["status"]=="SOURCE_BOX_NUMERIC_ESTIMATE" for g in groups),
              "max_parent_population_width":float(np.max(p1-p0)),
              "max_parent_temperature_width_K":float(np.max(temp.hi-temp.lo)),
              "primary_heat_total_erg_s":v,
              "maximum_heat_remainder_estimate_erg_H_s":float(np.max(heat_rem/nh)),
              "original_owner_inclusion":inclusion,"thermal":thermal,"groups":groups}
    return result, data


def run(repo:Path,lane:str,out:Path):
    edge = load("rei_joint_edge",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    stage = repo/edge.REL_STAGE
    worker = load("rei_joint_original_worker",stage/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    m = worker._kernel()
    if edge.sha256(worker.KERNEL_PATH)!=KERNEL_SHA:
        raise ValueError("ORIGINAL_KERNEL_HASH_CHANGED")
    decoded,src=edge.source_state(stage,lane,worker.state_io)
    if src["archive_sha256"]!=SOURCE_SHA or src["accepted_array_sha256"]!=STATE_SHA:
        raise ValueError("ORIGINAL_PARENT_SOURCE_IDENTITY_CHANGED")
    base,y,logt,nh,nhe=worker._context(m,lane)
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    duration=float(base.forcing.duration_seconds(0))
    start=duration*160/131072;stop=duration*161/131072;mid=(start+stop)/2
    X=m._I(decoded.population_lower,decoded.population_upper)
    T=m._I(decoded.log_temperature_lower,decoded.log_temperature_upper)
    report={"schema":"REI_T160_FULL_UNCERTAIN_PARENT_STAGE_INPUTS_V1",
            "lane":lane,"original_source":src["archive_sha256"],
            "original_array_sha256":src["accepted_array_sha256"],
            "kernel_sha256":KERNEL_SHA,
            "ticks":"160_to_161_of_131072",
            "parent":"ORIGINAL_FULL_UNCERTAIN_BOX_NOT_REPRESENTATIVE",
            "source_forcing":"ORIGINAL_SAME_CLOCK_POINT_FOR_GROUP_DIAGNOSTICS",
            "source_remainder":"PER_SITE_FIXED_FORCING_NUMERIC_OUTER_ESTIMATE_NOT_MPFR_CERT",
            "thermal_derivative":"ORIGINAL_FROZEN_HEAT_PARTIAL_NOT_COUPLED_ROOT",
            "joint_full_map_jacobian_remainder_certified":False,
            "original_gate":GATE,"original_width_gate":WIDTH,
            "original_failing_cross_box_logT":OLD_FAILURE,
            "central_dag":"28/88_REPORTED","working_dag":"33/88_REPORTED",
            "physical_fast":"4/7_REPORTED","canonical_delta":0,
            "production":"HOLD","auto_next_node":False,"steps":{}}
    out.mkdir(parents=True,exist_ok=True)
    def save():
        (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    save()
    full=half1=half2=None
    arrays={}
    for label,pop,tlog,a,b in (("full",X,T,start,stop),("half1",X,T,start,mid),
                                ("half2",None,None,mid,stop)):
        if label=="half2":
            if half1 is None:break
            pop=half1.population;tlog=half1.log_temperature
        original=m.event_box
        slots={};count=[0]
        def traced(mm,p,temp,clock):
            event=original(mm,p,temp,clock)
            n=count[0];count[0]+=1
            site = "parent" if n==0 else "predictor" if n==1 else (
                   "gamma" if n%2==0 else "final")
            rec,data=source_site(m,model,p,temp,clock,site,b-a,nh,nhe,event)
            slots[site]=rec
            arrays[label+"_"+site]=data
            return event
        try:
            m.event_box=traced
            q=m.run_step(model,base,parent_pop=pop,parent_logt=tlog,t0=a,t1=b,
                         total_h=nh,total_he=nhe)
        except Exception as e:
            report["steps"][label]={"status":"ORIGINAL_SOURCE_STAGE_ERROR","error":str(e),
                                   "source_site_calls":count[0],"sites":slots}
            save()
            raise
        finally:
            m.event_box=original
        report["steps"][label]={"status":q.classification,
                 "certified":bool(q.certified),"source_site_calls":count[0],
                 "site_count":len(slots),"sites":slots,"diagnostics":q.diagnostics}
        save()
        if not q.certified:break
        if label=="full":full=q
        if label=="half1":half1=q
        if label=="half2":half2=q
    if full is not None and half2 is not None:
        al=full.log_temperature;bl=half2.log_temperature
        cross=np.maximum(abs(al.lo-bl.hi),abs(al.hi-bl.lo))
        report["independent_logT_cross_box_upper"]=float(np.max(cross))
        report["status"]="REAL_FULL_PARENT_STAGE_INPUTS_COMPUTED_NO_DH_CERT"
    else:
        report["status"]="ORIGINAL_FULL_PARENT_STAGE_FAILURE_PRESERVED"
    # Source-only arrays are sampled at a nuclei-conserving expansion point
    # of each original STAGE BOX, not an accepted history and not an all-X D_h.
    if arrays:
        np.savez_compressed(out/"SOURCE_SITE_FIELDS.npz",
                            **{f"{k}_{channel}":v for k,d in arrays.items()
                               for channel,v in d.items()})
        report["source_site_field_npz"]="SOURCE_SITE_FIELDS.npz"
        report["source_site_field_sha256"]=hashlib.sha256(
               (out/"SOURCE_SITE_FIELDS.npz").read_bytes()).hexdigest()
        report["actual_source_site_node_evaluations"]=N*len(arrays)
    save()
    print(json.dumps({"status":report["status"],"lane":lane,
                      "site_node_evaluations":report.get("actual_source_site_node_evaluations",0),
                      "cross_box_logT":report.get("independent_logT_cross_box_upper"),
                      "canonical_delta":0},sort_keys=True),flush=True)
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument("--lane",required=True,choices=LANES)
    ap.add_argument("--out",required=True,type=Path)
    z=ap.parse_args()
    run(z.repo.resolve(),z.lane,z.out)
