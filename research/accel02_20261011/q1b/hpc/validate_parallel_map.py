#!/usr/bin/env python3
"""Two NEW implementation-validation maps; no production cursor or acceptance.

Compare frozen serial v4 and the cell-parallel candidate on the same next
interval from a restored committed parent. Write all receipts only to a new
private output directory. A failed serial map stops before candidate execution;
no map is retried and no trial/checkpoint is committed to production.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import traceback
import numpy as np

HERE=Path(__file__).resolve().parent
Q1B=HERE.parent
REPO=Q1B.parents[2]
for path in (Q1B/'c10',Q1B,Q1B.parent/'n1',Q1B/'c11/precision',
             Q1B/'c11/controller',Q1B/'c11/restart',Q1B/'c11/endpoint',
             Q1B/'c11/integration',Q1B/'c11/integration/production',HERE):
    sys.path.insert(0,str(path))
from prepare_hpc_run import inspect_private_parent,resolve_historical,sha,REL,verify_closure
from production_journal import durable_json
from run_hpc_chunk import runtime_inputs,save_state


def canonical(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {str(k):canonical(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [canonical(v) for v in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(canonical(value),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


class RHSReceipt:
    def __init__(self,native):self.native=native;self.input_hashes=[];self.calls=0;self.elapsed_s=0.
    def rhs(self,t,g,gas,cells):
        # Exactly the array order that NativeCell marshals into CELL_RHS_V1.
        payload=np.r_[t,g['a_rel'],g['b'],g['H'],g['s'],g['nH'],g['nHe'],gas,g['Tcmb_K'],len(cells),np.asarray(cells).ravel()]
        self.input_hashes.append(hashlib.sha256(payload.astype('<f8',copy=False).tobytes()).hexdigest())
        self.calls+=1
        started=time.monotonic()
        try:return self.native.rhs(t,g,gas,cells)
        finally:self.elapsed_s+=time.monotonic()-started


def run(args):
    from entry_checkpoint import unpack_entry_state
    from adaptive_controller import next_boundary
    from run_adaptive_native_v2 import strict_validate,ledger
    from cell_history_fields import physical_state_sha256,geometry_diagnostics
    from native_step_v3 import NativeCell
    from opacity_native import NativeOpacity
    from native_step_v4_diagnostics import positive_native_step as serial_map
    from native_step_hpc import positive_native_step as parallel_map
    from ordered_cell_pool import Pool
    out=args.output.resolve()
    if out.is_relative_to(HERE):raise ValueError('VALIDATION_OUTPUT_MUST_NOT_BE_PUBLIC_SOURCE_DIRECTORY')
    out.mkdir(parents=True,exist_ok=False)
    result=dict(schema='rei.hpc.two_map_implementation_validation.v1',status='SETUP_STARTED',
        diagnostic_physical_map_budget=2,physical_maps_started=0,physical_maps_completed=0,
        production_attempt_debit=0,production_cursor_changed=False,old_scientific_checks_replayed=0,
        scientific_admission=False)
    start=time.monotonic();pool=None;active_native=None;active_opacity=None;active_proxy=None
    phase='SETUP'
    try:
        for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            if os.environ.get(key)!='1':raise ValueError('REQUIRE_THREAD_COUNT_ONE:'+key)
        parent=inspect_private_parent(args.parent_repo,args.parent_root)
        meta=parent['loaded']['metadata'];arrays=parent['loaded']['arrays']
        provider,source,initial=runtime_inputs(dict(parent_repo=str(parent['repo'])))
        shape=initial['N'].shape
        state=unpack_entry_state(arrays['prefix_state'][-1],meta['cell_count'])
        for key in ('N','U_eV'):state[key]=np.asarray(state[key]).reshape(shape)
        state.update(t_s=float(arrays['prefix_clock'][-1]),nH_ref=meta['nH_ref'],nHe_ref=meta['nHe_ref'],
            R=np.asarray(meta['prefix_R'][-1]).reshape(shape),
            support=np.asarray(meta['prefix_support'][-1]).reshape(*shape,2))
        last=str(len(arrays['prefix_clock'])-1)
        state['diagnostics']=copy.deepcopy(meta['production_kernel_history'][last])
        parent_hash=physical_state_sha256(state)
        if state['diagnostics']['output24_kernel']['state_sha256']!=parent_hash:
            raise ValueError('PARENT_STATE_KERNEL_OWNER_MISMATCH')
        source_path=resolve_historical(parent['bundle']['source_module_path'],REPO)
        absorption_path=resolve_historical(parent['bundle']['absorption_module_path'],REPO)
        if sha(source_path)!=parent['bundle']['identity']['source'] or sha(absorption_path)!=parent['bundle']['absorption_sha256']:
            raise ValueError('FROZEN_SOURCE_ABSORPTION_IDENTITY')
        source_api=load_module('validation_pinned_source',source_path)
        absorption_api=load_module('validation_pinned_absorption',absorption_path)
        binary=parent['repo']/REL/'native/target/release/rei_q1b_cell_native_v1'
        sigma_binary=parent['repo']/REL.parent/'n1/native/target/release/rei_n1_native'
        cursor=parent['cursor'];target=parent['bundle']['target_time_s']
        t1,kind=next_boundary(state['t_s'],cursor['next_step_s'],target,parent['schedule']['hard_events_s'])
        launch=dict(schema='rei.hpc.two_map_validation_launch.v1',parent_checkpoint=parent['checkpoint'],
            parent_cursor=cursor,parent_state_sha256=parent_hash,t0_s=state['t_s'],t1_s=t1,boundary_kind=kind,
            source_sha256=sha(source_path),absorption_sha256=sha(absorption_path),
            gas_binary_sha256=sha(binary),sigma_binary_sha256=sha(sigma_binary),
            worker_count=args.workers,worker_timeout_s=args.timeout_s,
            map_budget=2,production_attempt_debit=0,h0_regenerations=0,
            exact_comparison=['physical_fields','all_original_diagnostics','refinement_records','native_rhs_input_hashes','native_rhs_and_sigma_counts'],
            code_pins={name:sha(HERE/name) for name in ('ordered_cell_pool.py','native_step_hpc.py','validate_parallel_map.py')},
            scientific_admission=False)
        durable_json(out/'LAUNCH.json',launch);save_state(out/'PARENT_INPUT.npz',state)
        def validate_new(value):
            strict_validate(value,initial,provider)
            geometry=geometry_diagnostics(source,value['t_s'])
            if geometry['max_error']>1e-11:raise ArithmeticError('ORIGINAL_GEOMETRY_GATE')
            return dict(ledger=ledger(value,initial),geometry=geometry)
        outputs={};refinements={};receipts={}
        for phase in ('SERIAL','PARALLEL'):
            directory=out/phase;directory.mkdir(exist_ok=False)
            durable_json(directory/'BEGIN.json',dict(t0_s=state['t_s'],t1_s=t1,parent_state_sha256=parent_hash,
                physical_map_ordinal=result['physical_maps_started']+1))
            phase_start=time.monotonic()
            active_native=NativeCell(binary=binary);active_proxy=RHSReceipt(active_native)
            if phase=='SERIAL':
                active_opacity=NativeOpacity(sigma_binary)
                if absorption_api.pop_refinement_records():raise ValueError('STALE_SERIAL_REFINEMENTS')
                result['physical_maps_started']+=1
                value=serial_map(copy.deepcopy(state),t1,source,active_opacity,active_proxy,
                                 source_api=source_api,absorption_api=absorption_api)
                refinements[phase]=absorption_api.pop_refinement_records()
                counters=dict(native_rhs_calls=active_native.calls,sigma_calls=active_opacity.native_calls,
                              sigma_energy_evaluations=active_opacity.energy_evaluations)
                timing=dict(phase_wall_s=time.monotonic()-phase_start,native_rhs_s=active_proxy.elapsed_s)
            else:
                pool=Pool(workers=args.workers,timeout_s=args.timeout_s,
                          opacity_binary=sigma_binary,absorption_path=absorption_path)
                pool.start()
                result['physical_maps_started']+=1
                value=parallel_map(copy.deepcopy(state),t1,source,pool,active_proxy,source_api=source_api)
                hpc=value.pop('hpc_metrics')
                refinements[phase]=pool.pop_refinement_records()
                counters=dict(native_rhs_calls=active_native.calls,sigma_calls=pool.native_calls,
                              sigma_energy_evaluations=pool.energy_evaluations)
                timing=dict(phase_wall_s=time.monotonic()-phase_start,map_metrics=hpc,pool_metrics=pool.metrics)
                if pool.metrics['opacity_binding']!='PINNED_NATIVE_OPACITY':raise ValueError('NON_NATIVE_VALIDATION_POOL')
            result['physical_maps_completed']+=1
            gates=validate_new(value)
            save_state(directory/'OUTPUT.npz',value)
            durable_json(directory/'DIAGNOSTICS.json',canonical(value['diagnostics']))
            durable_json(directory/'REFINEMENTS.json',canonical(refinements[phase]))
            receipt=dict(counters=counters,timing=timing,new_endpoint_gates=gates,
                physical_state_sha256=physical_state_sha256(value),full_result_sha256=digest(value),
                native_rhs_input_sha256=active_proxy.input_hashes,refinements_sha256=digest(refinements[phase]))
            durable_json(directory/'RESULT.json',canonical(receipt));receipts[phase]=receipt;outputs[phase]=value
            active_native.close();active_native=None
            if active_opacity is not None:active_opacity.close();active_opacity=None
            if pool is not None:pool.close()
            print(json.dumps(dict(event='NEW_IMPLEMENTATION_MAP_DURABLE',phase=phase,counters=counters,
                                 elapsed_s=timing['phase_wall_s'])),flush=True)
        checks=dict(full_physical_and_diagnostic_result_exact=digest(outputs['SERIAL'])==digest(outputs['PARALLEL']),
            physical_state_exact=receipts['SERIAL']['physical_state_sha256']==receipts['PARALLEL']['physical_state_sha256'],
            refinements_exact=digest(refinements['SERIAL'])==digest(refinements['PARALLEL']),
            native_rhs_inputs_exact=receipts['SERIAL']['native_rhs_input_sha256']==receipts['PARALLEL']['native_rhs_input_sha256'],
            native_call_counts_exact=receipts['SERIAL']['counters']==receipts['PARALLEL']['counters'],
            parent_state_unchanged=physical_state_sha256(state)==parent_hash)
        verify_closure(meta['restart_binding']['dependency_closure'],parent['repo'])
        if not all(checks.values()):raise ArithmeticError('HPC_EXACT_IMPLEMENTATION_PARITY_FAILED:'+str(checks))
        result.update(status='PASS_NEW_IMPLEMENTATION_PARITY',checks=checks,receipts=receipts,
            performance_scope='ONE_NEW_INTERVAL_TWO_MAPS_STARTUP_INCLUDED_NO_64_CORE_SCALING_OR_WHOLE_HISTORY_CLAIM',
            observed_serial_over_parallel_wall_ratio=receipts['SERIAL']['timing']['phase_wall_s']/receipts['PARALLEL']['timing']['phase_wall_s'])
    except BaseException as exc:
        result.update(status='FAILED_CLOSED_NO_RETRY',failure_phase=phase,
            failure=dict(type=type(exc).__name__,message=str(exc),notes=getattr(exc,'__notes__',[]),traceback=traceback.format_exc()))
        if active_proxy is not None:
            result['failure_native_rhs_calls_started']=active_proxy.calls
            result['failure_native_rhs_input_sha256']=active_proxy.input_hashes
        if active_opacity is not None:
            result['failure_serial_sigma_counts']=dict(calls=active_opacity.native_calls,energy_evaluations=active_opacity.energy_evaluations)
        if pool is not None:
            result['failure_pool_receipt']=pool.failure_receipt;result['failure_pool_metrics']=pool.metrics
    finally:
        if active_native is not None:
            try:active_native.close()
            except BaseException as exc:result['native_close_failure']=str(exc)
        if active_opacity is not None:
            try:active_opacity.close()
            except BaseException as exc:result['opacity_close_failure']=str(exc)
        if pool is not None:pool.close();result['pool_cleanup']=pool.cleanup_receipt
        result['elapsed_s']=time.monotonic()-start
        durable_json(out/'RESULT.json',canonical(result))
    print(json.dumps({k:v for k,v in result.items() if k not in ('receipts','failure_native_rhs_input_sha256','pool_cleanup')},sort_keys=True),flush=True)
    return 0 if result['status']=='PASS_NEW_IMPLEMENTATION_PARITY' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent-repo',type=Path,required=True)
    parser.add_argument('--parent-root',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--timeout-s',type=float,default=120.)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not 1<=args.workers<=48 or not np.isfinite(args.timeout_s) or args.timeout_s<=0:
        parser.error('workers1..48 and positive finite timeout required')
    return run(args)


if __name__=='__main__':raise SystemExit(main())
