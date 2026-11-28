#!/usr/bin/env python3
"""Source-bound low-order foreign-component benchmark. No new production pair files."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,statistics,sys,time
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
from wu088_hh.native_candidate import ForeignKernel
from wu088_hh.hardware import inspect_host
from build_native import build

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--n',type=int,default=32);ap.add_argument('--g',type=int,default=80)
    ap.add_argument('--z',type=float,default=16);ap.add_argument('--ia',type=int,default=0);ap.add_argument('--ib',type=int,default=0)
    ap.add_argument('--threads',default='1,2,4');ap.add_argument('--repeats',type=int,default=3)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError('new benchmark output path required')
    if not 0<=a.ia<12 or not 0<=a.ib<12 or not 1<=a.repeats<=10:ap.error('invalid pair/repeat request')
    if not 4<=a.n<=192 or not 1<=a.g<=192 or not np.isfinite(a.z) or abs(a.z)>64:ap.error('outside benchmark domain')
    runtime=a.runtime.resolve();driver=runtime/'r31a/wide_hybrid_run.py'
    if sha(driver)!='5add2f769bdaa9721ce1fe90dd02a2c6dd6a2b3c617b6eeec0032bd38849acb6':raise ValueError('scientific driver changed')
    hw=inspect_host(use_smt=True);os.sched_setaffinity(0,hw['cpus']);budget=hw['effective_cpu_budget']
    threads=sorted(set(int(x) for x in a.threads.split(',')))
    if not threads or any(t<1 or t>budget for t in threads):ap.error(f'threads must lie within effective budget {budget}')
    profile=json.loads((ROOT/'data/pair_cost_profile.json').read_text())
    model=runtime/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'
    if sha(model)!=profile['model_sha256']:raise ValueError('frozen model changed')
    sys.path.insert(0,str(runtime/'completion/mixed_h'))
    import native  # exact runtime grid; does not construct Native or compile H0.
    d,t,W,gs,gw=native.grid(a.n,a.g)
    pars=np.array([float(d['exponents'][a.ia]),float(d['exponents'][a.ib]),a.z,float(d['v'])])
    args=(t,gs,gw,W[0],pars);built=build()
    kernels={'reference':ForeignKernel(Path(built['libraries']['reference']['path'])),
             'candidate':ForeignKernel(Path(built['libraries']['candidate']['path']))}
    old=runtime/'r31a/hybrid12_wide_h.so'
    old_kernel=ForeignKernel(old);ref,sa=kernels['reference'](*args);historical,hsa=old_kernel(*args)
    old_equal=bool(np.array_equal(ref,historical) and np.array_equal(sa,hsa))
    if not old_equal:raise RuntimeError('rebuilt reference differs from archived original library for benchmark input')
    cases=[('reference',1)]+[('candidate',t) for t in threads]
    timings={f'{lane}_{nt}':[] for lane,nt in cases};checks=[]
    # Rotate order between repetitions to reduce fixed-order timing bias.
    for rep in range(a.repeats):
        order=cases[rep%len(cases):]+cases[:rep%len(cases)]
        for lane,nt in order:
            lib=kernels[lane];lib.set_threads(nt);start=time.perf_counter();cpu=time.process_time()
            val,absolute=lib(*args);dt=time.perf_counter()-start;dc=time.process_time()-cpu
            equal=bool(np.array_equal(val,ref) and np.array_equal(absolute,sa))
            check=dict(lane=lane,threads=nt,observed_threads=lib.observed_threads,numerical_array_exact_equal=equal,
                max_abs_component_delta=float(np.max(np.abs(val-ref))),wall_seconds=dt,cpu_seconds=dc)
            checks.append(check);timings[f'{lane}_{nt}'].append(dt)
            print(json.dumps(check),flush=True)
            if not equal:raise RuntimeError('candidate numerical equivalence failed; no promotion')
    med={k:statistics.median(v) for k,v in timings.items()}
    result=dict(schema='WU088_NATIVE_COMPONENT_BENCHMARK_V1',n=a.n,g=a.g,z=a.z,ia=a.ia,ib=a.ib,
        grid_source_sha256=sha(runtime/'completion/mixed_h/native.py'),model_sha256=sha(model),
        frozen_original_binary_sha256=sha(old),original_rebuilt_reference_equal=old_equal,
        build=built,host=hw,samples=checks,median_wall_seconds=med,
        measured_component_speedup_vs_reference={k:med['reference_1']/v for k,v in med.items()},
        full94_or_full49_validation=False,production_admitted=False,heavy_pair_state_mutation=False,
        scope='actual frozen107 quadrature inputs at specified n/g, one foreign primitive pair; not end-to-end H performance')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'status':'COMPONENT_BENCHMARK_COMPLETE_NOT_PROMOTED','report':str(a.out),'medians':med}))
if __name__=='__main__':main()
