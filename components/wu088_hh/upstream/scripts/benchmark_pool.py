#!/usr/bin/env python3
"""Topology-aware process/thread benchmark on identical foreign-component workloads."""
from pathlib import Path
import argparse,hashlib,json,multiprocessing,os,sys,time
from concurrent.futures import ProcessPoolExecutor
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
from wu088_hh.native_candidate import ForeignKernel
from wu088_hh.hardware import inspect_host, partition_affinity_groups
from wu088_hh.autotune import benchmark_configurations
from build_native import build
STATE=None


def init_worker(libpath,threads,grid,exponents,z,q,affinity_groups,counter,lock,barrier):
    global STATE
    with lock:
        idx=counter.value;counter.value+=1
    if idx>=len(affinity_groups):
        raise RuntimeError('worker affinity index overflow')
    cpus=set(affinity_groups[idx]);os.sched_setaffinity(0,cpus)
    kernel=ForeignKernel(Path(libpath));kernel.set_threads(threads)
    STATE=(kernel,grid,exponents,z,q,tuple(sorted(cpus)))
    barrier.wait()


def work(pair):
    kernel,grid,exponents,z,q,affinity=STATE;t,gs,gw,W=grid;i,j=pair
    pars=np.array([exponents[i],exponents[j],z,q]);start=time.perf_counter();cpu=time.process_time()
    out,absolute=kernel(t,gs,gw,W,pars)
    return dict(pair=pair,output=out,absolute=absolute,wall=time.perf_counter()-start,
                cpu=time.process_time()-cpu,team=kernel.observed_threads,
                affinity=list(sorted(os.sched_getaffinity(0))),planned_affinity=list(affinity))


def run_case(libpath,workers,threads,grid,d,z,pairs,affinity_groups):
    ctx=multiprocessing.get_context('spawn');counter=ctx.Value('i',0);lock=ctx.Lock();barrier=ctx.Barrier(workers);start=time.perf_counter()
    groups=[tuple(sorted(g)) for g in affinity_groups]
    with ProcessPoolExecutor(max_workers=workers,mp_context=ctx,
            initializer=init_worker,initargs=(libpath,threads,grid,d['exponents'],z,float(d['v']),groups,counter,lock,barrier)) as pool:
        rows=list(pool.map(work,pairs,chunksize=1))
    return rows,time.perf_counter()-start


def _cross_l3(groups,l3_by_cpu):
    return sum(len({l3_by_cpu[c] for c in g})>1 for g in groups)


def _observed_affinity_valid(rows,groups):
    planned={tuple(sorted(g)) for g in groups};observed={tuple(r['affinity']) for r in rows}
    if not observed or not observed<=planned:return False
    if len(observed)!=len(groups):return False
    obs=[set(g) for g in observed]
    return sum(len(g) for g in obs)==len(set().union(*obs))


def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',required=True,type=Path)
    p.add_argument('--n',type=int,default=32);p.add_argument('--g',type=int,default=80);p.add_argument('--z',type=float,default=16)
    p.add_argument('--pairs',type=int,default=12);p.add_argument('--repeats',type=int,default=2)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('new report path required')
    if not 4<=a.n<=192 or not 1<=a.g<=192 or not 1<=a.pairs<=12 or not 1<=a.repeats<=5 or not np.isfinite(a.z) or abs(a.z)>64:p.error('invalid benchmark parameters')
    runtime=a.runtime.resolve();profile=json.loads((ROOT/'data/pair_cost_profile.json').read_text())
    source=runtime/'r31a/wide_hybrid_run.py';model=runtime/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'
    for f,h in [(source,profile['scientific_driver_sha256']),(model,profile['model_sha256'])]:
        if hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise ValueError('frozen runtime source changed')
    sys.path.insert(0,str(runtime/'completion/mixed_h'));import native
    d,t,W,gs,gw=native.grid(a.n,a.g);grid=(t,gs,gw,W[0])
    hw_phys=inspect_host(use_smt=False);hw_log=inspect_host(use_smt=True)
    physical_budget=min(12,hw_phys['effective_cpu_budget'])
    logical_budget=min(24,hw_log['effective_cpu_budget'])
    pairs=[(i,j) for i in (0,3,7,11) for j in (0,7,11)][:a.pairs]
    configs=benchmark_configurations(physical_budget=physical_budget,logical_budget=logical_budget,pairs=len(pairs))
    topology={int(k):tuple(v) for k,v in hw_log['topology'].items()}
    l3_by_cpu={int(k):v for k,v in hw_log['l3_by_cpu'].items()}
    allowed=set(hw_log['allowed_logical_cpus'])
    built=build()
    ref_workers=min(physical_budget,len(pairs))
    ref_groups=partition_affinity_groups(topology,allowed,workers=ref_workers,kernel_threads=1,use_smt=False,l3_by_cpu=l3_by_cpu)
    baseline,reference_wall=run_case(built['libraries']['reference']['path'],ref_workers,1,grid,d,a.z,pairs,ref_groups)
    reference={tuple(r['pair']):r for r in baseline};results=[]
    for rep in range(a.repeats):
        order=configs[rep%len(configs):]+configs[:rep%len(configs)]
        for procs,threads,use_smt in order:
            groups=partition_affinity_groups(topology,allowed,workers=procs,kernel_threads=threads,use_smt=use_smt,l3_by_cpu=l3_by_cpu)
            rows,wall=run_case(built['libraries']['candidate']['path'],procs,threads,grid,d,a.z,pairs,groups)
            equal=all(np.array_equal(r['output'],reference[tuple(r['pair'])]['output']) and np.array_equal(r['absolute'],reference[tuple(r['pair'])]['absolute']) for r in rows)
            valid=_observed_affinity_valid(rows,groups)
            record=dict(repetition=rep,processes=procs,kernel_threads=threads,use_smt=use_smt,total_thread_budget=procs*threads,
                        batch_wall_including_spawn_s=wall,sum_pair_cpu_s=sum(r['cpu'] for r in rows),
                        numerical_array_exact_equal=equal,observed_teams=sorted(set(r['team'] for r in rows)),
                        affinity_groups=[sorted(g) for g in groups],observed_affinity_groups=sorted({tuple(r['affinity']) for r in rows}),
                        affinity_disjoint=valid,cross_l3_workers=_cross_l3(groups,l3_by_cpu))
            results.append(record);print(json.dumps(record),flush=True)
            if not equal:raise RuntimeError('parallel configuration changes scientific arrays')
            if not valid:raise RuntimeError('worker affinity groups were not observed disjointly')
    result=dict(schema='WU088_PROCESS_THREAD_TOPOLOGY_BENCHMARK_V2',n=a.n,g=a.g,z=a.z,pairs=pairs,
                source_identity={'driver_sha256':profile['scientific_driver_sha256'],'model_sha256':profile['model_sha256']},
                host=hw_log,physical_view=hw_phys,build_key=built['build_key'],reference_processes=ref_workers,
                reference_wall_s=reference_wall,physical_budget=physical_budget,logical_budget=logical_budget,samples=results,
                full_H0_cost_included=False,production_admitted=False,configuration_autopromotion=False,
                scope='foreign-component workload including spawn and explicit affinity; no provider promotion from this benchmark alone')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'status':'TOPOLOGY_POOL_BENCHMARK_COMPLETE_NOT_PROMOTED','report':str(a.out)}))
if __name__=='__main__':main()
