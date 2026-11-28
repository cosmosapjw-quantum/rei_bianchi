"""Fixed four-tile strip experiment, two guarded workers, create-only attempts.

No full-grid launch or automatic retry. Previous W1 and endpoint calculations
are read-only dependencies. The pinned native solver and process host are reused.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
RUNTIME=HERE/'runtime'
HOST=HERE.parent/'w1_parallel_20261002_v1/process_host/host.py'
HOST_SHA='1274f166132e0fed8af61b71db00f1f4bacae2e9fea1b8c97ba33599dd808c5e'
IDS=(20,52,105,57)
LIMITS={'precision_bits':128,'radius_exp':-57,'relative_goal':128,'max_evaluations':200000,
        'max_integration_calls':1024,'wall_seconds':120,'queued_panels':64,'degree_limit':64,'memory_mib':1024}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
def seal(o,key):return {**o,key:hashlib.sha256(canonical(o)).hexdigest()}
def read(p):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    return json.loads(Path(p).read_bytes(),object_pairs_hook=pairs)
def write(p,o):
    with Path(p).open('xb') as f:f.write(json.dumps(o,indent=2,sort_keys=True).encode()+b'\n');f.flush();os.fsync(f.fileno())
    fd=os.open(Path(p).parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def module(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def host():
    if sha(HOST)!=HOST_SHA:raise ValueError('process host pin changed')
    h=module(HOST,'_wu088_strip_process_host');h.identity();return h
def collection():return module(HERE/'collection/collector.py','_wu088_strip_collection')
def verify_scope():
    s=read(HERE/'SCOPE.json')
    if s['pilot_cell_ids']!=list(IDS) or s['native_limits']!=LIMITS or s['max_new_native_invocations']!=4 or s['max_concurrent_workers']!=2 or s['worker_wall_seconds']!=180 or s['worker_memory_mib']!=1024:
        raise ValueError('fixed bounded pilot scope changed')
    return s
def ref(p):return {'namespace':'continuation','path':str(Path(p).relative_to(HERE)),'sha256':sha(p)}

def prepare():
    verify_scope()
    if (RUNTIME/'PREPARE_STARTED.json').exists():raise ValueError('prepare already claimed')
    write(RUNTIME/'PREPARE_STARTED.json',{'runner_sha256':sha(__file__),'scope':ref(HERE/'SCOPE.json')})
    c=collection();ctx=c.context();plan=c.make_plan(ctx);reused=c.import_w1(ctx,plan)
    if len(reused)!=16:raise ValueError('all16W1reuse required')
    for n in ('plans','raw','normalized','attempts'):(RUNTIME/n).mkdir(exist_ok=False)
    write(RUNTIME/'GRID_PLAN.json',plan);write(RUNTIME/'REUSED_W1.json',reused)
    locals=[]
    for cell in IDS:
        local=c.local_plan(ctx,plan,cell);p=RUNTIME/'plans'/f'{cell:03d}.json';write(p,local)
        locals.append({'cell_id':cell,'file':ref(p),'plan_sha256':local['plan_sha256']})
    prepared=seal({'schema':'WU088_W3_STRIP_PREPARED_V1','scope':ref(HERE/'SCOPE.json'),'grid':ref(RUNTIME/'GRID_PLAN.json'),
        'reused':ref(RUNTIME/'REUSED_W1.json'),'local_plans':locals,'runner_sha256':sha(__file__),
        'collector_sha256':sha(HERE/'collection/collector.py'),'process_host':host().identity(),'limits':LIMITS,
        'pilot_cell_ids':list(IDS),'concurrency':2,'worker_wall_seconds':180,'worker_memory_mib':1024,
        'all_source_science_previous_runs_reused':True,'scientific_admission':False,'production_admission':False},'prepared_sha256')
    write(RUNTIME/'PREPARED.json',prepared)
    write(RUNTIME/'REUSE_ONLY_COVERAGE.json',c.collect_partial(plan,reused))
    print(json.dumps({'prepared_sha256':prepared['prepared_sha256'],'reused':len(reused),'new_pilot_cells':list(IDS)}))

def load_prepared(expected):
    verify_scope();m=read(RUNTIME/'PREPARED.json')
    if m.get('prepared_sha256')!=expected or seal({k:v for k,v in m.items()if k!='prepared_sha256'},'prepared_sha256')!=m:
        raise ValueError('prepared identity mismatch')
    if m['runner_sha256']!=sha(__file__) or m['collector_sha256']!=sha(HERE/'collection/collector.py') or m['process_host']!=host().identity():
        raise ValueError('prepared source changed')
    for r in (m['scope'],m['grid'],m['reused'],*[x['file']for x in m['local_plans']]):
        if ref(HERE/r['path'])!=r:raise ValueError('prepared payload changed')
    if m['pilot_cell_ids']!=list(IDS) or m['limits']!=LIMITS or m['concurrency']!=2 or m['worker_wall_seconds']!=180 or m['worker_memory_mib']!=1024:
        raise ValueError('prepared limits changed')
    return m

def worker(expected,cell):
    m=load_prepared(expected)
    if type(cell)is not int or cell not in IDS:raise ValueError('cell outside fixed pilot')
    attempt=RUNTIME/'attempts'/f'{cell:03d}';dispatch=read(attempt/'DISPATCH.json')
    if dispatch['cell_id']!=cell or dispatch['prepared_sha256']!=expected or (attempt/'RETURN.json').exists():raise ValueError('dispatch not owned or already returned')
    with (attempt/'WORKER_STARTED.json').open('x')as f:json.dump({'pid':os.getpid(),'cell_id':cell,'prepared_sha256':expected},f)
    c=collection();ctx=c.context();grid=read(RUNTIME/'GRID_PLAN.json')
    if c.make_plan(ctx)!=grid:raise ValueError('grid no longer bound to actual source')
    local=next(x for x in m['local_plans']if x['cell_id']==cell);plan=read(HERE/local['file']['path'])
    if c.local_plan(ctx,grid,cell)!=plan:raise ValueError('local plan mismatch')
    h=host();h.install(ctx['d']);w=ctx['w1_runner']
    ctx['d'].run_task(w.INPUT,HERE/local['file']['path'],local['plan_sha256'],0,w.BUILD,w.BUILD_SHA,LIMITS,RUNTIME/'raw'/f'{cell:03d}.json')
    print(json.dumps({'status':'NATIVE_RECEIPT_WRITTEN','cell_id':cell}))

def resources():
    cpus=sorted(os.sched_getaffinity(0));q=Path('/sys/fs/cgroup/cpu.max').read_text().split();mem=Path('/sys/fs/cgroup/memory.max').read_text().strip()
    if len(cpus)<2 or (q[0]!='max' and int(q[0])<2*int(q[1])):raise ValueError('two CPU quota unavailable')
    need=(2*(1024+1024)+2048)*1024**2
    if mem=='max' or int(mem)<need:raise ValueError('finite sufficient cgroup memory required')
    return {'affinity':cpus,'cpu_max':q,'memory_max_bytes':int(mem),'reserved_bytes':need,'concurrency':2}

def run_queue(ids,launch,complete,*,concurrency=2,wall_seconds=180):
    """Drain observed completions before dispatch; never retry an attempted ID.

    Test seam accepts synthetic launch/complete callbacks. Actual CLI supplies
    only its fixed guarded worker and validator; no command override exists.
    """
    pending=list(ids);active={};returns=[];dispatched=[];stop=False
    try:
        while pending or active:
            finished=[]
            for cell,h in list(active.items()):
                p=h['process'];code=p.poll()
                if code is None and time.monotonic_ns()-h['start']>wall_seconds*10**9:
                    h['timed_out']=True;p.kill();code=p.wait(timeout=10)
                if code is None:continue
                r=complete(cell,h,code);returns.append(r);finished.append(cell)
                if not r['accepted']:stop=True
            for cell in finished:del active[cell]
            if stop:pending=[]
            while pending and len(active)<concurrency:
                cell=pending.pop(0);dispatched.append(cell)
                try:active[cell]=launch(cell)
                except Exception as exc:
                    returns.append({'cell_id':cell,'accepted':False,'status':'WORKER_LAUNCH_FAILED','error':str(exc),'worker_returncode':None,'timed_out':False});stop=True;pending=[];break
            if active:time.sleep(.05)
        return dispatched,returns
    finally:
        for h in active.values():
            p=h['process']
            if p.poll()is None:p.kill();p.wait(timeout=10)
            for key in ('stdout','stderr'):
                if key in h and not h[key].closed:h[key].close()

def run(expected):
    m=load_prepared(expected);admission=resources();h=host();c=collection();ctx=c.context();grid=read(RUNTIME/'GRID_PLAN.json')
    reused=c.import_w1(ctx,grid)
    if reused!=read(RUNTIME/'REUSED_W1.json'):raise ValueError('fresh W1 reuse differs')
    write(RUNTIME/'RUN_STARTED.json',{'schema':'WU088_W3_STRIP_RUN_START_V1','prepared_sha256':expected,'resource_admission':admission,'runner_sha256':sha(__file__),'controller_pid':os.getpid(),'max_native_dispatches':4})
    records=list(reused);t0=time.monotonic_ns()
    def launch(cell):
        ad=RUNTIME/'attempts'/f'{cell:03d}';ad.mkdir(exist_ok=False)
        write(ad/'DISPATCH.json',{'cell_id':cell,'prepared_sha256':expected,'native_execution_requested':True,'native_evaluation_cap_charged':200000})
        so=(ad/'worker.stdout').open('xb');se=(ad/'worker.stderr').open('xb')
        command=[str(Path(sys.executable).resolve()),'-B',str(Path(__file__).resolve()),'worker','--prepared-sha256',expected,'--cell-id',str(cell)]
        try:p=h.spawn_guarded(command,stdout=so,stderr=se,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'},memory_mib=1024)
        except BaseException:so.close();se.close();raise
        return {'process':p,'stdout':so,'stderr':se,'start':time.monotonic_ns(),'timed_out':False}
    def complete(cell,handle,code):
        handle['stdout'].close();handle['stderr'].close();rp=RUNTIME/'raw'/f'{cell:03d}.json';error=None;norm=None
        try:
            if code!=0 or handle['timed_out']:raise ValueError('worker failed or timed out')
            norm=c.normalize_new(c.context(),grid,cell,rp);write(RUNTIME/'normalized'/f'{cell:03d}.json',norm);records.append(norm)
        except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError)as exc:error=str(exc)
        receipt=read(rp)if rp.exists()else None
        observed=bool(receipt and receipt.get('wrapper',{}).get('native_execution_observed')is True)
        r={'schema':'WU088_W3_STRIP_TILE_RETURN_V1','cell_id':cell,'accepted':norm is not None,'status':'RADIUS_MET'if norm else 'REJECTED','worker_returncode':code,'worker_pid':handle['process'].pid,'worker_started_file':ref(RUNTIME/'attempts'/f'{cell:03d}'/'WORKER_STARTED.json')if(RUNTIME/'attempts'/f'{cell:03d}'/'WORKER_STARTED.json').exists()else None,'timed_out':handle['timed_out'],'error':error,'native_execution_observed':observed,'native_receipt':ref(rp)if receipt else None,'normalized':ref(RUNTIME/'normalized'/f'{cell:03d}.json')if norm else None,'elapsed_wall_ns':time.monotonic_ns()-handle['start'],'residual_native_claim_observed':Path(str(rp)+'.claim').exists(),'root_removed_residual_claim':False}
        write(RUNTIME/'attempts'/f'{cell:03d}'/'RETURN.json',r);return r
    dispatched,returns=run_queue(IDS,launch,complete)
    for r in returns:
        if r['status']=='WORKER_LAUNCH_FAILED':
            p=RUNTIME/'attempts'/f"{r['cell_id']:03d}"/'RETURN.json'
            if p.parent.exists()and not p.exists():write(p,r)
    coverage=c.collect_partial(grid,records);write(RUNTIME/'COVERAGE.json',coverage)
    result={'schema':'WU088_W3_STRIP_SESSION_RESULT_V1','status':'PILOT_COMPLETE'if len(returns)==4 and all(r['accepted']for r in returns)else 'STOPPED_FIRST_REJECTION','prepared_sha256':expected,'native_dispatch_attempts':len(dispatched),'dispatched_cell_ids':dispatched,'returns':returns,'reused_W1_tiles':16,'accepted_new_cells':sum(r['accepted']for r in returns),'elapsed_wall_ns':time.monotonic_ns()-t0,'coverage':ref(RUNTIME/'COVERAGE.json'),'native_evaluation_cap_charged':200000*len(dispatched),'endpoint_included':False,'scientific_admission':False,'production_admission':False}
    write(RUNTIME/'SESSION_RESULT.json',result);print(json.dumps(result));return 0 if result['status']=='PILOT_COMPLETE'else 2

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('prepare','run','worker'));p.add_argument('--prepared-sha256');p.add_argument('--cell-id',type=int);a=p.parse_args()
    if a.action=='prepare':prepare();return 0
    if not a.prepared_sha256:raise ValueError('prepared SHA required')
    if a.action=='worker':worker(a.prepared_sha256,a.cell_id);return 0
    return run(a.prepared_sha256)

if __name__=='__main__':raise SystemExit(main())
