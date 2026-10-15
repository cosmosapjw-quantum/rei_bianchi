#!/usr/bin/env python3
"""C10 repeatable scientific convergence, spectrum transfer and speed experiments."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import csv
import json
import math
import os
from pathlib import Path
from statistics import median
from time import perf_counter
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import dynamic as d

INTERVAL=1e12
PHOTONS=1.
STEPS=32
FIELDS=("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_per_H","photon_U_eV_per_H")


def compact_result(r):
    return {"q":r["q"],"spectrum":r["source"],"nsteps":r["nsteps"],
            "nmu":r["nmu"],"ne":r["ne"],"H_interval":r["H_interval"],
            "dense_final":r["dense"]["final"],
            "dense_ledger":{k:r["dense"][k] for k in (
                "max_total_energy_rel_residual",
                "max_photon_plus_electron_rel_residual","substeps","rejections",
                "packet_bytes","stored_energy_bins")},
            "compressions":{key:{
                "age_count":v["age_count"],"max_delta":{name:val["max_abs"]
                      for name,val in v["dynamic_disagreement"].items()},
                "final":v["simulation"]["final"],"packet_bytes":v["simulation"]["packet_bytes"],
                "runtime_s_single":v["elapsed_integration_s"]}
                for key,v in r["alternatives"].items()}}


def case(job):
    q,source,nsteps,nmu,ne=job
    return d.one_run(q,source,nsteps,nmu,ne,PHOTONS,INTERVAL)


def maxdiff(a,b,field):
    return abs(a["dense"]["final"][field]-b["dense"]["final"][field])


def convergence(source):
    runs=[case((0.,source,n,12,16)) for n in (8,16,32,64,128)]
    metrics={}
    for name in FIELDS:
        gaps=[maxdiff(runs[i],runs[i+1],name) for i in range(4)]
        orders=[float(math.log(gaps[i]/gaps[i+1],2)) if gaps[i+1]>0 and gaps[i]>0
                else None for i in range(3)]
        metrics[name]={"adjacent_step_differences":gaps,"estimated_orders":orders}
    return {"source":source,"sequence":[8,16,32,64,128],
            "fields":metrics,"finest":compact_result(runs[-1])}


def spectral_refinement(source):
    runs=[case((0.,source,64,m,e)) for m,e in ((12,16),(16,24),(24,32))]
    return {"source":source,"grids":[{"nmu":r["nmu"],"ne":r["ne"],
                       "final":{k:r["dense"]["final"][k] for k in FIELDS}}
                      for r in runs],
            "final_adjacent_absolute_differences":{
                f: [maxdiff(runs[0],runs[1],f),maxdiff(runs[1],runs[2],f)]
                for f in FIELDS}}


def source_misuse_test():
    """BB source compression transferred to hard spectrum without refit."""
    m=d.c9.Scenario(d.ROOT)
    age=np.geomspace(m.ar,.2,d.c9.AGE_COUNT)
    src=d.c9.Spectrum()
    from benchmark import HardSource
    hard=HardSource()
    bbs=d.c9.build_packets(m,src,age,0)
    hards=d.c9.build_packets(m,hard,age,0)
    training,hold=d.c9.gas_states(m)
    ages=d.c9.source_age_weights(m,age,0.)
    mat=d.c9.evaluate_packets(bbs,np.vstack((training,hold)))
    fit=d.c9.design(mat,ages,5,len(training))
    frozen=d.weights_from_design(fit,len(age))
    gas=d.Gas.initial(m)
    dense=d.propagate(d.to_packets(hards,ages,gas,PHOTONS),gas,STEPS,INTERVAL)
    misuse=d.propagate(d.to_packets(hards,frozen,gas,PHOTONS),gas,STEPS,INTERVAL)
    hardmat=d.c9.evaluate_packets(hards,np.vstack((training,hold)))
    correctfit=d.c9.design(hardmat,ages,5,len(training))
    correct=d.propagate(d.to_packets(hards,d.weights_from_design(correctfit,len(age)),gas,PHOTONS),gas,STEPS,INTERVAL)
    return {"baseline_source":"BB50K", "target_source":"E^-1.5",
            "reuse_weights":"BB50K five-opacity-state positive C9 quadrature",
            "reused_age_count":fit["retained"],
            "refit_age_count":correctfit["retained"],
            "wrong_transfer":{k:v["max_abs"] for k,v in d.compare(dense,misuse).items()},
            "source_matched_refit":{k:v["max_abs"] for k,v in d.compare(dense,correct).items()}}


def compression_timing():
    model=d.c9.Scenario(d.ROOT)
    gas=d.Gas.initial(model)
    ages=np.geomspace(model.ar,.2,d.c9.AGE_COUNT)
    source=d.c9.Spectrum()
    cohorts=d.c9.build_packets(model,source,ages,0.)
    weights=d.c9.source_age_weights(model,ages,0.)
    train,hold=d.c9.gas_states(model)
    fit=d.c9.design(d.c9.evaluate_packets(cohorts,np.vstack((train,hold))),
                    weights,5,len(train))
    compact=d.weights_from_design(fit,len(ages))
    dense_pack=d.to_packets(cohorts,weights,gas,PHOTONS)
    compact_pack=d.to_packets(cohorts,compact,gas,PHOTONS)
    timings={}
    for label,pack in (("full_36",dense_pack),("positive_11",compact_pack)):
        for _ in range(2):
            d.propagate(pack,gas,STEPS,INTERVAL)
        samples=[]
        for _ in range(9):
            t0=perf_counter()
            run=d.propagate(pack,gas,STEPS,INTERVAL)
            samples.append(perf_counter()-t0)
        timings[label]={"wall_samples_s":samples,"median_s":median(samples),
                        "packet_bytes":pack.bytes,"bins":len(pack.E),
                        "exact_energy_residual":run["max_total_energy_rel_residual"]}
    ratio=timings["full_36"]["median_s"]/timings["positive_11"]["median_s"]
    return {"two_threads":False,"cpu_scope":"one process, BLAS 1 thread, repeated 9 times",
            "scope":"already-constructed spectral packet integration only",
            "measurements":timings,"median_speedup":ratio,
            "packet_memory_ratio":timings["full_36"]["packet_bytes"]/timings["positive_11"]["packet_bytes"]}


def parallel_timing():
    jobs=[(q,source,32,12,16) for source in ("bb50k","hard") for q in (-.01,0.,.01)]
    seq_samples=[];par_samples=[];seq_results=None;par_results=None
    for _ in range(3):
        t0=perf_counter()
        ss=[compact_result(case(job)) for job in jobs]
        seq_samples.append(perf_counter()-t0)
        if seq_results is None:seq_results=ss
    for _ in range(3):
        t0=perf_counter()
        with ProcessPoolExecutor(max_workers=3) as pool:
            pp=[compact_result(r) for r in pool.map(case,jobs)]
        par_samples.append(perf_counter()-t0)
        if par_results is None:par_results=pp
    # Exclude timing values from science parity; they are real wall-clock noise.
    def for_parity(x):
        for r in x:
            for v in r["compressions"].values():
                v.pop("runtime_s_single",None)
        return x
    assert for_parity(seq_results)==for_parity(par_results)
    return {"jobs":jobs,"samples_serial":seq_samples,"samples_parallel_3":par_samples,
            "median_serial_s":median(seq_samples),"median_parallel_s":median(par_samples),
            "whole_process_speedup":median(seq_samples)/median(par_samples),
            "science_reproducible":True}


def plot_history(case_bb,case_hard):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(8,9),sharex=True)
    for source, r in (("BB50K",case_bb),("E^-1.5",case_hard)):
        h=r["dense"]["history"]
        t=np.array([row["time_s"]/3.15576e7 for row in h])
        axes[0].plot(t,[row["x_HII"] for row in h],label=source)
        axes[1].plot(t,[row["x_HeII"] for row in h],label=source)
        axes[2].plot(t,[row["Tgas_K"] for row in h],label=source)
    for ax,ylabel in zip(axes,("x_HII","x_HeII","Gas temperature [K]")):
        ax.set_ylabel(ylabel);ax.grid(alpha=.25)
    axes[0].legend()
    axes[-1].set_xlabel("Proper time since frozen zbar=4 snapshot [years]")
    fig.suptitle("C10 photo-only evolving receiver (diagnostic, not cosmological history)")
    fig.tight_layout()
    target=HERE/"PILOT_HISTORY.png"
    fig.savefig(target,dpi=145)
    plt.close(fig)
    return str(target.relative_to(d.ROOT))


def save_csv(case_bb,case_hard):
    file=HERE/"PILOT_HISTORY.csv"
    with file.open("w",newline="") as fp:
        writer=csv.writer(fp,lineterminator="\\n")
        writer.writerow(["source","time_s","x_HII","x_HeII","x_HeIII",
                         "Tgas_K","photon_N_per_H","photon_U_eV_per_H"])
        for source,data in (("BB50K",case_bb),("hard",case_hard)):
            for h in data["dense"]["history"]:
                writer.writerow([source]+[h[k] for k in ("time_s","x_HII",
                    "x_HeII","x_HeIII","Tgas_K","photon_N_per_H",
                    "photon_U_eV_per_H")])
    return str(file.relative_to(d.ROOT))


def main():
    t0=perf_counter()
    bb=case((0.,"bb50k",64,12,16))
    hard=case((0.,"hard",64,12,16))
    result={"schema":"rei.source07.c10.dynamic.verified-pilot.v1",
            "scope":"frozen zbar4 proper photo-only H-He short interval; static geometry, no emission/recombination/cooling",
            "interval_s":INTERVAL,"initial_photons_per_H":PHOTONS,
            "canonical_cases":[compact_result(bb),compact_result(hard)],
            "time_convergence":[convergence("bb50k"),convergence("hard")],
            "energy_angle_convergence":[spectral_refinement("bb50k"),spectral_refinement("hard")],
            "cross_spectrum_negative_control":source_misuse_test(),
            "source_age_compression_runtime":compression_timing(),
            "parallel_six_jobs":parallel_timing(),
            "history_csv":save_csv(bb,hard),"history_plot":plot_history(bb,hard)}
    result["total_scientific_wall_s"]=perf_counter()-t0
    (HERE/"study_results.json").write_text(json.dumps(result,indent=2)+"\n")
    for key in ("canonical_cases","cross_spectrum_negative_control",
                "source_age_compression_runtime","parallel_six_jobs"):
        print(key)
        print(json.dumps(result[key],indent=2)[:5500])
    for entry in result["time_convergence"]:
        print("time_order",entry["source"],
              entry["fields"]["x_HII"]["estimated_orders"],
              entry["fields"]["Tgas_K"]["estimated_orders"])
    print("total_time",result["total_scientific_wall_s"])


if __name__=="__main__":
    main()
