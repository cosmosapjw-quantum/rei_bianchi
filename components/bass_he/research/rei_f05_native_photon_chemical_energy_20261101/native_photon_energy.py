#!/usr/bin/env python3
"""Original REI 4-group accepted-tick160 H/He PHOTO-origin energy split.
Requires immutable source repo from REI PR355. NO new IVP or source mutation.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, sys
from pathlib import Path
import numpy as np

N=46080
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
RHS_SHA="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36"
CHI=(13.598434599702,24.587389011,54.41776)
SPECIES=("HI","HeI","HeII")
EV=1.602176634e-12
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None: raise ImportError(str(path))
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod; spec.loader.exec_module(mod)
    return mod

def pair(ivobj):
    lo=float(np.asarray(ivobj.lo)); hi=float(np.asarray(ivobj.hi))
    if not math.isfinite(lo) or not math.isfinite(hi) or lo>hi:
        raise ArithmeticError("INVALID_SOURCE_INTERVAL")
    return [lo,hi]

def overlap(a,b):
    return a[0]<=b[1] and b[0]<=a[1]

def mid(x):
    return (x[0]+x[1])/2

def generate(rei,out):
    repo=Path(rei).resolve()
    own=Path(__file__).resolve().parents[2]
    sp=load("bass_he_original_chi",own/"research/rei_pw19_spectral_native_bridge_20261101/spectral_physics.py")
    if tuple(sp.CHI[s] for s in SPECIES)!=CHI or sp.EV_ERG!=EV:
        raise ValueError("BASS_HE_IONIZATION_ENERGY_CONSTANTS_CHANGED")
    witness=load("rei_original_witness_for_bass_he",repo/"research/rei_f05_photon_moment_volterra_20261101/original_group_witness.py")
    edge=witness.load("rei_original_edge_for_bass_he",repo/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker=witness.load("rei_original_worker_for_bass_he",repo/edge.REL_STAGE/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    if sha(worker.KERNEL_PATH)!=KERNEL_SHA: raise ValueError("NATIVE_26_EVENT_KERNEL_SOURCE_DRIFT")
    original=worker._kernel(); rim=original.rim
    if sha(rim.__file__)!=RHS_SHA: raise ValueError("ORIGINAL_SOURCE_RHS_DRIFT")
    accepted,src=edge.source_state(repo/edge.REL_STAGE,LANE,worker.state_io)
    if src["archive_sha256"]!=TAR_SHA or src["accepted_array_sha256"]!=STATE_SHA:
        raise ValueError("NATIVE_ACCEPTED_STATE_DRIFT")
    if accepted.population_lower.shape!=(N,5): raise ValueError("ORIGINAL_46080_STATE_MISSING")
    model=rim.ReducedIntervalModel.from_repo(repo)
    proper_time_s=float(worker._context(original,LANE)[0].forcing.duration_seconds(0))*160/131072
    forcing=model.forcing_bounds(proper_time_s,proper_time_s)
    pop=original._I(accepted.population_lower,accepted.population_upper)
    S=[rim.iv.sum_interval(rim.iv.Interval(pop.lo[:,k],pop.hi[:,k])) for k in (0,2,3)]
    for x in S:
        if pair(x)[0]<=0: raise ValueError("NONPOSITIVE_NATIVE_SOURCE_MOMENT")
    scale=rim.NH0_CM3*rim.iv.pow_const(1+forcing.z,2.0)*rim.MPC_CM
    group_rows=[]; species_rows=[]
    rates=[rim.iv.Interval(0.) for s in SPECIES]
    binds=[rim.iv.Interval(0.) for s in SPECIES]
    heats=[rim.iv.Interval(0.) for s in SPECIES]
    total_native_heat=rim.iv.Interval(0.)
    derivative_coeffs=[]
    for g in range(4):
        a=[
            scale*(float(model.inputs.sigma_cm2[0,g]) if model.inputs.owner_support[1,g] else 0.)/model.n_h_total,
            rim.YHE*scale*(float(model.inputs.sigma_cm2[1,g]) if model.inputs.owner_support[2,g] else 0.)/model.n_he_total,
            rim.YHE*scale*(float(model.inputs.sigma_cm2[2,g]) if model.inputs.owner_support[3,g] else 0.)/model.n_h_total]
        ext=forcing.external_subgrid[g]; j=forcing.current[g]
        parts=[a[k]*S[k] for k in range(3)]
        den=ext+parts[0]+parts[1]+parts[2]
        if pair(den)[0]<=0: raise ValueError("NONPOSITIVE_NATIVE_OPACITY_DENOMINATOR")
        q=[(parts[k]/den if model.inputs.owner_support[k+1,g] else rim.iv.Interval(0.)) for k in range(3)]
        qext=ext/den
        partition=qext+q[0]+q[1]+q[2]
        if pair(partition)[0]>1 or pair(partition)[1]<1:
            raise ArithmeticError("NATIVE_PHOTON_PARTITION_FAILURE")
        gg={"group":g,"native_photon_current_per_s":pair(j),
            "original_external_opacity":pair(ext),
            "resolved_rate_per_s":None,"primary_photoheat_erg_s":None,
            "binding_power_erg_s":None,"material_electronic_power_erg_s":None,
            "external_fraction":pair(qext)}
        gr=rim.iv.Interval(0.); gb=rim.iv.Interval(0.); gh=rim.iv.Interval(0.)
        for k,s in enumerate(SPECIES):
            r=j*q[k]; b=r*(CHI[k]*EV); h=r*(float(model.excess_eV[k,g])*EV)
            rates[k]=rates[k]+r; binds[k]=binds[k]+b; heats[k]=heats[k]+h
            gr=gr+r; gb=gb+b; gh=gh+h
            species_rows.append({"group":g,"species":s,"supported":bool(model.inputs.owner_support[k+1,g]),
                "allocation_fraction":pair(q[k]),"photo_events_per_s":pair(r),
                "chemical_binding_power_erg_s":pair(b),"primary_heat_power_erg_s":pair(h),
                "material_electronic_power_erg_s":pair(b+h),
                "ionization_potential_eV":CHI[k],"source_excess_eV":float(model.excess_eV[k,g])})
        gg["resolved_rate_per_s"]=pair(gr)
        gg["binding_power_erg_s"]=pair(gb)
        gg["primary_photoheat_erg_s"]=pair(gh)
        gg["material_electronic_power_erg_s"]=pair(gb+gh)
        group_rows.append(gg)
        derivative_coeffs.append({"a":[mid(pair(c)) for c in a],
            "external":mid(pair(ext)),"J":mid(pair(j)),
            "excess":[float(model.excess_eV[k,g]) for k in range(3)]})
    native=rim.ReducedIntervalModel.from_repo(repo)
    native_rates=native._explicit_photo_fields(
        tuple(rim.iv.Interval(pop.lo[:,k],pop.hi[:,k]) for k in range(5)),forcing)
    direct_rates=[pair(rim.iv.sum_interval(native_rates[k])) for k in range(3)]
    direct_heat=pair(rim.iv.sum_interval(native_rates[3]))
    checks=[overlap(pair(rates[k]),direct_rates[k]) for k in range(3)]
    sum_rates=rates[0]+rates[1]+rates[2]
    sum_binding=binds[0]+binds[1]+binds[2]
    sum_heat=heats[0]+heats[1]+heats[2]
    if not all(checks) or not overlap(pair(sum_heat),direct_heat):
        raise ArithmeticError("ORIGINAL_NATIVE_FIELD_ENERGY_SPLIT_NOT_MATCHING")
    if not overlap(pair(sum_rates),pair(sum([rates[0],rates[1],rates[2]],rim.iv.Interval(0.)))):
        raise ArithmeticError("SOURCE_RATE_INTERVAL_ARITHMETIC")
    s_mid=np.array([mid(pair(s)) for s in S],dtype=float)
    def pof(logscale):
        sc=s_mid*np.exp(logscale)
        total=np.zeros(3)
        for dr in derivative_coeffs:
            den=dr["external"]+sum(dr["a"][k]*sc[k] for k in range(3))
            if den<=0: raise ValueError("BAD_NUMERIC_MOMENTS")
            q=np.array([dr["a"][k]*sc[k]/den for k in range(3)])
            e=np.array(dr["excess"])
            total += dr["J"]*EV*np.array([
                np.dot(q,np.array(CHI)),np.dot(q,e),np.dot(q,np.array(CHI)+e)])
        return total
    jac=np.zeros((3,3))
    for dr in derivative_coeffs:
        den=dr["external"]+sum(dr["a"][k]*s_mid[k] for k in range(3))
        q=np.array([dr["a"][k]*s_mid[k]/den for k in range(3)])
        for row,w in enumerate((np.array(CHI),np.array(dr["excess"]),np.array(CHI)+np.array(dr["excess"]))):
            jac[row,:]+=dr["J"]*EV*q*(w-np.dot(q,w))
    fd=np.zeros((3,3))
    hstep=2e-4
    for k in range(3):
        e=np.zeros(3);e[k]=hstep
        fd[:,k]=(pof(e)-pof(-e))/(2*hstep)
    scale_check=np.maximum(np.maximum(np.abs(jac),np.abs(fd)),1e-12*np.max(np.abs(jac)))
    rel_discrepancy=np.max(np.abs(jac-fd)/scale_check)
    if rel_discrepancy>1e-5: raise ArithmeticError(f"THREE_MOMENT_GRADIENT_CHECK_{rel_discrepancy}")
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    csvpath=out/"NATIVE_REI_T160_FOUR_GROUP_THREE_SPECIES_PHOTOENERGY_12ROWS.csv"
    with csvpath.open("w",newline="") as handle:
        writer=csv.writer(handle,lineterminator="\n")
        writer.writerow(("group","species","supported","rate_lo_s","rate_hi_s","binding_lo_erg_s","binding_hi_erg_s","heat_lo_erg_s","heat_hi_erg_s"))
        for r in species_rows:
            writer.writerow((r["group"],r["species"],int(r["supported"]),*r["photo_events_per_s"],
                *r["chemical_binding_power_erg_s"],*r["primary_heat_power_erg_s"]))
    rec={
        "schema":"BASS_HE_SOURCE_NATIVE_F05_T160_PHOTON_BINDING_ENERGY_V1",
        "science_scope":"ORIGINAL_FOUR_GROUP_FROZEN_T160_MATERIAL_SOURCE_NO_NEW_IVP",
        "original_accepted_tick":"160/131072","nodes_read":N,
        "original_REI_archive_sha256":TAR_SHA,"original_REI_array_sha256":STATE_SHA,
        "original_REI_native_kernel_sha256":KERNEL_SHA,"original_REI_RHS_sha256":RHS_SHA,
        "BASS_HE_ionization_source_sha256":sha(own/"research/rei_pw19_spectral_native_bridge_20261101/spectral_physics.py"),
        "source_repo_pr":355,"native_proper_time_s":proper_time_s,
        "native_four_groups":group_rows,"source_photochannels":species_rows,
        "species_aggregate":{s:{
            "photo_events_per_s":pair(rates[k]),
            "chemical_binding_power_erg_s":pair(binds[k]),
            "primary_heat_power_erg_s":pair(heats[k])} for k,s in enumerate(SPECIES)},
        "total_original_photoionization_per_s":pair(sum_rates),
        "total_chemical_binding_power_erg_s":pair(sum_binding),
        "total_primary_heat_power_erg_s":pair(sum_heat),
        "total_material_electronic_power_erg_s":pair(sum_binding+sum_heat),
        "original_native_direct_species_events_per_s":dict(zip(SPECIES,direct_rates)),
        "original_native_direct_primary_heat_erg_s":direct_heat,
        "direct_native_overlap":{"species":dict(zip(SPECIES,checks)),
            "heat":overlap(pair(sum_heat),direct_heat)},
        "exact_three_moment_dP_dlnS_erg_s":jac.tolist(),
        "central_difference_three_moment_dP_dlnS_erg_s":fd.tolist(),
        "three_moment_finite_difference_max_scaled_error":float(rel_discrepancy),
        "native_G3_photon_current_upper_subnormal":pair(forcing.current[3])[1],
        "original_source_changed":False,"photon_transport_admitted":False,
        "official_tick161":False,"production":"HOLD",
        "central_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
        "physical_fast_DAG":"4/7_REPORTED","BASS_HE_physical_DAG":"14/18_REPORTED",
        "canonical_delta":0,"native_subagent":"NOT_RUN",
        "blind_external_referee":"NOT_RUN","same_author_hostile_review":"SCOPED"
    }
    p=out/"SCIENCE_RESULT.json"
    p.write_text(json.dumps(rec,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"SOURCE_NATIVE_ORIGINAL_ENERGY_SPLIT_PASS",
        "events_per_s":pair(sum_rates),"Bdot_erg_s":pair(sum_binding),
        "Qdot_erg_s":pair(sum_heat),"HeII_events_per_s":pair(rates[2]),
        "Jacobian_max_scaled_err":float(rel_discrepancy),
        "12row_csv_sha256":sha(csvpath),"result_json_sha256":sha(p),
        "dag_central":"28/88","canonical_delta":0},sort_keys=True))
    return rec

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--rei-repo",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ar=ap.parse_args()
    generate(ar.rei_repo,ar.out)
