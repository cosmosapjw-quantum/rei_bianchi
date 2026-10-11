#!/usr/bin/env python3
"""New true cold-process changed-C11 restore and exactly one controlled macro.

Original candidate dependencies remain immutable. Numeric controls are frozen;
only derived remaining invocation limits and a one-macro verification budget
are separately recorded. Reconstructed complete accepted prefix is compared
with the saved uninterrupted next generation, not with a replayed trajectory.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,os,platform,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;C11=HERE.parent;Q1B=C11.parent;REPO=HERE.parents[4]
sys.path.insert(0,str(HERE))
from cold_restart import sha,canonical_sha,verify_closure,compare_exact,state_from_loaded

def write_json(path,payload):
    with Path(path).open('x') as f:json.dump(payload,f,indent=2,allow_nan=False);f.write('\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--request',type=Path,required=True);ap.add_argument('--request-sha256',required=True);args=ap.parse_args()
    if sha(args.request)!=args.request_sha256:raise ValueError('C11_COLD_REQUEST_IDENTITY')
    request=json.loads(args.request.read_text());out=Path(request['output_directory'])
    if (out/'RESULT.json').exists():raise FileExistsError('C11_COLD_CREATE_ONLY')
    start=time.monotonic()
    result=dict(schema='rei.c11.cold_adaptive_restart.v1',status='IN_PROGRESS',created_utc=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(),parent_pid=os.getppid(),python=sys.version,executable=sys.executable,isolated=bool(sys.flags.isolated),
        numpy=np.__version__,platform=platform.platform(),argv=sys.argv,request_sha256=args.request_sha256,
        native_calls=0,opacity_calls=0,sigma_energy_evaluations=0,trial_map_calls=0,new_accepted_macros=0,
        old_completed_science_or_trajectory_replays=0,independent_physics_oracle=False,scientific_admission=False)
    try:
        if os.getpid()==request['parent_pid'] or os.getppid()!=request['parent_pid']:raise ValueError('C11_COLD_NOT_FRESH_CHILD')
        for key,digest in request['harness_identities'].items():
            if sha(REPO/key)!=digest:raise ValueError('C11_COLD_HARNESS_IDENTITY:'+key)
        pilot=REPO/request['pilot'];directory=pilot/'CHECKPOINTS';generation=request['generation']
        gp=directory/f'gen-{generation:08d}';npth=directory/f'gen-{generation+1:08d}'
        if sha(gp/'manifest.json')!=request['manifest_sha256'] or sha(npth/'manifest.json')!=request['next_manifest_sha256']:
            raise ValueError('C11_COLD_GENERATION_MANIFEST_IDENTITY')
        # No solver/provider import has occurred. Verify complete old41 closure
        # and new harness pins first, then load through the pinned validator.
        meta=json.loads((gp/'metadata.json').read_text());old_identity=json.loads((gp/'identity.json').read_text())
        deps=verify_closure(REPO,meta['restart_binding']['dependency_closure'])
        if deps!=json.loads((pilot/'LAUNCH.json').read_text())['dependency_closure']:
            raise ValueError('C11_COLD_ASRUN_LAUNCH_CLOSURE_MISMATCH')
        expected_identity=dict(source=sha(C11/'precision/source_precision.py'),grid=sha(Q1B/'GRID_C2.json'),
            binary=sha(Q1B/'native/target/release/rei_q1b_cell_native_v1'),physics_contract=sha(C11/'CONTRACT.json'),
            physical_validator=sha(HERE/'adaptive_checkpoint.py'),control=canonical_sha(meta['restart_binding']))
        if old_identity!=expected_identity:raise ValueError('C11_COLD_SIX_SLOT_IDENTITY')
        result.update(candidate_dependency_closure=deps,candidate_dependency_count=len(deps),
            closure_checked_before_simulation_imports=True,loaded_generation=generation,
            loaded_manifest_sha256=request['manifest_sha256'],expected_generation=generation+1,
            expected_manifest_sha256=request['next_manifest_sha256'],loaded_identity=old_identity)
        for path in (Q1B/'c10',Q1B,Q1B.parent/'n1',C11/'precision',C11/'controller',C11/'endpoint',C11/'integration',HERE):sys.path.insert(0,str(path))
        from adaptive_checkpoint import load_adaptive_checkpoint,make_adaptive_snapshot,adaptive_identity,write_adaptive_checkpoint
        from entry_checkpoint import unpack_entry_state
        from run_adaptive_native_v2 import runtime_inputs,strict_validate,save_state,checkpoint_scales,positive_native_step,NativeCell,NativeOpacity,source_precision,absorption_api,ledger
        from adaptive_controller import run_bounded,native_observables
        from adaptive_controller_v2 import effective_budget_controls,budget_lineage
        loaded=load_adaptive_checkpoint(directory,generation,expected_identity,expected_manifest_sha256=request['manifest_sha256'])
        expected=load_adaptive_checkpoint(directory,generation+1,expected_identity,expected_manifest_sha256=request['next_manifest_sha256'])
        a,m=loaded['arrays'],loaded['metadata'];ea,em=expected['arrays'],expected['metadata']
        provider,source,initial=runtime_inputs();shape=initial['N'].shape
        states=[state_from_loaded(a,m,shape,unpack_entry_state,i) for i in range(len(a['prefix_clock']))]
        # Original initial state is verified, not reintegrated.
        for key in ('gas','N','U_eV','R','support'):
            if not compare_exact(states[0][key],initial[key])['bitwise_equal']:raise ValueError('C11_COLD_ORIGINAL_IC_MISMATCH:'+key)
        if states[0]['counters']!=initial['counters'] or states[0]['nH_ref']!=initial['nH_ref'] or states[0]['nHe_ref']!=initial['nHe_ref']:
            raise ValueError('C11_COLD_ORIGINAL_IC_ORIGIN_MISMATCH')
        current=states[-1];cursor=copy.deepcopy(m['adaptive_cursor'])
        base=json.loads((C11/'controller/CONTROL_V1.json').read_text())
        remaining=effective_budget_controls(base,cursor);lineage=budget_lineage(base,remaining,cursor)
        controls=copy.deepcopy(remaining)
        controls['max_accepted_macros']=min(controls['max_accepted_macros'],1)
        if controls['max_attempts']<=0 or controls['max_accepted_macros']<=0:raise ValueError('C11_COLD_NO_REMAINING_BUDGET')
        numerical=lambda c:{k:v for k,v in c.items() if k not in ('max_attempts','max_accepted_macros')}
        if numerical(controls)!=numerical(m['restart_binding']['controls']) or numerical(controls)!=numerical(base):
            raise ValueError('C11_COLD_NUMERICAL_CONTROLS_CHANGED')
        runtime_lineage=dict(remaining_budget=lineage,uninterrupted_invocation_controls=m['restart_binding']['controls'],
            original_frozen_controls=base,remaining_controls=remaining,cold_verification_controls=controls,
            additional_verification_macro_cap=1,cap_reason='Requested exactly one next controlled macro; no further scientific trajectory replay',
            numerical_controls_changed=False,scientific_criteria_changed=False)
        write_json(out/'RUNTIME_BUDGET_LINEAGE.json',runtime_lineage)
        extended=dict(deps)
        extended.update({'dependency:'+k:v for k,v in request['harness_identities'].items()})
        end=m['restart_binding']['end_time_s'];events=m['restart_binding']['hard_events_s']
        result.update(from_t_s=current['t_s'],saved_cursor=cursor,runtime_budget_lineage=runtime_lineage,
            candidate_metadata_equality_claim=False,metadata_difference_reason='Derived remaining runtime cap and separately pinned cold harness lineage',
            loaded_state_sha256=hashlib.sha256(a['state'].tobytes()).hexdigest())
        attempts=[];accepted=[];calls=0
        with NativeOpacity() as opacity,NativeCell() as native:
            result['native_process_pids']={'gas':native.native.proc.pid,'opacity':opacity.native.proc.pid}
            def step(state,t1):
                nonlocal calls
                verify_closure(REPO,deps);calls+=1;stem=out/f'TRIAL_MAP_{calls:03d}'
                save_state(stem.with_name(stem.name+'_INPUT.npz'),state)
                write_json(stem.with_name(stem.name+'_REQUEST.json'),dict(t0_s=state['t_s'],t1_s=t1))
                value=positive_native_step(state,t1,source,opacity,native,source_api=source_precision,absorption_api=absorption_api)
                save_state(stem.with_name(stem.name+'_OUTPUT.npz'),value)
                write_json(stem.with_name(stem.name+'_DIAGNOSTICS.json'),value['diagnostics'])
                return value
            def on_accept(pair,trial,new_cursor):
                prospective=states+list(pair)
                na,nm=make_adaptive_snapshot(states=prospective,controls=controls,cursor=new_cursor,end_time_s=end,
                    hard_events=events,scales=a['scales'],dependency_closure=extended)
                nm['native_driver_binding']='ACTUAL_C11_COLD_PROCESS_NEXT_CONTROLLED_MACRO'
                nm['restart_origin_manifest_sha256']=request['manifest_sha256']
                nm['runtime_budget_lineage_sha256']=sha(out/'RUNTIME_BUDGET_LINEAGE.json')
                identity=adaptive_identity(source=C11/'precision/source_precision.py',grid=Q1B/'GRID_C2.json',
                    binary=Q1B/'native/target/release/rei_q1b_cell_native_v1',physics_contract=C11/'CONTRACT.json',metadata=nm)
                write_adaptive_checkpoint(out/'CHECKPOINTS',new_cursor['accepted_macros'],na,nm,identity)
                comparisons={key:compare_exact(value,ea[key]) for key,value in na.items()}
                support_cmp=compare_exact(np.asarray(nm['prefix_support']),np.asarray(em['prefix_support']))
                R_cmp=compare_exact(np.asarray(nm['prefix_R']),np.asarray(em['prefix_R']))
                row=dict(cursor=new_cursor,cursor_exact_equal=new_cursor==em['adaptive_cursor'],trial=trial,
                    array_comparisons=comparisons,support_history_comparison=support_cmp,R_history_comparison=R_cmp,
                    halfstep_ledgers=[ledger(v,initial) for v in pair],checkpoint_identity=identity)
                for i,value in enumerate(pair,1):save_state(out/f'ACCEPTED_HALF_{i:02d}.npz',value)
                write_json(out/'COMPARISON.json',row);accepted.append(row)
                if not(row['cursor_exact_equal'] and all(v['bitwise_equal'] for v in comparisons.values()) and support_cmp['bitwise_equal'] and R_cmp['bitwise_equal']):
                    raise ArithmeticError('C11_COLD_NEXT_MACRO_MISMATCH')
                states[:]=prospective
            def on_attempt(trial,new_cursor):
                row=dict(trial=trial,cursor=new_cursor);attempts.append(row)
                write_json(out/f'ATTEMPT_{new_cursor["attempts"]:03d}.json',row)
            try:
                outcome=run_bounded(current,end,step,lambda s:native_observables(s,provider),
                    lambda s:strict_validate(s,initial,provider),controls,hard_events=events,cursor=cursor,
                    on_accept=on_accept,on_attempt=on_attempt)
                result.update(controller_outcome_status=outcome['status'],final_cursor=outcome['cursor'],
                    to_t_s=outcome['state']['t_s'],new_accepted_macros=len(accepted),attempts=attempts)
            finally:
                result.update(native_calls=native.calls,opacity_calls=opacity.native_calls,
                    sigma_energy_evaluations=opacity.energy_evaluations,trial_map_calls=calls)
        if len(accepted)!=1:raise ArithmeticError('C11_COLD_DID_NOT_PRODUCE_ONE_ACCEPTED_MACRO')
        verify_closure(REPO,deps);result['closure_checked_after_simulation']=True
        result['status']='PASS_BITWISE_C11_COLD_NEXT_CONTROLLED_MACRO_AND_CURSOR'
    except Exception as exc:
        result.update(status='REJECTED',failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()))
        print(result['failure']['traceback'],flush=True)
    result['elapsed_s']=time.monotonic()-start
    write_json(out/'RESULT.json',result)
    print(json.dumps({k:result[k] for k in ('status','pid','parent_pid','native_calls','opacity_calls','trial_map_calls','new_accepted_macros','elapsed_s')}),flush=True)
    return 0 if result['status'].startswith('PASS_') else 1
if __name__=='__main__':raise SystemExit(main())
