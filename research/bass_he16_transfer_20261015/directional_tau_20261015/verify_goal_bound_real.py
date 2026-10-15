"""Reproduce real-source perturbation and bounded-memory sensitivity benchmark."""
from __future__ import annotations
import argparse
import json
import math
import sys
import time
import statistics
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from clock_decompose_signed import read_caches
from signed_prefix_tau import taucum
from directional_tau import read_geometry, directional_moments
from directional_goal_bound import maxima_chunked, maxima_vectorized, F_HE
from goal_error_budget import N_H0, A_REF


def quad(source, b, z=0.75):
    return np.longdouble(
        directional_moments(source,b,z_targets=(z,),angular_orders=(128,))
        [0]["selected"]["tau_legendre_a2"]
    )


def actual_perturbation_audit(base_cache, geom_cache, goal_json, z=0.75,
                              eps_b=1e-6, eps_x=1e-6):
    if not 0 < eps_b < 1e-4 or not 0 < eps_x < 1e-4:
        raise ValueError("Perturbation amplitudes outside preselected audit range")
    hist,manifest,elapsed=read_caches(base_cache)
    geom=read_geometry(geom_cache,base_cache,manifest)
    qcases=("SHEAR_HALF_PLUS","SHEAR_HALF_MINUS")
    originals={}
    for case in qcases:
        originals[case]=quad(hist[case],geom[case],z)
    odd_original=(originals[qcases[0]]-originals[qcases[1]])/2

    perturbed_geo={}
    for i,case in enumerate(qcases):
        a=hist[case]["a"]
        loga=np.log(a)
        form=np.sin(2*np.pi*(loga-loga[0])/(loga[-1]-loga[0]))
        pert_b=geom[case]+((1 if i==0 else -1)*eps_b)*form
        perturbed_geo[case]=quad(hist[case],pert_b,z)
    odd_geo=(perturbed_geo[qcases[0]]-perturbed_geo[qcases[1]])/2
    delta_geom=abs(odd_geo-odd_original)

    h=hist[qcases[0]]
    nH=np.asarray(N_H0*(A_REF/h["a"].astype(np.longdouble))**3,dtype=np.float64)
    ne_extra=nH*(1+3*float(F_HE))*eps_x
    ne_plus=h["ne_cm3"]+ne_extra
    tau_plus,_=taucum(h["t_s"],ne_plus)
    h_changed=dict(h,ne_cm3=ne_plus,tau=tau_plus)
    new_plus=quad(h_changed,geom[qcases[0]],z)
    odd_x=(new_plus-originals[qcases[1]])/2
    delta_x=abs(odd_x-odd_original)

    row=next(r for r in goal_json["derived_sampled_directional"]
             if r["q_abs"]=="0.005" and r["z_rel"]==z)
    cap_g=np.longdouble(row["sensitivity_coeff_geometry"])*eps_b
    cap_x=np.longdouble(row["sensitivity_coeff_ion_fractions"])*eps_x
    if delta_geom > cap_g or delta_x > cap_x:
        raise AssertionError("Real-source directional perturbation violates analytic conditional bound")
    return {
        "schema":"he18.axbi.directional_tau2_empirical_bound_test.v1",
        "status":"MANUFACTURED_PERTURBATIONS_ON_REAL_STORED_SOURCES_PASS",
        "q_abs":0.005,"z_rel":z,
        "sup_geometry_error_injected":eps_b,
        "sup_species_absolute_error_injected":eps_x,
        "baseline_odd_tau2":format(odd_original,".20g"),
        "geometry_modified_odd_tau2":format(odd_geo,".20g"),
        "species_modified_odd_tau2":format(odd_x,".20g"),
        "abs_delta_odd_due_to_geometry":format(delta_geom,".20g"),
        "conditional_geometry_upper_bound":format(cap_g,".20g"),
        "abs_delta_odd_due_to_species":format(delta_x,".20g"),
        "conditional_species_upper_bound":format(cap_x,".20g"),
        "geometry_falsification_test_pass":bool(delta_geom <= cap_g),
        "species_falsification_test_pass":bool(delta_x <= cap_x),
        "real_history_sha256":{c:manifest["cases"][c]["history_sha256"] for c in qcases},
        "limitations":"Algorithmic perturbation under frozen a,t,nH, not native ODE rerun or scientific enclosure",
    }


def benchmark_maxima(base_cache, geom_cache, nrepeat=5):
    hist,manifest,elapsed=read_caches(base_cache)
    geom=read_geometry(geom_cache,base_cache,manifest)
    measures={"chunk16384":[],"vectorized":[]}
    ratios=[]
    # ABBA/BAAB interleaving avoids bias from method-order or warm-up.
    schedule=(("chunk16384","vectorized"),("vectorized","chunk16384"))
    for rep in range(nrepeat):
        order=schedule[rep%2]
        for method in order:
            t0=time.perf_counter()
            for case in hist:
                h=hist[case]
                if method=="chunk16384":
                    L,M,m=maxima_chunked(h["a"],h["t_s"],h["ne_cm3"],geom[case],16384)
                else:
                    L,M=maxima_vectorized(h["a"],h["t_s"],h["ne_cm3"],geom[case])
                if rep==0:
                    ratios.append([case,method,float(L),float(M)])
            measures[method].append(time.perf_counter()-t0)
    compare={}
    for case in hist:
        c=next(x for x in ratios if x[0]==case and x[1]=="chunk16384")
        v=next(x for x in ratios if x[0]==case and x[1]=="vectorized")
        relL=abs(c[2]-v[2])/max(abs(v[2]),1e-30)
        relM=abs(c[3]-v[3])/max(abs(v[3]),1e-30)
        if max(relL,relM)>1e-10:raise ValueError("Chunk/source coefficient numerical mismatch")
        compare[case]={"rel_L":relL,"rel_M":relM}
    return {
        "schema":"he18.axbi.directional_goal_bound_performance.v1",
        "status":"USER_UBUNTU_MEASURED",
        "mode":"five source-cache histories x 200001 nodes, NumPy longdouble max derivative bound, no I/O or ODE",
        "nrepeat":nrepeat,
        "wall_seconds":measures,
        "median_seconds":{k:statistics.median(v) for k,v in measures.items()},
        "chunk_vs_vectorized_ratio":statistics.median(measures["chunk16384"])/statistics.median(measures["vectorized"]),
        "parity":compare,
        "space":"chunk O(16384) scratch elements versus O(200001) in vectorized; inputs O(N) shared",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--base-cache",type=Path,required=True)
    p.add_argument("--geometry-cache",type=Path,required=True)
    p.add_argument("--goal",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result={
        "empirical":actual_perturbation_audit(args.base_cache,args.geometry_cache,
                                             json.loads(args.goal.read_text())),
        "performance":benchmark_maxima(args.base_cache,args.geometry_cache)
    }
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
