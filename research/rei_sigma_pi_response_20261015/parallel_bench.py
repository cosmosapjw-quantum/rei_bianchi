"""Actually parallelize independent source-bound FV Einstein response experiments.

The native scientific ODE itself is unchanged and not implicitly multi-threaded.
Uses one process per independent initial-condition sample. Source identities,
q/π parameters and initial state remain identical across serial/parallel.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import hashlib,json,statistics,time
from pathlib import Path
import numpy as np
from response import one,BASE,source_lock,check_parent,CanonicalFVSpecies

HERE=Path(__file__).resolve().parent
CASES=[]
for q in (0.,5e-5,-5e-5,.0005):
 for kg,kn,A in ((.2,.2,.5),(.17,.2,.5),(.2,.17,.5),(.2,.2,.45)):
  CASES.append((q,kg,kn,A))

def work(params):
    r=one(*params,donor=None,n=51,rtol=4e-11,atol=4e-13)
    return r["obs"][-1,:].tolist(),r["physical"]["Sigma_end"]

def performance(trials=3):
    if check_parent()!= "91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5":
        raise RuntimeError("PARENT_FV_BYTE_IDENTITY_CHANGED")
    allres={}
    compare=None
    for workers in (1,2,4):
        tim=[];last=None
        for _ in range(trials):
            t=time.perf_counter()
            if workers==1:
                result=list(map(work,CASES))
            else:
                with ProcessPoolExecutor(max_workers=workers) as pool:
                    result=list(pool.map(work,CASES))
            tim.append(time.perf_counter()-t)
            last=np.array([a[0]+[a[1]] for a in result])
        if compare is None:compare=last
        err=float(np.max(abs(compare-last)))
        if err>3e-14:raise AssertionError("WORKER_PARALLEL_PHYSICS_MISMATCH")
        allres[str(workers)]={"wall_seconds":tim,"median_wall_s":statistics.median(tim),
             "max_abs_diff_vs_serial":err}
    return {"schema":"rei.sigma_pi.C5.actual_process_performance.v1",
      "physical_sources":len(CASES),"independent_cases":CASES,
      "phase":"full Einstein+gamma+nu+positive FD massive, no HHe electron donor during performance isolation",
      "same_initial_sources_and_solver_all_workers":True,
      "worker_counts":[1,2,4],"repetitions":trials,
      "performance":allres,
      "observed_speedup_2v1":allres["1"]["median_wall_s"]/allres["2"]["median_wall_s"],
      "observed_speedup_4v1":allres["1"]["median_wall_s"]/allres["4"]["median_wall_s"],
      "native_ionizing_HHe_solver_speedup":None,
      "global_memory_peak_RSS":None}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    z=performance()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(z,indent=2)+"\n")
    print(json.dumps({k:v for k,v in z.items() if k!="independent_cases"},indent=2))
