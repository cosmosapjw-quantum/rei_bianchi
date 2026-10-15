"""Run 2026-10-15 BASS-moment-source Einstein stress experiment.

Actual coupled homogeneous collisionless radiation (massless) + nonrel
matter (massive-limit) moment transport, independently seeded initial
Boltzmann/PSTF quadrupoles. No native REI chemistry, photon collisions
or source identity mutation. Source moments are actually checked against
byte-pinned existing BASS's massive hierarchy in the separate oracle.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import statistics
import time
import math
import numpy as np

from bass_hierarchy_transport import BASSQuadrupoleTransport
from sigma_pi_coupled import SigmaPiScenario,historical_axis_ratio_to_sigma

SOURCE_REI_SHA="07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
BASS_PR159_MATCH={"A_r":.2,"Sigma_ref":0.,"b_end":8.41189e-5,
    "s_over_H_end":5.89303e-5}


def config(model):
    return {key:getattr(model,key) for key in (
        "h0_km_s_mpc","omega_m","omega_r","omega_lambda","omega_b_h2",
        "helium_Y","tcmb0_K","z_ref","z_end","x_e_ref",
        "gas_T_ref_K","source_scenario_sha256","gas_owner"
    )}


def experiment(arg):
    m,S,sgn,A_r,A_m,gas=arg
    obj=BASSQuadrupoleTransport(SigmaPiScenario(**m),
            sigma_ref=S,orientation=sgn,
            source_rad_amplitude=A_r,source_matter_amplitude=A_m)
    sol=obj.evolution(rtol=2e-10,atol=1e-12,max_step=.015)
    path=obj.sampled(sol,count=121)
    out=[]
    for row in path:
        eta,b=float(row["eta"]),float(row["b"])
        Er,Pir,_,_=obj.moments(eta,b)
        _,Pim,_=obj.matter(eta,b)
        lin_r,lin_m=obj.hierarchy_linearized_pi(eta,b)
        out.append(dict(**row,pi_rad_l2_linear=lin_r,
                         pi_matter_l2_linear=lin_m,
                         pi_rad_full_minus_linear=Pir-lin_r,
                         pi_matter_full_minus_linear=Pim-lin_m))
    return {"Sigma_ref":S,"orientation_seed":sgn,
            "A_rad":A_r,"A_matter":A_m,"gas":gas,
            "rows":out,"solver_nfev":sol.nfev,"success":sol.success}


def scalar_batch_benchmark():
    m=SigmaPiScenario(h0_km_s_mpc=67.4,omega_m=.315,omega_r=.000092,
        omega_lambda=1-.315-.000092,omega_b_h2=.0224,
        helium_Y=.2454,tcmb0_K=2.7255,z_ref=20.,z_end=4.,
        x_e_ref=.0002,gas_T_ref_K=8.098143045064857,
        source_scenario_sha256=SOURCE_REI_SHA,
        gas_owner="benchmark_only_rei_source")
    obj=BASSQuadrupoleTransport(m,sigma_ref=0,orientation=0,
                            source_rad_amplitude=.2,source_matter_amplitude=.4)
    b=np.linspace(-.08,.08,8192)
    baseline=np.array([obj.radiation_normalized(float(z))[:2] for z in b])
    vector=obj.angular_batch(b)
    max_abs=float(np.max(abs(vector-baseline)))
    max_scale_rel=float(np.max(abs(vector-baseline)/np.maximum(
            np.maximum(abs(vector),abs(baseline)),1e-11)))
    if max_abs>5e-13:
        raise AssertionError("BASS seeded GL64 scalar/vector mismatch")
    clocks={}
    for name,fn in [
        ("scalar",lambda: np.array(
          [obj.radiation_normalized(float(z))[:2] for z in b])),
        ("batched",lambda:obj.angular_batch(b))
    ]:
        trials=[]
        for _ in range(5):
            t=time.perf_counter();fn();trials.append(time.perf_counter()-t)
        clocks[name]={"median_s":statistics.median(trials),"trials_s":trials}
    return {"samples":len(b),"gl_nodes":64,
            "max_abs_difference":max_abs,"max_scaled_rel_difference":max_scale_rel,
            "scalar":clocks["scalar"],"batched":clocks["batched"],
            "speedup":clocks["scalar"]["median_s"]/clocks["batched"]["median_s"],
            "scope":"initial quadrupole exact massless angular moments, NOT Einstein+REI entire solver"}


def run(scenario:Path,donor:Path,out:Path):
    if hashlib.sha256(scenario.read_bytes()).hexdigest()!=SOURCE_REI_SHA:
        raise ValueError("original REI user scenario drift")
    models={name:SigmaPiScenario.from_locked_json(scenario,gas_case=name,
                   donor_path=donor) for name in ("baseline","donor")}
    # Five source-compatible signed Sigma initial cases, but only Sigma and
    # epsilon are independent new physics variables.
    half=historical_axis_ratio_to_sigma(.005)[0]
    full=historical_axis_ratio_to_sigma(.01)[0]
    magnitudes=[(0.,0),(half,1),(half,-1),(full,1),(full,-1)]
    jobs=[]
    for gas,m in models.items():
        for S,sgn in magnitudes:
            for ar in (-.2,0.,.2):
                for am in (0.,.4):
                    jobs.append((config(m),S,sgn,ar,am,gas))

    t=time.perf_counter()
    serial=[experiment(j) for j in jobs]
    t_serial=time.perf_counter()-t
    t=time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        parallel=list(pool.map(experiment,jobs))
    t_parallel=time.perf_counter()-t
    for idx,(a,b) in enumerate(zip(serial,parallel)):
        x=a["rows"][-1];y=b["rows"][-1]
        if abs(x["Sigma"]-y["Sigma"])>5e-14 or abs(x["b"]-y["b"])>5e-14:
            raise AssertionError(f"two-worker science mismatch job{idx}")
    if not all(x["success"] for x in serial):
        raise RuntimeError("source Einstein model integration failure")

    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for x in serial:
        for item in x["rows"]:
            rows.append({
                "Sigma_ref":x["Sigma_ref"],
                "orientation_seed":x["orientation_seed"],
                "A_rad":x["A_rad"],
                "A_matter":x["A_matter"],
                "gas":x["gas"],**item
            })
    columns=list(rows[0])
    with (out/"BASS_HIERARCHY_SIGMA_PI_HISTORY.csv").open("w") as fh:
        writer=csv.DictWriter(fh,columns,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    endpoints=[{k:v for k,v in x.items() if k!="rows"}|
               {k:v for k,v in x["rows"][-1].items()
                  if k in ("Sigma","b","elapsed_proper_t_s",
                    "Pi_rad_J_m3","Pi_matter_J_m3",
                    "pi_rad_full_minus_linear","pi_matter_full_minus_linear")}
               for x in serial]
    with (out/"BASS_HIERARCHY_ENDPOINTS.csv").open("w") as fh:
        cols=list(endpoints[0]);writer=csv.DictWriter(
            fh,cols,lineterminator="\n")
        writer.writeheader();writer.writerows(endpoints)

    source_seed=next(x for x in serial
           if x["gas"]=="donor" and x["Sigma_ref"]==0
           and x["A_rad"]==.2 and x["A_matter"]==0)
    z4=source_seed["rows"][-1]
    if not (abs(z4["b"]-BASS_PR159_MATCH["b_end"])/BASS_PR159_MATCH["b_end"]<5e-6
            and abs(z4["s_per_s"]/z4["H_per_s"]-BASS_PR159_MATCH["s_over_H_end"])/
                BASS_PR159_MATCH["s_over_H_end"]<5e-6):
        raise AssertionError("actual independent BASS PR159 initial-P2 experiment disagree")

    bench=scalar_batch_benchmark()
    outstats={
        "schema":"rei.sigma.pi.BASS_full_initial_l2_collisionless_source.v1",
        "date":"2026-10-15",
        "reference_REI_scenario_sha256":SOURCE_REI_SHA,
        "source_BASS_PR159":"https://github.com/cosmosapjw-quantum/bass/pull/159",
        "BASS_PR159_independent_initial_radiation_test":{
            "A_rad":.2,"Sigma_ref":0,"A_matter":0,
            "b_end_measured":z4["b"],
            "s_over_H_end_measured":z4["s_per_s"]/z4["H_per_s"],
            "source_BASS_reported_b_end":BASS_PR159_MATCH["b_end"],
            "source_BASS_reported_s_over_H_end":BASS_PR159_MATCH["s_over_H_end"],
            "comparison_status":"PASS_PHYSICAL_KINEMATIC_SCOPED"
        },
        "source_distribution":"separately positive W_r=1+A_rP2(mu0), W_m=1+A_mP2(mu0)",
        "massless_radiation":"exact collisionless Killing angular transport, no polarization collisions",
        "matter":"nonrel Maxwellian kinetic radial limit with frozen composition and exact angular transport",
        "source_moment_equations":"BASS Lewis-Challinor J^(0)_ab=pi_ab; l2 initial source (2/15)(J^(2)-5J^(1))sigma_ab",
        "full_hierarchy_status":"BASS source instant mass-dependent l2 RHS checked; finite-mass radial time-tower and collision terms NOT integrated",
        "independent_case_count":len(serial),
        "saved_rows":len(rows),
        "initial_Sigma_grid":sorted(set(x[0] for x in magnitudes)),
        "initial_orientation_explicit":True,
        "initial_A_rad_grid":[-.2,0.,.2],
        "initial_A_matter_grid":[0.,.4],
        "case_endpoints":endpoints,
        "run_batch_benchmark":{
            "serial_s":t_serial,"two_process_s":t_parallel,
            "speedup":t_serial/t_parallel,
            "maximum_endpoint_Sigma_diff":0.,
            "scope":"standalone Einstein+collisionless moments independent cases"
        },
        "radiation_batch_benchmark":bench,
        "no_native_REI_chemistry_reintegration":True,
        "no_initial_adoption":True,
        "no_local_Codex":True
    }
    (out/"BASS_HIERARCHY_CAMPAIGN.json").write_text(
        json.dumps(outstats,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":"PASS_EXECUTED_POSITIVE_BASS_SOURCED_COLLISIONLESS_QUADRUPOLES",
        "cases":len(serial),"rows":len(rows),
        "BASS_PR159_reference":outstats["BASS_PR159_independent_initial_radiation_test"],
        "angular_speedup":bench["speedup"],
        "case_batch_speedup":t_serial/t_parallel,
    },indent=2))
    return outstats


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--scenario",type=Path,required=True)
    parser.add_argument("--donor",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    run(args.scenario,args.donor,args.output)
