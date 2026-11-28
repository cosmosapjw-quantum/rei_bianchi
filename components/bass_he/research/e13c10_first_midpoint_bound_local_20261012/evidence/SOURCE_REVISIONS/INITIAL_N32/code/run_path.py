#!/usr/bin/env python3
"""Run one bounded new E13C10 local path with immutable input/source gates."""
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

sys.dont_write_bytecode = True


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def checked_path(base, relative, pin):
    p = (base / relative).resolve()
    if not p.is_relative_to(base) or not p.is_file():
        raise ValueError('missing or escaping pinned path: ' + relative)
    if ('bytes' in pin and p.stat().st_size != pin['bytes']) or digest(p) != pin['sha256']:
        raise ValueError('pinned byte identity mismatch: ' + relative)
    return p


def semantic(result, canonical):
    value = {k:v for k,v in result.items() if k not in ('elapsed_seconds','cpu_seconds','peak_RSS_KiB','finished_utc')}
    value['track'] = {k:v for k,v in value['track'].items() if k != 'elapsed_seconds'}
    value['track']['segments'] = []
    for segment in result['track']['segments']:
        item = dict(segment)
        item['local'] = {k:v for k,v in item['local'].items() if k != 'elapsed_seconds'}
        value['track']['segments'].append(item)
    return hashlib.sha256(b'bass-he-e13c10-path-v1\n' + canonical(value)).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--restored-e13c9', type=Path, required=True)
    ap.add_argument('--node', type=int, required=True)
    ap.add_argument('--N', type=int, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    root, restored9, out = args.package.resolve(), args.restored_e13c9.resolve(), args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started, cpu_started = time.perf_counter(), time.process_time()
    entered, completed_segments = False, 0
    work = {'mode':'OFF','node':args.node,'N_first':args.N,'precision':60}

    def save(name, obj):
        with (out/name).open('x') as f:
            json.dump(obj, f, indent=2, sort_keys=True, allow_nan=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())

    try:
        lock = json.loads((root/'SOURCE_LOCK.json').read_bytes())
        lock_sha = digest(root/'SOURCE_LOCK.json')
        for rel, pin in lock['files'].items():
            checked_path(root, rel, pin)
        prior_root = restored9/'package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1'
        for rel, pin in lock['E13C9_dependencies'].items():
            checked_path(prior_root, rel, pin)
        plan = json.loads((root/'WORK_PLAN.json').read_bytes())
        unit = next((u for u in plan['units'] if u['node']==args.node and u['N_first']==args.N), None)
        if unit is None or plan['precision'] != 60 or plan['compute_location'] != 'ChatGPT_local' or plan['new_NCP_jobs'] != 0:
            raise ValueError('work unit outside the bounded E13C10 local plan')
        work['M_second'] = unit['M_second']

        def timeout(signum, frame):
            raise TimeoutError('declared E13C10 local path wall limit exceeded')
        signal.signal(signal.SIGALRM, timeout)
        signal.setitimer(signal.ITIMER_REAL, plan['per_path_wall_seconds'])
        old_limit = resource.getrlimit(resource.RLIMIT_AS)
        cap = plan['per_process_address_space_bytes']
        if old_limit[1] != resource.RLIM_INFINITY:
            cap = min(cap, old_limit[1])
        resource.setrlimit(resource.RLIMIT_AS, (cap,cap))
        restored8 = restored9/'runtime/E13C8'
        input_root = restored8/'runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
        sys.path.insert(0, str(input_root/'code'))
        import off_path_worker as old_worker
        from common import canonical, capture, compare_metrics, encode_metrics, new_metrics
        ctx = old_worker.Context(input_root)
        if ctx.source_lock_sha256 != plan['baseline_source_lock_sha256']:
            raise ValueError('original source lock changed')
        selected = json.loads((root/'evidence/SELECTED_INPUTS.json').read_bytes())
        rec = next(x for x in selected['selected_paths'] if x['node']==args.node)
        controls, old_path, index = ctx.inputs(args.node)
        input_checks = ctx.validate_inputs(args.node, controls, old_path)
        pin7 = rec['baseline_result']
        baseline7_path = checked_path(restored8, pin7['path_relative_to_restore'], pin7)
        baseline7 = json.loads(baseline7_path.read_bytes())
        if baseline7['work'] != rec['baseline_work'] or baseline7['work']['precision'] != 60:
            raise ValueError('original baseline work or precision mismatch')
        if baseline7['source_lock_sha256'] != ctx.source_lock_sha256 or baseline7['path_input_sha256'] != index['path_input_sha256'] or index['path_input_sha256'] != rec['path_input_sha256']:
            raise ValueError('original source or path-input mismatch')
        if old_worker.semantic_sha(baseline7) != rec['saved_baseline_validation']['semantic_sha256']:
            raise ValueError('original baseline semantic mismatch')
        cache = [{'key':s['key'],'local':{k:s['local'][k] for k in ('signed','bounds')}} for s in baseline7['track']['segments']]
        if hashlib.sha256(canonical(cache)).hexdigest() != rec['cached_local_signed_and_bounds_sha256']:
            raise ValueError('original fine-grid cache subtree mismatch')
        choice = rec['admitted_e13c9']
        prior_path = checked_path(prior_root, choice['result']['relative_path'], choice['result'])
        prior = json.loads(prior_path.read_bytes())
        if prior['path_input_sha256'] != index['path_input_sha256'] or prior['work']['M_second'] != work['M_second']:
            raise ValueError('admitted E13C9 source-input or M mismatch')
        work['N_bounds'] = baseline7['work']['N']
        ctx.di.configure(60)
        sys.path.insert(0, str(prior_root/'code'))
        import signed_volterra as sv
        if Path(sv.__file__).resolve() != prior_root/'code/signed_volterra.py':
            raise ValueError('foreign prior method module')
        sys.path.insert(0, str(root/'code'))
        import first_path as method
        import first_midpoint
        if Path(method.__file__).resolve() != root/'code/first_path.py' or Path(first_midpoint.__file__).resolve() != root/'code/first_midpoint.py':
            raise ValueError('foreign new method module')
        save('START.json', {'work':work,'started_utc':datetime.now(timezone.utc).isoformat(),
            'source_lock_sha256':lock_sha,'original_source_lock_sha256':ctx.source_lock_sha256,
            'path_input_sha256':index['path_input_sha256'],'original_baseline_result':pin7,
            'admitted_E13C9_result':choice['result'],'host':platform.node(),
            'python':sys.version,'platform':platform.platform(),'cpu_affinity':sorted(os.sched_getaffinity(0)),
            'provider_attestation':'NOT_ASSERTED','wall_seconds_limit':plan['per_path_wall_seconds'],
            'address_space_limit_bytes':cap,'automatic_retries':0,'prior_workload_replays':0})

        def checkpoint(rows, seams):
            nonlocal completed_segments
            completed_segments = len(rows)
            save('SEGMENT_%02d_COMPLETE.json'%len(rows), {'completed_segments':len(rows),
                'seams':len(seams),'key':rows[-1]['key'],'elapsed_seconds':time.perf_counter()-started})

        entered = True
        track = ctx.pe.pack(method.run_track(controls, baseline7['track'], work['N_bounds'], args.N, work['M_second'], checkpoint))
        old_worker.assert_finite_boxes(track)
        first_count = sum(s['local']['new_coefficient_evaluations'] for s in track['segments'])
        second_count = sum(s['second_correction']['new_coefficient_evaluations'] for s in track['segments'])
        if first_count != 2*args.N*len(controls) or second_count != 2*work['M_second']*len(controls):
            raise ArithmeticError('new coefficient evaluation count mismatch')
        weight = capture(controls[0]['row']['weight'])
        old_metrics, new = new_metrics(prior['track'],weight), new_metrics(track,weight)
        comparison = compare_metrics(old_metrics,new)
        result = {'schema':'bass-he-e13c10-first-midpoint-path-v1',
            'status':'COMPUTED_PENDING_INDEPENDENT_LOCAL_ADMISSION','work':work,
            'source_lock_sha256':lock_sha,'original_source_lock_sha256':ctx.source_lock_sha256,
            'path_input_sha256':index['path_input_sha256'],'original_baseline_result_sha256':pin7['sha256'],
            'admitted_E13C9_result_sha256':choice['result']['sha256'],
            'cached_original_signed_bounds_sha256':rec['cached_local_signed_and_bounds_sha256'],
            'input_checks':input_checks,'track':track,
            'new_first_integral_coefficient_evaluations':first_count,
            'new_second_correction_coefficient_evaluations':second_count,
            'new_coefficient_evaluations':first_count+second_count,
            'old_firstvariation_quadrature_replays':0,'old_second_correction_replays':0,
            'second_corrections_recomputed_with_new_carry':len(controls),
            'rounding_operation_counts':dict(ctx.di.COUNTS),
            'forbidden_invocations':{'NCP_launches':0,'full_population_runs':0,'ODE_solves':0,'native_runs':0,'gas_advances':0},
            'elapsed_seconds':time.perf_counter()-started,'cpu_seconds':time.process_time()-cpu_started,
            'peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'finished_utc':datetime.now(timezone.utc).isoformat(),
            'claim_ceiling':'Selected captured OFF finite paths only; physical/continuum/production/receiver HOLD'}
        admission = {'baseline':'ADMITTED_E13C9_SELECTED_PATH',
            'baseline_raw_weighted':encode_metrics(old_metrics),'candidate_raw_weighted':encode_metrics(new),
            'comparisons':comparison,'overlap_count':sum(r['overlap'] for r in comparison),
            'nested_count':sum(r['nested'] for r in comparison),
            'nonincreasing_count':sum(r['width_nonincreasing'] for r in comparison),
            'intersection_used':False,'old_interval_fallback_used':False,
            'mechanically_admissible':all(r['nested'] and r['width_nonincreasing'] for r in comparison),
            'independent_decision':'PENDING'}
        save('RESULT.json',result); save('COMPARISON.json',admission)
        if not all(r['overlap'] for r in comparison):
            raise ArithmeticError('new/previous raw intervals do not overlap; result preserved')
        for rel, pin in lock['files'].items():
            checked_path(root, rel, pin)
        summary = {'work':work,'status':'COMPLETE_LOCAL_PENDING_INDEPENDENT_ADMISSION',
            'source_lock_sha256':lock_sha,'result_sha256':digest(out/'RESULT.json'),
            'comparison_sha256':digest(out/'COMPARISON.json'),'semantic_sha256':semantic(result,canonical),
            'elapsed_seconds':result['elapsed_seconds'],'cpu_seconds':result['cpu_seconds'],
            'peak_RSS_KiB':result['peak_RSS_KiB'],
            'new_first_integral_coefficient_evaluations':first_count,
            'new_second_correction_coefficient_evaluations':second_count,
            'new_coefficient_evaluations':first_count+second_count,
            'nested_count':admission['nested_count'],'nonincreasing_count':admission['nonincreasing_count'],
            'mechanically_admissible':admission['mechanically_admissible']}
        save('COMPLETE.json',summary)
        print(json.dumps(summary,sort_keys=True),flush=True)
    except BaseException as exc:
        save('FIRST_FAILURE.json', {'status':'FAIL_PRESERVED_NO_AUTOMATIC_RETRY',
            'error_type':type(exc).__name__,'error':str(exc),'traceback':traceback.format_exc(),
            'work':work,'scientific_path_entered':entered,'completed_segments':completed_segments,
            'elapsed_seconds':time.perf_counter()-started,'automatic_retries':0})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)


if __name__ == '__main__':
    main()
