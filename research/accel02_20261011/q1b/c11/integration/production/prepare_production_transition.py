"""Declared PILOT02 gen3 -> whole-history child binding, executing zero maps.

prepare_transition(repo, output_root, schedule, extra_dependency_paths=())
returns the JSON-serializable TRANSITION_RESULT.json bundle. output_root must
be a new directory inside repo. schedule is a mapping or JSON path with exact
output_epochs_s, shared65_indices, target_time_s and hard_events_s. Root owns
materialization of the operational child after review. All original dependency
bytes are verified before importing any provider/checkpoint code or loading NPZ.
"""
from __future__ import annotations
import copy,hashlib,importlib,json,math,os,sys
from pathlib import Path
from production_control import production_controls,assert_runtime_only_controls,TARGET_TIME_S
C11_REL=Path('research/accel02_20261011/q1b/c11')
PARENT_REL=C11_REL/'integration/evidence/PILOT02/CHECKPOINTS/gen-00000003'
PARENT_MANIFEST='6df321273a05b681ea29a396017029a10be5968319c280591b2a3254d82d1c73'
PARENT_IDENTITY={
 'binary':'e29245acfee5be4d43c27935e2abd212d578685efa70dffbeffa8f96dd3e4b6f',
 'control':'266504b25197e2309e04ceb57cc147c22558f9f1430d86823f14c9e5b3bab494',
 'grid':'409a584cc4ee863dee97cd5fba60486abfd50be63a9c0955a258aeae755bffa0',
 'physical_validator':'e6c5db3d68ce325f6a7db1264b8a214e0d595c633672955aa1aad3f58ce2fa66',
 'physics_contract':'bb1aeed3926d441f981ce70720a52432b5b590557588846e977d25891e4bd838',
 'source':'7e6f51921a082a66490c8e7b9bc5a8cf5c7b9538c5f67a9ca9cd5b2d3e327bae'}
PHYSICAL_ARRAY_KEYS=('state','scales','counter_origins','prefix_clock','prefix_state','accepted_min','accepted_max')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)

def write_json(path,value):
    path=Path(path)
    with path.open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def verify_parent_payload(parent,expected_manifest=PARENT_MANIFEST):
    parent=Path(parent)
    require(parent.is_dir() and not parent.is_symlink(),'PARENT_DIRECTORY')
    require(sha(parent/'manifest.json')==expected_manifest,'PARENT_MANIFEST_IDENTITY')
    manifest=json.loads((parent/'manifest.json').read_text())
    require(set(manifest['files'])=={'arrays.npz','metadata.json','identity.json'},'PARENT_MANIFEST_FILES')
    require({p.name for p in parent.iterdir()}==set(manifest['files'])|{'manifest.json'},'PARENT_MEMBER_SET')
    for name,record in manifest['files'].items():
        p=parent/name
        require(p.is_file() and not p.is_symlink() and p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],'PARENT_MEMBER:'+name)
    return manifest

def _relative(repo,path):
    p=Path(path)
    if not p.is_absolute():p=repo/p
    p=p.resolve(strict=True)
    try:relative=p.relative_to(repo)
    except ValueError:raise ValueError('DEPENDENCY_OUTSIDE_REPO:'+str(p)) from None
    require(p.is_file(),'DEPENDENCY_NOT_FILE:'+str(relative))
    return relative

def verify_parent_before_import(repo):
    """Byte provenance preflight uses only stdlib; no arrays/provider execution."""
    repo=Path(repo).resolve(strict=True);parent=repo/PARENT_REL
    manifest=verify_parent_payload(parent)
    identity=json.loads((parent/'identity.json').read_text())
    require(identity==PARENT_IDENTITY,'PARENT_IDENTITY')
    metadata=json.loads((parent/'metadata.json').read_text())
    binding=metadata['restart_binding'];closure=binding['dependency_closure']
    require(len(closure)==41,'PARENT_DEPENDENCY_COUNT')
    require(canonical_sha(binding)==PARENT_IDENTITY['control'],'PARENT_CONTROL_IDENTITY')
    for key,expected in closure.items():
        require(key.startswith('dependency:'),'PARENT_DEPENDENCY_KEY')
        relative=Path(key.removeprefix('dependency:'))
        require(not relative.is_absolute() and '..' not in relative.parts,'PARENT_DEPENDENCY_PATH')
        require(_relative(repo,relative)==relative and sha(repo/relative)==expected,'PARENT_DEPENDENCY:'+str(relative))
    require(metadata['adaptive_cursor']['accepted_clock_s']==4539815858.150909,'PARENT_CLOCK')
    return dict(manifest=manifest,identity=identity,metadata=metadata,dependency_closure=closure)

def assert_prefix_preserved(parent_arrays,parent_metadata,child_arrays,child_metadata):
    """Byte-level physical equality, independently of snapshot validator claims."""
    for key in PHYSICAL_ARRAY_KEYS:
        a,b=parent_arrays[key],child_arrays[key]
        require(a.dtype==b.dtype and a.shape==b.shape and a.tobytes()==b.tobytes(),'PHYSICAL_ARRAY_CHANGED:'+key)
    changed_metadata={'next_segment','restart_binding','restart_binding_sha256','production_transition','production_scope'}
    require(set(child_metadata)==set(parent_metadata)|{'production_transition','production_scope'},'FORBIDDEN_METADATA_KEY_CHANGE')
    for key in set(parent_metadata)-changed_metadata:
        require(parent_metadata[key]==child_metadata[key],'PHYSICAL_METADATA_CHANGED:'+key)
    return dict(physical_arrays_bitwise=True,metadata_preserved=True,
        allowed_array_changes=['scheduled_clock final endpoint','segment_edges final endpoint'],
        allowed_metadata_changes=sorted(changed_metadata),native_map_calls=0)

def _schedule(repo,schedule):
    doc=json.loads(Path(schedule).read_text()) if isinstance(schedule,(str,Path)) else copy.deepcopy(schedule)
    require(isinstance(doc,dict),'SCHEDULE_OBJECT')
    require(doc['target_time_s']==TARGET_TIME_S and doc.get('end_time_s',TARGET_TIME_S)==TARGET_TIME_S,'SCHEDULE_TARGET')
    epochs=json.loads((repo/C11_REL/'integration/production_design/OUTPUT_EPOCHS.json').read_text())
    # Source epoch bytes are already in the pinned parent closure indirectly;
    # compare their published provenance before accepting a copied schedule.
    require(epochs['source']=='research/accel02_20261011/recovery/Q0_SOURCE_ATTRIBUTION.json' and
            epochs['source_sha256']=='91959c5e09073ae89afcfe14937e6bc2dc4478692143873471934f542fc1ad6d' and
            sha(repo/epochs['source'])==epochs['source_sha256'],'OUTPUT_EPOCH_SOURCE_IDENTITY')
    source=json.loads((repo/epochs['source']).read_text())
    source_times=[row['time_s'] for row in source['exact_source_history']]
    require(doc['output_epochs_s']==source_times==epochs['time_s'],'OUTPUT_EPOCHS_EXACT')
    require(doc['shared65_indices']==list(range(0,129,2)) and len(source_times)==129,'OUTPUT_SHARED65')
    values=doc['hard_events_s']
    require(isinstance(values,list) and all(type(t) in (int,float) and math.isfinite(t) and 0<=t<=TARGET_TIME_S for t in values),'HARD_EVENTS_DOMAIN')
    require(values==sorted(set(values)) and set(source_times[1:])<=set(values),'HARD_EVENTS_OUTPUT_BINDING')
    return doc,[float(t) for t in values if t>0]

def prepare_transition(repo,output_root,schedule,extra_dependency_paths=()):
    """Publish a new generation3 whose physical prefix equals the old generation3."""
    repo=Path(repo).resolve(strict=True);out=Path(output_root)
    if not out.is_absolute():out=repo/out
    out=out.resolve()
    try:out.relative_to(repo)
    except ValueError:raise ValueError('OUTPUT_ROOT_MUST_BE_INSIDE_REPO') from None
    if out.exists():raise FileExistsError(out)
    preflight=verify_parent_before_import(repo)
    doc,events=_schedule(repo,schedule)
    # No project module imported before complete parent manifest/dependency check.
    sys.path.insert(0,str(repo/C11_REL/'restart'))
    checkpoint=importlib.import_module('adaptive_checkpoint')
    require(Path(checkpoint.__file__).resolve()==repo/C11_REL/'restart/adaptive_checkpoint.py','CHECKPOINT_IMPORT_LOCATION')
    parent=checkpoint.load_adaptive_checkpoint(repo/PARENT_REL.parent,3,PARENT_IDENTITY,expected_manifest_sha256=PARENT_MANIFEST)
    arrays={k:v.copy() for k,v in parent['arrays'].items()};metadata=copy.deepcopy(parent['metadata'])
    cursor=metadata['adaptive_cursor']
    controls=production_controls(metadata['restart_binding']['controls'],cursor)
    assert_runtime_only_controls(metadata['restart_binding']['controls'],controls,cursor)
    out.mkdir(parents=True,exist_ok=False)
    write_json(out/'SCHEDULE.json',doc);write_json(out/'CONTROLS.json',controls)
    dependencies=copy.deepcopy(preflight['dependency_closure'])
    extra=[Path(__file__),Path(__file__).with_name('production_control.py'),
           repo/C11_REL/'integration/production_design/OUTPUT_EPOCHS.json',repo/'research/accel02_20261011/recovery/Q0_SOURCE_ATTRIBUTION.json',
           out/'SCHEDULE.json',out/'CONTROLS.json',*extra_dependency_paths]
    for p in extra:
        relative=_relative(repo,p);key='dependency:'+str(relative);digest=sha(repo/relative)
        require(key not in dependencies or dependencies[key]==digest,'IMMUTABLE_DEPENDENCY_CHANGED:'+key)
        dependencies[key]=digest
    transition=dict(schema='rei.q1b.c12.explicit_identity_transition.v1',parent_checkpoint=str(PARENT_REL),
        parent_manifest_sha256=PARENT_MANIFEST,parent_identity=PARENT_IDENTITY,parent_generation=3,
        parent_payload=preflight['manifest']['files'],parent_dependency_closure=preflight['dependency_closure'],
        parent_restart_binding_sha256=parent['metadata']['restart_binding_sha256'],
        child_run_root=str(out.relative_to(repo)),child_initial_generation=3,
        old_end_time_s=parent['metadata']['restart_binding']['end_time_s'],new_end_time_s=TARGET_TIME_S,
        old_controls=parent['metadata']['restart_binding']['controls'],new_controls=controls,
        schedule_path=str((out/'SCHEDULE.json').relative_to(repo)),schedule_sha256=sha(out/'SCHEDULE.json'),
        schedule_canonical_sha256=canonical_sha(doc),hard_events_omit_origin_only=True,
        preserved_cursor=cursor,preserved_prefix_states=int(arrays['prefix_clock'].size),
        preserved_array_sha256={k:hashlib.sha256(arrays[k].tobytes()).hexdigest() for k in PHYSICAL_ARRAY_KEYS},
        new_attempt_allowance=100,new_accepted_macro_allowance=100,counters_reset=False,
        allowed_changes=['runtime_total_caps','declared_end_time','hard_events','output_schedule','added_driver_dependency_pins'],
        old_completed_replays=0,native_map_calls=0,scientific_admission=False)
    write_json(out/'IDENTITY_TRANSITION.json',transition)
    relative=(out/'IDENTITY_TRANSITION.json').relative_to(repo)
    dependencies['dependency:'+str(relative)]=sha(out/'IDENTITY_TRANSITION.json')
    binding=dict(controls=controls,end_time_s=TARGET_TIME_S,hard_events_s=events,dependency_closure=dependencies)
    arrays['scheduled_clock'][-1]=TARGET_TIME_S;arrays['segment_edges'][-1]=TARGET_TIME_S
    metadata['next_segment']=[metadata['current_clock'],TARGET_TIME_S]
    metadata['restart_binding']=binding;metadata['restart_binding_sha256']=canonical_sha(binding)
    metadata['production_transition']=dict(path=str(relative),sha256=sha(out/'IDENTITY_TRANSITION.json'))
    metadata['production_scope']='FULL_TARGET_R0_C2_EXTENSION_INITIAL_SNAPSHOT_ZERO_NATIVE_MAPS'
    preservation=assert_prefix_preserved(parent['arrays'],parent['metadata'],arrays,metadata)
    identity=copy.deepcopy(PARENT_IDENTITY);identity['control']=canonical_sha(binding)
    checkpoint.validate_adaptive_snapshot(arrays,metadata)
    target=checkpoint.write_adaptive_checkpoint(out/'CHECKPOINTS',3,arrays,metadata,identity)
    loaded=checkpoint.load_adaptive_checkpoint(out/'CHECKPOINTS',3,identity,expected_manifest_sha256=sha(target/'manifest.json'))
    preservation=assert_prefix_preserved(parent['arrays'],parent['metadata'],loaded['arrays'],loaded['metadata'])
    result=dict(schema='rei.q1b.c12.transition_result.v1',checkpoint_directory=str(out/'CHECKPOINTS'),generation=3,
        generation_path=str(target),manifest_sha256=sha(target/'manifest.json'),identity=identity,controls=controls,
        cursor=cursor,target_time_s=TARGET_TIME_S,dependency_closure=dependencies,parent_dependency_count=41,
        transition_path=str(out/'IDENTITY_TRANSITION.json'),schedule_path=str(out/'SCHEDULE.json'),
        preservation=preservation,native_map_calls=0,old_completed_replays=0,scientific_admission=False)
    write_json(out/'TRANSITION_RESULT.json',result)
    return result
