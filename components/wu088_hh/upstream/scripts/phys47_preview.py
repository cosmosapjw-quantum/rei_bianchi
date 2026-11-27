#!/usr/bin/env python3
"""NONCERTIFYING original screened complex-ellipse NumPy kernel benchmark."""
from __future__ import annotations
import argparse, json, sys, time, cmath
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from wu088_hh.phys47_high_ell import high_ell_transfer,ellipse

def slow(rho,angles):
    rr=.7; r=20.
    out=[]
    for t in angles:
        mu=(rho*cmath.exp(1j*t)+cmath.exp(-1j*t)/rho)/2
        z=cmath.sqrt(r*r+rr*rr-2*r*rr*mu)
        out.append((1+1/z)*cmath.exp(-2*z))
    return np.array(out)

def fast(rho,angles):
    mu=(rho*np.exp(1j*angles)+np.exp(-1j*angles)/rho)/2
    s=np.sqrt(400+.49-28*mu)
    return (1+1/s)*np.exp(-2*s)


def benchmark(samples=8192,repeats=8):
    if not 64<=samples<=131072 or not 1<=repeats<=100:
        raise ValueError("bounded float diagnostic budget")
    angles=np.arange(samples,dtype=np.float64)*(2*np.pi/samples)
    rho=18
    t=time.perf_counter()
    for _ in range(repeats):
        a=fast(rho,angles)
    tf=time.perf_counter()-t
    t=time.perf_counter()
    for _ in range(repeats):
        b=slow(rho,angles)
    ts=time.perf_counter()-t
    diff=np.max(abs(a-b))
    rel=diff/max(np.max(abs(b)),1e-300)
    if not rel<1e-13:
        raise ArithmeticError("complex sampled screened original kernel mismatch")
    return {"schema":"WU088_HH_PHYS47_NONCERTIFYING_COMPLEX_VECTOR_BENCH_V1",
            "samples":samples,"repeats":repeats,"rho":rho,
            "numpy_vectorized_wall_s":tf,"scalar_python_wall_s":ts,
            "speedup":ts/tf,"relative_max_difference":float(rel),
            "physical_claim":"float complex-ellipse samples ONLY, not exact rational certificate"}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--samples",type=int,default=8192)
    p.add_argument("--repeats",type=int,default=8)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    v=benchmark(a.samples,a.repeats)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(v,indent=2)+"\n")
    print(json.dumps(v))
