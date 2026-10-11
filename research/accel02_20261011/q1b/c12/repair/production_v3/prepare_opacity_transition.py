"""Explicit absorption-arithmetic child of C2_FULL002 failed attempt66.

Source/provider identity, all physical prefix bytes, schedule and acceptance
thresholds are unchanged. A second externally debited failed physical attempt
reduces the completed-controller cap104 to103 while preserving cursor65/59/6.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2];REPO=HERE.parents[5]
C11=Q1B/'c11';V2=HERE.parent/'production_v2'
sys.path.insert(0,str(V2))
from prepare_failure_transition import copy_initial_output
sys.path.insert(0,str(C11/'integration/production'))
from production_journal import durable_json,sha
PARENT_REL=Path('research/accel02_20261011/q1b/c12/evidence/C2_FULL002')
SOURCE_REL=Path('research/accel02_20261011/q1b/c12/repair/source_candidate/source_precision_v2.py')
SOURCE_SHA='a29207b6ebee37024c35b87723dd64516e528a4f0a160b17ce9965b8dd7e0779'
PARENT_MANIFEST='2dd5d40aaf55768b8a2173e584cf6a3068bff8bd510f88deeca3da69d3c0c5a1'
TARGET=4.011926941800233e16

def require(ok,message):
    if not ok:raise ValueError(message)
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def opacity_debited_controls(original,cursor):
    require(original['max_attempts']==104 and original['max_accepted_macros']==103,'PARENT_TOTAL_ALLOCATION')
    require(cursor['attempts']==65 and cursor['accepted_macros']==59 and cursor['rejected_macros']==6 and
            cursor['accepted_boundaries']==118 and cursor['accepted_clock_s']==18619151741356.234,'PARENT_CURSOR')
    result=copy.deepcopy(original);result['max_attempts']=103
    return result,dict(original_all_attempt_cap=105,external_failed_attempt_debit=2,
        failed_lanes=[dict(run='C2_FULL001',attempt=42),dict(run='C2_FULL002',attempt=66)],
        parent_completed_attempts=65,child_completed_attempt_cap=103,remaining_completed_attempts=38,
        remaining_accepted_macros=44,counters_reset=False,next_child_attempt_number=66,
        next_physical_attempt_ordinal=68,total_budget_identity='completed_attempts + external_failed_attempt_debit <= 105',
        controller_count_identity='attempts=accepted_macros+rejected_macros',old_failed_attempt_resolved=False,
        source_identity_changed=False,absorption_arithmetic_identity_changed=True)


def opacity_child_identity(parent,binding):
    require(parent['source']==SOURCE_SHA,'UNCHANGED_SOURCE_IDENTITY')
    result=copy.deepcopy(parent);result['control']=canonical_sha(binding)
    return result


def assert_preserved(parent_arrays,parent_meta,arrays,meta):
    require(set(parent_arrays)==set(arrays) and len(arrays)==9,'ARRAY_SET')
    for key,value in parent_arrays.items():
        require(value.dtype==arrays[key].dtype and value.shape==arrays[key].shape and value.tobytes()==arrays[key].tobytes(),'ARRAY_CHANGED:'+key)
    require(set(meta)==set(parent_meta)|{'production_opacity_transition'},'METADATA_KEYS')
    for key in set(parent_meta)-{'restart_binding','restart_binding_sha256'}:
        require(parent_meta[key]==meta[key],'PHYSICAL_METADATA_CHANGED:'+key)
    for key in ('end_time_s','hard_events_s'):
        require(parent_meta['restart_binding'][key]==meta['restart_binding'][key],'SCHEDULE_CHANGED:'+key)
    return dict(all_nine_arrays_bitwise_equal=True,all_physical_metadata_equal=True,
        full_prefix_count=len(arrays['prefix_clock']),cursor_unchanged=True,kernel_history_unchanged=True,
        output_records_unchanged=True,native_calls=0)


def prepare_opacity_transition(repo,output_root,absorption_module_path,extra_dependency_paths=()):
    repo=Path(repo).resolve(strict=True);parent=repo/PARENT_REL;gp=parent/'CHECKPOINTS/gen-00000059'
    out=Path(output_root)
    if not out.is_absolute():out=repo/out
    out=out.resolve();require(out.is_relative_to(repo) and not out.exists(),'NEW_CHILD_DIRECTORY_REQUIRED')
    candidate=Path(absorption_module_path)
    if not candidate.is_absolute():candidate=repo/candidate
    candidate=candidate.resolve(strict=True)
    allowed=repo/'research/accel02_20261011/q1b/c12/repair/opacity_candidate'
    require(candidate.parent==allowed and candidate.name=='positive_absorption_v2.py','EXPECTED_OPACITY_CANDIDATE_DIRECTORY')
    require(sha(gp/'manifest.json')==PARENT_MANIFEST,'PARENT_MANIFEST_IDENTITY')
    manifest=json.loads((gp/'manifest.json').read_text())
    for name,record in manifest['files'].items():
        p=gp/name;require(p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],'PARENT_MEMBER:'+name)
    identity=json.loads((gp/'identity.json').read_text());metadata=json.loads((gp/'metadata.json').read_text())
    old_deps=metadata['restart_binding']['dependency_closure'];require(len(old_deps)==68,'PARENT_DEPENDENCY_COUNT')
    require(identity['control']==canonical_sha(metadata['restart_binding']),'PARENT_CONTROL_HASH')
    require(identity['source']==SOURCE_SHA and sha(repo/SOURCE_REL)==SOURCE_SHA,'UNCHANGED_SOURCE_IDENTITY')
    for key,digest in old_deps.items():
        relative=Path(key.removeprefix('dependency:'))
        require(key.startswith('dependency:') and not relative.is_absolute() and '..' not in relative.parts,'DEPENDENCY_PATH')
        require(sha(repo/relative)==digest,'OLD_DEPENDENCY_CHANGED:'+str(relative))
    begin_path=parent/'RUN/JOURNAL/attempt-00000066.begin.json';failure_path=parent/'RUN/JOURNAL/attempt-00000066.failure.json'
    begin=json.loads(begin_path.read_text());failure=json.loads(failure_path.read_text())
    require(not(parent/'RUN/JOURNAL/attempt-00000066.commit.json').exists(),'OLD_ATTEMPT_ALREADY_COMMITTED')
    require(not(parent/'CHECKPOINTS/gen-00000060').exists(),'PARENT_ALREADY_ADVANCED')
    require(failure['begin_sha256']==sha(begin_path) and failure['failure']['message'].startswith('INCIDENT_ORDER_PAIR:'),'EXPECTED_INCIDENT_FAILURE')
    require(begin['cursor']==metadata['adaptive_cursor'] and begin['checkpoint']==dict(generation=59,manifest_sha256=PARENT_MANIFEST),'FAILURE_PARENT_CURSOR')
    result_path=parent/'RUN/CHUNKS/chunk-00000009/RESULT.json';failed=json.loads(result_path.read_text())
    require(failed['status']=='FAILED_ATTEMPT' and failed['native_calls']==0 and failed['opacity_calls']==134 and failed['trial_map_calls']==1,'FAILURE_BEFORE_GAS')
    controls,allocation=opacity_debited_controls(metadata['restart_binding']['controls'],metadata['adaptive_cursor'])
    sys.path.insert(0,str(C11/'restart'))
    from adaptive_checkpoint import load_adaptive_checkpoint,write_adaptive_checkpoint
    loaded=load_adaptive_checkpoint(gp.parent,59,identity,expected_manifest_sha256=PARENT_MANIFEST)
    arrays={key:value.copy() for key,value in loaded['arrays'].items()};child=copy.deepcopy(loaded['metadata'])
    out.mkdir(parents=True,exist_ok=False)
    schedule=json.loads((parent/'SCHEDULE.json').read_text())
    require(schedule['target_time_s']==TARGET and schedule['hard_events_s']==metadata['restart_binding']['hard_events_s'],'ORIGINAL_SCHEDULE')
    durable_json(out/'SCHEDULE.json',schedule);durable_json(out/'CONTROLS.json',controls)
    output_copy=copy_initial_output(parent/'RUN',out/'RUN',metadata['production_output_records'])
    durable_json(out/'OUTPUT_COPY_RECEIPT.json',output_copy)
    deps=copy.deepcopy(old_deps)
    extra=[Path(__file__),HERE/'run_full_history_chunk_v3.py',candidate,begin_path,failure_path,result_path,
        parent/'RUN/ATTEMPTS/attempt-00000066/MAP_01_INPUT.npz',parent/'RUN/ATTEMPTS/attempt-00000066/MAP_01_REQUEST.json',
        parent/'RUN/INITIAL_OUTPUT_DONE.json',out/'SCHEDULE.json',out/'CONTROLS.json',out/'OUTPUT_COPY_RECEIPT.json',*extra_dependency_paths]
    for p in extra:
        p=Path(p)
        if not p.is_absolute():p=repo/p
        p=p.resolve(strict=True);require(p.is_relative_to(repo),'EXTRA_DEPENDENCY_OUTSIDE_REPO')
        key='dependency:'+str(p.relative_to(repo));digest=sha(p)
        require(key not in deps or deps[key]==digest,'OLD_DEPENDENCY_REPLACEMENT')
        deps[key]=digest
    transition=dict(schema='rei.c12.opacity_failure_identity_transition.v1',parent_run=str(PARENT_REL),parent_generation=59,
        parent_manifest_sha256=PARENT_MANIFEST,parent_identity=identity,parent_cursor=metadata['adaptive_cursor'],
        parent_failed_attempt=66,parent_failed_begin_sha256=sha(begin_path),parent_failed_record_sha256=sha(failure_path),
        old_failure_status_preserved=True,allocation=allocation,source_module_path=str(SOURCE_REL),source_sha256=SOURCE_SHA,
        absorption_module_path=str(candidate.relative_to(repo)),absorption_sha256=sha(candidate),
        absorption_semantics='REVIEW_REQUIRED_SAME_PROVIDER_SAME_TOLERANCE_NEW_POSITIVE_QUADRATURE_ARITHMETIC',
        physical_prefix_copied_without_maps=True,physics_and_criteria_changed=False,
        initial_h0_replayed=False,output_copy_receipt=output_copy,native_calls=0,completed_scientific_checks_replayed=0,scientific_admission=False)
    tp=out/'OPACITY_IDENTITY_TRANSITION.json';durable_json(tp,transition)
    deps['dependency:'+str(tp.relative_to(repo))]=sha(tp)
    binding=copy.deepcopy(metadata['restart_binding']);binding['controls']=controls;binding['dependency_closure']=deps
    child['restart_binding']=binding;child['restart_binding_sha256']=canonical_sha(binding)
    child['production_opacity_transition']=dict(path=str(tp.relative_to(repo)),sha256=sha(tp),allocation=allocation,
        absorption_module_path=str(candidate.relative_to(repo)),absorption_sha256=sha(candidate))
    preservation=assert_preserved(loaded['arrays'],loaded['metadata'],arrays,child)
    new_identity=opacity_child_identity(identity,binding)
    saved=write_adaptive_checkpoint(out/'CHECKPOINTS',59,arrays,child,new_identity)
    bundle=dict(schema='rei.c12.opacity_failure_transition_result.v1',checkpoint_directory=str(out/'CHECKPOINTS'),generation=59,
        manifest_sha256=sha(saved/'manifest.json'),generation_path=str(saved),identity=new_identity,controls=controls,
        cursor=metadata['adaptive_cursor'],target_time_s=TARGET,dependency_closure=deps,parent_dependency_count=68,
        schedule_path=str(out/'SCHEDULE.json'),source_module_path=str(SOURCE_REL),absorption_module_path=str(candidate.relative_to(repo)),
        absorption_sha256=sha(candidate),transition_path=str(tp),allocation=allocation,preservation=preservation,output_copy=output_copy,
        native_calls=0,scientific_admission=False)
    durable_json(out/'TRANSITION_RESULT.json',bundle)
    return bundle
