"""Matched-accuracy source radial chunk and actual Einstein IVP process benchmarks."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import statistics
import time
import numpy as np
from massive_radial import MassiveRadialGrid,MassiveRadialSpecies
from run_hierarchy import source_lock,public_sigma_from_q


def _median(f,n=4):
    ts=[]
    for _ in range(n):
        t=time.perf_counter()
        f()
        ts.append(time.perf_counter()-t)
    return dict(median_s=statistics.median(ts),trials_s=ts)


def _case(params):
    sigma,sign,amp=params
    m=MassiveRadialSpecies(source_lock(),2.7255,ellmax=8,
        Sigma_ref=sigma,orientation=sign,kappa_gamma=.2,kappa_nu=.2,
        mass_fraction=.1,massive_A=amp,mass_over_T_ref=30.,imax=2)
    sol,phys,_=m.integrate(81,rtol=3e-11,atol=2e-13)
    return dict(Sigma_end=phys[-1]["Sigma"],b_end=float(sol.y[1,-1]),
                J00_end=float(sol.y[m.main_size,-1]),nfev=sol.nfev)


def evaluate():
    grid=MassiveRadialGrid(30,96,32)
    xs=np.linspace(0,math.log(21/5),1024)
    bs=.02*np.sin(2*xs)
    reference=np.array([
        [j.j0,j.j2,j.j4]
        for j in (grid.moments(float(x),float(b),.5,2)
                  for x,b in zip(xs,bs))
    ])
    scalar=_median(lambda: [
        grid.moments(float(x),float(b),.5,2)
        for x,b in zip(xs,bs)
    ],4)
    chunks=[]
    for size in [16,32,64,128,256]:
        fn=lambda:grid.batch(xs,bs,.5,2,chunk=size)
        val=fn()
        maxabs=float(np.max(abs(val-reference)))
        if maxabs>1e-13:raise RuntimeError("chunk parity failure")
        record=_median(fn,5)
        chunks.append({
            "chunk":size,**record,
            "speedup_vs_one_scalar_owner_call_per_state":
                scalar["median_s"]/record["median_s"],
            "max_abs_difference":maxabs,
            "peak_rows_times_96x32":size*96*32,
            "minimum_working_element_bytes_per_3d_tensor":size*96*32*8,
        })
    sigma=public_sigma_from_q(.01)[0]
    combos=[(sg,ori,A) for sg,ori in ((0.,0),(sigma,1),(sigma,-1))
                         for A in (-.5,0.,.5)]
    t=time.perf_counter();serial=list(map(_case,combos))
    elapsed_serial=time.perf_counter()-t
    process=[]
    for workers in [2,4]:
        t=time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            cases=list(pool.map(_case,combos))
        elapsed=time.perf_counter()-t
        md=max(max(abs(a[k]-b[k]) for k in ("Sigma_end","b_end","J00_end"))
               for a,b in zip(serial,cases))
        if md>5e-13:raise ArithmeticError("process scientific parity fail")
        process.append(dict(workers=workers,wall_s=elapsed,
                            speedup=elapsed_serial/elapsed,
                            max_absolute_endpoint_difference=md))
    winner=min(chunks,key=lambda z:z["median_s"])
    return {
        "schema":"rei.bass160.massive_radial_ode_benchmark.v1",
        "single_thread_environment":"OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1",
        "scalar_owned_moment_once_per_sample":scalar,
        "source_cases":1024,"selected_chunk":winner["chunk"],
        "massive_radial_chunks":chunks,
        "physical_IVP_processes":{"cases":len(combos),
            "serial_wall_s":elapsed_serial,"parallel_runs":process,
            "warning":"independent background IVP only; no native REI full solver"},
        "scientific_stability":"identical values within stated max_abs tolerance",
        "not_full_REI_speedup":True,
    }


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",required=True,type=Path)
    v=cli.parse_args()
    result=evaluate()
    v.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "best_chunk":result["selected_chunk"],
        "speedups":[(c["chunk"],c["speedup_vs_one_scalar_owner_call_per_state"])
                     for c in result["massive_radial_chunks"]],
        "process":result["physical_IVP_processes"],
    },indent=2))
