"""Fail-closed, scalar-only recovery of one original whole-batch timeout."""
import copy
import hashlib
import json
import math
from pathlib import Path
import zipfile

from mpi_batch import atomic_create, code_identity, json_bytes, read_manifest, SAFE_TASK_ID

SCHEMA = 'bass-c2d-partial-batch-index-v1'
RECOVERED = 'WHOLE_BATCH_TIMEOUT_RECOVERED_WITHIN_ORIGINAL_BUDGET'
CHANGED_ANALYSIS_ALLOWED = {'code/analyze_states.py', 'code/analyze_all.py'}
CHANGED_EXECUTION_BOUNDARY_ALLOWED = {'code/mpi_batch.py','code/launch_ncp.py'}
NEW_HELPERS_ALLOWED = {'code/recovery_support.py', 'code/prepare_recovery.py'}
REGISTERED_BOUNDARY_PATCH_SHA256 = {
    'code/mpi_batch.py':'52e3d2749bf544a3976d83b1c098d358814e1d6b8f3c910cae4562326bec3928',
    'code/launch_ncp.py':'2026e1d3bfa61dd3c30e179f3101780ceadc29a7cc86fbce5059023dd11ec540'}


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(root, relative, exists=True):
    root = Path(root).resolve()
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('PATH_OUTSIDE_PACKAGE')
    path = root/relative
    if any(p.is_symlink() for p in (path, *path.parents) if p != root and root in p.parents):
        raise ValueError('SYMLINK_PATH')
    if not path.resolve().is_relative_to(root) or (exists and not path.exists()):
        raise ValueError('PATH_OUTSIDE_OR_MISSING')
    return path


def binding(root, path):
    path = Path(path)
    safe(root, path.relative_to(root))
    if not path.is_file():
        raise ValueError('EXPECTED_REGULAR_FILE')
    return {'path':str(path.relative_to(root)), 'bytes':path.stat().st_size, 'sha256':sha(path)}


def verify_binding(root, item):
    path = safe(root, item['path'])
    if binding(root, path) != item:
        raise ValueError('BOUND_FILE_CHANGED: '+item['path'])
    return path


def _code_record(run):
    if hashlib.sha256(json_bytes(run['code']['files'])).hexdigest() != run['code']['sha256']:
        raise ValueError('RUN_CODE_IDENTITY_INCONSISTENT')


def validate_pass(root, folder, task, run, execution):
    """Validate an actual successful final execution; never synthesize PASS."""
    if (execution.get('status') != 'WORKER_RESULT_PASS' or execution.get('returncode') != 0
            or execution.get('task_id') != task['task_id']
            or execution.get('code_sha256') != run['code']['sha256']
            or execution.get('selected_backend') != run['selected_backend']):
        raise ValueError('EXECUTION_NOT_VALID_PASS')
    for name in ('TASK_INPUT.json','RESULT.json','DATA.json'):
        path = safe(root, (folder/name).relative_to(root))
        meta = execution['artifacts'][name]
        if path.stat().st_size != meta['bytes'] or sha(path) != meta['sha256']:
            raise ValueError('EXECUTION_ARTIFACT_CHANGED: '+name)
    result, data = read(folder/'RESULT.json'), read(folder/'DATA.json')
    input_sha = sha(folder/'TASK_INPUT.json')
    if (read(folder/'TASK_INPUT.json') != task or result['status'] != 'PASS'
            or result['task_id'] != task['task_id'] or data['task_id'] != task['task_id']
            or result['parameters'] != task['parameters'] or data['parameters'] != task['parameters']
            or result['input_sha256'] != input_sha or execution['task_sha256'] != input_sha
            or result['code_identity_sha256'] != run['code']['sha256']
            or result['selected_backend'] != run['selected_backend'] or result['backend'] != run['backend']
            or result['evidence_file'] != 'DATA.json' or result['evidence_sha256'] != sha(folder/'DATA.json')
            or result['evidence_bytes'] != (folder/'DATA.json').stat().st_size
            or result['new_eigenstates'] != data['new_eigenstates']
            or execution['worker_result_sha256'] != sha(folder/'RESULT.json')):
        raise ValueError('PASS_BINDING_MISMATCH')
    if 'state_file' in result:
        if result['state_file'] != 'STATE.npz':
            raise ValueError('STATE_NAME_INVALID')
        path = safe(root, (folder/'STATE.npz').relative_to(root))
        if (sha(path) != result['state_sha256'] or path.stat().st_size != result['state_bytes']
                or execution['artifacts']['STATE.npz'] != {'sha256':sha(path),'bytes':path.stat().st_size}):
            raise ValueError('STATE_BINDING_MISMATCH')
    return result


def derive_partial_index(root, batch_relative):
    root = Path(root).resolve(); batch = safe(root, batch_relative)
    if (batch/'BATCH_SUMMARY.json').exists():
        raise ValueError('ORIGINAL_BATCH_ALREADY_HAS_SUMMARY')
    launch_path = batch.with_name(batch.name+'_LAUNCH.json')
    launch, run = read(launch_path), read(batch/'RUN_IDENTITY.json')
    manifest, manifest_sha, _ = read_manifest(batch/'MANIFEST_INPUT.json')
    _code_record(run)
    if (launch.get('returncode') != 124 or launch.get('timed_out') is not True
            or launch.get('cleanup_complete') is not True or launch.get('source_unchanged') is not True
            or launch.get('preflight_passed') is not True or launch.get('wall_cap_seconds') != 1800
            or launch['source_identity_before'] != run['code']
            or manifest_sha != run['manifest_sha256'] or manifest_sha != launch['manifest_sha256']):
        raise ValueError('NOT_ELIGIBLE_ORIGINAL_WHOLE_BATCH_TIMEOUT')
    if sha(root/'CONTRACT.json') != run['code']['files']['CONTRACT.json']:
        raise ValueError('CONTRACT_CHANGED')
    rows = []
    for task in manifest['tasks']:
        folder = batch/task['task_id']
        row = {'task_id':task['task_id'], 'parameters_sha256':hashlib.sha256(json_bytes(task['parameters'])).hexdigest(),
               'started':folder.exists(), 'artifacts':{}}
        if not folder.exists():
            row['classification'] = 'NOT_STARTED'
        else:
            safe(root, folder.relative_to(root))
            if not folder.is_dir():
                raise ValueError('TASK_DIRECTORY_INVALID')
            for path in sorted(folder.iterdir()):
                if path.is_symlink() or not path.is_file():
                    raise ValueError('UNEXPECTED_TASK_ARTIFACT')
                row['artifacts'][path.name] = binding(root, path)
            if (folder/'TASK_INPUT.json').exists() and read(folder/'TASK_INPUT.json') != task:
                raise ValueError('TASK_INPUT_CHANGED')
            if (folder/'TASK_EXECUTION.json').exists():
                execution = read(folder/'TASK_EXECUTION.json')
                if execution.get('status') == 'WORKER_RESULT_PASS':
                    validate_pass(root, folder, task, run, execution)
                    row['classification'] = 'COMPLETED_VALIDATED'
                else:
                    row['classification'] = 'FINAL_EXECUTION_FAILED_REQUIRES_CLASSIFICATION'
                    row['failure_class'] = execution.get('failure_class')
            elif (folder/'RESULT.json').exists():
                row['classification'] = 'RESULT_WITHOUT_VALID_PASS_REQUIRES_CLASSIFICATION'
            else:
                row['classification'] = 'INTERRUPTED_WITHOUT_RESULT'
        rows.append(row)
    return {'schema':SCHEMA, 'status':'WHOLE_BATCH_TIMEOUT_PARTIAL_EVIDENCE_ONLY',
            'batch':str(batch.relative_to(root)), 'manifest_sha256':manifest_sha,
            'code_sha256':run['code']['sha256'], 'bindings':{
                'manifest':binding(root,batch/'MANIFEST_INPUT.json'),
                'run':binding(root,batch/'RUN_IDENTITY.json'), 'launch':binding(root,launch_path)},
            'tasks':rows, 'scientific_acceptance':'NOT_INFERRED_FROM_EXECUTION',
            'original_batch_summary_fabricated':False}


def load_partial_batch(root, batch):
    """Collector view from a verified sidecar; original summaries stay absent."""
    root=Path(root).resolve();batch=Path(batch)
    index=read(batch/'PARTIAL_BATCH_INDEX.json')
    if index != derive_partial_index(root,batch.relative_to(root)):
        raise ValueError('PARTIAL_INDEX_STALE_OR_CHANGED')
    entries=[]
    for row in index['tasks']:
        if row['classification']=='COMPLETED_VALIDATED':
            entries.append(read(verify_binding(root,row['artifacts']['TASK_EXECUTION.json'])))
        else:
            entries.append({'task_id':row['task_id'],'status':row['classification']})
    return {'code_sha256':index['code_sha256'],'manifest_sha256':index['manifest_sha256'],
            'tasks':entries,'status':'DERIVED_PARTIAL_INDEX_VIEW_NOT_ORIGINAL_SUMMARY'}


def timeout_kill_classification(root,batch_relative,task_ids):
    """Verify an explicitly selected subset; never rewrite original classes."""
    root=Path(root).resolve();batch=safe(root,batch_relative)
    index=derive_partial_index(root,batch_relative)
    index_path=batch/'PARTIAL_BATCH_INDEX.json'
    if read(index_path)!=index:raise ValueError('PARTIAL_INDEX_CHANGED')
    if not task_ids or len(task_ids)!=len(set(task_ids)):
        raise ValueError('EXPLICIT_UNIQUE_TIMEOUT_KILL_SELECTION_REQUIRED')
    rows={row['task_id']:row for row in index['tasks']}
    manifest,_,_=read_manifest(batch/'MANIFEST_INPUT.json')
    tasks={task['task_id']:task for task in manifest['tasks']}
    run=read(batch/'RUN_IDENTITY.json');launch_path=batch.with_name(batch.name+'_LAUNCH.json')
    launch=read(launch_path)
    guard_sha=run['code']['files'].get('code/process_guard.py')
    if not isinstance(guard_sha,str) or len(guard_sha)!=64:
        raise ValueError('CLEANUP_GUARD_SOURCE_IDENTITY_MISSING')
    if any(launch.get('memory_events_delta',{}).get(key)!=0 for key in ('oom','oom_kill')):
        raise ValueError('OOM_CAUSE_NOT_EXCLUDED')
    findings=[]
    for task_id in task_ids:
        if task_id not in rows or rows[task_id]['classification']!='FINAL_EXECUTION_FAILED_REQUIRES_CLASSIFICATION':
            raise ValueError('TASK_NOT_AN_EXPLICIT_UNCLASSIFIED_FINAL_FAILURE')
        folder=batch/task_id;execution=read(folder/'TASK_EXECUTION.json')
        if (folder/'RESULT.json').exists() or (folder/'DATA.json').exists():
            raise ValueError('UNVALIDATED_RESULT_OR_DATA_PRESENT')
        if (execution.get('status')!='FAILED' or execution.get('failure_class')!='WORKER_NONZERO_EXIT'
                or execution.get('returncode')!=-9 or execution.get('task_id')!=task_id
                or execution.get('code_sha256')!=run['code']['sha256']
                or execution.get('selected_backend')!=run['selected_backend']
                or execution.get('process_cleanup',{}).get('status')!='NO_LIVE_OWNED_MEMBERS'):
            raise ValueError('FAILURE_IS_NOT_CLEANED_SIGNAL9_WORKER_EXIT')
        for name,meta in execution['artifacts'].items():
            if Path(name).name!=name:raise ValueError('UNSAFE_ARTIFACT_NAME')
            path=safe(root,(folder/name).relative_to(root))
            if path.stat().st_size!=meta['bytes'] or sha(path)!=meta['sha256']:
                raise ValueError('FAILED_EXECUTION_ARTIFACT_CHANGED')
        if (read(folder/'TASK_INPUT.json')!=tasks[task_id]
                or execution['task_sha256']!=sha(folder/'TASK_INPUT.json')
                or any((folder/name).stat().st_size!=0 for name in ('STDOUT.txt','STDERR.txt'))):
            raise ValueError('FAILED_TASK_INPUT_OR_LOGS_NOT_EXPECTED')
        owned=read(folder/'OWNED_PROCESS.json');leader=owned['leader']
        if (owned.get('task_id')!=task_id or owned.get('batch_owner_token')!=launch.get('batch_owner_token')
                or not owned.get('task_owner_token') or not owned.get('boot_id')
                or not isinstance(leader.get('pid_namespace_inode'),int) or leader['pid_namespace_inode']<=0):
            raise ValueError('TIMEOUT_KILL_OWNERSHIP_MISMATCH')
        matches=[]
        for stage in launch['owned_process_cleanup']:
            if stage['stage'] not in ('tasks_after_term','tasks_final'):continue
            for report in stage.get('reports',[]):
                if report.get('task_id')!=task_id or report.get('status')!='NO_LIVE_OWNED_MEMBERS' or report.get('remaining')!=[]:continue
                for signal in report.get('signals',[]):
                    if (signal.get('signal')==9 and signal.get('pid')==leader['pid']
                            and signal.get('start_time_ticks')==leader['start_time_ticks']):
                        matches.append({'stage':stage['stage'],'signal':signal})
        if len(matches)!=1:raise ValueError('NO_UNIQUE_BOUND_WHOLE_BATCH_CLEANUP_SIGKILL')
        findings.append({'task_id':task_id,
             'classification':'MANUALLY_VERIFIED_WHOLE_BATCH_TIMEOUT_KILLED',
             'original_classification':rows[task_id]['classification'],
             'task_execution':binding(root,folder/'TASK_EXECUTION.json'),
             'ownership':binding(root,folder/'OWNED_PROCESS.json'),
             'task_input':binding(root,folder/'TASK_INPUT.json'),
             'batch_owner_token':owned['batch_owner_token'],
             'task_owner_token':owned['task_owner_token'],'boot_id':owned['boot_id'],
             'namespace_pid':leader['pid'],'pid_namespace_inode':leader['pid_namespace_inode'],
             'procfs_pid':leader['procfs_pid'],'start_time_ticks':leader['start_time_ticks'],
             'cleanup_signal':matches[0],
             'namespace_evidence':'Recorded ownership namespace and PID/startticks; pinned cleanup guard validates ownership before signaling.'})
    return {'schema':'bass-c2d-explicit-timeout-kill-classification-v1',
            'selection_policy':'EXPLICIT_TASK_IDS_ONLY; other failures remain inadmissible',
            'partial_index':binding(root,index_path),'launch':binding(root,launch_path),
            'cleanup_guard_source_sha256':guard_sha,
            'tasks':findings,'original_records_rewritten':False,
            'scientific_failure_inferred':False}


def verify_timeout_classification(root,batch_relative,classification_relative):
    if classification_relative is None:return set(),None
    path=safe(root,classification_relative);document=read(path)
    ids=[row['task_id'] for row in document['tasks']]
    if document!=timeout_kill_classification(root,batch_relative,ids):
        raise ValueError('TIMEOUT_CLASSIFICATION_EVIDENCE_CHANGED')
    return set(ids),binding(root,path)


def verify_source_snapshot(root, run, snapshot_relative):
    path=safe(root,snapshot_relative)
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):
            raise ValueError('DUPLICATE_SOURCE_SNAPSHOT_MEMBER')
        for name,expected in run['code']['files'].items():
            if hashlib.sha256(archive.read(name)).hexdigest()!=expected:
                raise ValueError('SOURCE_SNAPSHOT_MISMATCH: '+name)
    return binding(root,path)


def verify_unchanged_physics(root, run, recovery_manifest_relative):
    current=code_identity(root)
    allowed_extra=NEW_HELPERS_ALLOWED|{str(Path(recovery_manifest_relative))}
    changed=[]
    for name,old_sha in run['code']['files'].items():
        if current['files'].get(name)!=old_sha:
            if name not in CHANGED_ANALYSIS_ALLOWED|CHANGED_EXECUTION_BOUNDARY_ALLOWED:
                raise ValueError('FROZEN_SCIENTIFIC_SOURCE_CHANGED: '+name)
            if name in CHANGED_EXECUTION_BOUNDARY_ALLOWED and current['files'][name]!=REGISTERED_BOUNDARY_PATCH_SHA256[name]:
                raise ValueError('UNREGISTERED_EXECUTION_BOUNDARY_PATCH: '+name)
            changed.append(name)
    extras=set(current['files'])-set(run['code']['files'])
    if not extras<=allowed_extra:
        raise ValueError('UNREGISTERED_NEW_SOURCE_FILES: '+str(sorted(extras-allowed_extra)))
    return current, sorted(changed), sorted(extras)


def inventory_attempts(root):
    """Count any task directory as started, including failed/partial attempts."""
    actual={};upper={};launches=[];started=[]
    for batch in sorted((root/'evidence').glob('*MPI')):
        if not (batch/'RUN_IDENTITY.json').exists():
            continue
        safe(root,batch.relative_to(root))
        launch_path=batch.with_name(batch.name+'_LAUNCH.json')
        if not launch_path.exists():
            raise ValueError('OTHER_BATCH_STILL_RUNNING_OR_UNRESOLVED')
        launch=read(launch_path)
        if launch.get('cleanup_complete') is not True or launch.get('source_unchanged') is not True:
            raise ValueError('PRIOR_BATCH_CLEANUP_OR_SOURCE_UNRESOLVED')
        manifest,_,_=read_manifest(batch/'MANIFEST_INPUT.json')
        for task in manifest['tasks']:
            kind=task['parameters']['kind'];upper[kind]=upper.get(kind,0)+1
            if (batch/task['task_id']).exists():
                actual[kind]=actual.get(kind,0)+1
                started.append({'batch':str(batch.relative_to(root)),'task_id':task['task_id'],'kind':kind})
    # Conservatively charge every recorded launcher, even a failed preflight.
    for path in sorted((root/'evidence').glob('*_LAUNCH.json')):
        launch=read(path);elapsed=launch['elapsed_seconds']
        if isinstance(elapsed,bool) or not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed) or elapsed<0:
            raise ValueError('INVALID_LAUNCH_WALL')
        launches.append({'binding':binding(root,path),'elapsed_seconds':elapsed})
    return {'actual_started_by_kind':actual,'manifest_upper_bound_by_kind':upper,
            'started_tasks':started,'launches':launches,
            'charged_wall_seconds':sum(x['elapsed_seconds'] for x in launches)}


def _budget_check(contract, counts):
    limits=contract['operational_limits']
    pairs=counts.get('prolate',0)+counts.get('bridge',0)
    checks={'parity':counts.get('parity',0)<=limits['parity_evaluations_max'],
            'overlap':counts.get('overlap',0)<=limits['overlap_edge_orders_max'],
            'operator_refinement':counts.get('operator_refinement',0)<=limits['operator_refinement_tasks_max'],
            'prolate_pairs':pairs<=limits.get('new_prolate_pairs_max',limits['new_eigenstates_total_max']//2),
            'spherical_selected_states':counts.get('sphere',0)<=limits.get('new_spherical_eigenstates_max',limits['new_eigenstates_total_max']),
            'selected_states':2*pairs+counts.get('sphere',0)<=limits['new_eigenstates_total_max']}
    if not all(checks.values()):
        raise ValueError('EXECUTION_ATTEMPT_BUDGET_EXCEEDED: '+str(checks))
    return checks


def make_recovery_plan(root,batch_relative,manifest_relative,recovery_batch_relative,
                       snapshot_relative='provenance/FOLLOWUP_CODE_SNAPSHOT.zip',margin_seconds=30,
                       classification_relative=None):
    root=Path(root).resolve();batch=safe(root,batch_relative)
    index=derive_partial_index(root,batch_relative)
    run=read(batch/'RUN_IDENTITY.json');original,_,_=read_manifest(batch/'MANIFEST_INPUT.json')
    snapshot=verify_source_snapshot(root,run,snapshot_relative)
    classified,classification_binding=verify_timeout_classification(root,batch_relative,classification_relative)
    if any(r['classification'] not in ('COMPLETED_VALIDATED','NOT_STARTED','INTERRUPTED_WITHOUT_RESULT')
           and r['task_id'] not in classified for r in index['tasks']):
        raise ValueError('MANUAL_CLASSIFICATION_REQUIRED_NO_AUTOMATIC_REPLAY')
    tasks=[];mapping=[]
    for row,task in zip(index['tasks'],original['tasks']):
        if row['classification']=='COMPLETED_VALIDATED':continue
        if task['parameters']['kind'] not in ('overlap','sphere_observe','parity'):
            raise ValueError('RECOVERY_WOULD_ADD_EIGENSTATE_OR_UNAUTHORIZED_TASK')
        new_id='rec_'+task['task_id']
        if not SAFE_TASK_ID.fullmatch(new_id):raise ValueError('RECOVERY_TASK_ID_TOO_LONG')
        tasks.append({'task_id':new_id,'parameters':copy.deepcopy(task['parameters'])})
        mapping.append({'original_task_id':task['task_id'],'recovery_task_id':new_id,
                        'original_classification':row['classification'],'parameters_sha256':row['parameters_sha256']})
    if not tasks:raise ValueError('NO_RECOVERY_WORK_NEEDED')
    inv=inventory_attempts(root);limits=read(root/'CONTRACT.json')['operational_limits']
    contract=read(root/'CONTRACT.json');remaining=limits['total_active_science_wall_seconds']-inv['charged_wall_seconds']
    if isinstance(margin_seconds,bool) or margin_seconds<5:raise ValueError('CLEANUP_MARGIN_TOO_SMALL')
    cap=min(1800,math.floor(remaining-margin_seconds))
    if cap<1:raise ValueError('NO_REMAINING_ORIGINAL_WALL_BUDGET')
    predicted=dict(inv['actual_started_by_kind']);upper=dict(inv['manifest_upper_bound_by_kind'])
    for task in tasks:
        kind=task['parameters']['kind'];predicted[kind]=predicted.get(kind,0)+1;upper[kind]=upper.get(kind,0)+1
    gates=_budget_check(contract,predicted)
    recovery={'schema':1,'tasks':tasks,'limits':copy.deepcopy(original['limits'])}
    recovery['limits']['task_wall_seconds']=min(300,limits['task_wall_seconds'],cap)
    target=safe(root,manifest_relative,exists=False);out=safe(root,recovery_batch_relative,exists=False)
    if target.exists() or any(p.exists() for p in (out,out.with_name(out.name+'_LAUNCH.json'),out.with_name(out.name+'_LOG.txt'))):
        raise FileExistsError('RECOVERY_TARGET_ALREADY_EXISTS')
    current,changed,extra=verify_unchanged_physics(root,run,manifest_relative)
    plan={'schema':'bass-c2d-recovery-plan-v1','status':'READY_FOR_FRESH_RESOURCE_PREFLIGHT',
          'partial_index':index,'original_source_snapshot':snapshot,'original_run_binding':binding(root,batch/'RUN_IDENTITY.json'),
          'timeout_kill_classification':classification_binding,
          'recovery_manifest_path':str(target.relative_to(root)),
          'recovery_manifest_sha256':hashlib.sha256(json_bytes(recovery)).hexdigest(),
          'recovery_batch':str(out.relative_to(root)),'task_mapping':mapping,
          'validated_completed_replays':0,'new_eigenstates_requested':0,
          'prior_attempt_inventory':inv,'predicted_actual_attempts_after_recovery':predicted,
          'manifest_upper_bound_including_recovery':upper,'attempt_budget_gates':gates,
          'wall_budget':{'original_total_seconds':limits['total_active_science_wall_seconds'],
             'charged_prior_seconds':inv['charged_wall_seconds'],'remaining_before_margin_seconds':remaining,
             'cleanup_margin_seconds':margin_seconds,'recovery_wall_cap_seconds':cap},
          'allowed_analysis_changes':changed,'new_helper_files':extra,
          'scientific_acceptance':'SEPARATE_GATES_REQUIRED; full_C2_closed=false'}
    return index,recovery,plan


def finalize_plan_source(root,plan):
    run=read(verify_binding(root,plan['original_run_binding']))
    current,changed,extra=verify_unchanged_physics(root,run,plan['recovery_manifest_path'])
    plan=copy.deepcopy(plan);plan['source_identity_for_recovery']=current
    plan['allowed_analysis_changes']=changed;plan['new_helper_files']=extra
    return plan


def verify_recovered(root,plan_relative):
    root=Path(root).resolve();plan_path=safe(root,plan_relative);plan=read(plan_path)
    original_batch=safe(root,plan['partial_index']['batch'])
    if read(original_batch/'PARTIAL_BATCH_INDEX.json')!=plan['partial_index'] or derive_partial_index(root,original_batch.relative_to(root))!=plan['partial_index']:
        raise ValueError('ORIGINAL_PARTIAL_EVIDENCE_CHANGED')
    classification=plan.get('timeout_kill_classification')
    if classification is not None:verify_binding(root,classification)
    classified,_=verify_timeout_classification(root,original_batch.relative_to(root),
                                               None if classification is None else classification['path'])
    if any(row['classification'] not in ('COMPLETED_VALIDATED','NOT_STARTED','INTERRUPTED_WITHOUT_RESULT')
           and row['task_id'] not in classified for row in plan['partial_index']['tasks']):
        raise ValueError('UNADMITTED_ORIGINAL_FAILURE_IN_RECOVERY_PLAN')
    prior_wall=0.0
    for item in plan['prior_attempt_inventory']['launches']:
        actual=read(verify_binding(root,item['binding']))['elapsed_seconds']
        if actual!=item['elapsed_seconds']:
            raise ValueError('PRIOR_WALL_COPY_DIFFERS_FROM_BOUND_RECEIPT')
        prior_wall+=actual
    original_run=read(verify_binding(root,plan['original_run_binding']))
    verify_binding(root,plan['original_source_snapshot'])
    original_total=read(root/'CONTRACT.json')['operational_limits']['total_active_science_wall_seconds']
    margin=plan['wall_budget']['cleanup_margin_seconds']
    if (plan['wall_budget']['original_total_seconds']!=original_total
            or plan['wall_budget']['charged_prior_seconds']!=prior_wall or margin<5
            or plan['wall_budget']['recovery_wall_cap_seconds']!=min(1800,math.floor(original_total-prior_wall-margin))
            or plan['wall_budget']['recovery_wall_cap_seconds']<1):
        raise ValueError('RECOVERY_WALL_PLAN_NOT_ORIGINAL_BUDGET')
    current,_,_=verify_unchanged_physics(root,original_run,plan['recovery_manifest_path'])
    if current!=plan['source_identity_for_recovery']:raise ValueError('RECOVERY_SOURCE_IDENTITY_CHANGED')
    batch=safe(root,plan['recovery_batch']);launch_path=batch.with_name(batch.name+'_LAUNCH.json')
    launch=read(launch_path);run=read(batch/'RUN_IDENTITY.json');summary=read(batch/'BATCH_SUMMARY.json')
    manifest,manifest_sha,_=read_manifest(batch/'MANIFEST_INPUT.json')
    if (manifest_sha!=plan['recovery_manifest_sha256'] or sha(root/plan['recovery_manifest_path'])!=manifest_sha
            or launch.get('returncode')!=0 or launch.get('timed_out') is not False
            or launch.get('cleanup_complete') is not True or launch.get('source_unchanged') is not True
            or launch.get('preflight_passed') is not True
            or launch['wall_cap_seconds']!=plan['wall_budget']['recovery_wall_cap_seconds']
            or launch['source_identity_before']!=plan['source_identity_for_recovery']
            or run['code']!=plan['source_identity_for_recovery'] or run['manifest_sha256']!=manifest_sha
            or run['selected_backend']!=original_run['selected_backend'] or run['backend']!=original_run['backend']
            or launch['manifest_sha256']!=manifest_sha or summary['manifest_sha256']!=manifest_sha
            or summary['code_sha256']!=run['code']['sha256']):
        raise ValueError('RECOVERY_EXECUTION_NOT_VALID_SUCCESS')
    original,_hash,_raw=read_manifest(original_batch/'MANIFEST_INPUT.json')
    originals={t['task_id']:t for t in original['tasks']}
    exact_mapping=[{'original_task_id':row['task_id'],'recovery_task_id':'rec_'+row['task_id'],
                    'original_classification':row['classification'],'parameters_sha256':row['parameters_sha256']}
                   for row in plan['partial_index']['tasks'] if row['classification']!='COMPLETED_VALIDATED']
    if plan['task_mapping']!=exact_mapping or plan['validated_completed_replays']!=0 or plan['new_eigenstates_requested']!=0:
        raise ValueError('RECOVERY_PLAN_MAPPING_CHANGED')
    expected=[{'task_id':m['recovery_task_id'],'parameters':originals[m['original_task_id']]['parameters']} for m in plan['task_mapping']]
    if manifest['tasks']!=expected or [x['task_id'] for x in summary['tasks']]!=[t['task_id'] for t in expected]:
        raise ValueError('RECOVERY_TASKS_CHANGED_OR_REPLAYED')
    for task,execution in zip(expected,summary['tasks']):
        taskdir=batch/task['task_id']
        if read(taskdir/'TASK_EXECUTION.json')!=execution:raise ValueError('RECOVERY_SUMMARY_EXECUTION_CHANGED')
        validate_pass(root,taskdir,task,run,execution)
    inv=inventory_attempts(root)
    prior_paths={item['binding']['path'] for item in plan['prior_attempt_inventory']['launches']}
    actual_prior_paths={item['binding']['path'] for item in inv['launches']} - {str(launch_path.relative_to(root))}
    if len(prior_paths)!=len(plan['prior_attempt_inventory']['launches']) or prior_paths!=actual_prior_paths:
        raise ValueError('PRIOR_LAUNCH_SET_INCOMPLETE_OR_DUPLICATED')
    _budget_check(read(root/'CONTRACT.json'),inv['actual_started_by_kind'])
    if inv['charged_wall_seconds']>original_total:
        raise ValueError('ORIGINAL_TOTAL_WALL_BUDGET_EXCEEDED')
    completed=sum(r['classification']=='COMPLETED_VALIDATED' for r in plan['partial_index']['tasks'])
    if completed+len(expected)!=len(original['tasks']):raise ValueError('ORIGINAL_TASK_COVERAGE_INCOMPLETE')
    return {'schema':'bass-c2d-recovery-verification-v1','status':RECOVERED,
            'plan':binding(root,plan_path),'recovery_launch':binding(root,launch_path),
            'original_task_count':len(original['tasks']),'original_validated_completed':completed,
            'recovery_task_count':len(expected),'completed_task_replays':0,'new_eigenstates_requested':0,
            'final_attempt_inventory':inv,'scientific_acceptance':'NOT_INFERRED; scientific gates remain separate',
            'full_C2_closed':False}
