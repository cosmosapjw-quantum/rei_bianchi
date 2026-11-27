#!/usr/bin/env python3
"""Execute one new E13C9 correction work unit, never a baseline replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback


def digest(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--restored-e13c8', type=Path, required=True)
    ap.add_argument('--node', type=int, required=True)
    ap.add_argument('--M', type=int, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    root, restored, out = args.package.resolve(), args.restored_e13c8.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    completed_segments, entered = 0, False
    work = {'mode':'OFF','node':args.node,'M_second':args.M,'precision':60}
    def save(name, obj):
        with (out/name).open('x') as f:
            json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
    try:
        plan = json.loads((root/'WORK_PLAN.json').read_bytes())
        source_lock = json.loads((root/'SOURCE_LOCK.json').read_bytes())
        lock_sha = digest(root/'SOURCE_LOCK.json')
        for rel,pin in source_lock['files'].items():
            p=(root/rel).resolve()
            if not p.is_relative_to(root) or not p.is_file() or p.stat().st_size!=pin['bytes'] or digest(p)!=pin['sha256']:
                raise ValueError('E13C9 source identity mismatch: '+rel)
        regular = args.node in plan['nodes'] and args.M in plan['M_second']
        targeted = any(x['node']==args.node and x['M_second']==args.M
            for x in plan.get('additional_local_units', []))
        if not (regular or targeted) or plan['precision']!=60:
            raise ValueError('work unit outside E13C9 local plan')
        if plan['compute_location']!='ChatGPT_local' or plan['new_NCP_jobs']!=0:
            raise ValueError('unexpected E13C9 execution scope')
        def timeout(signum, frame):
            raise TimeoutError('declared E13C9 per-path wall budget exceeded')
        signal.signal(signal.SIGALRM,timeout)
        signal.setitimer(signal.ITIMER_REAL,plan['per_path_wall_seconds'])
        memory=plan['per_process_address_space_bytes']
        old=resource.getrlimit(resource.RLIMIT_AS)
        cap=memory if old[1]==resource.RLIM_INFINITY else min(memory,old[1])
        resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
        input_root=restored/'runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
        sys.path.insert(0,str(input_root/'code'))
        import off_path_worker as old_worker
        from common import canonical,capture,compare_metrics,encode_metrics,new_metrics
        ctx=old_worker.Context(input_root)
        if ctx.source_lock_sha256!=plan['baseline_source_lock_sha256']:
            raise ValueError('original source lock changed')
        selected=json.loads((root/'evidence/SELECTED_PATHS.json').read_bytes())
        rec=next(x for x in selected['selected_paths'] if x['node']==args.node)
        controls,old_path,index=ctx.inputs(args.node)
        checks=ctx.validate_inputs(args.node,controls,old_path)
        pin=rec['baseline_result']
        baseline_path=(restored/pin['path_relative_to_restore']).resolve()
        if not baseline_path.is_relative_to(restored) or baseline_path.stat().st_size!=pin['bytes'] or digest(baseline_path)!=pin['sha256']:
            raise ValueError('baseline result byte identity mismatch')
        baseline=json.loads(baseline_path.read_bytes())
        if baseline['work']!=rec['baseline_work'] or baseline['work']['precision']!=60:
            raise ValueError('baseline work/resolution/precision mismatch')
        if baseline['source_lock_sha256']!=ctx.source_lock_sha256 or baseline['path_input_sha256']!=index['path_input_sha256'] or index['path_input_sha256']!=rec['path_input_sha256']:
            raise ValueError('baseline source/path-input mismatch')
        if old_worker.semantic_sha(baseline)!=rec['saved_baseline_validation']['semantic_sha256']:
            raise ValueError('baseline numerical semantic mismatch')
        cache=[{'key':s['key'],'local':{k:s['local'][k] for k in ('signed','bounds')}} for s in baseline['track']['segments']]
        if hashlib.sha256(canonical(cache)).hexdigest()!=rec['cached_local_signed_and_bounds_sha256']:
            raise ValueError('cached signed/bounds subtree mismatch')
        ctx.di.configure(60)
        import signed_volterra as method
        if Path(method.__file__).resolve()!=root/'code/signed_volterra.py':
            raise ValueError('foreign new method module')
        work['N_base']=baseline['work']['N']
        save('START.json',{'work':work,'started_utc':datetime.now(timezone.utc).isoformat(),
            'source_lock_sha256':lock_sha,'baseline_source_lock_sha256':ctx.source_lock_sha256,
            'path_input_sha256':index['path_input_sha256'],'baseline_result':pin,
            'cached_signed_bounds_sha256':rec['cached_local_signed_and_bounds_sha256'],
            'host':platform.node(),'python':sys.version,'platform':platform.platform(),
            'cpu_affinity':sorted(os.sched_getaffinity(0)),'provider_attestation':'NOT_ASSERTED',
            'wall_seconds_limit':plan['per_path_wall_seconds'],'address_space_limit_bytes':cap,
            'automatic_retries':0,'full_firstvariation_quadrature_replays':0})
        def checkpoint(rows,seams):
            nonlocal completed_segments
            completed_segments=len(rows)
            save('SEGMENT_%02d_COMPLETE.json'%len(rows),{'completed_segments':len(rows),'seams':len(seams),
                'key':rows[-1]['key'],'elapsed_seconds':time.perf_counter()-started})
        entered=True
        track=ctx.pe.pack(method.run_track(controls,baseline['track'],work['N_base'],args.M,checkpoint))
        old_worker.assert_finite_boxes(track)
        count=sum(s['second_correction']['new_coefficient_evaluations'] for s in track['segments'])
        if count!=2*args.M*len(controls):
            raise ArithmeticError('new correction evaluation count mismatch')
        weight=capture(controls[0]['row']['weight'])
        old_metrics,new= new_metrics(baseline['track'],weight),new_metrics(track,weight)
        comparison=compare_metrics(old_metrics,new)
        result={'schema':'bass-he-e13c9-signed-second-volterra-path-v1',
            'status':'COMPUTED_PENDING_INDEPENDENT_LOCAL_ADMISSION','work':work,
            'source_lock_sha256':lock_sha,'baseline_source_lock_sha256':ctx.source_lock_sha256,
            'path_input_sha256':index['path_input_sha256'],'baseline_result_sha256':pin['sha256'],
            'cached_signed_bounds_sha256':rec['cached_local_signed_and_bounds_sha256'],
            'input_checks':checks,'track':track,'new_coefficient_evaluations':count,
            'new_prefix_cells':args.M*len(controls),'new_signed_rectangle_cells':args.M*len(controls),
            'baseline_firstvariation_quadrature_replays':0,'rounding_operation_counts':dict(ctx.di.COUNTS),
            'forbidden_invocations':{'NCP_launches':0,'full_first2_reruns':0,'ODE_solves':0,'native_runs':0,'gas_advances':0},
            'elapsed_seconds':time.perf_counter()-started,'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'finished_utc':datetime.now(timezone.utc).isoformat(),
            'claim_ceiling':'Selected captured OFF finite paths only; physical/continuum/production/receiver HOLD'}
        admission={'baseline_raw_weighted':encode_metrics(old_metrics),'candidate_raw_weighted':encode_metrics(new),
            'comparisons':comparison,'overlap_count':sum(r['overlap'] for r in comparison),
            'nested_count':sum(r['nested'] for r in comparison),
            'nonincreasing_count':sum(r['width_nonincreasing'] for r in comparison),
            'intersection_used':False,'old_interval_fallback_used':False,
            'mechanically_admissible':all(r['nested'] and r['width_nonincreasing'] for r in comparison),
            'independent_decision':'PENDING'}
        save('RESULT.json',result); save('COMPARISON.json',admission)
        if not all(r['overlap'] for r in comparison):
            raise ArithmeticError('raw candidate/baseline non-overlap; raw result preserved')
        for rel,pin9 in source_lock['files'].items():
            if digest(root/rel)!=pin9['sha256']:
                raise RuntimeError('source changed during actual execution: '+rel)
        scientific={k:v for k,v in result.items() if k not in ('elapsed_seconds','peak_RSS_KiB','finished_utc')}
        scientific['track']={k:v for k,v in track.items() if k!='elapsed_seconds'}
        summary={'work':work,'status':'COMPLETE_LOCAL_PENDING_INDEPENDENT_ADMISSION',
            'source_lock_sha256':lock_sha,'result_sha256':digest(out/'RESULT.json'),
            'comparison_sha256':digest(out/'COMPARISON.json'),
            'semantic_sha256':hashlib.sha256(b'bass-he-e13c9-path-v1\n'+canonical(scientific)).hexdigest(),
            'elapsed_seconds':result['elapsed_seconds'],'peak_RSS_KiB':result['peak_RSS_KiB'],
            'new_coefficient_evaluations':count,'baseline_firstvariation_quadrature_replays':0,
            'nested_count':admission['nested_count'],'nonincreasing_count':admission['nonincreasing_count']}
        save('COMPLETE.json',summary)
        print(json.dumps(summary,sort_keys=True),flush=True)
    except BaseException as exc:
        save('FIRST_FAILURE.json',{'status':'FAIL_PRESERVED_NO_AUTOMATIC_RETRY',
            'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),
            'work':work,'scientific_path_entered':entered,'completed_segments':completed_segments,
            'elapsed_seconds':time.perf_counter()-started,'automatic_retries':0})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    main()
