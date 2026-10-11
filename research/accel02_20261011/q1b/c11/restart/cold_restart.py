#!/usr/bin/env python3
"""Fresh-process C10 saved-boundary restore and one native split-step check.

This harness adds operational evidence only. It never integrates the completed
trajectory, changes a C10 byte, or admits a changed C11 solver/checkpoint schema.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback
import numpy as np

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
Q1B=HERE.parents[1]
C10=Q1B/'c10'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify_closure(root,pins):
    actual={}
    for key,expected in pins.items():
        if not key.startswith('dependency:'):raise ValueError('DEPENDENCY_KEY')
        relative=Path(key.split(':',1)[1])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('DEPENDENCY_PATH')
        path=Path(root)/relative
        actual[key]=sha(path)
        if actual[key]!=expected:raise ValueError('DEPENDENCY_MISMATCH:'+str(relative))
    return actual

def compare_exact(actual,expected):
    a=np.asarray(actual);b=np.asarray(expected)
    if a.shape!=b.shape or a.dtype!=b.dtype:
        return dict(bitwise_equal=False,shape_equal=a.shape==b.shape,dtype_equal=a.dtype==b.dtype)
    # Bytes distinguish signed zero. Difference count uses bytes per element too.
    ab=np.ascontiguousarray(a).view(np.uint8).reshape(-1,a.dtype.itemsize)
    bb=np.ascontiguousarray(b).view(np.uint8).reshape(-1,b.dtype.itemsize)
    return dict(bitwise_equal=bool(np.array_equal(ab,bb)),shape=list(a.shape),dtype=str(a.dtype),
        different_entries=int(np.any(ab!=bb,axis=1).sum()),
        max_absolute_difference=float(np.max(np.abs(a-b))) if a.size else 0.)

def state_from_loaded(arrays,meta,shape,unpack,index=-1):
    s=unpack(arrays['prefix_state'][index],meta['cell_count'])
    for k in ('N','U_eV'):s[k]=s[k].reshape(shape)
    s.update(t_s=float(arrays['prefix_clock'][index]),nH_ref=meta['nH_ref'],nHe_ref=meta['nHe_ref'],
        R=np.asarray(meta['prefix_R'][index]).reshape(shape),
        support=np.asarray(meta['prefix_support'][index]).reshape((*shape,2)))
    return s

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--request',required=True,type=Path)
    parser.add_argument('--request-sha256',required=True);args=parser.parse_args()
    if sha(args.request)!=args.request_sha256:raise ValueError('REQUEST_IDENTITY_MISMATCH')
    request=json.loads(args.request.read_text());out=Path(request['output_directory'])
    if (out/'RESULT.json').exists():raise FileExistsError('COLD_RESTART_CREATE_ONLY')
    started=time.monotonic()
    result=dict(schema='rei.c11.cold_restart.v1',status='IN_PROGRESS',created_utc=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(),parent_pid=os.getppid(),expected_parent_pid=request['parent_pid'],
        argv=sys.argv,python_executable=sys.executable,python_version=sys.version,
        python_isolated=bool(sys.flags.isolated),platform=platform.platform(),numpy_version=np.__version__,
        request_sha256=args.request_sha256,harness_sha256=sha(__file__),
        native_calls=0,opacity_calls=0,sigma_energy_evaluations=0,
        prior_completed_trajectory_replays=0,new_next_steps=0,
        scope='ACTUAL_C10_FIXED_SPLIT_BOUNDARY_COLD_PROCESS_RESTART',
        changed_C11_solver_restart='NOT_EVALUATED',adaptive_long_run_restart='NOT_EVALUATED',
        independent_numerical_oracle=False,scientific_admission=False)
    try:
        if os.getpid()==request['parent_pid'] or os.getppid()!=request['parent_pid']:
            raise ValueError('NOT_EXPECTED_FRESH_CHILD_PROCESS')
        for relative,pin in request['harness_identities'].items():
            if sha(REPO/relative)!=pin:raise ValueError('HARNESS_IDENTITY_MISMATCH:'+relative)
        # Verify checkpoint manifests/file identities and actual dependency files
        # before importing simulation code or starting either native process.
        directory=REPO/request['checkpoint_directory'];generation=request['generation']
        saved=directory/f'gen-{generation:08d}'
        if sha(saved/'manifest.json')!=request['checkpoint_manifest_sha256']:
            raise ValueError('CHECKPOINT_MANIFEST_IDENTITY_MISMATCH')
        metadata=json.loads((saved/'metadata.json').read_text())
        old_identity=json.loads((saved/'identity.json').read_text())
        actual_closure=verify_closure(REPO,metadata['dependency_closure'])
        expected_identity={
            'source':sha(C10/'source_entry.py'),'grid':sha(Q1B/'GRID_C2.json'),
            'binary':sha(Q1B/'native/target/release/rei_q1b_cell_native_v1'),
            'control':canonical_sha(actual_closure),
            'physics_contract':sha(C10/'CONTRACT.json'),
            'physical_validator':sha(C10/'entry_checkpoint.py')}
        if old_identity!=expected_identity:raise ValueError('CHECKPOINT_SIX_SLOT_IDENTITY_MISMATCH')
        result.update(checkpoint_directory=request['checkpoint_directory'],generation=generation,
            checkpoint_manifest_sha256=request['checkpoint_manifest_sha256'],
            checkpoint_identity=expected_identity,dependency_closure=actual_closure,
            dependency_closure_verified_before_simulation=True)
        sys.path.insert(0,str(C10));sys.path.insert(0,str(Q1B));sys.path.insert(0,str(Q1B.parent/'n1'))
        from entry_checkpoint import load_entry_checkpoint,unpack_entry_state,pack_entry_state,make_entry_snapshot,validate_entry_snapshot,COUNTERS
        from run_native_entry import ledger
        from provider import HistoryProvider
        from grid_cells import load_grid
        from source_cells import CellSource
        from opacity_native import NativeOpacity
        from native_step import NativeCell,positive_native_step
        loaded=load_entry_checkpoint(directory,generation,expected_identity,
            expected_manifest_sha256=request['checkpoint_manifest_sha256'])
        la,lm=loaded['arrays'],loaded['metadata']
        p=HistoryProvider(r=0.);grid=load_grid(Q1B/'GRID_C2.json');src=CellSource(p,grid)
        shape=(len(src.mu),len(src.edges)-1)
        state=state_from_loaded(la,lm,shape,unpack_entry_state)
        ini=state_from_loaded(la,lm,shape,unpack_entry_state,0)
        t1=float(lm['next_segment'][1])
        if lm['next_segment']!=[state['t_s'],request['expected_next_t_s']]:
            raise ValueError('UNEXPECTED_CHECKPOINT_NEXT_BOUNDARY')
        # Read saved expected boundary only; no expected-state computation.
        expected_path=REPO/request['expected_boundary']
        if sha(expected_path)!=request['expected_boundary_sha256']:
            raise ValueError('EXPECTED_BOUNDARY_IDENTITY_MISMATCH')
        with np.load(expected_path,allow_pickle=False) as h:expected={k:h[k].copy() for k in h.files}
        result.update(from_t_s=state['t_s'],to_t_s=t1,loaded_state_sha256=hashlib.sha256(la['state'].tobytes()).hexdigest(),
            expected_boundary=request['expected_boundary'],expected_boundary_sha256=request['expected_boundary_sha256'],
            loaded_validation=loaded['current_validation'])
        with NativeOpacity() as opacity,NativeCell() as native:
            result['native_process_pids']={'gas':native.native.proc.pid,'opacity':opacity.native.proc.pid}
            try:
                advanced=positive_native_step(state,t1,src,opacity,native)
                result['new_next_steps']=1
            finally:
                result.update(native_calls=native.calls,opacity_calls=opacity.native_calls,
                    sigma_energy_evaluations=opacity.energy_evaluations)
        actual={k:advanced[k] for k in ('gas','N','U_eV','R','support')}
        actual.update(counters=np.array([advanced['counters'][k] for k in COUNTERS]),t_s=np.asarray(advanced['t_s']))
        with (out/'ACTUAL_NEXT_BOUNDARY.npz').open('xb') as f:np.savez_compressed(f,**actual)
        comparisons={k:compare_exact(actual[k],expected[k]) for k in actual}
        result.update(comparisons=comparisons,next_boundary_ledger=ledger(advanced,ini),
            actual_next_boundary_sha256=sha(out/'ACTUAL_NEXT_BOUNDARY.npz'),
            actual_next_step_diagnostics=advanced['diagnostics'])
        if not all(v['bitwise_equal'] for v in comparisons.values()):
            raise ArithmeticError('COLD_RESTART_NEXT_BOUNDARY_MISMATCH')
        if not result['next_boundary_ledger']['pass_local_ledgers']:
            raise ArithmeticError('COLD_RESTART_FIXED_INITIAL_LEDGER_REJECTED')
        # Recreate complete accepted prefix from saved prefix + this one new
        # step; validate without changing old generation/checkpoint files.
        packed=pack_entry_state(advanced['gas'],advanced['N'].ravel(),advanced['U_eV'].ravel(),advanced['counters'])
        states=np.vstack([la['prefix_state'],packed]);clocks=np.r_[la['prefix_clock'],t1]
        Rs=np.concatenate([np.asarray(lm['prefix_R']),advanced['R'].reshape(1,-1)])
        supports=np.concatenate([np.asarray(lm['prefix_support']),advanced['support'].reshape(1,-1,2)])
        na,nm=make_entry_snapshot(clocks=clocks,states=states,R=Rs,support=supports,
            all_boundary_clocks=la['scheduled_clock'],nH_ref=lm['nH_ref'],nHe_ref=lm['nHe_ref'],
            scales=la['scales'],physical_binding=lm['physical_binding'])
        result['reconstructed_prefix_validation']=validate_entry_snapshot(na,nm)
        next_loaded=load_entry_checkpoint(directory,generation+1,expected_identity,
            expected_manifest_sha256=request['next_checkpoint_manifest_sha256'])
        result['all_array_comparisons_to_saved_next_generation']={k:compare_exact(v,next_loaded['arrays'][k]) for k,v in na.items()}
        result['support_history_comparison']=compare_exact(np.asarray(nm['prefix_support']),np.asarray(next_loaded['metadata']['prefix_support']))
        result['R_history_comparison']=compare_exact(np.asarray(nm['prefix_R']),np.asarray(next_loaded['metadata']['prefix_R']))
        if not all(v['bitwise_equal'] for v in result['all_array_comparisons_to_saved_next_generation'].values()):
            raise ArithmeticError('COLD_RESTART_FULL_PREFIX_MISMATCH')
        if not(result['support_history_comparison']['bitwise_equal'] and result['R_history_comparison']['bitwise_equal']):
            raise ArithmeticError('COLD_RESTART_SUPPORT_GEOMETRY_HISTORY_MISMATCH')
        if verify_closure(REPO,metadata['dependency_closure'])!=actual_closure:
            raise ArithmeticError('COLD_RESTART_POST_STEP_DEPENDENCY_DRIFT')
        result['dependency_closure_verified_after_simulation']=True
        result['status']='PASS_BITWISE_C10_COLD_PROCESS_NEXT_BOUNDARY'
    except Exception as exc:
        result.update(status='REJECTED',failure={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()})
        print(result['failure']['traceback'],flush=True)
    result['elapsed_s']=time.monotonic()-started
    (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','pid','parent_pid','native_calls','opacity_calls','new_next_steps','elapsed_s')}),flush=True)
    return 0 if result['status'].startswith('PASS_') else 1

if __name__=='__main__':raise SystemExit(main())
