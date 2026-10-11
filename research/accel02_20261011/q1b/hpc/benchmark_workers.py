#!/usr/bin/env python3
"""Candidate-only, at most four new maps; never rerun the saved serial baseline.

Each eligible worker count executes ONE map from the same pinned parent, with a
new pool and startup included. Trusted baseline RESULT and LAUNCH hashes are
required external inputs. Recommendation scope is one sample/configuration on this host,
not a scaling guarantee, optimal production setting, or scientific admission.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import traceback
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from validate_parallel_map import (Q1B,REPO,canonical,digest,load_module,RHSReceipt,
                                  inspect_private_parent,resolve_historical,sha,REL,
                                  verify_closure,durable_json,runtime_inputs,save_state)
from resource_plan import plan,memory_limit_bytes

REQUIRED_CHECKS={'full_physical_and_diagnostic_result_exact','physical_state_exact',
                 'refinements_exact','native_rhs_inputs_exact','native_call_counts_exact','parent_state_unchanged'}
SAMPLE_CHECKS={'full_result_exact','physical_state_exact','refinement_records_exact',
               'native_rhs_input_arguments_exact','native_call_counts_exact','parent_state_unchanged'}


def require(value,message):
    if not value:raise ValueError(message)


def check_code_pins(baseline_pins,current_pins):
    for name,digest_value in current_pins.items():
        require(baseline_pins.get(name)==digest_value,'BASELINE_CODE_PIN_MISMATCH:'+name)


def recommend(samples):
    """Only complete exact-parity samples may compete; ties favor fewer workers."""
    eligible=[s for s in samples if s.get('status')=='PASS_EXACT_PARITY' and
              set(s.get('exact_checks',{}))==SAMPLE_CHECKS and all(v is True for v in s['exact_checks'].values()) and
              isinstance(s.get('phase_wall_s'),(int,float)) and
              math.isfinite(s['phase_wall_s']) and s['phase_wall_s']>0]
    if not eligible:return None
    best=min(eligible,key=lambda s:(s['phase_wall_s'],s['workers']))
    return dict(workers=best['workers'],sample_wall_s=best['phase_wall_s'],
        objective='MINIMUM_ONE_SAMPLE_MAP_LATENCY_WITH_POOL_STARTUP_INCLUDED',
        samples_per_configuration=1,warmup_maps=0,
        guarantee=False,whole_history_admission=False,
        limitation='No replicate noise estimate or 64-core scaling guarantee; persistent-pool production optimum may differ.')


def read_state(path,diagnostics=None):
    from native_step_v3 import COUNTER_NAMES
    with np.load(path,allow_pickle=False) as values:
        state={key:values[key].copy() for key in ('gas','N','U_eV','R','support')}
        state.update({key:float(values[key]) for key in ('t_s','nH_ref','nHe_ref')})
        state['counters']={key:float(value) for key,value in zip(COUNTER_NAMES,values['counters'],strict=True)}
    if diagnostics is not None:state['diagnostics']=diagnostics
    return state


def inspect_baseline(directory,expected_result_sha256,expected_launch_sha256):
    from cell_history_fields import physical_state_sha256
    directory=Path(directory).resolve(strict=True)
    require(re.fullmatch('[0-9a-f]{64}',expected_result_sha256) is not None,'BASELINE_EXTERNAL_SHA256_FORMAT')
    require(re.fullmatch('[0-9a-f]{64}',expected_launch_sha256) is not None,'BASELINE_EXTERNAL_LAUNCH_SHA256_FORMAT')
    require(sha(directory/'RESULT.json')==expected_result_sha256,'BASELINE_EXTERNAL_RESULT_HASH_MISMATCH')
    # RESULT authenticates its saved serial receipt, but contains no LAUNCH
    # digest. Authenticate LAUNCH independently BEFORE trusting parent/code/
    # source/binary pins; deriving this digest from the untrusted directory
    # would not establish provenance.
    require(sha(directory/'LAUNCH.json')==expected_launch_sha256,'BASELINE_EXTERNAL_LAUNCH_HASH_MISMATCH')
    result=json.loads((directory/'RESULT.json').read_text())
    require(result.get('status')=='PASS_NEW_IMPLEMENTATION_PARITY','BASELINE_NOT_ACTUAL_PARITY_PASS')
    require(set(result.get('checks',{}))==REQUIRED_CHECKS and all(v is True for v in result['checks'].values()),
            'BASELINE_REQUIRED_CHECKS')
    require(result.get('physical_maps_completed')==result.get('physical_maps_started')==2 and
            result.get('production_attempt_debit')==0 and result.get('production_cursor_changed') is False,
            'BASELINE_VALIDATION_SCOPE')
    launch=json.loads((directory/'LAUNCH.json').read_text())
    current_pins={name:sha(HERE/name) for name in ('ordered_cell_pool.py','native_step_hpc.py','validate_parallel_map.py')}
    require(set(launch.get('code_pins',{}))==set(current_pins),'BASELINE_CODE_PIN_NAMES')
    check_code_pins(launch['code_pins'],current_pins)
    serial=json.loads((directory/'SERIAL/RESULT.json').read_text())
    require(serial==result['receipts']['SERIAL'],'BASELINE_SERIAL_RECEIPT_BINDING')
    diagnostics=json.loads((directory/'SERIAL/DIAGNOSTICS.json').read_text())
    refinements=json.loads((directory/'SERIAL/REFINEMENTS.json').read_text())
    output=read_state(directory/'SERIAL/OUTPUT.npz',diagnostics)
    require(digest(output)==serial['full_result_sha256'] and
            physical_state_sha256(output)==serial['physical_state_sha256'],'BASELINE_SERIAL_OUTPUT_HASH')
    require(digest(refinements)==serial['refinements_sha256'],'BASELINE_SERIAL_REFINEMENT_HASH')
    parent_input=read_state(directory/'PARENT_INPUT.npz')
    require(physical_state_sha256(parent_input)==launch['parent_state_sha256'],'BASELINE_PARENT_INPUT_HASH')
    require(output['t_s']==launch['t1_s'] and parent_input['t_s']==launch['t0_s'],'BASELINE_MAP_TIME_BINDING')
    names=('RESULT.json','LAUNCH.json','PARENT_INPUT.npz','SERIAL/RESULT.json',
           'SERIAL/OUTPUT.npz','SERIAL/DIAGNOSTICS.json','SERIAL/REFINEMENTS.json')
    files={name:sha(directory/name) for name in names}
    return dict(directory=directory,result=result,launch=launch,serial=serial,
                output=output,refinements=refinements,parent_input=parent_input,file_sha256=files)


def verify_baseline_files(baseline):
    for relative,expected in baseline['file_sha256'].items():
        require(sha(baseline['directory']/relative)==expected,'BASELINE_DRIFT_DURING_BENCHMARK:'+relative)


def resource_fit(workers):
    cpus=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count()
    available=memory_limit_bytes()
    try:
        value=plan(affinity_cpus=cpus,available_bytes=available,requested_workers=workers,
                   reserve_cores=2,coordinator_gib=8.,worker_gib=1.,reserve_gib=8.)
    except ValueError as exc:
        return dict(eligible=False,requested_workers=workers,affinity_cpus=cpus,
                    available_memory_bytes=available,reason=str(exc))
    return dict(eligible=value['workers']==workers,plan=value,
                reason=None if value['workers']==workers else 'REQUESTED_CONFIGURATION_EXCEEDS_RESOURCE_BUDGET_NO_SILENT_DOWNGRADE')


def run(args):
    from entry_checkpoint import unpack_entry_state
    from adaptive_controller import next_boundary
    from cell_history_fields import physical_state_sha256
    from native_step_v3 import NativeCell
    from ordered_cell_pool import Pool
    from native_step_hpc import positive_native_step
    out=args.output.resolve()
    require(not out.is_relative_to(HERE),'BENCHMARK_OUTPUT_MUST_BE_PRIVATE')
    out.mkdir(parents=True,exist_ok=False)
    result=dict(schema='rei.hpc.worker_count_benchmark.v1',status='SETUP_STARTED',
        diagnostic_physical_map_budget=len(args.workers),physical_maps_started=0,physical_maps_completed=0,
        serial_baseline_replays=0,warmup_maps=0,production_attempt_debit=0,
        production_cursor_changed=False,scientific_admission=False,samples=[])
    pool=native=proxy=None;start=time.monotonic();active_workers=None
    try:
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            require(os.environ.get(key)=='1','REQUIRE_THREAD_COUNT_ONE:'+key)
        baseline=inspect_baseline(args.baseline,args.baseline_result_sha256,args.baseline_launch_sha256)
        parent=inspect_private_parent(args.parent_repo,args.parent_root)
        meta=parent['loaded']['metadata'];arrays=parent['loaded']['arrays']
        launch=baseline['launch']
        require(parent['checkpoint']==launch['parent_checkpoint'] and parent['cursor']==launch['parent_cursor'],
                'BASELINE_PARENT_IS_NOT_CURRENT_IMMUTABLE_COMMITTED_PARENT')
        provider,source,initial=runtime_inputs(dict(parent_repo=str(parent['repo'])))
        shape=initial['N'].shape
        state=unpack_entry_state(arrays['prefix_state'][-1],meta['cell_count'])
        for key in ('N','U_eV'):state[key]=np.asarray(state[key]).reshape(shape)
        state.update(t_s=float(arrays['prefix_clock'][-1]),nH_ref=meta['nH_ref'],nHe_ref=meta['nHe_ref'],
            R=np.asarray(meta['prefix_R'][-1]).reshape(shape),support=np.asarray(meta['prefix_support'][-1]).reshape(*shape,2))
        state['diagnostics']=copy.deepcopy(meta['production_kernel_history'][str(len(arrays['prefix_clock'])-1)])
        parent_hash=physical_state_sha256(state)
        require(parent_hash==launch['parent_state_sha256'],'BASELINE_PARENT_STATE_IDENTITY')
        t1,kind=next_boundary(state['t_s'],parent['cursor']['next_step_s'],parent['bundle']['target_time_s'],parent['schedule']['hard_events_s'])
        require(t1==launch['t1_s'] and state['t_s']==launch['t0_s'] and kind==launch['boundary_kind'],'BASELINE_INTERVAL_BINDING')
        source_path=resolve_historical(parent['bundle']['source_module_path'],REPO)
        absorption_path=resolve_historical(parent['bundle']['absorption_module_path'],REPO)
        binary=parent['repo']/REL/'native/target/release/rei_q1b_cell_native_v1'
        sigma_binary=parent['repo']/REL.parent/'n1/native/target/release/rei_n1_native'
        for key,path in (('source_sha256',source_path),('absorption_sha256',absorption_path),
                         ('gas_binary_sha256',binary),('sigma_binary_sha256',sigma_binary)):
            require(sha(path)==launch[key],'BASELINE_PHYSICS_OR_BINARY_PIN:'+key)
        require(sha(source_path)==parent['bundle']['identity']['source'] and
                sha(absorption_path)==parent['bundle']['absorption_sha256'],'PARENT_SOURCE_ABSORPTION_PIN')
        source_api=load_module('benchmark_pinned_source',source_path)
        durable_json(out/'LAUNCH.json',dict(schema='rei.hpc.candidate_scaling_launch.v1',
            parent_checkpoint=parent['checkpoint'],parent_cursor=parent['cursor'],parent_state_sha256=parent_hash,
            baseline_result_external_sha256=args.baseline_result_sha256,
            baseline_launch_external_sha256=args.baseline_launch_sha256,baseline_file_sha256=baseline['file_sha256'],
            candidate_worker_counts=args.workers,maximum_new_physical_maps=len(args.workers),
            maps_per_configuration=1,warmup_maps=0,serial_replays=0,
            coordinator_gib=8.,memory_reserve_gib=8.,worker_memory_estimate_gib=1.,reserve_cores=2,
            source_and_numerics_unchanged=True,production_attempt_debit=0,
            benchmark_code_sha256=sha(__file__),code_pins=launch['code_pins'],
            serial_wall_time_comparability='NOT_ASSUMED_SAVED_BASELINE_MAY_BE_FROM_ANOTHER_HOST',
            scientific_admission=False))
        for active_workers in args.workers:
            check_code_pins(launch['code_pins'],{name:sha(HERE/name) for name in launch['code_pins']})
            verify_baseline_files(baseline)
            fit=resource_fit(active_workers)
            directory=out/f'WORKERS_{active_workers:02d}';directory.mkdir(exist_ok=False)
            durable_json(directory/'RESOURCE_PLAN.json',fit)
            if not fit['eligible']:
                sample=dict(workers=active_workers,status='SKIPPED_RESOURCE_BUDGET',resource_check=fit,
                            physical_maps=0)
                durable_json(directory/'RESULT.json',sample);result['samples'].append(sample)
                continue
            durable_json(directory/'BEGIN.json',dict(parent_state_sha256=parent_hash,t0_s=state['t_s'],t1_s=t1,
                workers=active_workers,map_budget=1,serial_replays=0))
            phase_start=time.monotonic()
            native=NativeCell(binary=binary);proxy=RHSReceipt(native)
            pool=Pool(workers=active_workers,timeout_s=args.timeout_s,
                      opacity_binary=sigma_binary,absorption_path=absorption_path)
            pool.start()
            require(pool.metrics['opacity_binding']=='PINNED_NATIVE_OPACITY','BENCHMARK_PINNED_NATIVE_REQUIRED')
            result['physical_maps_started']+=1
            value=positive_native_step(copy.deepcopy(state),t1,source,pool,proxy,source_api=source_api)
            phase_elapsed=time.monotonic()-phase_start
            result['physical_maps_completed']+=1
            hpc=value.pop('hpc_metrics');refinements=pool.pop_refinement_records()
            counters=dict(native_rhs_calls=native.calls,sigma_calls=pool.native_calls,
                          sigma_energy_evaluations=pool.energy_evaluations)
            reference=baseline['serial']
            checks=dict(full_result_exact=digest(value)==reference['full_result_sha256'],
                physical_state_exact=physical_state_sha256(value)==reference['physical_state_sha256'],
                refinement_records_exact=digest(refinements)==reference['refinements_sha256'],
                native_rhs_input_arguments_exact=proxy.input_hashes==reference['native_rhs_input_sha256'],
                native_call_counts_exact=counters==reference['counters'],
                parent_state_unchanged=physical_state_sha256(state)==parent_hash)
            save_state(directory/'OUTPUT.npz',value)
            durable_json(directory/'DIAGNOSTICS.json',canonical(value['diagnostics']))
            durable_json(directory/'REFINEMENTS.json',canonical(refinements))
            sample=dict(workers=active_workers,status='PASS_EXACT_PARITY' if all(checks.values()) else 'FAILED_PARITY',
                exact_checks=checks,phase_wall_s=phase_elapsed,map_metrics=hpc,pool_metrics=pool.metrics,
                counters=counters,native_rhs_input_sha256=proxy.input_hashes,
                full_result_sha256=digest(value),physical_state_sha256=physical_state_sha256(value),
                refinements_sha256=digest(refinements))
            # Same-result equality already inherits the saved endpoint gates;
            # do not rerun ledger/domain validations on identical output bytes.
            durable_json(directory/'RESULT.json',canonical(sample));result['samples'].append(sample)
            pool.close();native.close();native=None
            if not all(checks.values()):raise ArithmeticError('CANDIDATE_PARITY_FAILED_NO_RETRY')
            print(json.dumps(dict(event='WORKER_SAMPLE_DURABLE',workers=active_workers,
                                 phase_wall_s=phase_elapsed,status=sample['status'])),flush=True)
        verify_baseline_files(baseline)
        verify_closure(meta['restart_binding']['dependency_closure'],parent['repo'])
        result['recommendation']=recommend(result['samples'])
        result['status']='COMPLETE_CANDIDATE_ONLY_SCALER' if result['recommendation'] else 'RESOURCE_BLOCKED_NO_NATIVE'
    except BaseException as exc:
        result.update(status='FAILED_CLOSED_NO_RETRY',active_workers=active_workers,
            failure=dict(type=type(exc).__name__,message=str(exc),notes=getattr(exc,'__notes__',[]),traceback=traceback.format_exc()))
        if proxy is not None:result['active_native_rhs_calls_started']=proxy.calls
        if pool is not None:
            result['active_pool_metrics']=pool.metrics;result['pool_failure_receipt']=pool.failure_receipt
        # Earlier passing results remain evidence, but do not recommend a
        # production configuration after a partially failed benchmark campaign.
        result['recommendation']=None
    finally:
        if pool is not None:pool.close();result['last_pool_cleanup']=pool.cleanup_receipt
        if native is not None:
            try:native.close()
            except BaseException as exc:result['native_close_failure']=str(exc)
        result['elapsed_s']=time.monotonic()-start
        durable_json(out/'RESULT.json',canonical(result))
    print(json.dumps({k:v for k,v in result.items() if k not in ('samples','last_pool_cleanup','active_pool_metrics')},sort_keys=True),flush=True)
    return 0 if result['status']=='COMPLETE_CANDIDATE_ONLY_SCALER' else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent-repo',type=Path,required=True)
    parser.add_argument('--parent-root',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--baseline-result-sha256',required=True,
                        help='Trusted external SHA-256 of the saved validation RESULT.json; never infer it from untrusted baseline content')
    parser.add_argument('--baseline-launch-sha256',required=True,
                        help='Trusted external SHA-256 of the saved validation LAUNCH.json, authenticating its parent/code/source/binary pins')
    parser.add_argument('--workers',type=int,nargs='+',default=[8,16,32,48])
    parser.add_argument('--timeout-s',type=float,default=120.)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if (not 1<=len(args.workers)<=4 or args.workers!=sorted(set(args.workers)) or
        any(not 1<=w<=48 for w in args.workers) or not math.isfinite(args.timeout_s) or args.timeout_s<=0):
        parser.error('one to four unique increasing worker counts1..48 and positive finite timeout required')
    return run(args)


if __name__=='__main__':raise SystemExit(main())
