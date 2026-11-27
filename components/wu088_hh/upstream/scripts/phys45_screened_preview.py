#!/usr/bin/env python3
"""Separate float64 vectorized screened 21-mode kernel and exact science containment."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys45_screened_preview import preview_matrix,vectorized_vs_scalar


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--exact",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 p.add_argument("--nodes",type=int,default=512)
 p.add_argument("--iterations",type=int,default=120)
 a=p.parse_args()
 cert=json.loads(a.exact.read_bytes())
 lmax=cert["lmax"]
 previews=[preview_matrix(n=n,lmax=lmax) for n in sorted(set((128,256,a.nodes)))]
 mainp=previews[-1]
 arr=np.array(mainp["matrix_float64"])
 matrix=cert["certified_V_matrix_interval"]
 ok=all(float(matrix[i][j][0])<=arr[i,j]<=float(matrix[i][j][1])
        for i in range(lmax+1) for j in range(lmax+1))
 if not ok:raise ArithmeticError("noncert independent Gauss outside strict exact rational interval")
 bench=vectorized_vs_scalar(n=a.nodes,lmax=lmax,iterations=a.iterations)
 scientific={
 "schema":"WU088_HH_PHYS45_NONCERTIFYING_GAUSS_AND_VECTOR_BENCH_V1",
 "interval_source":str(a.exact),
 "all_441_float64_samples_inside_exact_rational_certificates":ok,
 "nodes_experiment":[
    {"nodes":z["mu_nodes"],"V00":z["matrix_float64"][0][0],
     "V01":z["matrix_float64"][0][1],
     "lambda_min_float":z["min_eigen_float"],
     "lambda_max_float":z["max_eigen_float"]} for z in previews],
 "performance":bench,
 "not_a_proof":"float Gauss quadrature + eigenvalues only; original Fraction matrix provides certified values and analytic proof",
 }
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(scientific,indent=2)+"\n")
 print(json.dumps({
  "float_in_strict_brackets":ok,
  "vectorization_speedup":bench["speedup_scalar_over_batched"],
  "float_num_modes":lmax+1,
  "float_nodes":a.nodes,
  "max_float_same_quadrature_difference":bench["max_matrix_abs_difference"],
  "output":str(a.out)
 }))
if __name__=="__main__":
 main()
