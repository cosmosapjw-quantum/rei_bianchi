"""Counterfactual decomposition of directional tau: geometry-only vs native coupled.

This operation substitutes the signed-q b(a) onto the ZERO reference normal
clock, ne(t), tau(t) and a-grid. It deliberately does *not* solve the coupled
Einstein/atomic equations and is only a linear-geometry sensitivity diagnostic.
"""
import argparse
import json
from pathlib import Path

import numpy as np

from directional_tau import (
    ANGULAR_N, CASE_ORDER, TARGET_ZREL, PREC, directional_moments,
    read_caches, read_geometry,
)

def calculate(base_cache: Path, geometry_cache: Path):
    data, parent, timing = read_caches(base_cache)
    geometries = read_geometry(geometry_cache, base_cache, parent)
    ref=data["ZERO"]
    a0=ref["a"]
    reference_loga=np.log(a0)
    results={}
    for case in CASE_ORDER:
        qloga=np.log(data[case]["a"])
        geo=np.interp(reference_loga,qloga,geometries[case])
        # Pin exact start/end geometries to avoid extrapolation of slightly
        # different float64 input endpoint representations.
        if a0[0] < data[case]["a"][0] or a0[-1] > data[case]["a"][-1]:
            raise ValueError("Counterfactual reference mean-a domain not supported")
        output=directional_moments(ref,geo,TARGET_ZREL,ANGULAR_N)
        results[case]=output
    out=[]
    for iz,z in enumerate(TARGET_ZREL):
        def m(case,key):
            return PREC(results[case][iz]["selected"][key])
        full=[]
        # Signs are compared at the same observer mean-a endpoint and local angle.
        for q,neg,pos in (
            (0.005,"SHEAR_HALF_MINUS","SHEAR_HALF_PLUS"),
            (0.01,"SHEAR_MINUS","SHEAR_PLUS")
        ):
            even=(m(pos,"tau_sky_monopole")+m(neg,"tau_sky_monopole"))/2-m("ZERO","tau_sky_monopole")
            oddq=(m(pos,"tau_legendre_a2")-m(neg,"tau_legendre_a2"))/2
            full.append({
                "q":q,
                "geometry_only_even_monopole":format(even,".20g"),
                "geometry_only_odd_tau_a2":format(oddq,".20g"),
            })
        out.append({"z_rel":z,"geometry_only":full})
    return {
        "schema":"he18.axbi.frozen_zero_gas_geometry.v1",
        "status":"COUNTERFACTUAL_GEOMETRY_ONLY_NONAUTHORITATIVE",
        "reference":"ZERO n_e(t), t(a), tau(t) held fixed, but b_q(a) imported from signed source",
        "interpretation":"Not a self-consistent Bianchi radiation/ionization solution; quantifies geometry-induced directional redshift response only, without native q-dependent gas and clock evolution",
        "original_source_sha256":{case:parent["cases"][case]["history_sha256"] for case in CASE_ORDER},
        "directional":out
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base-cache",type=Path,required=True)
    p.add_argument("--geometry-cache",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=calculate(args.base_cache,args.geometry_cache)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
