#!/usr/bin/env python3
"""Continue explicit absorption-repaired child of preserved failed attempt66.

CLI --transition-bundle <P0 TRANSITION_RESULT.json> --run-directory <new run root>
    [--new-attempt-cap 3 --wall-s 45]
Each repeated invocation performs only NEW attempts. The accepted checkpoint
binding retains103 completed attempts plus2 external failed debits, macrocap103, fulltarget.
"""
from __future__ import annotations
import argparse
import copy
import fcntl
import hashlib
import json
import math
import os
import platform
from pathlib import Path
import sys
import time
import traceback
HERE=Path(__file__).resolve().parent
Q1B=HERE.parents[2];C11=Q1B/'c11';REPO=HERE.parents[5]
OLD_PRODUCTION=C11/'integration/production'
sys.path.insert(0,str(OLD_PRODUCTION))
sys.path.insert(0,str(HERE))
from production_journal import AttemptJournal,JournalError,durable_json,ensure_json,sha,fsync_dir,run_chunk,reconcile_output_records


def verify_closure(mapping):
    for key,expected in mapping.items():
        relative=Path(key.removeprefix('dependency:'))
        if not key.startswith('dependency:') or relative.is_absolute() or '..' in relative.parts:
            raise ValueError('DEPENDENCY_PATH')
        if sha(REPO/relative)!=expected:raise ValueError('DEPENDENCY_DRIFT:'+str(relative))


def save_state(path,state):
    import numpy as np
    from native_step_v3 import COUNTER_NAMES
    with Path(path).open('xb') as f:
        np.savez_compressed(f,t_s=state['t_s'],gas=state['gas'],N=state['N'],U_eV=state['U_eV'],
            R=state['R'],support=state['support'],counters=np.array([state['counters'][k] for k in COUNTER_NAMES]),
            nH_ref=state['nH_ref'],nHe_ref=state['nHe_ref'])
        f.flush();os.fsync(f.fileno())
    fsync_dir(Path(path).parent)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def source_paths():
    """Old68 remain pinned; only this versioned lane and candidate are added."""
    return [HERE/'run_full_history_chunk_v3.py',HERE/'prepare_opacity_transition.py',
            Q1B/'c12/repair/source_candidate/source_precision_v2.py',
            Q1B/'c12/repair/opacity_candidate/positive_absorption_v2.py']


def prefix_states(loaded,shape):
    import numpy as np
    from entry_checkpoint import unpack_entry_state
    a,m=loaded['arrays'],loaded['metadata'];states=[]
    for i,t in enumerate(a['prefix_clock']):
        s=unpack_entry_state(a['prefix_state'][i],m['cell_count'])
        for k in ('N','U_eV'):s[k]=s[k].reshape(shape)
        s.update(t_s=float(t),nH_ref=m['nH_ref'],nHe_ref=m['nHe_ref'],
            R=np.asarray(m['prefix_R'][i]).reshape(shape),support=np.asarray(m['prefix_support'][i]).reshape((*shape,2)))
        # Newly generated native kernels are diagnostic metadata, not hidden
        # physical components. Parent prefix0..6 remains untouched.
        diag=m.get('production_kernel_history',{}).get(str(i))
        if diag is not None:s['diagnostics']=copy.deepcopy(diag)
        states.append(s)
    return states


def _run(args):
    import numpy as np
    started=time.monotonic();bundle=json.loads(args.transition_bundle.read_text())
    deps=bundle['dependency_closure'];verify_closure(deps)
    for path in source_paths():
        key='dependency:'+str(path.relative_to(REPO))
        if deps.get(key)!=sha(path):raise ValueError('NEW_EXECUTED_LEAF_NOT_PINNED:'+str(path))
    for path in (Q1B/'c10',Q1B,Q1B.parent/'n1',C11/'precision',C11/'controller',C11/'restart',C11/'endpoint',C11/'integration'):
        sys.path.insert(0,str(path))
    from adaptive_checkpoint import load_adaptive_checkpoint,make_adaptive_snapshot,write_adaptive_checkpoint,adaptive_identity
    from run_adaptive_native_v2 import runtime_inputs,strict_validate,NativeCell,NativeOpacity,ledger,convert
    import importlib.util
    expected_source=Q1B/'c12/repair/source_candidate/source_precision_v2.py'
    source_path=REPO/bundle['source_module_path']
    if source_path!=expected_source or sha(source_path)!=bundle['identity']['source']:
        raise ValueError('REPAIRED_SOURCE_IDENTITY')
    sys.path.insert(0,str(source_path.parent))
    spec=importlib.util.spec_from_file_location('c12_source_precision_v2',source_path)
    source_precision=importlib.util.module_from_spec(spec);sys.modules[spec.name]=source_precision
    spec.loader.exec_module(source_precision)
    absorption_path=REPO/bundle['absorption_module_path']
    expected_absorption=Q1B/'c12/repair/opacity_candidate/positive_absorption_v2.py'
    if absorption_path!=expected_absorption or sha(absorption_path)!=bundle['absorption_sha256']:
        raise ValueError('REPAIRED_ABSORPTION_IDENTITY')
    sys.path.insert(0,str(absorption_path.parent))
    spec=importlib.util.spec_from_file_location('c12_positive_absorption_v2',absorption_path)
    absorption_api=importlib.util.module_from_spec(spec);sys.modules[spec.name]=absorption_api
    spec.loader.exec_module(absorption_api)
    if not callable(getattr(absorption_api,'pop_refinement_records',None)):
        raise ValueError('ABSORPTION_REFINEMENT_RECEIPT_API_REQUIRED')
    from adaptive_controller import run_bounded,native_observables,next_boundary
    from native_step_v4_diagnostics import positive_native_step
    from cell_history_fields import build_record,physical_state_sha256,geometry_diagnostics,FIELDS24
    directory=Path(bundle['checkpoint_directory']);identity=bundle['identity'];controls=bundle['controls']
    schedule=json.loads(Path(bundle['schedule_path']).read_text());target=bundle['target_time_s']
    if target!=4.011926941800233e16 or controls['max_attempts']!=103 or controls['max_accepted_macros']!=103:
        raise ValueError('FULL_TARGET_ALLOCATION_CONTRACT')
    out=args.run_directory.resolve()
    if out!=directory.parent/'RUN' or not(out/'INITIAL_OUTPUT_DONE.json').exists():
        raise ValueError('REPAIRED_LANE_REQUIRES_MIGRATED_INITIAL_RECEIPT_NO_H0_REPLAY')
    if bundle['allocation']['external_failed_attempt_debit']!=2 or bundle['allocation']['remaining_completed_attempts']!=38:
        raise ValueError('FAILED_ATTEMPT_ALLOCATION_DEBIT')
    out.mkdir(parents=True,exist_ok=True)
    try:out.relative_to(REPO)
    except ValueError:raise ValueError('RUN_DIRECTORY_OUTSIDE_REPO') from None
    lock=(out/'RUN.lock').open('a+')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise JournalError('ANOTHER_CHUNK_PROCESS_OWNS_RUN') from None
    seed_checkpoint=dict(generation=bundle['generation'],manifest_sha256=bundle['manifest_sha256'])
    journal=AttemptJournal(out/'JOURNAL',bundle['cursor'],seed_checkpoint)
    def load(ref):
        return load_adaptive_checkpoint(directory,ref['generation'],identity,expected_manifest_sha256=ref['manifest_sha256'])
    def publish_rows(rows):
        reconcile_output_records(out/'OUTPUT24',rows)
    def reconcile(begin):
        generation=begin['cursor']['accepted_macros']+1;gp=directory/f'gen-{generation:08d}'
        if not gp.exists():return None
        restored=load(dict(generation=generation,manifest_sha256=sha(gp/'manifest.json')))
        transaction=restored['metadata'].get('production_transaction')
        if transaction is None or transaction['begin_sha256']!=sha(journal._path(begin['attempt'],'begin')):
            raise JournalError('ATOMIC_CHECKPOINT_TRANSACTION_MISMATCH')
        publish_rows(transaction['output_records'])
        receipt=dict(cursor=restored['metadata']['adaptive_cursor'],trial=transaction['trial'],
            checkpoint=dict(generation=generation,manifest_sha256=sha(gp/'manifest.json')))
        return receipt
    journal.resume(reconcile)
    loaded=load(journal.head['checkpoint']);binding=loaded['metadata']['restart_binding']
    if binding['controls']!=controls or binding['end_time_s']!=target or binding['hard_events_s']!=schedule['hard_events_s'] or binding['dependency_closure']!=deps:
        raise ValueError('PRODUCTION_BINDING_MISMATCH')
    saved_cursor=loaded['metadata']['adaptive_cursor'];live_cursor=journal.head['cursor']
    # Rejections only can place the journal ahead of its accepted checkpoint.
    for k in ('accepted_clock_s','accepted_macros','accepted_boundaries'):
        if saved_cursor[k]!=live_cursor[k]:raise ValueError('JOURNAL_CHECKPOINT_PREFIX_MISMATCH')
    provider,source,initial=runtime_inputs();states=prefix_states(loaded,initial['N'].shape)
    kernel_history=copy.deepcopy(loaded['metadata'].get('production_kernel_history',{}))
    output_history=copy.deepcopy(loaded['metadata'].get('production_output_records',[]))
    prefix_identity={state['t_s']:physical_state_sha256(state) for state in states}
    for record in output_history:
        i=record['epoch_index'];t=record['time_s']
        if t!=schedule['output_epochs_s'][i] or prefix_identity.get(t)!=record['state_sha256']:
            raise ValueError('OUTPUT_HISTORY_PREFIX_IDENTITY')
    publish_rows(output_history)
    if physical_state_sha256(states[0])!=physical_state_sha256(initial):raise ValueError('ORIGINAL_IC_CHANGED')
    def validate(state):
        strict_validate(state,initial,provider)
        geometry=geometry_diagnostics(source,state['t_s'])
        if geometry['max_error']>1e-11:raise ArithmeticError('ORIGINAL_GEOMETRY_GATE')
    validate(states[-1])
    chunks=out/'CHUNKS';chunks.mkdir(exist_ok=True)
    sequence=1+max([int(p.name.split('-')[1]) for p in chunks.glob('chunk-*') if p.is_dir()] or [0])
    chunk=chunks/f'chunk-{sequence:08d}';chunk.mkdir(exist_ok=False)
    launch=dict(schema='rei.c12.full_history_chunk_launch.v1',argv=sys.argv,pid=os.getpid(),python=sys.version,
        platform=platform.platform(),numpy=np.__version__,transition_bundle_sha256=sha(args.transition_bundle),
        checkpoint=journal.head['checkpoint'],cursor=journal.head['cursor'],identity=identity,dependency_closure=deps,
        total_controls=controls,total_controls_canonical_sha256=canonical_sha(controls),
        new_attempt_cap=args.new_attempt_cap,cooperative_wall_s=args.wall_s,target_time_s=target,
        physics_and_criteria_changed=False,old_completed_replays=0,
        failure_resume_lineage=bundle['allocation'],source_module_path=bundle['source_module_path'],
        source_identity=identity['source'],old_failed_attempt_resolved=False,
        absorption_module_path=bundle['absorption_module_path'],absorption_sha256=bundle['absorption_sha256'])
    durable_json(chunk/'LAUNCH.json',launch)
    # Preserve executable bytes once; files are verified against child closure.
    for key,digest in deps.items():
        rel=Path(key.removeprefix('dependency:'))
        if rel.suffix=='.py':
            dst=out/'ASRUN'/rel
            if dst.exists():
                if sha(dst)!=digest:raise ValueError('ASRUN_SOURCE_DRIFT')
            else:
                dst.parent.mkdir(parents=True,exist_ok=True)
                with dst.open('xb') as f:f.write((REPO/rel).read_bytes());f.flush();os.fsync(f.fileno())
    calls=0;new_checkpoints=[];result=None
    with NativeOpacity() as opacity,NativeCell() as native:
        try:
            initial_record=out/'OUTPUT24'/'epoch-000.json';init_begin=out/'INITIAL_OUTPUT_BEGIN.json'
            init_done=out/'INITIAL_OUTPUT_DONE.json'
            if init_done.exists():
                receipt=json.loads(init_done.read_text())
                record=receipt['record']
                if record['state_sha256']!=physical_state_sha256(initial) or record['kernel']['state_sha256']!=physical_state_sha256(initial):
                    raise JournalError('INITIAL_OUTPUT_STATE_KERNEL_IDENTITY')
                publish_rows([record])
                if receipt['row_sha256']!=sha(initial_record):raise JournalError('INITIAL_OUTPUT_ROW_HASH')
            else:
                raise JournalError('REPAIRED_LANE_INITIAL_RECEIPT_MISSING_NO_H0_REPLAY')
            initial_saved=json.loads(initial_record.read_text())
            if output_history:
                if output_history[0]!=initial_saved:raise JournalError('INITIAL_OUTPUT_CHECKPOINT_HISTORY_DISAGREES')
            else:output_history.append(initial_saved)
            def request(c):
                t1,kind=next_boundary(c['accepted_clock_s'],c['next_step_s'],target,schedule['hard_events_s'])
                return dict(t0_s=c['accepted_clock_s'],t1_s=t1,boundary_kind=kind,target_time_s=target,
                    input_state_sha256=physical_state_sha256(states[-1]),
                    external_failed_attempt_debit=2,new_physical_attempt_ordinal=c['attempts']+3)
            def attempt(cursor,number):
                nonlocal calls
                step_count=0;accepted_receipt=None
                adir=out/'ATTEMPTS'/f'attempt-{number:08d}';adir.mkdir(parents=True,exist_ok=False)
                one=copy.deepcopy(controls);one['max_attempts']=one['max_accepted_macros']=1
                durable_json(adir/'CONTROL_LINEAGE.json',dict(total_controls=controls,
                    total_controls_canonical_sha256=canonical_sha(controls),actual_effective_controls=one,
                    actual_effective_controls_canonical_sha256=canonical_sha(one),saved_cursor=cursor,
                    remaining_total_attempts=controls['max_attempts']-cursor['attempts'],
                    remaining_total_accepted_macros=controls['max_accepted_macros']-cursor['accepted_macros'],
                    runtime_cap_policy='ONE_NEW_TRIAL_GUARDED_BY_TOTAL_REMAINING_ALLOCATION',
                    remaining_budget_helper_applications=0,counters_reset=False,numerical_controls_changed=False))
                def step(state,t1):
                    nonlocal calls,step_count
                    verify_closure(deps);calls+=1;step_count+=1;stem=adir/f'MAP_{step_count:02d}'
                    save_state(stem.with_name(stem.name+'_INPUT.npz'),state)
                    durable_json(stem.with_name(stem.name+'_REQUEST.json'),dict(t0_s=state['t_s'],t1_s=t1,
                        input_file_sha256=sha(stem.with_name(stem.name+'_INPUT.npz')),
                        input_state_sha256=physical_state_sha256(state),dependency_closure=deps))
                    if absorption_api.pop_refinement_records():raise ValueError('STALE_ABSORPTION_REFINEMENT_RECORDS')
                    try:
                        value=positive_native_step(state,t1,source,opacity,native,source_api=source_precision,absorption_api=absorption_api)
                    finally:
                        refinements=absorption_api.pop_refinement_records()
                        durable_json(stem.with_name(stem.name+'_ABSORPTION_REFINEMENTS.json'),convert(dict(records=refinements)))
                    value['diagnostics']['absorption_refinements']=refinements
                    save_state(stem.with_name(stem.name+'_OUTPUT.npz'),value)
                    durable_json(stem.with_name(stem.name+'_DIAGNOSTICS.json'),convert(value['diagnostics']))
                    return value
                def accepted(pair,trial,new_cursor):
                    nonlocal accepted_receipt
                    prospective=states+list(pair);records=[];generation=new_cursor['accepted_macros']
                    prospective_kernels=copy.deepcopy(kernel_history)
                    for half,state in enumerate(pair,1):
                        validate(state)
                        prospective_kernels[str(len(states)+half-1)]=dict(gamma=state['diagnostics']['gamma'],
                            output24_kernel=copy.deepcopy(state['diagnostics']['output24_kernel']))
                        save_state(adir/f'ACCEPTED_HALF_{half}.npz',state)
                        t=float(state['t_s'])
                        if t in schedule['output_epochs_s']:
                            i=schedule['output_epochs_s'].index(t)
                            records.append(build_record(state,source,source_api=source_precision,epoch_index=i,
                                generation=generation,state_sha256=physical_state_sha256(state),ledger=ledger(state,initial)))
                    arrays,metadata=make_adaptive_snapshot(states=prospective,controls=controls,cursor=new_cursor,
                        end_time_s=target,hard_events=schedule['hard_events_s'],scales=loaded['arrays']['scales'],dependency_closure=deps)
                    metadata['production_kernel_history']=prospective_kernels
                    metadata['production_output_records']=output_history+records
                    metadata['production_transition']=copy.deepcopy(loaded['metadata']['production_transition'])
                    metadata['production_repair_transition']=copy.deepcopy(loaded['metadata']['production_repair_transition'])
                    metadata['production_opacity_transition']=copy.deepcopy(loaded['metadata']['production_opacity_transition'])
                    metadata['native_driver_binding']='ACTUAL_C12_OPACITY_REPAIRED_FULL_TARGET_DURABLE_CHUNK'
                    metadata['production_transaction']=dict(attempt=number,
                        begin_sha256=sha(journal._path(number,'begin')),trial=trial,output_records=records)
                    actual_identity=adaptive_identity(source=source_path,grid=Q1B/'GRID_C2.json',
                        binary=Q1B/'native/target/release/rei_q1b_cell_native_v1',physics_contract=C11/'CONTRACT.json',metadata=metadata)
                    if actual_identity!=identity:raise ValueError('CHECKPOINT_BINDING_DRIFT')
                    path=write_adaptive_checkpoint(directory,generation,arrays,metadata,identity)
                    checkpoint=dict(generation=generation,manifest_sha256=sha(path/'manifest.json'))
                    states[:]=prospective;kernel_history.clear();kernel_history.update(prospective_kernels)
                    new_checkpoints.append(checkpoint);output_history.extend(records);publish_rows(records)
                    accepted_receipt=dict(cursor=new_cursor,trial=trial,checkpoint=checkpoint)
                    print(json.dumps(convert(dict(event='ACCEPTED_CHECKPOINT',checkpoint=checkpoint,cursor=new_cursor,
                        elapsed_s=time.monotonic()-started,output_epoch_indices=[r['epoch_index'] for r in records]))),flush=True)
                # This invocation cap never enters accepted checkpoint identity.
                outcome=run_bounded(states[-1],target,step,lambda s:native_observables(s,provider),validate,one,
                    hard_events=schedule['hard_events_s'],cursor=cursor,on_accept=accepted)
                if len(outcome['attempts'])!=1:raise ValueError('EXACTLY_ONE_NEW_TRIAL_REQUIRED')
                trial=outcome['attempts'][0]
                receipt=accepted_receipt if trial['accepted'] else dict(cursor=outcome['cursor'],trial=trial,
                    checkpoint=copy.deepcopy(journal.head['checkpoint']))
                if receipt['cursor']!=outcome['cursor']:raise ValueError('TRANSACTION_CURSOR_MISMATCH')
                durable_json(adir/'RESULT.json',convert(receipt))
                return convert(receipt)
            result=run_chunk(journal,attempt,target=target,total_attempts=controls['max_attempts'],
                total_macros=controls['max_accepted_macros'],new_attempt_cap=args.new_attempt_cap,
                wall_s=max(1e-9,args.wall_s-(time.monotonic()-started)),request=request,reconcile=reconcile)
            if result['status']=='REACHED_FULL_TARGET':
                final_loaded=load(result['checkpoint'])
                authoritative=final_loaded['metadata']['production_output_records']
                if len(authoritative)!=129:raise ValueError('FULL129_CHECKPOINT_OUTPUT_COUNT')
                publish_rows(authoritative)
                rows=[json.loads((out/'OUTPUT24'/f'epoch-{i:03d}.json').read_text()) for i in range(129)]
                if any(row['time_s']!=schedule['output_epochs_s'][i] or list(row['fields'])!=list(FIELDS24)
                       for i,row in enumerate(rows)):
                    # durable_json sorts map keys: keys are a set; schema supplies ordering.
                    if any(row['time_s']!=schedule['output_epochs_s'][i] or set(row['fields'])!=set(FIELDS24)
                           for i,row in enumerate(rows)):raise ValueError('FULL129_OUTPUT_BINDING')
                durable_json(out/'FULL_HISTORY_REACHED.json',dict(cursor=result['cursor'],checkpoint=result['checkpoint'],
                    output_epochs=129,fields=list(FIELDS24),shared65_indices=schedule['shared65_indices'],
                    scientific_admission=False,convergence='NOT_EVALUATED'))
        except Exception as exc:
            result=dict(schema='rei.c12.production_chunk_result.v1',status='FAILED_CHUNK_SETUP_OR_PUBLICATION',
                failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()),
                cursor=journal.head['cursor'],checkpoint=journal.head['checkpoint'],scientific_admission=False)
        finally:
            if result is None:result=dict(status='UNEXPECTED_NO_RESULT',scientific_admission=False)
            result.update(native_calls=native.calls,opacity_calls=opacity.native_calls,
                sigma_energy_evaluations=opacity.energy_evaluations,trial_map_calls=calls,
                elapsed_s=time.monotonic()-started,new_checkpoints=new_checkpoints,
                output_epoch_count=len(list((out/'OUTPUT24').glob('epoch-*.json'))),
                target_time_s=target,old_completed_replays=0)
    verify_closure(deps);durable_json(chunk/'RESULT.json',convert(result))
    print(json.dumps(convert(result)),flush=True)
    return 0 if result['status'] in ('CHUNK_ATTEMPT_BOUNDARY','CHUNK_WALL_BOUNDARY','ALLOCATION_EXHAUSTED','REACHED_FULL_TARGET','CHUNK_RECOVERED_COMMIT_BOUNDARY') else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transition-bundle',type=Path,required=True)
    parser.add_argument('--run-directory',type=Path,required=True)
    parser.add_argument('--new-attempt-cap',type=int,default=3)
    parser.add_argument('--wall-s',type=float,default=45.)
    args=parser.parse_args()
    if args.new_attempt_cap<=0 or not(math.isfinite(args.wall_s) and args.wall_s>0):parser.error('positive budgets required')
    return _run(args)

if __name__=='__main__':raise SystemExit(main())
