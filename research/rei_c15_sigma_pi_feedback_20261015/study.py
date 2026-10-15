#!/usr/bin/env python3
"""Reproducible C15 Einstein-sourced Sigma and real H/He/UV/BASS state study."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import csv,hashlib,json,math,statistics,sys,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from coupled import Parameters,EinsteinBoltzmann,KAPPA,source_identity

SCENARIOS=(
 ("isotropic_zero",Parameters(0.,0,0.,0.,0.,0.)),
 ("gamma_nu_positive",Parameters(0.,0,.2,.2,0.,0.)),
 ("massive_positive",Parameters(0.,0,0.,0.,.1,.5)),
 ("massive_negative",Parameters(0.,0,0.,0.,.1,-.5)),
 ("Einstein_gamma_nu_massive",Parameters(0.,0,.2,.2,.1,.5)),
 ("GRAVITY_PI_DISABLED_CONTROL",Parameters(0.,0,.2,.2,.1,.5,enable_primordial_pi=False,enable_matter_pi=False,enable_ionizing_pi=False)),
 ("Sigma_positive_orientation",Parameters(.002,1,.2,.2,.1,.5)),
 ("Sigma_negative_orientation",Parameters(.002,-1,.2,.2,.1,.5)),
)
FIELDS=("Sigma","b","x_HII","x_HeII","Tgas_K",
        "remaining_UV_photons_perH","collision_tau","gamma_J2",
        "nu_J2","Pi_gamma","Pi_nu","Pi_massive","Pi_UV","Pi_total_source")


def run_named(item,nsteps=64,compress=True,fast_massive=True):
    name,p=item
    m=EinsteinBoltzmann(p,fast_massive=fast_massive)
    out=m.run(nsteps=nsteps,compress=compress)
    out["scientific_case"]=name
    return out


def serial_and_parallel():
    start=time.perf_counter()
    serial=[run_named(x,nsteps=64) for x in SCENARIOS]
    serial_time=time.perf_counter()-start
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        parallel=list(pool.map(run_named,SCENARIOS))
    parallel_time=time.perf_counter()-start
    assert serial==parallel,"C15_DYNAMIC_SCIENCE_NONDETERMINISM_SERIAL_PARALLEL"
    return {"cases":serial,"parallel_profiling":{
        "independent_scenarios":len(SCENARIOS),"workers":3,
        "whole_batch_serial_s":serial_time,
        "whole_batch_parallel_s":parallel_time,
        "speedup":serial_time/parallel_time,
        "all_science_states_bitwise_identical":True,
        "not_a_native_solver_benchmark":True}}


def time_refinement():
    p=Parameters(0.,0,.2,.2,.1,.5)
    r=[EinsteinBoltzmann(p).run(nsteps=n) for n in (8,16,32,64,128)]
    fields={}
    for k in ("Sigma","b","x_HII","Tgas_K",
              "remaining_UV_photons_perH","collision_tau"):
        delta=[abs(r[i]["final"][k]-r[i+1]["final"][k]) for i in range(4)]
        order=[math.log(delta[i]/delta[i+1],2)
               if delta[i]>0 and delta[i+1]>0 else None for i in range(3)]
        fields[k]={"adjacent_grid_diff":delta,"self_convergence_order":order}
    return {"num_intervals":[8,16,32,64,128],
            "fields":fields,"finest":r[-1]["final"],
            "scope":"same native source/momentum quadrature, empirical step convergence only"}


def spectral_refinement():
    p=Parameters(0.,0,.2,.2,.1,.5)
    cases={}
    for grid in ("4X8","8X8","16X8","32X8","8X16"):
        a=EinsteinBoltzmann(p,source_grid=grid).run(nsteps=64)
        cases[grid]={"end":{k:a["final"][k] for k in FIELDS},
                    "N_source":a["final"]["source_photons_perH"],
                    "N_UV_packets":a["final"]["UV_packets"],
                    "source_grid":grid}
    fine=cases["32X8"]["end"]
    return {"cases":cases,"absolute_diff_vs_32X8":{
        k:{name:abs(v["end"][k]-fine[k]) for name,v in cases.items()}
        for k in ("Sigma","Tgas_K","x_HII","remaining_UV_photons_perH")},
        "source_lock":"native Rust AxbiSource threshold-segment spectral grids, no invented blackbody source"}


def fast_BASS_moments():
    p=Parameters(0.,0,.2,.2,.1,.5)
    fast=EinsteinBoltzmann(p,fast_massive=True)
    original=EinsteinBoltzmann(p,fast_massive=False)
    rng=np.random.default_rng(17)
    xx=rng.uniform(.000001,.0005,2048)
    bb=rng.uniform(-.0005,.0005,2048)
    references=np.array([original.massive_source_3moments(float(x),float(b))
                         for x,b in zip(xx,bb)])
    values=np.array([fast.massive_source_3moments(float(x),float(b))
                     for x,b in zip(xx,bb)])
    relative=np.max(abs(references-values)/np.maximum(abs(references),1e-13))
    assert relative<2e-13
    trials={}
    for key,obj in (("original",original),("source_moment_vectorized",fast)):
        for x,b in zip(xx[:50],bb[:50]):obj.massive_source_3moments(float(x),float(b))
        times=[]
        for _ in range(7):
            start=time.perf_counter()
            for x,b in zip(xx,bb):obj.massive_source_3moments(float(x),float(b))
            times.append(time.perf_counter()-start)
        trials[key]={"wall_samples_s":times,"median_s":statistics.median(times)}
    return {"input_samples":len(xx),"max_source_owner_rel_error":float(relative),
            "comparison":trials,
            "speedup_original_to_reduced_source_quadrature":
            trials["original"]["median_s"]/trials["source_moment_vectorized"]["median_s"],
            "identical_Fermi_Dirac_source_quadrature":True,
            "scope":"local original PR140 j0^0/j0^1/j2^0 moment microkernel only"}


def compressed_benchmark():
    p=Parameters(0.,0,.2,.2,.1,.5)
    out={}
    for key,compress in (("uncompressed",False),("positive_cohort_2nodes",True)):
        for _ in range(2):EinsteinBoltzmann(p).run(nsteps=128,compress=compress)
        times=[]
        for _ in range(5):
            start=time.perf_counter()
            s=EinsteinBoltzmann(p).run(nsteps=128,compress=compress)
            times.append(time.perf_counter()-start)
        out[key]={"samples_s":times,"median_s":statistics.median(times),
                  "end_packets":s["final"]["UV_packets"],
                  "max_number_ledger_abs":s["errors"]["photochemical_number_abs_max"],
                  "end_Sigma":s["final"]["Sigma"],
                  "end_temperature_K":s["final"]["Tgas_K"]}
    return {"nsteps":128,"source":"native MD14/BB50K 8x8",
            "runs_each":5,"matched_positive_states":out,
            "whole_scoped_solver_speedup":out["uncompressed"]["median_s"]/
                        out["positive_cohort_2nodes"]["median_s"],
            "UV_packet_count_ratio":out["uncompressed"]["end_packets"]/
                                   out["positive_cohort_2nodes"]["end_packets"],
            "not_entire_native_AX08_memory_or_runtime":True}


def plot_tables(cases):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(9,10),sharex=True)
    path=HERE/"SIGMA_PI_HHE_COUPLED_HISTORY.csv"
    with path.open("w",newline="") as f:
        col=("scientific_case","a","elapsed_s","Sigma","orientation","b",
             "Pi_gamma","Pi_nu","Pi_massive","Pi_UV",
             "Pi_total_source","x_HII","x_HeII","Tgas_K",
             "remaining_UV_photons_perH","collision_tau")
        writer=csv.writer(f,lineterminator="\n")
        writer.writerow(col)
        for case in cases:
            x=[r["elapsed_s"]/3.15576e7 for r in case["history"]]
            if case["scientific_case"] in (
                  "isotropic_zero","gamma_nu_positive","massive_positive",
                  "Einstein_gamma_nu_massive","GRAVITY_PI_DISABLED_CONTROL"):
                axs=axes
                axes[0].plot(x,[r["Sigma"] for r in case["history"]],
                             label=case["scientific_case"].replace("_"," "))
                axes[1].plot(x,[r["Pi_total_source"] for r in case["history"]],
                             label=case["scientific_case"].replace("_"," "))
                axes[2].plot(x,[r["Tgas_K"] for r in case["history"]],
                             label=case["scientific_case"].replace("_"," "))
            for r in case["history"]:
                writer.writerow([case["scientific_case"]]+[r.get(z,None) for z in col[1:]])
    axes[0].set_ylabel("Sigma=|sigma|/H")
    axes[1].set_ylabel("Pi source [Pa]")
    axes[2].set_ylabel("H/He gas T [K]")
    axes[2].set_xlabel("Proper time since a=0.1999 [years]")
    for a in axes:
        a.grid(alpha=.25);a.legend(fontsize=7)
    axes[0].set_title("C15 active Einstein Pi-source, fixed near-z4 model")
    fig.tight_layout()
    fig.savefig(HERE/"SIGMA_PI_HHE_COUPLED_HISTORY.png",dpi=145)
    plt.close(fig)
    return {"plot":"SIGMA_PI_HHE_COUPLED_HISTORY.png",
            "csv":path.name,"rows":sum(len(x["history"]) for x in cases)}


def main():
    start=time.perf_counter()
    series=serial_and_parallel()
    results={"schema":"rei.c15.true_Einstein_bass_stress_reionization_short.v1",
             "source":source_identity(),
             "scoped_scenario":"warm prespecified a=.1999 to .2, stellar native MD14 source, Case A RR/DR H-He, PR137 unpolarized gamma/nu, PR140 collisionless massive matter with baryon-safe fraction",
             "series":series["cases"],
             "source_parallel":series["parallel_profiling"],
             "time_refinement":time_refinement(),
             "native_source_spectral_refinement":spectral_refinement(),
             "BASS_massive_source_optimization":fast_BASS_moments(),
             "positive_UV_cohort_optimization":compressed_benchmark()}
    results["artifacts"]=plot_tables(series["cases"])
    results["study_total_wall_s"]=time.perf_counter()-start
    (HERE/"C15_STUDY_RESULTS.json").write_text(json.dumps(results,indent=2)+"\n")
    for case in series["cases"]:
        print("CASE",case["scientific_case"],"Sigma",case["final"]["Sigma"],
              "H",case["final"]["H"],"matter_Pi",case["final"]["Pi_massive"],
              "radiation_Pi",case["final"]["Pi_gamma"]+case["final"]["Pi_nu"],
              "UV_Pi",case["final"]["Pi_UV"],"T",case["final"]["Tgas_K"],flush=True)
    print("BENCH",results["positive_UV_cohort_optimization"]["whole_scoped_solver_speedup"],
          results["BASS_massive_source_optimization"]["speedup_original_to_reduced_source_quadrature"],
          results["source_parallel"]["speedup"],flush=True)
    print("TOTAL",results["study_total_wall_s"],flush=True)

if __name__=="__main__":
    main()
