#!/usr/bin/env python3
"""Science-resolution representative native exactness gate; no pair-state mutation."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import numpy as np
from wu088_hh.autotune import representative_pairs, validate_tuning_profile
from wu088_hh.hardware import inspect_host, partition_affinity_groups
from wu088_hh.native_candidate import ForeignKernel
from wu088_hh.scheduler import predict_costs,verify_profile
from build_native import build


def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--tuning-profile',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--z',default='16,64');a=p.parse_args()
    if a.out.exists():raise FileExistsError('new regression report path required')
    zs=[float(x) for x in a.z.split(',')]
    if not zs or any(not np.isfinite(z) or abs(z)>64 for z in zs):p.error('invalid z list')
    runtime=a.runtime.resolve();timing=json.loads((ROOT/'data/pair_cost_profile.json').read_text())
    driver=runtime/'r31a/wide_hybrid_run.py';model=runtime/'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz'
    verify_profile(timing,driver_sha=sha(driver),model_sha=sha(model),g=80,gamma_scale='unit')
    built=build();host=inspect_host(use_smt=True);profile=json.loads(a.tuning_profile.read_text())
    validate_tuning_profile(profile,host,built['build_key']);selected=profile['selected'];threads=int(selected['kernel_threads'])
    topology={int(k):tuple(v) for k,v in host['topology'].items()};l3={int(k):v for k,v in host['l3_by_cpu'].items()};allowed=set(host['allowed_logical_cpus'])
    group=partition_affinity_groups(topology,allowed,workers=1,kernel_threads=threads,use_smt=bool(selected.get('use_smt',False)),l3_by_cpu=l3)[0]
    os.sched_setaffinity(0,group)
    ref=ForeignKernel(Path(built['libraries']['reference']['path']));cand=ForeignKernel(Path(built['libraries']['candidate']['path']));cand.set_threads(threads)
    old=ForeignKernel(runtime/'r31a/hybrid12_wide_h.so')
    sys.path.insert(0,str(runtime/'completion/mixed_h'));import native
    d,t,W,gs,gw=native.grid(160,80);q=float(d['v']);rows=[]
    for z in zs:
        costs,_=predict_costs(timing,n=160,z=z)
        for pair in representative_pairs(costs):
            i,j=pair;pars=np.array([d['exponents'][i],d['exponents'][j],z,q],dtype=np.float64);args=(t,gs,gw,W[0],pars)
            rv,ra=ref(*args);ov,oa=old(*args)
            if not (np.array_equal(rv,ov) and np.array_equal(ra,oa)):
                raise RuntimeError('rebuilt reference differs from archived native provider')
            start=time.perf_counter();cv,ca=cand(*args);wall=time.perf_counter()-start
            equal=bool(np.array_equal(cv,rv) and np.array_equal(ca,ra))
            row=dict(z=z,pair=list(pair),predicted_cost_s=costs[pair],candidate_wall_s=wall,
                     numerical_array_exact_equal=equal,max_abs_component_delta=float(np.max(np.abs(cv-rv))),
                     observed_threads=cand.observed_threads)
            rows.append(row);print(json.dumps(row),flush=True)
            if not equal:raise RuntimeError('science-resolution representative exactness failed')
    result=dict(schema='WU088_R31M_SCIENCE_RESOLUTION_NATIVE_REGRESSION_V1',n=160,g=80,z=zs,
                tuning_profile_sha256=sha(a.tuning_profile),build_key=built['build_key'],selected=selected,
                affinity=sorted(group),rows=rows,all_exact=all(r['numerical_array_exact_equal'] for r in rows),
                production_provider_promoted=False,promotion_eligible_pending_independent_review=True,
                heavy_pair_state_mutation=False,status='PASS_REPRESENTATIVE_NATIVE_EXACTNESS_NOT_PROMOTED')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'status':result['status'],'report':str(a.out),'pairs':len(rows)}))
if __name__=='__main__':main()
