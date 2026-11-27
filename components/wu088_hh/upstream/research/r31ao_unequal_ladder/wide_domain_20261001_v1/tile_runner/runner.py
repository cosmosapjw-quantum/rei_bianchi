"""Fixed-source sequential <=16 tile pilot; raw-native normalization and collection."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
NEW=HERE.parent
LADDER=NEW.parent
DRIVER=NEW/'log_native_driver/driver.py'
COLLECTOR=NEW/'tile_collection/collector.py'
INPUT=LADDER/'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz'
BUILD=NEW/'runtime/build_log_cached'
DRIVER_SHA='cd344bb9c455fbf625aedd12ee1f048a1617baa2fdd5dd2c08bce90750044286'
COLLECTOR_SHA='0c8345ccae9a91ab38f2f15619ee5d58317dd22d7eab12268c2c47f91a7c5d94'
BUILD_SHA='1a71c74c73400ec36e9ba21d8f4d9c6655c596dabdc3a3cba3c1378d184e1d50'
SOURCE_SHA='faf2525e0270d38db7873380f84264a15e89f64568033727fd7724204f5e840c'
INPUT_SHA='8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
MAX_BYTES=16*1024*1024

class TileError(ValueError):pass
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sealed(value,key):return {**value,key:digest(canonical(value))}
def source_sha():return digest(Path(__file__).read_bytes())
def read(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>MAX_BYTES:raise TileError('bounded regular file required')
    data=p.read_bytes()
    if len(data)>MAX_BYTES:raise TileError('file grew past cap')
    return data
def write_new(path,value):
    with Path(path).open('xb') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True).encode()+b'\n')
def import_fixed(path,name,sha):
    if digest(read(path))!=sha:raise TileError('fixed dependency source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
def modules():
    return import_fixed(DRIVER,'wu088_tile_log_driver',DRIVER_SHA),import_fixed(COLLECTOR,'wu088_tile_collector',COLLECTOR_SHA)
def selfhash(d,value,key,expected=None):
    if type(value) is not dict or key not in value:raise TileError('missing envelope digest')
    actual=d.checked_hash(value[key])
    if actual!=digest(canonical({k:v for k,v in value.items() if k!=key})) or expected is not None and actual!=expected:
        raise TileError('envelope digest mismatch: '+key)

def context():
    """Verify exact fixed runtime bytes before reading/normalizing or dispatching."""
    d,c=modules();source=d.source_identity()
    if source['sha256']!=SOURCE_SHA:raise TileError('current log source identity changed')
    raw=read(INPUT)
    if digest(raw)!=INPUT_SHA:raise TileError('fixed Frozen107 archive changed')
    manifest=d.parse_json(read(BUILD/'BUILD.json'));selfhash(d,manifest,'manifest_sha256',BUILD_SHA)
    config=d.build_configuration('cached')
    if manifest.get('schema')!='WU088_LOG2_NATIVE_DRIVER_BUILD_V1' or manifest.get('source')!=source or \
       manifest.get('callback_mode')!='cached' or manifest.get('flags')!=d.FLAGS or \
       manifest.get('callback_mode_flags')!=config['mode_flags'] or manifest.get('callback_sources')!=config['sources']:
        raise TileError('fixed native build/source/mode mismatch')
    if manifest.get('archive_sha256')!=INPUT_SHA or digest(read(BUILD/'primitive_worker'))!=manifest.get('binary_sha256'):
        raise TileError('native binary or archive binding mismatch')
    adapter,gate=d.dependencies();record=adapter.decode_npz(raw,expected_archive_sha256=INPUT_SHA,scope='FROZEN107_PINNED')
    if record['canonical_record_sha256']!=manifest['input_record_sha256']:raise TileError('canonical input record mismatch')
    provenance=Path(manifest['backend_provenance']);prefix=Path(manifest['prefix'])
    if digest(read(provenance))!=manifest['backend_provenance_sha256']:raise TileError('backend provenance changed')
    backend=gate.verify_backend(provenance,prefix)
    env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','LD_LIBRARY_PATH':str(prefix/'lib')}
    result=subprocess.run(['/usr/bin/ldd',str((BUILD/'primitive_worker').resolve())],env=env,capture_output=True,text=True,timeout=15,check=True)
    linkage=gate.verify_linkage(result.stdout,{name:value['binary_path'] for name,value in backend['libraries'].items()})
    if linkage!=manifest['linkage']:raise TileError('actual backend linkage changed')
    planner=d.module('wu088_tile_endpoint_planner',d.PLAN_MODULE)
    return {'d':d,'c':c,'raw':raw,'record':record,'manifest':manifest,'planner':planner}

def validate_global(ctx,plan,expected):
    d=ctx['d'];d.checked_hash(expected)
    if plan.get('plan_sha256')!=expected:raise TileError('global physical plan mismatch')
    ctx['planner'].validate_plan(plan,source_archive_bytes=ctx['raw'])
    if plan['archive_sha256']!=INPUT_SHA or plan['input_record']!=ctx['record']:
        raise TileError('global plan does not bind fixed input')
    d.log2_window(plan['window'])
    return plan

def bound_grid(ctx,global_plan,index,step=3):
    c=ctx['c'];m=ctx['manifest']
    grid=c.plan_grid(global_plan['window'],index,-48,max_log_step=step,max_tiles=16)
    return c.bind_plan(grid,global_endpoint_plan_sha256=global_plan['plan_sha256'],archive_sha256=INPUT_SHA,
        input_record_sha256=m['input_record_sha256'],build_manifest_sha256=BUILD_SHA,
        build_source_sha256=SOURCE_SHA,validator_source_sha256=source_sha())

def native_plan(ctx,global_plan,window):
    return ctx['planner'].build_plan(global_plan['input_record'],window,precision_bits=global_plan['precision_bits'],
        panels=global_plan['panels'],caps=global_plan['caps'],source_archive_bytes=ctx['raw'])

def limits_for(ctx,grid):
    return ctx['d'].limits_checked({**ctx['d'].DEFAULT_LIMITS,'radius_exp':grid['tile_radius_exp']})

def prepare(global_plan_path,global_plan_sha,index,outdir,step=3):
    ctx=context();d=ctx['d'];global_plan=validate_global(ctx,d.parse_json(read(global_plan_path)),global_plan_sha)
    grid=bound_grid(ctx,global_plan,index,step);limits=limits_for(ctx,grid)
    out=Path(outdir).resolve();out.mkdir(parents=False,exist_ok=False);(out/'plans').mkdir()
    write_new(out/'GLOBAL_PLAN.json',global_plan);local=[]
    for tile in grid['tiles']:
        plan=native_plan(ctx,global_plan,tile['window']);relative='plans/%02d.json'%tile['tile_id'];write_new(out/relative,plan)
        local.append({'tile_id':tile['tile_id'],'path':relative,'file_sha256':digest(read(out/relative)),'plan_sha256':plan['plan_sha256']})
    manifest={'schema':'WU088_FIXED_SEQUENTIAL_TILE_RUN_V1','grid':grid,'local_plans':local,
        'global_plan_file_sha256':digest(read(out/'GLOBAL_PLAN.json')),'limits':limits,
        'fixed_paths':{'input':str(INPUT),'driver':str(DRIVER),'build':str(BUILD)},
        'driver_sha256':DRIVER_SHA,'collector_sha256':COLLECTOR_SHA,'validator_source_sha256':source_sha(),
        'max_native_executions':grid['tile_count'],'max_dispatched_evaluations':grid['tile_count']*limits['max_evaluations'],
        'max_native_wall_seconds':grid['tile_count']*(limits['wall_seconds']+5),
        'aggregate_wall_scope':'sum of native process hard caps; Python validation and plan overhead excluded',
        'concurrency':1,'stop_on_first_rejection':True,'endpoint_included':False,'production_admission':False}
    manifest=sealed(manifest,'manifest_sha256');write_new(out/'PREPARED.json',manifest);return manifest

def load_prepared(outdir,expected_sha,ctx=None):
    ctx=context() if ctx is None else ctx;d=ctx['d'];root=Path(outdir).resolve()
    m=d.parse_json(read(root/'PREPARED.json'));selfhash(d,m,'manifest_sha256',d.checked_hash(expected_sha))
    global_bytes=read(root/'GLOBAL_PLAN.json')
    if digest(global_bytes)!=m['global_plan_file_sha256']:raise TileError('prepared global file changed')
    global_plan=validate_global(ctx,d.parse_json(global_bytes),m['grid']['bindings']['global_endpoint_plan_sha256'])
    grid=bound_grid(ctx,global_plan,m['grid']['primitive_index'],m['grid']['max_log_step'])
    limits=limits_for(ctx,grid)
    if m['schema']!='WU088_FIXED_SEQUENTIAL_TILE_RUN_V1' or m['grid']!=grid or m['limits']!=limits or \
       m['validator_source_sha256']!=source_sha() or m['driver_sha256']!=DRIVER_SHA or m['collector_sha256']!=COLLECTOR_SHA or \
       m['fixed_paths']!={'input':str(INPUT),'driver':str(DRIVER),'build':str(BUILD)} or type(m['concurrency']) is not int or m['concurrency']!=1 or \
       m['stop_on_first_rejection'] is not True or m['endpoint_included'] is not False or m['production_admission'] is not False or \
       type(m['max_native_executions']) is not int or m['max_native_executions']!=grid['tile_count'] or \
       type(m['max_dispatched_evaluations']) is not int or m['max_dispatched_evaluations']!=grid['tile_count']*20000 or \
       type(m['max_native_wall_seconds']) is not int or m['max_native_wall_seconds']!=grid['tile_count']*35 or len(m['local_plans'])!=grid['tile_count']:
        raise TileError('prepared fixed execution contract changed')
    plans=[]
    for i,tile in enumerate(grid['tiles']):
        entry=m['local_plans'][i];expected_path='plans/%02d.json'%i
        if set(entry)!={'tile_id','path','file_sha256','plan_sha256'} or entry['tile_id']!=i or entry['path']!=expected_path:
            raise TileError('local plan path/order mismatch')
        path=root/expected_path
        if not path.resolve().is_relative_to(root):raise TileError('local plan symlink escape')
        payload=read(path)
        if digest(payload)!=entry['file_sha256']:raise TileError('local plan bytes changed')
        plan=d.parse_json(payload);expected=native_plan(ctx,global_plan,tile['window'])
        if plan!=expected or plan['plan_sha256']!=entry['plan_sha256']:raise TileError('local plan identity mismatch')
        plans.append(plan)
    ctx['global_plan']=global_plan
    return ctx,m,plans

def normalize(ctx,grid,local_plan,tile_id,receipt_bytes):
    """Read-only native evidence validation before exact collector normalization."""
    d,c=ctx['d'],ctx['c'];m=ctx['manifest'];c._validate_plan(grid)
    global_plan=validate_global(ctx,ctx['global_plan'],grid['bindings']['global_endpoint_plan_sha256'])
    if grid!=bound_grid(ctx,global_plan,grid['primitive_index'],grid['max_log_step']):
        raise TileError('global physical plan and tiling geometry mismatch')
    if grid['bindings']!={'global_endpoint_plan_sha256':grid['bindings']['global_endpoint_plan_sha256'],
        'archive_sha256':INPUT_SHA,'input_record_sha256':m['input_record_sha256'],
        'build_manifest_sha256':BUILD_SHA,'build_source_sha256':SOURCE_SHA,'validator_source_sha256':source_sha()}:
        raise TileError('collector authority binding mismatch')
    if type(tile_id) is not int or not 0<=tile_id<grid['tile_count']:raise TileError('tile index out of range')
    ctx['planner'].validate_plan(local_plan,source_archive_bytes=ctx['raw'])
    if local_plan['input_record']!=ctx['record'] or local_plan['window']!=grid['tiles'][tile_id]['window']:
        raise TileError('local physical tile/input mismatch')
    limits=limits_for(ctx,grid);task=local_plan['tasks'][grid['primitive_index']]
    record=d.parse_json(receipt_bytes);selfhash(d,record,'result_sha256')
    if 'wrapper' not in record:raise TileError('source-bound wrapper required')
    wrapper=record['wrapper'];native={k:v for k,v in record.items() if k not in ('wrapper','result_sha256')}
    d.validate_result(native,plan=local_plan,task=task,manifest=m,limits=limits)
    command=[str((BUILD/'primitive_worker').resolve()),str(task['index']),*[local_plan['window'][k] for k in ('l_t','T_t','l_u','T_u')],
             *[str(limits[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations','max_integration_calls','wall_seconds','queued_panels','degree_limit')],
             task['task_sha256'],local_plan['plan_sha256']]
    expected={'schema':'WU088_LOG2_NATIVE_INTERIOR_WRAPPER_V1','build_manifest_sha256':BUILD_SHA,
        'binary_sha256':m['binary_sha256'],'build_source':m['source'],'archive_sha256':INPUT_SHA,
        'input_record_sha256':m['input_record_sha256'],'native_limits':limits,'command':command,
        'coordinate_map':'LOG2_EXACT_POWER_ENDPOINTS_V1','physical_window':local_plan['window'],
        'log2_window':d.log2_window(local_plan['window']),'backend_provenance_sha256':m['backend_provenance_sha256'],
        'linkage':m['linkage'],'native_execution_observed':True,'scope':'CONDITIONAL_COMPACT_INTERIOR_ONLY',
        'evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'validation_level':'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY','endpoint_plan_module_sha256':digest(read(d.PLAN_MODULE)),
        'historical_abi_admission':False,'independent_scientific_review':False,'returncode':0}
    if type(wrapper) is not dict or set(wrapper)!=set(expected)|{'elapsed_wall_ns','native_stdout_sha256','native_stderr_sha256'}:
        raise TileError('exact native wrapper keys required')
    for key,value in expected.items():
        if canonical(wrapper[key])!=canonical(value):raise TileError('native wrapper mismatch: '+key)
    if type(wrapper['elapsed_wall_ns']) is not int or wrapper['elapsed_wall_ns']<0:raise TileError('elapsed integer ns required')
    for key in ('native_stdout_sha256','native_stderr_sha256'):d.checked_hash(wrapper[key])
    rectangle={};radii={}
    for part in ('real','imag'):
        lo,hi=d.dyadic_interval(native['rectangle'][part]);rectangle[part]={'lower':str(lo),'upper':str(hi)};radii[part]=str((hi-lo)/2)
    return c.seal_normalized_record({'schema':'WU088_TRUSTED_NORMALIZED_TILE_V1','tile_id':tile_id,
        'primitive_index':grid['primitive_index'],'global_plan_sha256':grid['plan_sha256'],
        'window':grid['tiles'][tile_id]['window'],'requested_radius_exp':grid['tile_radius_exp'],'precision_bits':128,
        'status':'RADIUS_MET','accepted':True,'endpoint_included':False,'normalization_applied':False,
        'bindings':grid['bindings'],'native_plan_sha256':local_plan['plan_sha256'],
        'native_receipt_sha256':digest(receipt_bytes),'rectangle':rectangle,'reported_radius':radii})

def run_prepared(outdir,expected_sha):
    root=Path(outdir).resolve()
    if os.path.lexists(root/'RUN_RESULT.json') or os.path.lexists(root/'RUN_START.json'):
        raise TileError('existing started/completed run is not rerun')
    fd=os.open(root/'RUN.claim',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        ctx,m,plans=load_prepared(root,expected_sha);d=ctx['d'];grid=m['grid'];limits=m['limits']
        (root/'raw').mkdir();(root/'normalized').mkdir()
        started=time.monotonic_ns();write_new(root/'RUN_START.json',{'prepared_sha256':expected_sha,'validator_source_sha256':source_sha(),'pid':os.getpid()})
        results=[];normalized=[];status='STOPPED_FIRST_REJECTION';error=None;charged=0
        for tile in grid['tiles']:
            i=tile['tile_id'];raw_path=root/'raw'/('%02d.json'%i);tick=time.monotonic_ns()
            charged+=limits['max_evaluations']
            if charged>m['max_dispatched_evaluations']:raise TileError('aggregate evaluation admission exceeded')
            entry={'tile_id':i,'local_plan_sha256':plans[i]['plan_sha256'],'native_cap_charged':limits['max_evaluations']}
            try:
                # Strict sequential call. No threads or fork-from-thread preexec.
                d.run_task(INPUT,root/m['local_plans'][i]['path'],plans[i]['plan_sha256'],grid['primitive_index'],BUILD,BUILD_SHA,limits,raw_path)
                fresh=context();fresh['global_plan']=ctx['global_plan']
                norm=normalize(fresh,grid,plans[i],i,read(raw_path));write_new(root/'normalized'/('%02d.json'%i),norm)
                normalized.append(norm);entry['status']='ACCEPTED';entry['raw_receipt_sha256']=digest(read(raw_path))
            except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as exc:
                error=str(exc);entry['status']='REJECTED';entry['error']=error
                if raw_path.is_file():entry['raw_receipt_sha256']=digest(read(raw_path))
                entry['elapsed_wall_ns']=time.monotonic_ns()-tick;results.append(entry);break
            entry['elapsed_wall_ns']=time.monotonic_ns()-tick;results.append(entry)
        if len(normalized)==grid['tile_count']:
            try:
                collected=ctx['c'].collect(grid,normalized);write_new(root/'COLLECTED.json',collected);status='COMPLETE_COMPACT_INTERIOR_RADIUS_MET'
            except (ValueError,OSError,KeyError,TypeError) as exc:
                status='COLLECTION_REFUSED';error=str(exc)
        final=sealed({'schema':'WU088_FIXED_TILE_EXECUTION_RETURN_V1','status':status,'prepared_sha256':expected_sha,
            'global_endpoint_plan_sha256':grid['bindings']['global_endpoint_plan_sha256'],'tiling_plan_sha256':grid['plan_sha256'],
            'validator_source_sha256':source_sha(),'attempted_tiles':len(results),'accepted_tiles':len(normalized),
            'native_cap_charged':charged,'max_dispatched_evaluations':m['max_dispatched_evaluations'],
            'elapsed_wall_ns':time.monotonic_ns()-started,'error':error,'tiles':results,
            'endpoint_included':False,'full_domain_integral':False,'scientific_admission':False,'production_admission':False},'result_sha256')
        write_new(root/'RUN_RESULT.json',final);return final
    finally:
        os.close(fd);(root/'RUN.claim').unlink()

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('prepare');p.add_argument('--global-plan',required=True);p.add_argument('--global-plan-sha256',required=True)
    p.add_argument('--task-index',type=int,required=True);p.add_argument('--output-dir',required=True);p.add_argument('--max-log-step',type=int,default=3)
    p=sub.add_parser('run');p.add_argument('--prepared-dir',required=True);p.add_argument('--prepared-sha256',required=True)
    p=sub.add_parser('normalize');p.add_argument('--prepared-dir',required=True);p.add_argument('--prepared-sha256',required=True)
    p.add_argument('--tile-id',type=int,required=True);p.add_argument('--raw-receipt',required=True);p.add_argument('--output',required=True)
    args=ap.parse_args()
    try:
        if args.mode=='prepare':result=prepare(args.global_plan,args.global_plan_sha256,args.task_index,args.output_dir,args.max_log_step)
        elif args.mode=='run':result=run_prepared(args.prepared_dir,args.prepared_sha256)
        else:
            ctx,m,plans=load_prepared(args.prepared_dir,args.prepared_sha256)
            if type(args.tile_id) is not int or not 0<=args.tile_id<len(plans):raise TileError('tile ID out of range')
            result=normalize(ctx,m['grid'],plans[args.tile_id],args.tile_id,read(args.raw_receipt));write_new(args.output,result)
        print(json.dumps({'status':result.get('status','PREPARED_OR_NORMALIZED'),'identity':result.get('manifest_sha256',result.get('result_sha256',result.get('record_sha256')))}))
        return 2 if result.get('status') in ('STOPPED_FIRST_REJECTION','COLLECTION_REFUSED') else 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print('TILE_RUNNER_REFUSED: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
