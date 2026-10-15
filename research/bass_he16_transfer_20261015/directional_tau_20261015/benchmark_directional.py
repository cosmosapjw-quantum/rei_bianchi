"""Measured vectorization/parallelization and native-row decimation diagnostics.

Performance is POSTPROCESSING ONLY. Decimation is not a rigorous source ODE or
photon-transport error bound.
"""
from __future__ import annotations
import argparse
import bisect
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import statistics
from time import perf_counter

import numpy as np
from numpy.polynomial.legendre import leggauss

from directional_tau import (
    CASE_ORDER, PREC, KAPPA, TARGET_ZREL,
    read_caches, read_geometry, directional_moments,
    solve_directional_redshift, tau_between_source_and_observer,
)


def reference_scalar_roots(loga, b, mu_values, redshift):
    """Independent Python math+bisect scalar implementation of geometric roots."""
    L = loga.tolist()
    B = b.tolist()
    def single(m):
        def f(u):
            j=max(0,min(len(L)-2,bisect.bisect_right(L,u)-1))
            x=(u-L[j])/(L[j+1]-L[j])
            db=B[j]+x*(B[j+1]-B[j])-B[-1]
            r=(1-m*m)*math.exp(2*db)+m*m*math.exp(-4*db)
            return L[-1]-u+.5*math.log(r)-math.log1p(redshift)
        lo,hi=L[0],L[-1]
        if f(lo)<-1e-13 or f(hi)>1e-13:
            raise ValueError("Out of source domain")
        for i in range(58):
            midpoint=(lo+hi)*.5
            if f(midpoint)>0:lo=midpoint
            else:hi=midpoint
        return (lo+hi)*.5
    return np.array([single(m) for m in mu_values])


def kernel_speed(data,b,repeat=7,nmu=128,target=.5):
    mus,_=leggauss(nmu)
    loga=np.log(data["a"])
    vector=[];scalar=[]
    v,s=None,None
    for _ in range(repeat):
        st=perf_counter()
        v,info=solve_directional_redshift(loga,b,mus,target)
        vector.append(perf_counter()-st)
        st=perf_counter()
        s=reference_scalar_roots(loga,b,mus,target)
        scalar.append(perf_counter()-st)
    discrepancy=float(np.max(abs(v-s)))
    if discrepancy>3e-14:
        raise ValueError(f"Independent direction redshift root parity failed: {discrepancy}")
    return {
      "n_mu":nmu,"target_zrel":target,"repeats":repeat,
      "scalar_independent_median_s":statistics.median(scalar),
      "numpy_vectorized_median_s":statistics.median(vector),
      "vectorization_speed_ratio":statistics.median(scalar)/statistics.median(vector),
      "max_abs_emission_ln_a_difference":discrepancy,
      "scope":"redshift root kernel only; not source IO or native solver",
    }


def independent_case_moment_parallel(data,geometries,repeats=5):
    observed={}
    for jobs in (1,2,4):
        wall=[]
        last=None
        for _ in range(repeats):
            start=perf_counter()
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                values=list(pool.map(lambda case:directional_moments(data[case],geometries[case]),
                                     CASE_ORDER))
            wall.append(perf_counter()-start)
            compact={case:[v["selected"]["tau_legendre_a2"] for v in xs]
                     for case,xs in zip(CASE_ORDER,values)}
            if last is not None and last!=compact:
                raise ValueError("Race/non-deterministic repeated angular results")
            last=compact
        observed[str(jobs)]={"measured_wall_s":wall,"median_wall_s":statistics.median(wall)}
        if jobs==1:serial=last
        elif serial!=last:raise ValueError("Serial vs thread-parallel result differed")
    return {
        "jobs":observed,
        "best_jobs":min(observed,key=lambda v:observed[v]["median_wall_s"]),
        "all_serial_parallel_angular_coefficients_equal":True,
        "scope":"five cached-case angle-root+quadrature postprocessors; Python ThreadPool, not subagents",
    }


def coarse_source_sensitivity(data,geometry,case="SHEAR_PLUS",
                              target=.5,mu_count=128):
    source=data[case]
    b=geometry[case]
    mus,w=leggauss(mu_count)
    tau_full,info=tau_between_source_and_observer(source,b,target,mus)
    p2=(3*mus*mus-1)/2
    def moments(vals):
        return (float(np.dot(w.astype(PREC),vals)/2),
                float(PREC(5)/2*np.dot(w.astype(PREC),vals*p2.astype(PREC))))
    ref=tuple(map(float,moments(tau_full)))
    outcomes=[]
    for stride in (2,4,8,16,32):
        idx=np.arange(0,len(b),stride,dtype=int)
        if idx[-1]!=len(b)-1:idx=np.r_[idx,len(b)-1]
        coarse={k:v[idx] for k,v in source.items()}
        coarse["tau"] = np.concatenate((
            [PREC(0)],
            np.cumsum(np.diff(coarse["t_s"]).astype(PREC)*
                      (coarse["ne_cm3"][:-1].astype(PREC)+coarse["ne_cm3"][1:].astype(PREC))
                      *KAPPA/2,dtype=PREC)))
        vals,_=tau_between_source_and_observer(coarse,b[idx],target,mus)
        m=moments(vals)
        outcomes.append({
            "stride":stride,
            "rows":len(idx),
            "tau_monopole":m[0],"tau_a2":m[1],
            "delta_monopole_vs_original":m[0]-ref[0],
            "delta_a2_vs_original":m[1]-ref[1],
            "relative_quad_discrepancy":abs(m[1]-ref[1])/abs(ref[1]),
        })
    return {
        "case":case, "z_rel":target, "mu":mu_count,
        "native_row_stride_probe_only_not_error_enclosure":True,
        "full_grid_monopole":ref[0],"full_grid_a2":ref[1],
        "downsampled":outcomes,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-cache",type=Path,required=True)
    p.add_argument("--geometry-cache",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data,manifest,elapsed=read_caches(args.base_cache)
    geometry=read_geometry(args.geometry_cache,args.base_cache,manifest)
    results={
       "schema":"he18.axbi.directional_tau_performance.v1",
       "status":"LOCAL_NATIVE_PYTHON_BENCHMARK_NUMERICALLY_CHECKED",
       "root_reference":kernel_speed(data["SHEAR_PLUS"],geometry["SHEAR_PLUS"]),
       "five_case_parallel":independent_case_moment_parallel(data,geometry),
       "stored_row_sensitivity":coarse_source_sensitivity(data,geometry),
       "input_cache_read_elapsed_s":elapsed,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(results,indent=2)+"\n")
    print(json.dumps(results,indent=2))


if __name__=="__main__":
    main()
