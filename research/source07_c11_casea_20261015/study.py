#!/usr/bin/env python3
"""C11 numerical convergence, matched source compression, and real CPU profiling."""
from __future__ import annotations

import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import median
from time import perf_counter

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import casea as x
from rate_table import CaseARates

FIELDS=("x_HII","x_HeII","x_HeIII","Tgas_K","photon_N_per_H",
        "photon_U_eV_per_H","radiative_escape_eV_per_H")


def ratio(a,b):
    return (a/b) if b!=0 else None


def comparison(dense:dict,light:dict):
    hist1,hist2=dense["history"],light["history"]
    if len(hist1)!=len(hist2):raise ValueError("mismatched histories")
    return {k:{
      "max_abs":max(abs(v[k]-u[k]) for v,u in zip(hist1,hist2)),
      "endpoint_signed":hist2[-1][k]-hist1[-1][k]
    } for k in FIELDS}


def scenario(q:float,source:str,nsteps:int=32,compress:bool=False):
    r=x.one_run(q,source,nsteps=nsteps,compress=compress)
    return r


def safe(r):
    return {k:r[k] for k in (
        "q","spectrum","compressed","kept_age_nodes","nsteps","nmu","ne",
        "interval_s","initial_H_dt","table_sha256","accepted","rejected",
        "max_energy_residual_eV_per_H",
        "max_electron_photon_residual_per_H","photon_packet_bytes","final")}


def time_convergence(source:str):
    rs=[scenario(0.,source,n,True) for n in (8,16,32,64,128)]
    metrics={}
    for k in FIELDS:
        differences=[abs(rs[i+1]["final"][k]-rs[i]["final"][k]) for i in range(4)]
        order=[math.log(differences[j]/differences[j+1],2) if differences[j+1] else None
               for j in range(3)]
        metrics[k]={"adjacent_differences":differences,"estimated_order":order}
    return {"source":source,"grids":[8,16,32,64,128],
            "metrics":metrics,"finest":safe(rs[-1])}


def benchmarks():
    # No data construction in benchmark timed block.
    model=x.C9.Scenario(x.ROOT)
    g=x.c10.Gas.initial(model)
    rates=CaseARates()
    source=x.C9.Spectrum()
    dense,_=x.build_source("bb50k",0.,g,False)
    compressed,kept=x.build_source("bb50k",0.,g,True)
    assert kept==11
    timings={}
    for name,pkt in (("dense",dense),("compressed",compressed)):
        def do():
            return x.evolve(x.ReservoirState(g,pkt),rates,1e12,32)
        for _ in range(2):do()
        samples=[]
        for _ in range(9):
            t0=perf_counter();res=do();samples.append(perf_counter()-t0)
        timings[name]={"wall_samples_s":samples,"median_s":median(samples),
                       "packet_bytes":pkt.bytes,"energy_residual":res["max_energy_residual_eV_per_H"],
                       "final":res["final"]}
    return {"timing":"local repeated Python integration only; source/rates table already constructed",
            "n_repetitions":9,"BLAS_threads":1,
            "dense_vs_compressed_speedup":timings["dense"]["median_s"]/timings["compressed"]["median_s"],
            "packet_memory_ratio":timings["dense"]["packet_bytes"]/timings["compressed"]["packet_bytes"],
            "samples":timings}


def one_parallel_job(job):
    q,source=job
    return safe(scenario(q,source,32,True))


def parallel_jobs():
    tasks=[(q,source) for source in ("bb50k","hard") for q in (-.01,0.,.01)]
    seq=[];par=[]
    science_serial=None
    science_parallel=None
    for j in range(3):
        t0=perf_counter()
        a=list(map(one_parallel_job,tasks))
        seq.append(perf_counter()-t0)
        if science_serial is None:science_serial=a
    for j in range(3):
        t0=perf_counter()
        with ProcessPoolExecutor(max_workers=3) as pool:
            a=list(pool.map(one_parallel_job,tasks))
        par.append(perf_counter()-t0)
        if science_parallel is None:science_parallel=a
    if science_serial!=science_parallel:
        raise RuntimeError("PARALLEL_SCIENCE_MISMATCH")
    return {"tasks":tasks,"serial_wall_samples_s":seq,"parallel_wall_samples_s":par,
            "median_serial_s":median(seq),"median_parallel_s":median(par),
            "wall_speedup":median(seq)/median(par),
            "science_byte_float_exact_match":True}


def make_plot(bb,hard):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(8,9),sharex=True)
    for label,obj in (("BB50K",bb),("Hard E^-1.5",hard)):
        h=obj["history"]
        tt=np.array([r["time_s"]/3.15576e7 for r in h])
        axes[0].plot(tt,[r["x_HII"] for r in h],label=label)
        axes[1].plot(tt,[r["x_HeII"] for r in h],label=label)
        axes[2].plot(tt,[r["Tgas_K"] for r in h],label=label)
    axes[0].legend()
    axes[-1].set_xlabel("Proper time since frozen zbar=4 receiver [years]")
    for ax,ylabel in zip(axes,("H II fraction","He II fraction","Gas temperature [K]")):
        ax.set_ylabel(ylabel);ax.grid(alpha=.23)
    fig.suptitle("SOURCE07 C11: photoionization + Grackle RR/DR & cooling (conditional)")
    fig.tight_layout()
    out=HERE/"CASEA_PHOTO_HHE.png"
    fig.savefig(out,dpi=140)
    plt.close(fig)
    return out.name


def main():
    t0=perf_counter()
    case_bb=scenario(0.,"bb50k",64,False)
    case_hard=scenario(0.,"hard",64,False)
    light_bb=scenario(0.,"bb50k",64,True)
    light_hard=scenario(0.,"hard",64,True)
    data={
        "schema":"rei.source07.c11.caseA.RR_DR_only.frozen_receiver.v1",
        "scoped_claim":"Source-locked Grackle Case A RR/DR cooling + exact He-chain; only fixed receiver, no cosmic source/cooling channels other than RR/DR",
        "rates_sha256":case_bb["table_sha256"],
        "canonical_cases":{"bb50k":safe(case_bb),"hard":safe(case_hard)},
        "compressed_cases":{"bb50k":safe(light_bb),"hard":safe(light_hard)},
        "compression_error":{"bb50k":comparison(case_bb,light_bb),
                             "hard":comparison(case_hard,light_hard)},
        "time_convergence":{"bb50k":time_convergence("bb50k"),
                            "hard":time_convergence("hard")},
        "matched_benchmark":benchmarks(),
        "parallel_batch":parallel_jobs(),
        "figure":make_plot(case_bb,case_hard)
    }
    data["local_study_elapsed_s"]=perf_counter()-t0
    (HERE/"study_results.json").write_text(json.dumps(data,indent=2)+"\n")
    for k in ("bb50k","hard"):
        print(k,"dense",data["canonical_cases"][k]["final"])
        print(k,"compressed",data["compressed_cases"][k]["final"])
        print(k,"maxcomp",data["compression_error"][k])
        print(k,"time-orders",data["time_convergence"][k]["metrics"]["x_HII"]["estimated_order"],
              data["time_convergence"][k]["metrics"]["Tgas_K"]["estimated_order"])
    print("speed",data["matched_benchmark"]["dense_vs_compressed_speedup"],
          "memory",data["matched_benchmark"]["packet_memory_ratio"],
          "parallel",data["parallel_batch"]["wall_speedup"])
    print("DONE",data["local_study_elapsed_s"],"s")


if __name__=="__main__":
    main()
