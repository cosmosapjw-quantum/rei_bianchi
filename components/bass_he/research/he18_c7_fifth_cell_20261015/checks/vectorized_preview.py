#!/usr/bin/env python3
"""Vectorized, non-admitting preview of fourth-cell photon redshift/thresholds.

The true interval solver ALWAYS processes every node and independently certifies
branch guards. Float64 screening here is a diagnostic, never an opacity gate.
"""
import json,time
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def preview():
    import sys
    sys.path.insert(0,str(ROOT/"src"))
    from warm_interval import WarmSource,Jet,V,lo,hi
    src=WarmSource()
    env=src.env(Jet.variable(V("0.5"),0))
    a=float((lo(env["a"].c[0])+hi(env["a"].c[0]))/2)
    b=float((lo(env["b"].c[0])+hi(env["b"].c[0]))/2)
    with np.load(ROOT/"inputs/P01_STATE.npz",allow_pickle=False) as n:
        q=np.asarray(n["q_eV"],dtype=np.float64)
        mu=np.asarray(n["mu0"],dtype=np.float64)
    mu2=mu*mu
    t0=time.perf_counter()
    energy=q*np.sqrt(np.exp(2*b)*(1-mu2)+np.exp(-4*b)*mu2)/a
    vector_ms=(time.perf_counter()-t0)*1000
    whole=json.loads((ROOT/"results/whole_jets.json").read_text())
    exact=whole["nodes"]
    assert len(energy)==len(exact)==2904
    # Verification of the preview only, not a source admissibility assumption.
    escaped=0
    for i,node in enumerate(exact):
        lower,upper=map(lambda s:float(Q(s)),node["E"])
        tol=max(1e-12*max(1,abs(energy[i])),1e-12)
        if energy[i]<lower-tol or energy[i]>upper+tol:escaped+=1
    transparent=sum(all(all(Q(z)==0 for z in coeff)
                    for coeff in node["sigma"]) for node in exact)
    assert escaped==0,"NONCERTIFIED_PREVIEW_OUTSIDE_INTERVAL"
    return dict(schema="he18.c7.vectorized_diagnostic.v1",nodes=2904,
        numpy_vectorized_preview_ms=vector_ms,
        below_HI_edge_count=int(np.sum(energy<13.60)),
        rigorous_transparent_count=transparent,
        preview_outside_whole_interval=escaped,
        used_to_skip_physics=False,
        source_ODE_calls=0)
if __name__=="__main__":
    target=ROOT/"results/VECTORIZED_PREVIEW.json"
    if target.exists():raise SystemExit("REFUSE_OVERWRITE")
    out=preview()
    target.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
