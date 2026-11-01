#!/usr/bin/env python3
"""Four original-group three-moment aggregate photon allocation witness.

Exactly one native accepted tick160 46,080-cell source snapshot; no new
history, per-node atlas, producer implementation or worker mutation.
All source interval operations reuse the immutable original interval types.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import numpy as np

NODES=46080
SOURCE_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
CONTINUOUS_RHS_SHA="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36"
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def sha(path):
    obj=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for blk in iter(lambda:stream.read(1024*1024),b""):
            obj.update(blk)
    return obj.hexdigest()

def interval_pair(x):
    lo=float(np.asarray(x.lo))
    hi=float(np.asarray(x.hi))
    if not (math.isfinite(lo) and math.isfinite(hi) and lo<=hi):
        raise ArithmeticError("NONFINITE_OR_INVALID_ORIGINAL_PHOTON_INTERVAL")
    return [lo,hi]

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2])
    arg.add_argument("--out",type=Path,required=True)
    a=arg.parse_args()
    repo=a.repo.resolve()
    edge=load("rei_f05_moment_original_edge",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker=load("rei_f05_moment_original_worker",repo/edge.REL_STAGE/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    if sha(worker.KERNEL_PATH)!=KERNEL_SHA:
        raise ValueError("ORIGINAL_NATIVE_26EVENT_KERNEL_SHA_DRIFT")
    original=worker._kernel()
    rim=original.rim
    if sha(Path(rim.__file__))!=CONTINUOUS_RHS_SHA:
        raise ValueError("ORIGINAL_CONTINUOUS_PHOTON_OWNER_SHA_DRIFT")
    accepted,src=edge.source_state(repo/edge.REL_STAGE,LANE,worker.state_io)
    if src["archive_sha256"]!=SOURCE_SHA or src["accepted_array_sha256"]!=STATE_SHA:
        raise ValueError("ORIGINAL_ACCEPTED_PARENT_SOURCE_SHA_DRIFT")
    if accepted.population_lower.shape!=(NODES,5):
        raise ValueError("ORIGINAL_SPATIAL_NODE_NUMBER_DRIFT")
    phys,_,_,nH,nHe=worker._context(original,LANE)
    model=rim.ReducedIntervalModel.from_repo(repo)
    t=float(phys.forcing.duration_seconds(0))*160/131072
    forcing=model.forcing_bounds(t,t)
    pop=original._I(accepted.population_lower,accepted.population_upper)
    ss=[rim.iv.sum_interval(rim.iv.Interval(pop.lo[:,k],pop.hi[:,k]))
        for k in (0,2,3)]
    if any(interval_pair(v)[0]<=0 for v in ss):
        raise ValueError("POSITIVE_GLOBAL_MOMENTS_NOT_CERTIFIED")
    scale=rim.NH0_CM3*rim.iv.pow_const(1+forcing.z,2.0)*rim.MPC_CM
    rows=[]
    total_rate=rim.iv.Interval(0.0)
    total_heat=rim.iv.Interval(0.0)
    for group in range(4):
        cx=[
            scale*(float(model.inputs.sigma_cm2[0,group]) if model.inputs.owner_support[1,group] else 0.0)/model.n_h_total,
            rim.YHE*scale*(float(model.inputs.sigma_cm2[1,group]) if model.inputs.owner_support[2,group] else 0.0)/model.n_he_total,
            rim.YHE*scale*(float(model.inputs.sigma_cm2[2,group]) if model.inputs.owner_support[3,group] else 0.0)/model.n_h_total,
        ]
        E=forcing.external_subgrid[group]
        D=E
        parts=[]
        for source in range(3):
            term=cx[source]*ss[source]
            parts.append(term)
            D=D+term
        if interval_pair(D)[0]<=0:
            raise ArithmeticError("ORIGINAL_PHOTON_DENOMINATOR_NONPOSITIVE")
        qs=[x/D for x in parts]
        q0=E/D
        qsum=q0
        for q in qs:
            qsum=qsum+q
        cover=interval_pair(qsum)
        if cover[0]>1 or cover[1]<1:
            raise ArithmeticError("ORIGINAL_GROUP_PARTITION_EXCLUDES_ONE")
        eps=(
            float(model.excess_eV[0,group])*qs[0]+
            float(model.excess_eV[1,group])*qs[1]+
            float(model.excess_eV[2,group])*qs[2]
        )
        resolved_fraction=qs[0]+qs[1]+qs[2]
        group_rate=forcing.current[group]*resolved_fraction
        group_heat=forcing.current[group]*eps*rim.EV_ERG
        total_rate=total_rate+group_rate
        total_heat=total_heat+group_heat
        rows.append({
          "group":group,
          "original_j_photon_current_native_interval":interval_pair(forcing.current[group]),
          "original_external_opacity_interval":interval_pair(E),
          "original_total_opacity_interval":interval_pair(D),
          "HI_opacity_share_interval":interval_pair(qs[0]),
          "HeI_opacity_share_interval":interval_pair(qs[1]),
          "HeII_opacity_share_interval":interval_pair(qs[2]),
          "external_opacity_share_interval":interval_pair(q0),
          "four_owner_partition_interval":cover,
          "primary_excess_heat_per_incoming_group_photon_eV_interval":interval_pair(eps),
          "active_owner_support":[bool(model.inputs.owner_support[z,group]) for z in (1,2,3)],
          "resolved_photon_rate_original_units_interval":interval_pair(group_rate),
          "primary_photoheat_erg_s_interval":interval_pair(group_heat)
        })
    originals=tuple(rim.iv.Interval(pop.lo[:,j],pop.hi[:,j]) for j in range(5))
    native_hi,native_hei,native_heii,native_heat=model._explicit_photo_fields(originals,forcing)
    native_total_rate=rim.iv.sum_interval(native_hi+native_hei+native_heii)
    native_total_heat=rim.iv.sum_interval(native_heat)
    rateA=interval_pair(total_rate);rateB=interval_pair(native_total_rate)
    heatA=interval_pair(total_heat);heatB=interval_pair(native_total_heat)
    rate_overlap=rateA[0]<=rateB[1] and rateB[0]<=rateA[1]
    heat_overlap=heatA[0]<=heatB[1] and heatB[0]<=heatA[1]
    if not(rate_overlap and heat_overlap):
        raise ArithmeticError("ORIGINAL_GROUP_PARTITION_DISJOINT_FROM_NATIVE_46080_PHOTO_FIELDS")
    receipt={
      "schema":"REI_F05_NATIVE_TICK160_FOUR_GROUP_THREE_MOMENT_PARTITION_V1",
      "claim":"SOURCE_LOCKED_ORIGINAL_INTERVAL_GROUP_AGGREGATE_NOT_CONTINUUM_IVP",
      "original_nodes":NODES,
      "original_accepted_tick":"160/131072",
      "original_archive_sha256":SOURCE_SHA,
      "original_state_sha256":STATE_SHA,
      "original_kernel_sha256":KERNEL_SHA,
      "original_continuous_rhs_sha256":CONTINUOUS_RHS_SHA,
      "lane":LANE,"source_record":src["state_member"],
      "proper_time_s":t,
      "original_n_H_total":float(model.n_h_total),
      "original_n_He_total":float(model.n_he_total),
      "global_source_moment_particle_interval":{k:interval_pair(x) for k,x in zip(("HI","HeI","HeII"),ss)},
      "photon_groups":rows,
      "derived_group_resolved_rate_total_interval":rateA,
      "original_native_46080_node_resolved_rate_total_interval":rateB,
      "derived_group_primary_heat_total_erg_s_interval":heatA,
      "original_native_46080_node_primary_heat_erg_s_interval":heatB,
      "native_group_total_rate_overlap":rate_overlap,
      "native_group_total_heat_overlap":heat_overlap,
      "verified_partitions":4,
      "source_code_pinned":True,
      "no_production_mutation":True,
      "central_dag":"28/88_REPORTED","working_dag":"33/88_REPORTED",
      "physical_fast_dag":"4/7_REPORTED","canonical_delta":0,
      "continuum_tube_residual_log_norm":"NOT_COMPUTED"
    }
    out=a.out.resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "result":"ORIGINAL_FOUR_GROUP_INTERVAL_ALLOCATION_PASS",
      "node_count":NODES,
      "moment_ranges":receipt["global_source_moment_particle_interval"],
      "rows":[{"g":row["group"],"HI":row["HI_opacity_share_interval"],"HeI":row["HeI_opacity_share_interval"],"HeII":row["HeII_opacity_share_interval"],"external":row["external_opacity_share_interval"],"excess_eV":row["primary_excess_heat_per_incoming_group_photon_eV_interval"]} for row in rows],
      "canonical_delta":0},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
