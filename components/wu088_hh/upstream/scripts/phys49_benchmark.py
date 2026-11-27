#!/usr/bin/env python3
"""PHYS49 matched high-ell source-block vectorization and rational-search CPU."""
from __future__ import annotations
import argparse,json,sys,time,statistics,hashlib
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys49_dirichlet_collar import high_l_dirichlet_collar
from phys49_dirichlet_preview import angular_basis


def benchmark(source:Path,repeats:int=12):
    if not 3<=repeats<=120:raise ValueError("bounded benchmark repetitions")
    # Exact original 21-mode, one-target N20 certificate: compare 25
    # candidate rho search against already-certified rho18.
    records={}
    for tag,rhos in (("all_25_rhos",tuple(range(4,29))),("locked_rho18",(18,))):
        elapsed=[]
        out=None
        for _ in range(repeats):
            t=time.perf_counter()
            result=high_l_dirichlet_collar(source,Ns=(20,),rhos=rhos,workers=1)
            elapsed.append(time.perf_counter()-t)
            if out is None:out=result
            elif result["exact_outward_tail_rows"]!=out["exact_outward_tail_rows"]:
                raise ArithmeticError("nonrepeatable original rational source result")
        records[tag]={
            "rhos":list(rhos),"repeats":repeats,
            "median_wall_s":statistics.median(elapsed),
            "scoped_output":out["exact_outward_tail_rows"][0],
        }
    if records["all_25_rhos"]["scoped_output"]!=records["locked_rho18"]["scoped_output"]:
        raise ArithmeticError("rho18 does not recover same original N20 bound")
    # Matched original screened angular Gram integral, the same 64 radial
    # and 128 angular nodes, one BLAS thread for both options.
    nrad=64;nmu=128
    mu,w=np.polynomial.legendre.leggauss(nmu)
    Ph=angular_basis(mu,28)[:,21:29]
    r=20+(7/(nrad+1))*np.arange(1,nrad+1)
    samples=[]
    for ri in r:
        sep=np.sqrt(ri*ri+.7**2-2*ri*.7*mu)
        S=(1+1/sep)*np.exp(-2*sep)
        samples.append(w*S/2)
    def vectorized():
        return [Ph.T @ (wt[:,None]*Ph) for wt in samples]
    def scalar():
        out=[]
        for wt in samples:
            v=np.empty((8,8))
            for ell in range(8):
                for j in range(8):
                    v[ell,j]=np.sum(wt*Ph[:,ell]*Ph[:,j])
            out.append(v)
        return out
    fv=vectorized();sv=scalar()
    max_diff=max(float(np.max(np.abs(x-y))) for x,y in zip(fv,sv))
    if max_diff>1e-30:raise ArithmeticError("batched Gram not parity with scalar")
    times={}
    for tag,fn in (("batched_numpy_Gram",vectorized),("pairwise_numpy_sums",scalar)):
        rows=[]
        for _ in range(repeats):
            t=time.perf_counter()
            fn()
            rows.append(time.perf_counter()-t)
        times[tag]=statistics.median(rows)
    return {
        "schema":"WU088_HH_PHYS49_MATCHED_HIGH_ELL_BLOCK_BENCH_V1",
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "exact_rational_N20":records,
        "rational_25candidate_over_certified_rho18_speedup":
            records["all_25_rhos"]["median_wall_s"]/records["locked_rho18"]["median_wall_s"],
        "float_screened_Gram": {
            "n_radial":nrad,"n_angular":nmu,"partial_waves":list(range(21,29)),
            "median_times_s":times,
            "scalar_over_batched_speedup":times["pairwise_numpy_sums"]/times["batched_numpy_Gram"],
            "max_abs_same_quadrature_mat_difference":max_diff,
        },
        "scope":"exact rational same N20 certificate vs fixed rho; float Gram benchmark explicitly NONCERTIFYING and not REI runtime"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--repeats",type=int,default=12)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    data=benchmark(a.source,a.repeats)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({
        "exact_rational_speedup":data["rational_25candidate_over_certified_rho18_speedup"],
        "noncert_numpy_batched_speedup":data["float_screened_Gram"]["scalar_over_batched_speedup"],
        "matrix_abs_diff":data["float_screened_Gram"]["max_abs_same_quadrature_mat_difference"],
    }))
if __name__=="__main__":main()
