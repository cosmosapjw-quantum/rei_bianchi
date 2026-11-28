"""Resumable bounded W1 range-native tiles; exact source-bound normalization."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import signal
import sys
import time

HERE=Path(__file__).resolve().parent
NEW=HERE.parent
LADDER=NEW.parent
OLD=LADDER/'wide_domain_20261001_v1'
DRIVER=OLD/'range_native_driver/driver.py'
HOST=NEW/'process_host/host.py'
PRIOR=OLD/'runtime/W1_TILED'
GLOBAL=PRIOR/'GLOBAL_PLAN.json'
IMPORTED=OLD/'runtime/RANGE_TILE00_COMPLETION.json'
GLOBAL_SHA='844b7df830fec1ebe36af239373f66fdc2b4112c55377702c6c1d3cf78524b2c'
GLOBAL_FILE_SHA='e69eaa21d74da6451fb575141659caeb38280e9f921a9f014bd4683d033ded07'
PRIOR_SHA='18fc5c4c6b678a7bea31223de7b1b107972c9bafceb7f99e8983f34cb02cf8fb'
IMPORTED_SHA='89cef714e9758932036854d218330c775920d6131114df8a236cf7d171bc5c5e'
LIMITS={'precision_bits':128,'radius_exp':-52,'relative_goal':128,'max_evaluations':200000,
        'max_integration_calls':1024,'wall_seconds':120,'queued_panels':64,'degree_limit':64,'memory_mib':1024}
COLLECTOR=OLD/'tile_collection/collector.py'
INPUT=LADDER/'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz'
BUILD=OLD/'runtime/build_range_cached'
DRIVER_SHA='e91238a21d5cffc3c513330ceb561f882d44a92f8654b1a0d6fa1117e59949dc'
COLLECTOR_SHA='0c8345ccae9a91ab38f2f15619ee5d58317dd22d7eab12268c2c47f91a7c5d94'
BUILD_SHA='13965d2210e976f0d7a190fba58f8c3c1bf366521e8dd1bd5e9a28cdae9e9342'
SOURCE_SHA='de1e32d8a68146a49d269614c2259ec06f10a5294ffa05b15d375239518bcae1'
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
    with Path(path).open('xb') as stream:
        stream.write(json.dumps(value,indent=2,sort_keys=True).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
    fd=os.open(Path(path).parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def import_fixed(path,name,sha):
    if digest(read(path))!=sha:raise TileError('fixed dependency source changed: '+str(path))
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module
def modules():
    return import_fixed(DRIVER,'wu088_w1_range_driver',DRIVER_SHA),import_fixed(COLLECTOR,'wu088_tile_collector',COLLECTOR_SHA)
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
    if manifest.get('schema')!='WU088_LOG2_RANGE_NATIVE_DRIVER_BUILD_V1' or manifest.get('source')!=source or \
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
    if grid['tile_count']!=16 or grid['tile_radius_exp']!=-52:raise TileError('fixed sixteen-tile W1 scope required')
    return ctx['d'].limits_checked(LIMITS)

def host_module():
    return import_fixed(HOST,'wu088_w1_process_host',digest(read(HOST)))

def contract(ctx,workers):
    if type(workers) is not int or not 1<=workers<=4:raise TileError('one to four workers required')
    d=ctx['d'];global_bytes=read(GLOBAL)
    if digest(global_bytes)!=GLOBAL_FILE_SHA or digest(read(PRIOR/'PREPARED.json'))!=PRIOR_SHA:
        raise TileError('pinned prior plan artifact changed')
    global_plan=validate_global(ctx,d.parse_json(global_bytes),GLOBAL_SHA);ctx['global_plan']=global_plan
    grid=bound_grid(ctx,global_plan,0,3);limits=limits_for(ctx,grid)
    prior=d.parse_json(read(PRIOR/'PREPARED.json'))
    local=[{**entry,'path':str(PRIOR/entry['path'])} for entry in prior['local_plans']]
    if len(local)!=16 or any(e['tile_id']!=i or e['path']!=str(PRIOR/'plans'/('%02d.json'%i)) for i,e in enumerate(local)):
        raise TileError('prior local-plan ordering/path mismatch')
    return sealed({'schema':'WU088_RESUMABLE_RANGE_W1_PREPARED_V1','grid':grid,'local_plans':local,
        'global_plan_file_sha256':GLOBAL_FILE_SHA,'prior_prepared_file_sha256':PRIOR_SHA,'limits':limits,
        'fixed_paths':{'input':str(INPUT),'driver':str(DRIVER),'build':str(BUILD),'global_plan':str(GLOBAL)},
        'driver_sha256':DRIVER_SHA,'collector_sha256':COLLECTOR_SHA,'validator_source_sha256':source_sha(),
        'process_host':host_module().identity(),'imported_tile':{'tile_id':0,'path':str(IMPORTED),'file_sha256':IMPORTED_SHA,
        'origin':'PRIOR_VERIFIED_EXECUTION_REUSED','new_native_execution':False},
        'max_native_executions':15,'max_dispatched_evaluations':15*limits['max_evaluations'],
        'max_native_wall_seconds':15*(limits['wall_seconds']+5),'worker_wall_seconds':180,'worker_memory_mib':1024,
        'aggregate_wall_scope':'sum of native hard caps; wrapper validation overhead excluded',
        'concurrency':workers,'stop_on_first_rejection':True,'endpoint_included':False,
        'full_domain_integral':False,'scientific_admission':False,'production_admission':False},'manifest_sha256')

def validated_plan(ctx,m,tile_id):
    if type(tile_id) is not int or not 0<=tile_id<16:raise TileError('tile index required')
    entry=m['local_plans'][tile_id];payload=read(entry['path'])
    if digest(payload)!=entry['file_sha256']:raise TileError('local plan bytes changed')
    plan=ctx['d'].parse_json(payload);expected=native_plan(ctx,ctx['global_plan'],m['grid']['tiles'][tile_id]['window'])
    if plan!=expected or plan['plan_sha256']!=entry['plan_sha256']:raise TileError('local plan identity mismatch')
    return plan

def prepare(outdir,workers=3):
    ctx=context();m=contract(ctx,workers)
    plans=[validated_plan(ctx,m,i) for i in range(16)]
    norm=normalize(ctx,m['grid'],plans[0],0,read(IMPORTED),origin='imported',receipt_path=IMPORTED)
    out=Path(outdir).resolve();out.mkdir(parents=False,exist_ok=False)
    for child in ('raw','normalized','attempts','sessions'):(out/child).mkdir()
    write_new(out/'PREPARED.json',m)
    write_new(out/'IMPORTED_TILE00.json',sealed({'schema':'WU088_REUSED_RANGE_TILE_V1',
        'prepared_sha256':m['manifest_sha256'],**m['imported_tile'],
        'normalized_record_sha256':norm['record_sha256']},'import_sha256'))
    write_new(out/'normalized/00.json',norm)
    return m

def load_prepared(outdir,expected_sha,ctx=None,tile_id=None):
    ctx=context() if ctx is None else ctx;d=ctx['d'];root=Path(outdir).resolve()
    m=d.parse_json(read(root/'PREPARED.json'));selfhash(d,m,'manifest_sha256',d.checked_hash(expected_sha))
    expected=contract(ctx,m.get('concurrency'))
    if canonical(m)!=canonical(expected):raise TileError('prepared fixed execution contract changed')
    plans={i:validated_plan(ctx,m,i) for i in (range(16) if tile_id is None else [tile_id])}
    return ctx,m,plans

def normalize(ctx,grid,local_plan,tile_id,receipt_bytes,*,origin='new',receipt_path=None):
    """Read-only native evidence validation before exact collector normalization."""
    if origin not in ('new','imported'):raise TileError('explicit receipt origin required')
    if origin=='imported' and (tile_id!=0 or digest(receipt_bytes)!=IMPORTED_SHA or Path(receipt_path).resolve()!=IMPORTED.resolve()):
        raise TileError('only exact prior tile zero may be imported')
    if origin=='new' and tile_id==0:raise TileError('completed tile zero must never rerun')
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
    if local_plan!=native_plan(ctx,global_plan,grid['tiles'][tile_id]['window']) or local_plan['input_record']!=ctx['record'] or local_plan['window']!=grid['tiles'][tile_id]['window']:
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
    extra={'elapsed_wall_ns','native_stdout_sha256','native_stderr_sha256'}
    if origin=='new':extra.add('process_host')
    if type(wrapper) is not dict or set(wrapper)!=set(expected)|extra:
        raise TileError('exact native wrapper keys required')
    for key,value in expected.items():
        if canonical(wrapper[key])!=canonical(value):raise TileError('native wrapper mismatch: '+key)
    if type(wrapper['elapsed_wall_ns']) is not int or wrapper['elapsed_wall_ns']<0:raise TileError('elapsed integer ns required')
    for key in ('native_stdout_sha256','native_stderr_sha256'):d.checked_hash(wrapper[key])
    if origin=='new':
        if receipt_path is None:raise TileError('new receipt path required')
        host_module().validate_receipt(wrapper['process_host'],command=command,limits=limits,output_path=Path(receipt_path))
        if wrapper['process_host'].get('timed_out') is not False or wrapper['process_host'].get('native_execution_evidence')!='SOURCE_BOUND_NATIVE_STDOUT':
            raise TileError('accepted native execution must have positive source-bound stdout and no timeout')
        stdout=read(str(receipt_path)+'.stdout');stderr=read(str(receipt_path)+'.stderr')
        if digest(stdout)!=wrapper['native_stdout_sha256'] or digest(stderr)!=wrapper['native_stderr_sha256']:
            raise TileError('retained native stream hash mismatch')
        if canonical(d.parse_json(stdout))!=canonical(native):raise TileError('native receipt differs from retained stdout')
    rectangle={};radii={}
    for part in ('real','imag'):
        lo,hi=d.dyadic_interval(native['rectangle'][part]);rectangle[part]={'lower':str(lo),'upper':str(hi)};radii[part]=str((hi-lo)/2)
    return c.seal_normalized_record({'schema':'WU088_TRUSTED_NORMALIZED_TILE_V1','tile_id':tile_id,
        'primitive_index':grid['primitive_index'],'global_plan_sha256':grid['plan_sha256'],
        'window':grid['tiles'][tile_id]['window'],'requested_radius_exp':grid['tile_radius_exp'],'precision_bits':128,
        'status':'RADIUS_MET','accepted':True,'endpoint_included':False,'normalization_applied':False,
        'bindings':grid['bindings'],'native_plan_sha256':local_plan['plan_sha256'],
        'native_receipt_sha256':digest(receipt_bytes),'rectangle':rectangle,'reported_radius':radii})

def load_state(root,ctx,m,plans):
    """Revalidate original evidence; normalized files alone never authorize reuse."""
    records={};failures=[];attempted=[];grid=m['grid'];d=ctx['d']
    imported=normalize(ctx,grid,plans[0],0,read(IMPORTED),origin='imported',receipt_path=IMPORTED)
    expected_import=sealed({'schema':'WU088_REUSED_RANGE_TILE_V1','prepared_sha256':m['manifest_sha256'],
        **m['imported_tile'],'normalized_record_sha256':imported['record_sha256']},'import_sha256')
    if d.parse_json(read(root/'IMPORTED_TILE00.json'))!=expected_import:
        raise TileError('imported tile provenance changed')
    if d.parse_json(read(root/'normalized/00.json'))!=imported:raise TileError('imported normalization changed')
    records[0]=imported
    for directory,suffix in [('raw','.json'),('normalized','.json'),('attempts','')]:
        for p in (root/directory).iterdir():
            if directory=='raw' and (p.name.endswith('.stdout') or p.name.endswith('.stderr')):continue
            if directory=='raw' and p.name.endswith('.claim'):raise TileError('stale native output claim requires inspection')
            allowed={('%02d'%i)+suffix for i in range(1,16)}
            if directory=='normalized':allowed.add('00.json')
            if p.name not in allowed or p.is_symlink():raise TileError('unrecognized campaign artifact: '+str(p))
    for i in range(1,16):
        ad=root/'attempts'/('%02d'%i);rp=root/'raw'/('%02d.json'%i);np=root/'normalized'/('%02d.json'%i)
        if not ad.exists():
            if rp.exists() or np.exists():raise TileError('receipt without dispatch ownership')
            continue
        attempted.append(i)
        start=d.parse_json(read(ad/'DISPATCH.json'));selfhash(d,start,'dispatch_sha256')
        wanted={'schema':'WU088_W1_TILE_DISPATCH_V1','tile_id':i,'prepared_sha256':m['manifest_sha256'],
            'validator_source_sha256':source_sha(),'plan_sha256':plans[i]['plan_sha256'],
            'native_cap_charged':m['limits']['max_evaluations'],'native_execution_requested':True}
        if {k:v for k,v in start.items() if k!='dispatch_sha256'}!=wanted:raise TileError('dispatch identity changed')
        if not (ad/'RETURN.json').is_file():raise TileError('unresolved dispatched tile requires inspection; never automatically rerun')
        result=d.parse_json(read(ad/'RETURN.json'));selfhash(d,result,'return_sha256')
        if result.get('dispatch_sha256')!=start['dispatch_sha256'] or result.get('tile_id')!=i or result.get('status') not in ('ACCEPTED','REJECTED'):
            raise TileError('terminal tile identity mismatch')
        if result.get('raw_receipt_sha256')!=(digest(read(rp)) if rp.is_file() else None):raise TileError('terminal raw receipt binding changed')
        if result['status']=='REJECTED':
            if np.exists():raise TileError('rejected tile cannot have normalized acceptance')
            failures.append(i);continue
        if result.get('worker_returncode')!=0 or result.get('timed_out') is not False:raise TileError('accepted worker did not finish normally')
        norm=normalize(ctx,grid,plans[i],i,read(rp),receipt_path=rp)
        if d.parse_json(read(np))!=norm or result.get('normalized_record_sha256')!=norm['record_sha256']:
            raise TileError('normalized acceptance changed')
        records[i]=norm
    if len(attempted)>m['max_native_executions']:raise TileError('campaign native admission exceeded')
    return records,failures,attempted

def worker(root,prepared_sha,tile_id):
    if type(tile_id) is not int or not 1<=tile_id<16:raise TileError('worker may only run missing tiles 1..15')
    root=Path(root).resolve();ctx,m,plans=load_prepared(root,prepared_sha,tile_id=tile_id)
    ad=root/'attempts'/('%02d'%tile_id)
    dispatch=ctx['d'].parse_json(read(ad/'DISPATCH.json'));selfhash(ctx['d'],dispatch,'dispatch_sha256')
    if dispatch.get('prepared_sha256')!=prepared_sha or dispatch.get('tile_id')!=tile_id or dispatch.get('plan_sha256')!=plans[tile_id]['plan_sha256']:
        raise TileError('worker dispatch not owned')
    if (ad/'RETURN.json').exists():raise TileError('finished tile not rerun')
    host_module().install(ctx['d'])
    ctx['d'].run_task(INPUT,m['local_plans'][tile_id]['path'],plans[tile_id]['plan_sha256'],0,BUILD,BUILD_SHA,m['limits'],root/'raw'/('%02d.json'%tile_id))
    return {'status':'NATIVE_RECEIPT_WRITTEN','tile_id':tile_id}

def resource_admission(m):
    workers=m['concurrency'];cpus=len(os.sched_getaffinity(0))
    quota=Path('/sys/fs/cgroup/cpu.max').read_text().split()
    effective=min(float(cpus),float('inf') if quota[0]=='max' else int(quota[0])/int(quota[1]))
    mem=Path('/sys/fs/cgroup/memory.max').read_text().strip()
    mem_limit=None if mem=='max' else int(mem)
    if effective<workers:raise TileError('actual affinity/cgroup CPU budget insufficient')
    # Reserve 2 GiB outside bounded 1 GiB Python workers, each native <=1 GiB.
    need=workers*(m['worker_memory_mib']+m['limits']['memory_mib'])*1024**2+2*1024**3
    if mem_limit is None or need>mem_limit:raise TileError('actual cgroup memory budget insufficient for Python plus native processes')
    return {'affinity':sorted(os.sched_getaffinity(0)),'cpu_max':quota,'effective_cpus':effective,
            'memory_max_bytes':mem_limit,'reservation_bytes':need,'concurrency':workers,
            'python_worker_memory_mib':m['worker_memory_mib'],'native_memory_mib':m['limits']['memory_mib']}

def run_prepared(outdir,expected_sha,max_new_tiles=15):
    if type(max_new_tiles) is not int or not 0<=max_new_tiles<=15:raise TileError('bounded missing tile count required')
    root=Path(outdir).resolve();fd=os.open(root/'RUN.claim',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    handles={};session=None
    try:
        os.write(fd,str(os.getpid()).encode());os.fsync(fd)
        ctx,m,plans=load_prepared(root,expected_sha);records,failures,attempted=load_state(root,ctx,m,plans)
        admission=resource_admission(m);host=host_module();started=time.monotonic_ns()
        sessions=sorted((root/'sessions').iterdir());session=root/'sessions'/('%03d'%len(sessions));session.mkdir(exist_ok=False)
        write_new(session/'START.json',{'schema':'WU088_W1_SESSION_START_V1','prepared_sha256':expected_sha,
            'pid':os.getpid(),'prior_attempted_tiles':attempted,'prior_accepted_tiles':sorted(records),
            'max_new_tiles':max_new_tiles,'resource_admission':admission})
        pending=[] if failures else [i for i in range(1,16) if i not in attempted][:max_new_tiles]
        dispatched=[];new_results=[];stop=bool(failures);first_error=None
        while pending or handles:
            while pending and len(handles)<m['concurrency'] and not stop:
                i=pending.pop(0);ad=root/'attempts'/('%02d'%i);ad.mkdir(exist_ok=False)
                dispatch=sealed({'schema':'WU088_W1_TILE_DISPATCH_V1','tile_id':i,'prepared_sha256':expected_sha,
                    'validator_source_sha256':source_sha(),'plan_sha256':plans[i]['plan_sha256'],
                    'native_cap_charged':m['limits']['max_evaluations'],'native_execution_requested':True},'dispatch_sha256')
                write_new(ad/'DISPATCH.json',dispatch);dispatched.append(i)
                so=(ad/'worker.stdout').open('xb');se=(ad/'worker.stderr').open('xb')
                command=[sys.executable,'-B',str(Path(__file__).resolve()),'worker','--directory',str(root),
                    '--prepared-sha256',expected_sha,'--tile-id',str(i)]
                try:
                    worker_env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'}
                    process=host.spawn_guarded(command,stdout=so,stderr=se,env=worker_env,memory_mib=m['worker_memory_mib'])
                    handles[i]={'process':process,'stdout':so,'stderr':se,'start':time.monotonic_ns(),'dispatch':dispatch,'timeout':False}
                except Exception as exc:
                    so.close();se.close();stop=True;pending=[];first_error=str(exc)
                    result=sealed({'tile_id':i,'dispatch_sha256':dispatch['dispatch_sha256'],'status':'REJECTED',
                        'worker_returncode':None,'timed_out':False,'error':str(exc),'raw_receipt_sha256':None,
                        'normalized_record_sha256':None},'return_sha256')
                    write_new(ad/'RETURN.json',result);new_results.append(result)
            if stop:pending=[]
            finished=[]
            for i,handle in sorted(handles.items()):
                p=handle['process'];code=p.poll()
                if code is None and (time.monotonic_ns()-handle['start'])/1e9>m['worker_wall_seconds']:
                    handle['timeout']=True
                    os.killpg(p.pid,signal.SIGKILL);code=p.wait(timeout=10)
                if code is None:continue
                handle['stdout'].close();handle['stderr'].close();rp=root/'raw'/('%02d.json'%i);np=root/'normalized'/('%02d.json'%i)
                error=None;norm=None
                try:
                    if code!=0 or handle['timeout']:raise TileError('worker exit/timeout refusal: '+str(code))
                    # Each completion rechecks fixed source/binary/backend before adoption.
                    fresh=context();fresh['global_plan']=ctx['global_plan']
                    if host.identity()!=m['process_host']:raise TileError('process host changed during run')
                    candidate=normalize(fresh,m['grid'],plans[i],i,read(rp),receipt_path=rp);write_new(np,candidate);norm=candidate;records[i]=norm
                except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as exc:
                    error=str(exc);first_error=first_error or error;stop=True;pending=[]
                result=sealed({'tile_id':i,'dispatch_sha256':handle['dispatch']['dispatch_sha256'],
                    'status':'ACCEPTED' if norm is not None else 'REJECTED','worker_returncode':code,'timed_out':handle['timeout'],
                    'error':error,'raw_receipt_sha256':digest(read(rp)) if rp.is_file() else None,
                    'normalized_record_sha256':norm['record_sha256'] if norm is not None else None,
                    'elapsed_wall_ns':time.monotonic_ns()-handle['start']},'return_sha256')
                write_new(root/'attempts'/('%02d'%i)/'RETURN.json',result);new_results.append(result);finished.append(i)
            for i in finished:del handles[i]
            if handles:time.sleep(.05)
        status='STOPPED_FIRST_REJECTION' if stop else 'PARTIAL_COMPACT_INTERIOR'
        collected=None
        if len(records)==16:
            collected=ctx['c'].collect(m['grid'],[records[i] for i in range(16)])
            target=root/'COLLECTED.json'
            if target.exists():
                if ctx['d'].parse_json(read(target))!=collected:raise TileError('existing collected result changed')
            else:write_new(target,collected)
            status='COMPLETE_COMPACT_INTERIOR_RADIUS_MET'
        result=sealed({'schema':'WU088_RESUMABLE_W1_SESSION_RESULT_V1','status':status,'prepared_sha256':expected_sha,
            'new_dispatched_tiles':dispatched,'new_dispatch_count':len(dispatched),'reused_tile_ids':[0],
            'accepted_tile_ids':sorted(records),'accepted_tiles':len(records),'prior_attempted_tiles':attempted,
            'total_native_dispatch_count':len(attempted)+len(dispatched),'new_native_cap_charged':len(dispatched)*200000,
            'total_native_cap_charged':(len(attempted)+len(dispatched))*200000,
            'max_dispatched_evaluations':m['max_dispatched_evaluations'],'elapsed_wall_ns':time.monotonic_ns()-started,
            'error':first_error,'tile_returns':new_results,'collection_sha256':collected['result_sha256'] if collected else None,
            'endpoint_included':False,'full_domain_integral':False,'scientific_admission':False,'production_admission':False},'result_sha256')
        write_new(session/'RESULT.json',result);return result
    finally:
        for handle in handles.values():
            p=handle['process']
            if p.poll() is None:
                try:os.killpg(p.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                p.wait(timeout=10)
            handle['stdout'].close();handle['stderr'].close()
        os.close(fd);(root/'RUN.claim').unlink()

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('prepare');p.add_argument('--directory',required=True);p.add_argument('--workers',type=int,default=3)
    for mode in ('run','worker','inspect'):
        p=sub.add_parser(mode);p.add_argument('--directory',required=True);p.add_argument('--prepared-sha256',required=True)
        if mode=='run':p.add_argument('--max-new-tiles',type=int,default=15)
        if mode=='worker':p.add_argument('--tile-id',type=int,required=True)
    args=ap.parse_args()
    try:
        if args.mode=='prepare':result=prepare(args.directory,args.workers)
        elif args.mode=='worker':result=worker(args.directory,args.prepared_sha256,args.tile_id)
        elif args.mode=='run':result=run_prepared(args.directory,args.prepared_sha256,args.max_new_tiles)
        else:
            ctx,m,plans=load_prepared(args.directory,args.prepared_sha256)
            records,failures,attempted=load_state(Path(args.directory),ctx,m,plans)
            result={'accepted_tiles':sorted(records),'rejected_tiles':failures,'attempted_tiles':attempted,'new_native_executions':0}
        print(json.dumps(result,sort_keys=True));return 0
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print('W1_RUNNER_REFUSED: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
