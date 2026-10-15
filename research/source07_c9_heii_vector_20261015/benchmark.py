#!/usr/bin/env python3
"""Compare same-physics C8 scalar loops versus vectorized C9 and hard-spectrum holdout.

No production chemistry or continuous emissivity solver is executed.
For reproducibility run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1.
"""
from __future__ import annotations
import json
import math
import statistics
import time
from pathlib import Path

import numpy as np
import experiment as c9

reference=Path(__file__).resolve().parents[1]/"source07_c8_age_compression_20261015/experiment.py"
scope={"__file__":str(reference),"__name__":"independent_c8_oracle"}
exec(compile(reference.read_text().split("\nresults=[]\n")[0],str(reference),"exec"),scope)
scalar=scope["vector"]
OUTPUT=Path(__file__).with_name("benchmark_results.json")


def timed(fn, repeats=3):
    values=[]
    for _ in range(repeats):
        t0=time.perf_counter()
        value=fn()
        values.append((time.perf_counter()-t0,value))
    return statistics.median(dt for dt,_ in values),values[-1][1]


def same_physics_benchmark():
    model=c9.Scenario(c9.ROOT)
    spec=c9.Spectrum()
    ages=np.geomspace(model.ar,.2,c9.AGE_COUNT)
    gas,_=c9.gas_states(model)
    q=.0
    def slow():
        return np.asarray([[scalar(float(a),q,tuple(g)) for a in ages] for g in gas])
    def fast():
        packets=c9.build_packets(model,spec,ages,q)
        return c9.evaluate_packets(packets,gas),packets
    slow_time,oracle=timed(slow)
    fast_time,(result,packets)=timed(fast)
    reduced=result[:,:,[0,1,2,3,5]]
    denominator=np.maximum(np.abs(oracle),1e-25)
    max_rel=float(np.max(np.abs(reduced-oracle)/denominator))
    bytes_precompute=int(sum(sum(part.nbytes for part in packet) for packet in packets))
    assert max_rel<1e-9, max_rel
    return {"q":q,"ages":len(ages),"gas_states":len(gas),
            "C8_scalar_median_s":slow_time,"C9_vector_median_s":fast_time,
            "same_physics_speedup":slow_time/fast_time,
            "C8_scalar_vs_C9_max_rel_error":max_rel,
            "precomputed_packet_memory_bytes":bytes_precompute,
            "packet_memory_is_not_whole_solver_memory":True}


class HardSource:
    """Independent power-law photon stress, not the frozen MD14/BB50K spectrum."""
    alpha=1.5
    norm=(1.-alpha)/(100.**(1.-alpha)-13.6**(1.-alpha))
    def phi(self,energies):
        return self.norm*np.asarray(energies,dtype=float)**(-self.alpha)


def source_transfer_stress():
    model=c9.Scenario(c9.ROOT)
    ages=np.geomspace(model.ar,.2,c9.AGE_COUNT)
    train,hold=c9.gas_states(model)
    gas=np.vstack((train,hold))
    w=c9.source_age_weights(model,ages,0.)
    bb=c9.evaluate_packets(c9.build_packets(model,c9.Spectrum(),ages,0.),gas)
    hard=c9.evaluate_packets(c9.build_packets(model,HardSource(),ages,0.),gas)
    # LP positive weights trained to BB50K, reused without retraining on hard source.
    sparse_bb=c9.design(bb,w,len(train),len(train))
    sparse_hard=c9.design(hard,w,len(train),len(train))
    def pull_weights(design):
        result=np.zeros(len(ages))
        for i,v in design["weights"]:
            result[i]=v
        return result
    bb_compressed=pull_weights(sparse_bb)
    hard_compressed=pull_weights(sparse_hard)
    def holdout_err(data,weights):
        full=data[:,:,:6].transpose(0,2,1)@w
        got=data[:,:,:6].transpose(0,2,1)@weights
        err=np.abs(got-full)/np.maximum(np.abs(full),1e-25)
        return {"max_relative":float(np.max(err[len(train):])),
                "by_feature":np.max(err[len(train):],axis=0).tolist(),
                "max_relative_training":float(np.max(err[:len(train)]))}
    def heii_frac(data):
        summed=w@data[4,:,:]
        return float(summed[4]/max(summed[2:5].sum(),1e-30))
    return {"q":0.,"hard_source":"phi(E) proportional to E^-1.5, emitted 13.6-100 eV; diagnostic only",
            "BB50K_HeII_absorption_fraction_train_4":heii_frac(bb),
            "hard_HeII_absorption_fraction_train_4":heii_frac(hard),
            "BB_fit_applied_to_hard":holdout_err(hard,bb_compressed),
            "hard_refit_on_hard":holdout_err(hard,hard_compressed),
            "hard_self_ledger":c9.physics_ledger(hard),
            "BB_retained":sparse_bb["retained"],"hard_retained":sparse_hard["retained"],
            "BB_fit_age_indices": [int(i) for i,_ in sparse_bb["weights"]],
            "hard_fit_age_indices": [int(i) for i,_ in sparse_hard["weights"]]}


def main():
    t=time.perf_counter()
    result={"same_physics_vectorization":same_physics_benchmark(),
            "cross_spectrum_stress":source_transfer_stress(),
            "elapsed_s":time.perf_counter()-t}
    OUTPUT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
