"""Same-workload massive finite-radial source memory/throughput controls.

Actual original PR140 MassiveRadialGrid source and actual NumPy batch path;
precomputed inputs, one calculation of complete J0/J2/J4 tower per reference.
Memory via tracemalloc is Python/NumPy allocations, NOT whole process RSS.
"""
from __future__ import annotations
import argparse,json,statistics,time,tracemalloc,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from initial_cancellation import source_identity
from massive_radial import MassiveRadialGrid

def timed(f,n=4):
    f()
    vals=[];state=None
    for i in range(n):
        a=time.perf_counter()
        state=f()
        vals.append(time.perf_counter()-a)
    return statistics.median(vals),vals,state

def memory(f):
    f()
    tracemalloc.start()
    try:
        out=f()
        actual,peak=tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak,out

def run():
    source_identity()
    g=MassiveRadialGrid(30.,nr=96,nmu=32)
    xx=np.linspace(0,1.43,768)
    bs=.02*np.sin(2*xx)
    A=.5
    def baseline():
        return np.array([[v.j0,v.j2,v.j4] for v in
           (g.moments(float(x),float(b),A,2) for x,b in zip(xx,bs))])
    ref_time,ref_repeats,ref=timed(baseline)
    runs=[]
    for chunk in (4,8,16,32,64,128):
        fn=lambda chunk=chunk:g.batch(xx,bs,A,2,chunk=chunk)
        t,times,result=timed(fn,n=5)
        peak,_=memory(fn)
        maxabs=float(np.max(abs(result-ref)))
        if maxabs>8e-15:
            raise ArithmeticError(f"SOURCE_KINETIC_CONE_VEC_NOT_MATCHED {chunk} {maxabs}")
        runs.append({"chunk":chunk,"wall_median_seconds":t,
            "wall_individual_seconds":times,"tracemalloc_peak_bytes":peak,
            "max_tensor_absolute_error_vs_fair_scalar":maxabs,
            "speedup_vs_fair_scalar":ref_time/t})
    return {"schema":"rei.BASS.massive_J_i.chunk_source_benchmark.v1",
        "source_pr140_sha":"b1cba753083ad83049c23ff538834564b49b7b6e",
        "input_samples":len(xx),"mass_over_Tref":30.,
        "initial_A_massive":A,"radial_GL_nodes":96,"angular_GL_nodes":32,
        "full_J_towers":["J0_i","J2_i","J4_i"],"i_max":2,
        "scalar_fair_reference_wall_median_s":ref_time,
        "scalar_repeats":ref_repeats,
        "measurements":runs,
        "actual_peak_memory_type":"tracemalloc traced Python+NumPy, not total RSS",
        "parallelism":"single process source-vector batch, process-level case throughput in separate PARALLEL_BENCHMARK.json",
        "whole_EoR_solver_speedup":None}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    v=run()
    args.output.write_text(json.dumps(v,indent=2)+"\n")
    print("FAIR_SCALAR",v["scalar_fair_reference_wall_median_s"])
    for k in v["measurements"]:
        print("CHUNK",k["chunk"],"SPEEDUP",k["speedup_vs_fair_scalar"],
              "PEAK_MB",k["tracemalloc_peak_bytes"]/1e6,"MAX_ERROR",k["max_tensor_absolute_error_vs_fair_scalar"])
