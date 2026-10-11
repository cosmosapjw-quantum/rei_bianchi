"""New source-identity lane from the actual C2_FULL001 failed attempt42.

No old journal is resolved, rewritten or replayed. Parent generation39 physical
prefix/cursor/outputs/kernels are copied exactly. The failed exception consumes
one externally recorded attempt; completed-controller cap105 becomes104, while
attempts=accepted+rejected remains intact. No native/source computation occurs.
"""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2];REPO=HERE.parents[5]
C11=Q1B/'c11';OLD_PRODUCTION=C11/'integration/production'
sys.path.insert(0,str(OLD_PRODUCTION))
from production_journal import durable_json,ensure_json,sha,fsync_dir,canonical_bytes
PARENT_REL=Path('research/accel02_20261011/q1b/c12/evidence/C2_FULL001')
GENERATION=39
PARENT_MANIFEST='334703270be3839466082f1e83355320736e565aaf6840ba6b45ce32a9c46992'
SOURCE_REL=Path('research/accel02_20261011/q1b/c12/repair/source_candidate/source_precision_v2.py')
TARGET=4.011926941800233e16


def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)


def failure_debited_controls(original,cursor):
    require(original['max_attempts']==105 and original['max_accepted_macros']==103,'PARENT_TOTAL_ALLOCATION')
    require(cursor['attempts']==41 and cursor['accepted_macros']==39 and cursor['rejected_macros']==2 and
            cursor['accepted_boundaries']==78 and cursor['accepted_clock_s']==11419941379473.664,'PARENT_CURSOR')
    result=copy.deepcopy(original);result['max_attempts']=104
    return result,dict(original_all_attempt_cap=105,external_failed_attempt_debit=1,
        parent_failed_attempt=42,parent_completed_attempts=41,child_completed_attempt_cap=104,
        remaining_completed_attempts=63,remaining_accepted_macros=64,counters_reset=False,
        controller_count_identity='attempts=accepted_macros+rejected_macros',
        total_budget_identity='completed_attempts + external_failed_attempt_debit <= 105',
        next_child_attempt_number=42,next_physical_attempt_ordinal=43,
        old_failed_attempt_resolved=False,new_source_identity_required=True)


def assert_preserved(parent_arrays,parent_metadata,child_arrays,child_metadata):
    require(set(parent_arrays)==set(child_arrays) and len(parent_arrays)==9,'ARRAY_SET')
    for key,a in parent_arrays.items():
        b=child_arrays[key]
        require(a.dtype==b.dtype and a.shape==b.shape and a.tobytes()==b.tobytes(),'ARRAY_CHANGED:'+key)
    allowed={'restart_binding','restart_binding_sha256','production_repair_transition'}
    require(set(child_metadata)==set(parent_metadata)|{'production_repair_transition'},'METADATA_KEYS')
    for key in set(parent_metadata)-allowed:
        require(parent_metadata[key]==child_metadata[key],'PHYSICAL_METADATA_CHANGED:'+key)
    before,after=parent_metadata['restart_binding'],child_metadata['restart_binding']
    for key in ('end_time_s','hard_events_s'):
        require(before[key]==after[key],'SCHEDULE_CHANGED:'+key)
    require(parent_metadata['adaptive_cursor']==child_metadata['adaptive_cursor'],'CURSOR_CHANGED')
    return dict(all_nine_arrays_bitwise_equal=True,all_physical_metadata_equal=True,
        full_prefix_count=len(parent_arrays['prefix_clock']),cursor_unchanged=True,
        output_records_unchanged=True,kernel_history_unchanged=True,native_calls=0)


def copy_initial_output(parent_run,child_run,authoritative_records):
    parent_run=Path(parent_run);child_run=Path(child_run)
    require(bool(authoritative_records) and authoritative_records[0]['epoch_index']==0,'INITIAL_OUTPUT_NOT_IN_CHECKPOINT')
    done=json.loads((parent_run/'INITIAL_OUTPUT_DONE.json').read_text())
    row=authoritative_records[0]
    require(done['record']==row,'INITIAL_OUTPUT_CHECKPOINT_RECORD')
    require(sha(parent_run/'OUTPUT24/epoch-000.json')==done['row_sha256'],'INITIAL_OUTPUT_HASH')
    require(json.loads((parent_run/'OUTPUT24/epoch-000.json').read_text())==row,'INITIAL_OUTPUT_CONTENT')
    begin=json.loads((parent_run/'INITIAL_OUTPUT_BEGIN.json').read_text())
    require(begin['state_sha256']==row['state_sha256']==row['kernel']['state_sha256'],'INITIAL_OUTPUT_STATE')
    paths=['INITIAL_OUTPUT_BEGIN.json','INITIAL_OUTPUT_DONE.json']
    paths += [f'OUTPUT24/epoch-{r["epoch_index"]:03d}.json' for r in authoritative_records]
    for rel in paths:
        source=parent_run/rel;target=child_run/rel;data=source.read_bytes()
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        fsync_dir(target.parent)
    return dict(mode='COPY_EXISTING_AUTHORITATIVE_OUTPUT_WITH_RECEIPT',copied_files={p:sha(child_run/p) for p in paths},
        new_opacity_calls=0,new_gas_calls=0,old_h0_calls_replayed=False)


def prepare_failure_transition(repo,output_root,extra_dependency_paths=()):
    repo=Path(repo).resolve(strict=True);parent=repo/PARENT_REL;gp=parent/f'CHECKPOINTS/gen-{GENERATION:08d}'
    out=Path(output_root)
    if not out.is_absolute():out=repo/out
    out=out.resolve();require(out.is_relative_to(repo),'CHILD_OUTSIDE_REPO')
    require(not out.exists(),'CHILD_ALREADY_EXISTS')
    require(sha(gp/'manifest.json')==PARENT_MANIFEST,'PARENT_MANIFEST_IDENTITY')
    manifest=json.loads((gp/'manifest.json').read_text())
    for name,record in manifest['files'].items():
        path=gp/name;require(path.stat().st_size==record['bytes'] and sha(path)==record['sha256'],'PARENT_MEMBER:'+name)
    identity=json.loads((gp/'identity.json').read_text());metadata=json.loads((gp/'metadata.json').read_text())
    old_deps=metadata['restart_binding']['dependency_closure'];require(len(old_deps)==53,'PARENT_DEPENDENCY_COUNT')
    require(identity['control']==canonical_sha(metadata['restart_binding']),'PARENT_CONTROL_HASH')
    for key,pin in old_deps.items():
        relative=Path(key.removeprefix('dependency:'))
        require(key.startswith('dependency:') and not relative.is_absolute() and '..' not in relative.parts,'DEPENDENCY_PATH')
        require(sha(repo/relative)==pin,'OLD_DEPENDENCY_CHANGED:'+str(relative))
    begin_path=parent/'RUN/JOURNAL/attempt-00000042.begin.json'
    failure_path=parent/'RUN/JOURNAL/attempt-00000042.failure.json'
    begin=json.loads(begin_path.read_text());failure=json.loads(failure_path.read_text())
    require(not(parent/'RUN/JOURNAL/attempt-00000042.commit.json').exists(),'OLD_FAILED_ATTEMPT_ALREADY_COMMITTED')
    require(not(parent/'CHECKPOINTS/gen-00000040').exists(),'PARENT_ALREADY_ADVANCED')
    require(failure['begin_sha256']==sha(begin_path) and failure['failure']['message']=='SOURCE_ENTRY_CELL_MOMENT_DOMAIN','EXPECTED_FIRST_FAILURE')
    require(begin['cursor']==metadata['adaptive_cursor'] and begin['checkpoint']==dict(generation=39,manifest_sha256=PARENT_MANIFEST),'FAILURE_PARENT_CURSOR')
    launch_result=parent/'RUN/CHUNKS/chunk-00000013/RESULT.json'
    failed_result=json.loads(launch_result.read_text())
    require(failed_result['status']=='FAILED_ATTEMPT' and failed_result['native_calls']==0 and failed_result['opacity_calls']==0 and
            failed_result['trial_map_calls']==1,'FAILURE_BEFORE_NATIVE')
    controls,allocation=failure_debited_controls(metadata['restart_binding']['controls'],metadata['adaptive_cursor'])
    source=repo/SOURCE_REL;require(source.is_file(),'NEW_SOURCE_MISSING')
    require(sha(source)!=identity['source'],'NEW_SOURCE_IDENTITY_REQUIRED')
    sys.path.insert(0,str(repo/'research/accel02_20261011/q1b/c11/restart'))
    from adaptive_checkpoint import load_adaptive_checkpoint,write_adaptive_checkpoint
    loaded=load_adaptive_checkpoint(gp.parent,39,identity,expected_manifest_sha256=PARENT_MANIFEST)
    arrays={k:v.copy() for k,v in loaded['arrays'].items()};child=copy.deepcopy(loaded['metadata'])
    out.mkdir(parents=True,exist_ok=False)
    schedule=json.loads((parent/'SCHEDULE.json').read_text())
    require(schedule['target_time_s']==TARGET and schedule['hard_events_s']==metadata['restart_binding']['hard_events_s'],'ORIGINAL_SCHEDULE')
    durable_json(out/'SCHEDULE.json',schedule);durable_json(out/'CONTROLS.json',controls)
    output_copy=copy_initial_output(parent/'RUN',out/'RUN',metadata['production_output_records'])
    durable_json(out/'OUTPUT_COPY_RECEIPT.json',output_copy)
    deps=copy.deepcopy(old_deps)
    # Retain failed bytes as immutable provenance, not as a completed trial.
    extra=[Path(__file__),HERE/'run_full_history_chunk_v2.py',source,begin_path,failure_path,launch_result,
        parent/'RUN/ATTEMPTS/attempt-00000042/MAP_01_INPUT.npz',parent/'RUN/ATTEMPTS/attempt-00000042/MAP_01_REQUEST.json',
        parent/'RUN/INITIAL_OUTPUT_DONE.json',out/'SCHEDULE.json',out/'CONTROLS.json',out/'OUTPUT_COPY_RECEIPT.json',
        *extra_dependency_paths]
    for path in extra:
        path=Path(path)
        if not path.is_absolute():path=repo/path
        path=path.resolve(strict=True);require(path.is_relative_to(repo),'EXTRA_DEPENDENCY_OUTSIDE_REPO')
        key='dependency:'+str(path.relative_to(repo));pin=sha(path)
        require(key not in deps or deps[key]==pin,'EXTRA_DEPENDENCY_REPLACES_OLD')
        deps[key]=pin
    transition=dict(schema='rei.c12.failed_source_identity_transition.v1',parent_run=str(PARENT_REL),parent_generation=39,
        parent_manifest_sha256=PARENT_MANIFEST,parent_identity=identity,parent_cursor=metadata['adaptive_cursor'],
        old_failed_attempt=42,old_failed_begin_sha256=sha(begin_path),old_failed_record_sha256=sha(failure_path),
        old_failure_status_preserved=True,new_run_first_completed_controller_attempt=42,new_physical_attempt_ordinal=43,
        new_source_path=str(SOURCE_REL),new_source_sha256=sha(source),allocation=allocation,
        physical_prefix_copied_without_maps=True,original_physics_and_criteria_changed=False,
        source_candidate_semantics='REVIEW_REQUIRED_SAME_PROVIDER_NEW_ARITHMETIC',output_copy_receipt=output_copy,
        initial_h0_replayed=False,native_calls=0,completed_scientific_checks_replayed=0,scientific_admission=False)
    durable_json(out/'FAILURE_IDENTITY_TRANSITION.json',transition)
    tp=out/'FAILURE_IDENTITY_TRANSITION.json';deps['dependency:'+str(tp.relative_to(repo))]=sha(tp)
    binding=copy.deepcopy(metadata['restart_binding']);binding['controls']=controls;binding['dependency_closure']=deps
    child['restart_binding']=binding;child['restart_binding_sha256']=canonical_sha(binding)
    child['production_repair_transition']=dict(path=str(tp.relative_to(repo)),sha256=sha(tp),allocation=allocation)
    preservation=assert_preserved(loaded['arrays'],loaded['metadata'],arrays,child)
    child_identity=copy.deepcopy(identity);child_identity['source']=sha(source);child_identity['control']=canonical_sha(binding)
    saved=write_adaptive_checkpoint(out/'CHECKPOINTS',39,arrays,child,child_identity)
    bundle=dict(schema='rei.c12.failed_source_transition_result.v1',checkpoint_directory=str(out/'CHECKPOINTS'),generation=39,
        manifest_sha256=sha(saved/'manifest.json'),generation_path=str(saved),identity=child_identity,controls=controls,
        cursor=metadata['adaptive_cursor'],target_time_s=TARGET,dependency_closure=deps,parent_dependency_count=53,
        schedule_path=str(out/'SCHEDULE.json'),source_module_path=str(SOURCE_REL),transition_path=str(tp),
        allocation=allocation,preservation=preservation,output_copy=output_copy,native_calls=0,scientific_admission=False)
    durable_json(out/'TRANSITION_RESULT.json',bundle)
    return bundle
