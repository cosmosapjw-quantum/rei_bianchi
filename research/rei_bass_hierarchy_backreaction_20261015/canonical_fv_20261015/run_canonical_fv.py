"""Actual positive Lagrangian finite-volume REI/BASS coupling science campaign.

Runs q0 and signed Sigma-ref models with nonbaryonic collisionless mass
phase-space cells; gamma/massless-nu energy/number PR137 and optional
actual frozen original HHe-electron Thomson source. Independent PR140
J-index massive hierarchy and BASS160 direct Vlasov supply source checks,
NEVER reference truth injected into FV numerical state.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import math
import statistics
import time
from pathlib import Path
import numpy as np

from canonical_fv import CanonicalMomentumFV,CanonicalFVSpecies
from massive_radial import MassiveRadialSpecies
from run_hierarchy import source_lock,actual_electrons,public_sigma_from_q

HERE=Path(__file__).resolve().parent
BASS160_SHA="1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790"
REI_HHE_ORIGINAL_SHA="4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f"


def _settings():
    SigmaFull=public_sigma_from_q(.01)[0]
    return [
        ("gamma_nu_only",0.,0,0.,0.,30.,True),
        ("massive_plus",0.,0,.1,.5,30.,True),
        ("massive_minus",0.,0,.1,-.5,30.,True),
        ("massive_relativistic",0.,0,.1,.5,3.,True),
        ("massive_cold",0.,0,.1,.5,300.,True),
        ("massive_without_thomson",0.,0,.1,.5,30.,False),
        ("signed_shear_plus",SigmaFull,1,.1,.5,30.,True),
        ("signed_shear_minus",SigmaFull,-1,.1,.5,30.,True),
    ]


def _solve(name,Sigma,orient,fm,A,mass,donor,geom,reference=False):
    src=source_lock()
    common=dict(Sigma_ref=Sigma,orientation=orient,kappa_gamma=.2,
                kappa_nu=.2,ne_source=donor,mass_fraction=fm,
                massive_A=A)
    if reference:
        obj=MassiveRadialSpecies(src,2.7255,8,**common,
            mass_over_T_ref=mass,imax=2,nr=96,nmu=32)
    else:
        obj=CanonicalFVSpecies(src,2.7255,8,**common,
            mass_over_Tref=mass,radial_cells=geom[0],
            angular_cells=geom[1],subcell_gauss_order=geom[2])
    sol,diagnostics,elapsed=obj.integrate(n=121,rtol=3e-11,atol=3e-13)
    last=diagnostics[-1]
    return obj,sol,diagnostics,elapsed,{
        "name":name,"Sigma_end":float(last["Sigma"]),
        "b_end":float(sol.y[1,-1]),
        "Pi_matter_J_m3":float(last["Pi_matter_J_m3"]),
        "Pi_radiation_J_m3":float(last["Pi_radiation_J_m3"]),
        "Gamma_T_end_per_s":float(last["GammaT"]),
        "gamma_J2_end":float(last["E_gamma"][2]),
        "nu_J2_end":float(last["E_nu"][2]),
        "H_end_per_s":float(last["H"]),
        "elapsed_proper_time_s":float(sol.y[0,-1]/src.href),
        "nfev":int(sol.nfev),"wall_s":elapsed
    }


def _case_process(settings):
    name,Sigma,orient,fm,A,mass=settings
    # Reproduce one fully isolated case without any external electron
    # file access; this is a process-batch performance regression only.
    o,s,w,t,r=_solve(name,Sigma,orient,fm,A,mass,None,
                     (24,12,3),reference=False)
    return r["Sigma_end"],r["b_end"],r["Pi_matter_J_m3"]


def _bench_processes():
    cases=[(f"proc_{i}",public_sigma_from_q(v)[0],
             int(np.sign(v)),.1,A,30.)
           for i,(v,A) in enumerate([
              (0.,.5),(0.,-.5),(.005,.5),(-.005,-.5),
              (.01,.5),(-.01,.5),(0.,0.),(.005,-.5)
           ])]
    t=time.perf_counter()
    serial=list(map(_case_process,cases))
    serial_wall=time.perf_counter()-t
    runs=[]
    for workers in (2,4):
        t=time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            parallel=list(pool.map(_case_process,cases))
        clock=time.perf_counter()-t
        worst=max(abs(a-b) for x,y in zip(serial,parallel)
                  for a,b in zip(x,y))
        if worst>3e-13:
            raise AssertionError("parallel original BASS physical result drift")
        runs.append({"workers":workers,"wall_s":clock,
                     "speedup_vs_serial":serial_wall/clock,
                     "max_absolute_output_difference":worst})
    return {"cases":len(cases),"serial_wall_s":serial_wall,
            "parallel":runs,"scope":"independent reduced Einstein+collisionless FV+gamma/nu physical backgrounds"}


def _bench_moments():
    cells=CanonicalMomentumFV(30.,.5,24,12,gauss_order=3)
    N=1536
    eta=np.linspace(0,math.log(21/5),N)
    b=.025*np.sin(eta*3)
    expected=np.array([
        [r.rho,r.pressure_perp,r.pressure_parallel]
        for r in (cells.moments(float(x),float(v)) for x,v in zip(eta,b))
    ])
    times={}
    def scalar():
        return np.array([[r.rho,r.pressure_perp,r.pressure_parallel]
            for r in (cells.moments(float(x),float(v)) for x,v in zip(eta,b))])
    for name,fn,loops in [
        ("scalar",scalar,3),
        ("chunk8",lambda:cells.moment_batch(eta,b,8),5),
        ("chunk16",lambda:cells.moment_batch(eta,b,16),5),
        ("chunk32",lambda:cells.moment_batch(eta,b,32),5),
        ("chunk64",lambda:cells.moment_batch(eta,b,64),5),
    ]:
        trial=[];test=fn()
        if np.max(np.abs(test-expected))>3e-14:
            raise AssertionError(f"wrong vectorized FV cell moment {name}")
        for i in range(loops):
            begin=time.perf_counter();fn();trial.append(time.perf_counter()-begin)
        times[name]={"median_s":statistics.median(trial),
                     "trial_s":trial}
    fastest=min((k for k in times if k!="scalar"),key=lambda z:times[z]["median_s"])
    return {"sources":N,"positive_packets":cells.packet_count,
            "all_source_moment_absolute_parity":3e-14,
            "times":times,"fastest":fastest,
            "speedup_vs_once_per_state_scalar":times["scalar"]["median_s"]/times[fastest]["median_s"],
            "scope":"FV moment source only, no REI chemical production"}


def run(original_owner:Path,bass160:Path,output:Path):
    from hashlib import sha256
    source_code=bass160/"research/rei_axbi_sigma_matter_20261015/sigma_matter.py"
    if sha256(source_code.read_bytes()).hexdigest()!=BASS160_SHA:
        raise ValueError("BASS original source SHA invalid")
    donor,donor_meta=actual_electrons(original_owner)
    if donor_meta["history_sha256"]!=REI_HHE_ORIGINAL_SHA:
        raise ValueError("original frozen REI HHe source drift")
    results=[]
    rows=[]
    geom=(24,12,3)
    for name,Sigma,sign,fm,Am,mass,scatter in _settings():
        param=(donor if scatter else None)
        model,sol,points,sec,fv=_solve(
             name,Sigma,sign,fm,Am,mass,param,geom)
        _,reference,ref_points,refsec,source=_solve(
             name,Sigma,sign,fm,Am,mass,param,geom,reference=True)
        delta=abs(fv["Sigma_end"]-source["Sigma_end"])
        if delta>2e-8:
            raise AssertionError(f"FV source/Einst coupling too far {name}: {delta}")
        massNumber=model.momentum.total_cell_number
        for idx,x in enumerate(sol.t):
            point=points[idx]
            M=model.momentum.moments(float(x),float(sol.y[1,idx]))
            rows.append({
                "case":name,
                "zbar":1/point["a"]-1,
                "eta":float(x),
                "Sigma":point["Sigma"],
                "orientation":point["epsilon_sigma"],
                "b":float(sol.y[1,idx]),
                "H_s_inv":point["H"],
                "s_s_inv":point["s"],
                "Pi_massive_J_m3":point["Pi_matter_J_m3"],
                "Pi_gamma_J_m3":point["Pi_gamma_J_m3"],
                "Pi_nu_J_m3":point["Pi_nu_J_m3"],
                "massive_rho_norm":M.rho,
                "massive_number_cell_ref":massNumber,
                "massive_number_physical":M.ncell_number,
                "gamma_N0":point["N_gamma"][0],
                "nu_N0":point["N_nu"][0],
            })
        results.append({"configuration":{
                "name":name,"Sigma_ref":Sigma,"orientation":sign,
                "massive_fraction_nonbaryonic":fm,
                "initial_A_massive":Am,"mass_over_T_ref":mass,
                "actual_saved_HHe_Thomson":scatter,
                "canonical_radial_cells":geom[0],
                "canonical_angular_cells":geom[1],
                "subcell_Gauss_order":geom[2],
            },"fv":fv,"original_PR140_reference":source,
            "Sigma_difference_abs":delta,
            "b_difference_abs":abs(fv["b_end"]-source["b_end"]),
            "Pi_matter_difference_abs":abs(fv["Pi_matter_J_m3"]-source["Pi_matter_J_m3"]),
            "final_mass_particle_number_ratio":points[-1]["massive_physical_number_norm"]/
              (massNumber*math.exp(-3*float(sol.t[-1]))),
            "wall_ratio_FV_over_reference":sec/refsec,
        })
    if len(rows)!=8*121:
        raise AssertionError("missing true kinetic-Einstein state rows")
    output.mkdir(parents=True,exist_ok=True)
    with (output/"CANONICAL_FV_HISTORY.csv").open("w") as f:
        keys=list(rows[0])
        writer=csv.DictWriter(f,fieldnames=keys,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    benchmark=_bench_moments()
    process=_bench_processes()
    summary={
        "schema":"rei.bass.canonical_positive_Lagrangian_FV.v1",
        "date":"2026-10-15",
        "source_original_REI_HEAD":"b1cba753083ad83049c23ff538834564b49b7b6e",
        "source_BASS160_PY_SHA256":BASS160_SHA,
        "source_REI_HHe_electron_history_SHA256":REI_HHE_ORIGINAL_SHA,
        "source_electron_C2_max_relative_error":donor_meta["max_relative_electron_density_interpolation_error"],
        "science_mode":"strictly collisionless canonical 2D cells, original gamma/massless-nu unpolarized Thomson; no collision operator for massive",
        "cell_ODE":"invariant canonical q_i -> exact dNcell/deta=0; physical p drift encoded by moving grid, no high-l/i moment oracle",
        "source_quadrature":"positive Gauss3 subcell from compactified q∈[0,infinity) and reference mu∈[-1,1]",
        "number_of_cases":len(results),
        "actual_einstein_history_rows":len(rows),
        "case_results":results,
        "FV_source_speed":benchmark,
        "independent_case_process_speed":process,
        "result_admission":"SCOPED_POSITIVE_PHASE_CELL_COLLISIONLESS_VLASOV_EINSTEIN",
        "not_admitted":[
            "Eulerian conservative momentum flux discretization with collisions",
            "finite-mass collisional redistribution or Compton recoil",
            "full BASS polarized photon E/B Thomson",
            "two-way HHe reactive gas/photoionization under backreacting metric",
            "native REI AX08 production 20->4 and observational CMB/optical depth"
        ],
    }
    (output/"RESULTS.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"science":summary["result_admission"],
        "cases":len(results),"rows":len(rows),
        "FV_source_speedup":benchmark["speedup_vs_once_per_state_scalar"],
        "process_speedup":[e["speedup_vs_serial"] for e in process["parallel"]],
        "cases_end_Sigma":[{z["configuration"]["name"]:z["fv"]["Sigma_end"]}
                         for z in results],
        "source_max_Sigma_abs_difference":max(t["Sigma_difference_abs"] for t in results)
    },indent=2))
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-owner",required=True,type=Path)
    p.add_argument("--bass160-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    c=p.parse_args()
    run(c.original_owner,c.bass160_root,c.output)
