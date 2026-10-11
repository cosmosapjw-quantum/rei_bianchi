#!/usr/bin/env python3
"""Create-only C11 actual native pilot, prospectively bounded by CONTROL_V1.

Every trial input/result is retained. Every accepted macro transaction records
both halfstep boundaries and the controller cursor; restart scope is macro ends.
This is a local prerequisite, never whole-history scientific admission.
"""
from pathlib import Path
import argparse, hashlib, json, math, platform, sys, time, traceback
from datetime import datetime, timezone
import numpy as np
HERE=Path(__file__).resolve().parent
C11=HERE.parent;Q1B=C11.parent;C10=Q1B/'c10'
for directory in (C10,Q1B,Q1B.parent/'n1',C11/'precision',C11/'controller',C11/'restart'):
    sys.path.insert(0,str(directory))
from provider import HistoryProvider
from grid_cells import load_grid
from source_cells import CellSource
from opacity_native import NativeOpacity
from native_step_v2 import NativeCell,initial_state,positive_native_step,gas_energy_eV,gas_admissible,COUNTER_NAMES
from run_native_entry import convert,ledger,fields,dependency_identity as baseline_dependencies
from entry_checkpoint import pack_entry_state
from adaptive_controller import run_bounded,native_observables,validate_controls
import source_precision


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,payload):
    with Path(path).open('x') as f:json.dump(convert(payload),f,indent=2,allow_nan=False);f.write('\n')
def save_state(path,state):
    with Path(path).open('xb') as f:
        np.savez_compressed(f,t_s=state['t_s'],gas=state['gas'],N=state['N'],U_eV=state['U_eV'],
            R=state['R'],support=state['support'],counters=np.array([state['counters'][x] for x in COUNTER_NAMES]),
            nH_ref=state['nH_ref'],nHe_ref=state['nHe_ref'])


def dependency_identity():
    mapping=baseline_dependencies()
    paths=[HERE/'native_step_v2.py',HERE/'run_adaptive_native.py',C11/'precision/source_precision.py',
        C11/'controller/adaptive_controller.py',C11/'controller/CONTROL_V1.json',
        C11/'restart/adaptive_checkpoint.py',C11/'CONTRACT.json',
        Q1B/'native/target/release/rei_q1b_cell_native_v1',Q1B/'GRID_C2.json']
    mapping.update({'dependency:'+str(path.relative_to(Q1B.parents[2])):sha(path) for path in paths})
    return mapping


def runtime_inputs():
    provider=HistoryProvider(r=0.)
    source=CellSource(provider,load_grid(Q1B/'GRID_C2.json'))
    with np.load(Q1B/'evidence/SOURCE_C2.npz') as saved:initial=initial_state(source,saved_initial=saved)
    return provider,source,initial


def strict_validate(state,initial,provider):
    if not gas_admissible(state['gas'],provider.geometry(state['t_s'])):
        raise ArithmeticError('C11_STRICT_GAS_DOMAIN')
    n,u,r,s=(np.asarray(state[k]) for k in ('N','U_eV','R','support'))
    if not(n.shape==u.shape==r.shape and s.shape==(*n.shape,2) and
            all(np.isfinite(v).all() for v in (n,u,r,s)) and
            np.all(n>=0) and np.all(u>=0) and np.all(r>0) and np.all(s>0)):
        raise ArithmeticError('C11_STRICT_RADIATION_DOMAIN')
    if np.any(u[n==0]!=0):raise ArithmeticError('C11_EMPTY_CELL_ENERGY')
    active=n>0
    mean=u[active]/(r[active]*n[active])
    if not(np.all(s[...,0][active]<mean) and np.all(mean<s[...,1][active])):
        raise ArithmeticError('C11_UNIMPLEMENTED_MOMENT_ENDPOINT')
    if not ledger(state,initial)['pass_local_ledgers']:
        raise ArithmeticError('C11_ORIGINAL_IC_LEDGER_REJECTED')


def checkpoint_scales(initial):
    n=initial['N'].size
    e0=math.fsum(initial['U_eV'].ravel())+gas_energy_eV(initial['gas'],initial['nH_ref'],initial['nHe_ref'])
    return np.r_[np.ones(3),initial['gas'][3],np.full(n,initial['nH_ref']),np.full(n,e0),
        np.full(2,initial['nH_ref']),np.full(5,e0)]


def main():
    from adaptive_checkpoint import make_adaptive_snapshot,adaptive_identity,write_adaptive_checkpoint,load_adaptive_checkpoint
    parser=argparse.ArgumentParser();parser.add_argument('--label',required=True);args=parser.parse_args()
    out=HERE/'evidence'/args.label;out.mkdir(parents=False,exist_ok=False)
    controls=json.loads((C11/'controller/CONTROL_V1.json').read_text());validate_controls(controls)
    end=controls['bounded_run_request']['end_s']
    provider,source,initial=runtime_inputs();strict_validate(initial,initial,provider)
    if not (controls['observable_scales']['ne_cm3']==initial['nH_ref'] and
            controls['observable_scales']['photon_cm3']==initial['nH_ref'] and
            controls['distribution_scales']['N_ref_distribution']==initial['nH_ref'] and
            controls['distribution_scales']['U_eV_ref_distribution']==13.598434599702*initial['nH_ref']):
        raise ValueError('C11_FIXED_SCALE_INITIAL_REFERENCE_BINDING')
    dependencies=dependency_identity();events=list(source_precision.provider_event_times(source,0.,end))
    launch=dict(schema='rei.q1b.c11.actual_native_launch.v1',created_utc=datetime.now(timezone.utc).isoformat(),
        argv=sys.argv,python=platform.python_version(),numpy=np.__version__,controls=controls,
        dependency_closure=dependencies,hard_events_s=events,initial_time_s=0.,end_time_s=end,
        old_completed_replays=0,source_api='c11.precision.source_precision',scientific_admission=False)
    write_json(out/'LAUNCH.json',launch);save_state(out/'INITIAL.npz',initial)
    asrun=out/'ASRUN';asrun.mkdir()
    for key,digest in dependencies.items():
        path=Q1B.parents[2]/key.removeprefix('dependency:')
        if path.suffix=='.py':
            target=asrun/key.removeprefix('dependency:');target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:f.write(path.read_bytes())
    states=[initial];rows=[];attempts=[];calls=0;start=time.monotonic();cursor=None
    result=dict(schema='rei.q1b.c11.actual_native_bounded.v1',status='RUNNING',accepted_boundaries=rows,
        attempts=attempts,dependency_closure=dependencies,scientific_admission=False,old_completed_replays=0,
        bounded_final_s=end,claim='NEW_SOURCE_AND_FIXED_SCALE_CONTROLLER_LOCAL_PREREQUISITE_ONLY')
    try:
        with NativeOpacity() as opacity,NativeCell() as native:
            def step(state,t1):
                nonlocal calls
                if dependency_identity()!=dependencies:raise ArithmeticError('C11_RUNTIME_DEPENDENCY_DRIFT')
                calls+=1;stem=out/f'TRIAL_MAP_{calls:03d}'
                save_state(stem.with_name(stem.name+'_INPUT.npz'),state)
                write_json(stem.with_name(stem.name+'_REQUEST.json'),{'t0_s':state['t_s'],'t1_s':t1,'call':calls,'dependency_closure':dependencies})
                value=positive_native_step(state,t1,source,opacity,native,source_api=source_precision)
                save_state(stem.with_name(stem.name+'_OUTPUT.npz'),value)
                write_json(stem.with_name(stem.name+'_DIAGNOSTICS.json'),value['diagnostics'])
                return value
            def validate(state):strict_validate(state,initial,provider)
            def on_accept(pair,trial,prospective_cursor):
                nonlocal cursor
                prospective=states+list(pair)
                arrays,metadata=make_adaptive_snapshot(states=prospective,controls=controls,cursor=prospective_cursor,
                    end_time_s=end,hard_events=events,scales=checkpoint_scales(initial),dependency_closure=dependencies)
                metadata['native_driver_binding']='ACTUAL_C11_NATIVE_'+args.label
                identity=adaptive_identity(source=C11/'precision/source_precision.py',grid=Q1B/'GRID_C2.json',
                    binary=Q1B/'native/target/release/rei_q1b_cell_native_v1',physics_contract=C11/'CONTRACT.json',metadata=metadata)
                generation=prospective_cursor['accepted_macros']
                write_adaptive_checkpoint(out/'CHECKPOINTS',generation,arrays,metadata,identity)
                restored=load_adaptive_checkpoint(out/'CHECKPOINTS',generation,identity)
                if not np.array_equal(restored['arrays']['prefix_state'],arrays['prefix_state']):
                    raise ArithmeticError('C11_CHECKPOINT_PREFIX_ROUNDTRIP')
                write_json(out/f'CHECKPOINT_{generation:03d}_IDENTITY.json',identity)
                for value in pair:
                    row=dict(index=len(rows)+1,t_s=value['t_s'],fields=fields(value,provider),ledger=ledger(value,initial),
                        diagnostics=value['diagnostics'],macro_generation=generation)
                    rows.append(row)
                    save_state(out/f'ACCEPTED_{len(rows):03d}.npz',value)
                states[:]=prospective;cursor=prospective_cursor
                write_json(out/f'CHECKPOINT_{generation:03d}_RESULT.json',dict(cursor=cursor,trial=trial,
                    accepted_boundaries=rows,identity=identity))
                print(json.dumps(convert(dict(checkpoint=generation,cursor=cursor,trial=trial,
                    native_calls=native.calls,opacity_calls=opacity.native_calls,elapsed_s=time.monotonic()-start))),flush=True)
            def on_attempt(trial,prospective_cursor):
                attempts.append(trial)
                write_json(out/f'ATTEMPT_{len(attempts):03d}.json',dict(trial=trial,cursor=prospective_cursor))
            try:
                outcome=run_bounded(initial,end,step,lambda s:native_observables(s,provider),validate,controls,
                    hard_events=events,on_accept=on_accept,on_attempt=on_attempt)
                result.update(status=outcome['status'],cursor=outcome['cursor'],last_accepted_s=outcome['state']['t_s'])
            finally:
                result.update(native_calls=native.calls,opacity_calls=opacity.native_calls,
                    sigma_energy_evaluations=opacity.energy_evaluations,trial_map_calls=calls)
    except Exception as exc:
        result.update(status='REJECTED_BOUNDED_ATTEMPT',failure=dict(type=type(exc).__name__,message=str(exc),
            notes=getattr(exc,'__notes__',[]),diagnostics=getattr(exc,'diagnostics',None),traceback=traceback.format_exc()),
            last_accepted_s=states[-1]['t_s'],cursor=cursor)
        print(result['failure']['traceback'],flush=True)
    result['elapsed_s']=time.monotonic()-start
    write_json(out/'RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','last_accepted_s','elapsed_s')}),flush=True)
    return 0 if result['status']=='REACHED_REQUESTED_BOUNDARY' else 1

if __name__=='__main__':raise SystemExit(main())
