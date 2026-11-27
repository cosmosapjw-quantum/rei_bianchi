#!/usr/bin/env python3
"""Original REI 26-event H/He/OTS stoichiometric energy source, accepted tick160.
One physical nuclei-conserving source point + original accepted interval enclosure.
Requires matching original REI PR355 checkout; never mutates original REI.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, importlib.util, io, json, math, sys
from pathlib import Path
import numpy as np

N=46080
REI_HEAD="70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00"
TAR_SHA="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
ARRAY_SHA="cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
KERNEL_SHA="579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644"
RHS_SHA="b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36"
PARENT_RESULT_SHA="d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8"
CHI=np.array([13.598434599702,24.587389011,54.41776])
EV=1.602176634e-12
LANE="LOCAL_NEUTRAL_HAZARD_PRIMARY"
RATE_NAMES=("HI_ION","HEI_ION","HEII_ION","HII_CASE_B","HEII_GROUND","HEII_CASE_B","HEIII_GROUND","HEIII_N2","HEIII_CASCADE")

def sha(p):
    d=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            d.update(b)
    return d.hexdigest()

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:raise ImportError(str(path))
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def interval_pair(r):
    lo=float(np.asarray(r.lo)); hi=float(np.asarray(r.hi))
    if not(np.isfinite(lo) and np.isfinite(hi) and lo<=hi):
        raise ArithmeticError("INVALID_SOURCE_ORIGINAL_INTERVAL")
    return [lo,hi]

def native_sum(rim,interval):
    return interval_pair(rim.iv.sum_interval(interval))

def checksum_gzip(rows,columns,path):
    out=Path(path)
    with out.open("wb") as f, gzip.GzipFile(filename="",mode="wb",fileobj=f,mtime=0,compresslevel=6) as z:
        with io.TextIOWrapper(z,encoding="utf-8",newline="") as w:
            writer=csv.writer(w,lineterminator="\n")
            writer.writerow(columns)
            writer.writerows(rows)
    return sha(out)

def total_point(a):
    a=np.asarray(a)
    if not np.isfinite(a).all():raise ArithmeticError("SOURCE_NAN_OR_INF")
    return float(np.sum(a,dtype=np.float64))

def generate(rei,out):
    root=Path(__file__).resolve().parents[2]
    rei=Path(rei).resolve()
    if __import__("subprocess").check_output(["git","-C",str(rei),"rev-parse","HEAD"],text=True).strip()!=REI_HEAD:
        raise ValueError("ORIGINAL_REI_PR355_HEAD_CHANGED")
    psrc=root/"research/rei_f05_native_photon_chemical_energy_20261101/results/SCIENCE_RESULT.json"
    if sha(psrc)!=PARENT_RESULT_SHA:raise ValueError("IMMUTABLE_PR149_PHOTOENERGY_RESULT_DRIFT")
    pref=json.loads(psrc.read_text())
    w=load("original_rei355_ots_witness",rei/"research/rei_f05_photon_moment_volterra_20261101/original_group_witness.py")
    edge=load("original_rei355_ots_edge",rei/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
    worker=load("original_rei355_ots_worker",rei/edge.REL_STAGE/"analysis/attempt_worker.py")
    worker.jax_guard.install_if_missing()
    if sha(worker.KERNEL_PATH)!=KERNEL_SHA:raise ValueError("ORIGINAL_SEALED_26EVENT_KERNEL_DRIFT")
    original=worker._kernel()
    rim=original.rim
    if sha(rim.__file__)!=RHS_SHA:raise ValueError("ORIGINAL_CONTINUOUS_REDUCED_RHS_DRIFT")
    if not np.array_equal(CHI,np.array([rim.CHI_H_EV,rim.CHI_HEI_EV,rim.CHI_HEII_EV])):
        raise ValueError("CHEMICAL_IONIZATION_POTENTIAL_MISMATCH")
    accepted,srec=edge.source_state(rei/edge.REL_STAGE,LANE,worker.state_io)
    if srec["archive_sha256"]!=TAR_SHA or srec["accepted_array_sha256"]!=ARRAY_SHA:
        raise ValueError("ORIGINAL_ACCEPTED_F05_MATERIAL_DRIFT")
    model=rim.ReducedIntervalModel.from_repo(rei)
    phys,_,_,nH,nHe=worker._context(original,LANE)
    if len(nH)!=N or len(nHe)!=N:raise ValueError("NATIVE_CELL_GRAIN_CHANGED")
    point_pop=edge.element_conserving_parent_candidate(
        accepted.population_lower,accepted.population_upper,nH,nHe)
    point_logt=(accepted.log_temperature_lower+accepted.log_temperature_upper)/2.
    if not np.isfinite(point_logt).all():raise ValueError("T_LOG_NOT_FINITE")
    coord=np.vstack([point_pop[:,0]/model.n_h,point_pop[:,2]/model.n_he,
                     point_pop[:,4]/(point_pop[:,3]+point_pop[:,4]),point_logt])
    state=model.coordinates_to_state(coord)
    pop=state.values[:5].T
    T=state.temperature_K
    if pop.shape!=(N,5) or not np.allclose(pop,point_pop,atol=1.e-14,rtol=5.e-14):
        raise ValueError("REALIZED_26EVENT_STATE_NOT_ORIGINAL_CONSERVING_POINT")
    V=np.asarray(model.inputs.comoving_volume_cm3)/(1.+5.95)**3
    if (V<=0).any() or not np.isfinite(V).all():raise ValueError("ORIGINAL_VOLUME_INVALID")
    ne=(pop[:,1]+pop[:,3]+2*pop[:,4])/V
    f=0.1
    v=model.source_v_point(point_logt)
    if np.any((v<0)|(v>1)):raise ValueError("BAD_SOURCE_HUMMER_SEATON_PROBABILITY")
    duration=float(phys.forcing.duration_seconds(0))
    t0=duration*160/131072
    dt=duration/131072
    point_forcing=model.solver.forcing.point(interval=0,time_s=t0)
    owner=model.solver._owner(state,point_forcing)
    photo=model.solver.backend.photo_fields(owner)
    ev=model.event.evaluate_event_flux(populations=pop,temperature_K=T,
        proper_volume_cm3=V,photo_hi=photo.HI,photo_hei=photo.HeI,
        photo_heii=photo.HeII,v=v,f=np.full(N,f))
    point_photo=np.column_stack([photo.HI,photo.HeI,photo.HeII])
    native_ion=np.column_stack([ev.event_rates[n] for n in RATE_NAMES[:3]])
    collision=native_ion-point_photo
    # Distinct original-source microscopic collisional rates, independently.
    event= model.event
    collision_by_beta=np.column_stack([
        pop[:,0]*ne*event._beta_hi(T),
        pop[:,2]*ne*event._beta_hei(T),
        pop[:,3]*ne*event._beta_heii(T)])
    c_scale=np.maximum(np.abs(native_ion),1e-300)
    max_coll_reldiff=float(np.max(np.abs(collision-collision_by_beta)/c_scale))
    if max_coll_reldiff>6e-14 or np.any(collision<-1e-14*c_scale):
        raise ArithmeticError("SOURCE_IONIZATION_COLLISION_SPLIT_DIFFERENT")
    # Negative numerical roundoff for inactive/zero native groups must not be
    # interpreted as negative collisional events.
    nH_now=pop[:,0]+pop[:,1]
    nHe_now=pop[:,2]+pop[:,3]+pop[:,4]
    if not np.allclose(nH_now,nH,atol=1e-14,rtol=5e-14) or not np.allclose(nHe_now,nHe,atol=1e-14,rtol=5e-14):
        raise ArithmeticError("ORIGINAL_ELEMENT_COUNTS_NOT_PRESERVED")
    if np.max(np.abs(ev.population_rhs[:,0]+ev.population_rhs[:,1]))>1e-11*np.max(np.abs(ev.population_rhs[:,1])):
        raise ArithmeticError("SOURCE_H_NUCLEAR_DERIVATIVE_BROKEN")
    he_nuc=ev.population_rhs[:,2]+ev.population_rhs[:,3]+ev.population_rhs[:,4]
    he_scale=np.maximum(np.max(np.abs(ev.population_rhs[:,2:5]),axis=1),1e-290)
    if np.max(np.abs(he_nuc)/he_scale)>2e-13:
        raise ArithmeticError("SOURCE_HE_NUCLEAR_DERIVATIVE_BROKEN")
    Bdot=EV*(CHI[0]*ev.population_rhs[:,1]
             +CHI[1]*(ev.population_rhs[:,3]+ev.population_rhs[:,4])
             +CHI[2]*ev.population_rhs[:,4])
    Pphoto=EV*(point_photo@CHI)
    Pcoll=EV*(collision@CHI)
    Pots=np.asarray(ev.chemical_ots_energy_rate_erg_s)
    OTS_heat=np.asarray(ev.resolved_ots_heating_erg_s)
    OTS_unresolved=np.asarray(ev.unresolved_ots_energy_erg_s)
    OTS_escaped=np.asarray(ev.escaped_ots_energy_erg_s)
    primary_heat=np.asarray(photo.heating)
    dchem=Bdot-(Pphoto+Pcoll+Pots)
    dres=Pots+OTS_heat+OTS_unresolved+OTS_escaped
    sc1=np.maximum.reduce([np.abs(Bdot),np.abs(Pphoto),np.abs(Pcoll),np.abs(Pots),np.full(N,1e-140)])
    sc2=np.maximum.reduce([np.abs(Pots),OTS_heat,OTS_unresolved,OTS_escaped,np.full(N,1e-140)])
    err1=float(np.max(np.abs(dchem)/sc1))
    err2=float(np.max(np.abs(dres)/sc2))
    if err1>2e-12 or err2>2e-12:raise ArithmeticError(f"ORIGINAL_NET_OTS_SOURCE_STOICHIOMETRY_FAIL:{err1},{err2}")
    if np.any(OTS_unresolved<-1e-13*sc2) or np.any(OTS_escaped<-1e-13*sc2):
        raise ArithmeticError("ORIGINAL_RECOMBINATION_NEGATIVE_EMISSION_RESERVOIR")

    # Independent interval source enclosure; no assumed smooth v(T) below 10k.
    I=rim.iv.Interval
    al=accepted.population_lower;ah=accepted.population_upper
    ahi=I(al[:,0],ah[:,0])/model.n_h
    ahei=I(al[:,2],ah[:,2])/model.n_he
    arhe3=I(al[:,4],ah[:,4])/(I(al[:,3],ah[:,3])+I(al[:,4],ah[:,4]))
    coord_iv=I(np.stack([ahi.lo,ahei.lo,arhe3.lo,accepted.log_temperature_lower]),
               np.stack([ahi.hi,ahei.hi,arhe3.hi,accepted.log_temperature_upper]))
    Vbox=model.source_v_interval(coord_iv)
    rb=model.rhs_details(coordinates=coord_iv,time_lower_s=t0,time_upper_s=t0,
                         v_interval=Vbox,f_interval=model.scalar_interval(f))
    rhsnet=EV*(CHI[0]*rb.population_rhs[1]
               +CHI[1]*(rb.population_rhs[3]+rb.population_rhs[4])
               +CHI[2]*rb.population_rhs[4])
    ivs={
        "Bdot_net_erg_s":native_sum(rim,rhsnet),
        "original_resolved_heat_photo_plus_OTS_erg_s":native_sum(rim,rb.resolved_photoheat),
        "OTS_unresolved_erg_s":native_sum(rim,rb.unresolved_ots_energy_rate),
        "OTS_escaped_erg_s":native_sum(rim,rb.escaped_ots_energy_rate)}
    src_rates={
       "original_9_event_fluxes_per_s":{n:total_point(ev.event_rates[n]) for n in RATE_NAMES},
       "photo_event_per_s":{n:total_point(point_photo[:,i]) for i,n in enumerate(("HI","HeI","HeII"))},
       "collisional_event_per_s":{n:total_point(collision[:,i]) for i,n in enumerate(("HI","HeI","HeII"))}}
    power={
       "Bdot_net_erg_s":total_point(Bdot),
       "photo_binding_positive_erg_s":total_point(Pphoto),
       "collisional_binding_positive_erg_s":total_point(Pcoll),
       "OTS_chemical_rate_erg_s":total_point(Pots),
       "OTS_resolved_heat_erg_s":total_point(OTS_heat),
       "OTS_unresolved_residual_erg_s":total_point(OTS_unresolved),
       "OTS_escaped_erg_s":total_point(OTS_escaped),
       "primary_photoheat_erg_s":total_point(primary_heat),
       "original_total_resolved_heat_erg_s":total_point(primary_heat+OTS_heat)}
    for k,pt in (("Bdot_net_erg_s",power["Bdot_net_erg_s"]),
                 ("OTS_unresolved_erg_s",power["OTS_unresolved_residual_erg_s"]),
                 ("OTS_escaped_erg_s",power["OTS_escaped_erg_s"]),
                 ("original_resolved_heat_photo_plus_OTS_erg_s",power["original_total_resolved_heat_erg_s"])):
        lo,hi=ivs[k]
        if not lo-1e-11*max(abs(lo),abs(hi),abs(pt))<=pt<=hi+1e-11*max(abs(lo),abs(hi),abs(pt)):
            raise ArithmeticError("ORIGINAL_INTERVAL_ENCLOSURE_EXCLUDES_SOURCE_POINT_"+k)
    for k,vv in (("photo_binding_positive_erg_s","total_chemical_binding_power_erg_s"),
                 ("primary_photoheat_erg_s","total_primary_heat_power_erg_s")):
        lo,hi=pref[vv]
        if not lo-1e-10*abs(lo)<=power[k]<=hi+1e-10*abs(hi):
            raise ArithmeticError("PARENT_PR149_GROSS_PHOTO_SOURCE_MISMATCH_"+k)
    if any(k not in ev.event_rates for k in RATE_NAMES):raise ValueError("MISSING_NATIVE_REACTION_RATE")
    colnames=["cell","temperature_K","electron_density_cm3","original_v","Bdot_net_erg_s",
       "photo_binding_erg_s","collisional_binding_erg_s","OTS_chemical_erg_s",
       "OTS_heat_erg_s","OTS_unresolved_erg_s","OTS_escaped_erg_s",
       "primary_photoheat_erg_s","HI_ion_per_s","HeI_ion_per_s","HeII_ion_per_s"]
    colnames += ["rate_"+k for k in RATE_NAMES]
    SOURCE_BRANCHES=("y","z","y2a","y2b","A_H","A_HeI")
    if any(k not in ev.branches for k in SOURCE_BRANCHES):
        raise ValueError("MISSING_ORIGINAL_NATIVE_OTS_BRANCHES")
    colnames += ["branch_"+k for k in SOURCE_BRANCHES]
    rows=zip(range(N),T,ne,v,Bdot,Pphoto,Pcoll,Pots,OTS_heat,
             OTS_unresolved,OTS_escaped,primary_heat,
             native_ion[:,0],native_ion[:,1],native_ion[:,2],
             *[ev.event_rates[k] for k in RATE_NAMES],
             *[ev.branches[k] for k in SOURCE_BRANCHES])
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    csv_name="REI_ORIGINAL_T160_46080_HHE_26EVENT_ENERGY_SOURCE.csv.gz"
    csvsha=checksum_gzip(rows,colnames,out/csv_name)
    stats={
      "original_nodes":N,"source_time_s":t0,"original_tick_dt_s":dt,
      "temperature_min_max_K":[float(T.min()),float(T.max())],
      "v_min_max":[float(v.min()),float(v.max())],
      "num_below_1e4_K":int(np.count_nonzero(T<1e4)),
      "one_interior_state":"element_conserving_component_box_midpoint_not_certified_correlated_history",
      "chemical_residual_max_scaled":err1,
      "OTS_residual_max_scaled":err2,
      "collisional_split_max_scaled":max_coll_reldiff,
      "nuclei_conservation":"CHECKED",
      "interval_enclosure_of_source_point":"4_OF_4",
      "photo_ancestor_source_interval":"2_OF_2",
      "source_interval_energy_bounds":ivs,
      "original_reaction_rate":src_rates,
      "physical_energy_powers":power,
      "frozen_Bdot_net_times_one_original_tick_erg":power["Bdot_net_erg_s"]*dt,
      "original_OTS_energy_accounting_residual_is_defined_not_spectral_emissivity":True,
      "num_helium_hard_photons_claimed":False}
    data={"schema":"BASS_HE_F05_ORIGINAL_26EVENT_OTS_STOICHIOMETRIC_ENERGY_V1",
      "scope":"SINGLE_ORIGINAL_ACCEPTED_T160_46080_SOURCE_INNER_POINT_AND_ORIGINAL_INTERVAL_BOUNDS",
      "repo_source_head":REI_HEAD,"source_original_tar_sha256":TAR_SHA,
      "source_original_array_sha256":ARRAY_SHA,"kernel_sha256":KERNEL_SHA,
      "source_original_rhs_sha256":RHS_SHA,
      "source_original_event_sha256":sha(model.event.__file__),
      "original_parent_PR149_SCIENCE_JSON_SHA256":PARENT_RESULT_SHA,
      "source_point_method":"original_edge.element_conserving_parent_candidate plus midpoint logT",
      "result":stats,"derived_46080_csv":csv_name,"derived_46080_csv_sha256":csvsha,
      "provenance":"REAL_ORIGINAL_SOURCE_CODE_NOT_LITERATURE_SURROGATE",
      "claim":"ORIGINAL_26EVENT_LOCAL_REACTION_SOURCE_STOICHIOMETRY_ONLY",
      "independent_external_author":"NOT_RUN",
      "canonical_DAG":"28/88_REPORTED","working_DAG":"33/88_REPORTED",
      "physical_fast_DAG":"4/7_REPORTED","bass_he_physical_DAG":"14/18_REPORTED",
      "canonical_delta":0,"official_tick161":False,"source_mutated":False,
      "photon_spectral_emissivity_admitted":False,"production":"HOLD"}
    p=out/"SCIENCE_RESULT.json"
    p.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"result":"PASS_ORIGINAL_REI26_OTS_SOURCE_ENERGY",
      "power":power,"max_stoichiometry_relative":err1,
      "max_ots_energy_relative":err2,"source_interval_comparisons":4,
      "original_46080_csv_sha256":csvsha,"science_json_sha256":sha(p),
      "canonical_delta":0},sort_keys=True),flush=True)
    return data

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--rei-repo",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    generate(args.rei_repo,args.out)
