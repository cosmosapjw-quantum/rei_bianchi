#!/usr/bin/env python3
"""One shared scheduler for typed-cap independent cases and one ZERO segment."""
import argparse, importlib.util, json, os, pathlib, re, selectors, signal
import subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
AREA=HERE/'post_cap_001';OWN=AREA/'dispatch';RUNTIME=OWN/'runtime_001'
BINDING=AREA/'POST_CAP_DISPATCH_BINDING.json'
REVIEW=ROOT/'research/axbi_goal_20261014/reviews/POST_CAP_DISPATCH_REVIEW.json'
ZERO_BINDING=AREA/'ZERO_CONTINUATION_BINDING.json'
ZERO_REVIEW=ROOT/'research/axbi_goal_20261014/reviews/ZERO_CONTINUATION_REVIEW.json'
DECISION=ROOT/'research/axbi_goal_20261014/scenario/POST_FLRW_CAP_EXECUTION_DECISION.json'
QUEUE=['SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'];SEGMENT='ZERO_RESOURCE_CONTINUATION_001';MIB=1024*1024

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
RECOVER=load(HERE/'recover_queue.py','post_cap_original_recovery')
ORIGINAL=RECOVER.frozen_module()
def digest(path):return RECOVER.digest(path)
def save(path,value):
    data=(json.dumps(value,indent=2)+'\n').encode()
    # Post-cap metadata uses the new segment's128MiB reserve, capped here at1MiB.
    if RECOVER.bytes_under(OWN)+len(data)>MIB:raise RuntimeError('POST_CAP_METADATA_RESERVE')
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_bytes(data);temp.replace(path)

def typed_cap(case,external_code,groups):
    """Only exited, exactly bound accepted-step stops are nonblocking."""
    startfile=case['output'].parent/(case['case']+'_raw')/'execution_start.json'
    start=json.loads(startfile.read_text())
    if groups.get(start['observed_process_pid']):return False
    terminal=case['output']/'RETURN.txt';checkpoint=case['output']/'checkpoint.txt'
    if not terminal.exists() or not checkpoint.exists() or external_code!=101:return False
    values=RECOVER.key_values(terminal.read_text());lines=checkpoint.read_text().splitlines()
    if len(lines)!=6 or lines[0]!='AXBI_CHECKPOINT_V2':return False
    saved=[float(x) for x in lines[1].split()];counts=[int(x) for x in lines[2].split()]
    if values.get('status')!='STOPPED_CHECKPOINTED' or 'AXBI_RUNTIME_CAP' not in values.get('result',''):return False
    if counts[0]!=200000 or int(values.get('accepted','-1'))!=200000:return False
    if float(values['a'])!=saved[0] or int(values['attempts'])!=counts[1] or int(values['rhs_evaluations'])!=counts[4]:return False
    if float(values['max_newton_residual'])>1e-11 or float(values['last_error'])>=2e-4:return False
    if (case['output']/'case_id.txt').read_text()!=case['case']:return False
    if digest(case['output']/'config.cfg')!=digest(case['config']):return False
    if digest(case['output']/'source_identity.txt')!=json.loads(DECISION.read_text())['actual_zero_stop']['source_identity_sha256']:return False
    if start['binary_sha256']!=json.loads(BINDING.read_text())['original_binary_sha256']:return False
    # Inspect accepted-state gate rows once at terminal; VALUE rows stay values.
    with (case['output']/'ledgers.csv').open() as stream:
        if any(line.rstrip().endswith(',FAIL') for line in stream):return False
    return True

class Policy:
    def __init__(self):self.queue=list(QUEUE);self.dispatched=[];self.segment_dispatched=False;self.blocked=False
    def next(self,original_statuses,occupied,segment_ready,exists):
        if any(s not in ['LIVE','SUCCESS','ACCEPTED_STEP_CAP'] for s in original_statuses):self.blocked=True
        if self.blocked or occupied>=2:return None
        if segment_ready and not self.segment_dispatched:
            if exists(SEGMENT):self.blocked=True;raise RuntimeError('EXISTING_ZERO_SEGMENT_NO_RETRY')
            self.segment_dispatched=True;return SEGMENT
        if not self.queue or 2+len(self.dispatched)>=5:return None
        name=self.queue[0]
        if exists(name):self.blocked=True;raise RuntimeError('EXISTING_ORIGINAL_CASE_NO_RETRY')
        self.queue.pop(0);self.dispatched.append(name);return name

def observer_state(allow_parent=None):
    """Old observer must be irreversibly stopped; no second dispatcher."""
    groups=RECOVER.process_groups();old=[]
    for members in groups.values():
        for member in members:
            argv=member['argv'];pid=member['pid']
            if pid==os.getpid() or pid==allow_parent:continue
            if any(x.endswith('/run_campaign.py') for x in argv) and '--run' in argv:raise RuntimeError('ORIGINAL_DISPATCHER_STILL_ACTIVE')
            if any(x.endswith('/post_cap_dispatch.py') for x in argv) and ('--observe' in argv or '--start-detached' in argv):raise RuntimeError('ANOTHER_POST_CAP_DISPATCHER_ACTIVE')
            if any(x.endswith('/recover_queue.py') for x in argv) and '--observe' in argv:old.append(member)
    path=HERE/'recovery/runtime_001/RECOVERY_RECEIPT.json'
    receipt=json.loads(path.read_text())
    if receipt['status']!='STOPPED_AFTER_FAILURE' or receipt['jobs_dispatched'] or receipt['new_actual_starts']!=0:raise RuntimeError('RECOVERY_NOT_OBSERVATION_ONLY')
    return groups,dict(live_observer_processes=old,status=receipt['status'],receipt_sha256=digest(path),role='UNCHANGED_OBSERVATION_ONLY_NO_DISPATCH')

def scientific_groups(groups):
    return {pgid for pgid,members in groups.items() if any(any(arg.endswith('/axbi_reionization') or arg.endswith('/axbi_resource_continuation') for arg in member['argv']) for member in members)}

def validate():
    b=json.loads(BINDING.read_text());r=json.loads(REVIEW.read_text())
    if r.get('dispatch_execution_authorized') is not True:raise RuntimeError('DISPATCH_REVIEW_REQUIRED')
    for name,sha in r['reviewed_input_sha256'].items():
        if digest(ROOT/name)!=sha:raise RuntimeError('DISPATCH_REVIEWED_INPUT_CHANGED:'+name)
    if r['reviewed_input_sha256'].get(str(pathlib.Path(__file__).relative_to(ROOT)))!=digest(__file__):raise RuntimeError('ENTRYPOINT_NOT_REVIEWED')
    original,cases=ORIGINAL.frozen_plan()
    if original['binary_sha256']!=b['original_binary_sha256']:raise RuntimeError('ORIGINAL_BINARY_CHANGED')
    d=json.loads(DECISION.read_text());z=d['actual_zero_stop']
    for name,sha in [(z['checkpoint'],z['checkpoint_sha256']),(z['terminal'],z['terminal_sha256']),(z['config'],z['config_sha256'])]:
        if digest(ROOT/name)!=sha:raise RuntimeError('FROZEN_ZERO_STOP_CHANGED')
    return b,original,{c['case']:c for c in cases}

def segment_plan():
    if not ZERO_BINDING.exists() or not ZERO_REVIEW.exists():return None
    r=json.loads(ZERO_REVIEW.read_text())
    if r.get('continuation_execution_authorized') is not True:return None
    for name,sha in r['reviewed_input_sha256'].items():
        if digest(ROOT/name)!=sha:raise RuntimeError('CONTINUATION_REVIEW_CHANGED:'+name)
    dispatch=json.loads(REVIEW.read_text())
    if dispatch['reviewed_input_sha256'].get(str(ZERO_BINDING.relative_to(ROOT)))!=digest(ZERO_BINDING):raise RuntimeError('CONTINUATION_BINDING_NOT_DISPATCH_REVIEWED')
    b=json.loads(ZERO_BINDING.read_text());binary=ROOT/b['new_binary_path']
    if r['authorized_driver_argv']!=b['driver_argv'] or r['binary_sha256']!=b['new_binary_sha256'] or b['review_identity']['sha256']!=digest(ZERO_REVIEW):raise RuntimeError('CONTINUATION_WRAPPER_REVIEW_SCOPE')
    if digest(binary)!=b['new_binary_sha256']:raise RuntimeError('CONTINUATION_BINARY_CHANGED')
    out=ROOT/b['output_segment_path'];expected=ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_continuation_001'
    if out!=expected or (ROOT/b['driver_argv'][0]).resolve()!=binary.resolve():raise RuntimeError('CONTINUATION_ARGV_OUTPUT_SCOPE')
    return dict(binding=b,binary=binary,output=out,driver_argv=[str(binary)]+b['driver_argv'][1:])

def run_segment(plan,cpu,active,lock,launches):
    out=plan['output'];raw=out.parent/'ZERO_continuation_001_raw'
    if out.exists() or raw.exists():raise RuntimeError('EXISTING_CONTINUATION_NO_RETRY')
    raw.mkdir();argv=['/usr/bin/time','-v','-o',str(raw/'time.log'),'/usr/bin/timeout','--foreground','--signal=KILL','10799s','/usr/bin/taskset','-c',str(cpu),'/usr/bin/prlimit','--as=2147483648','--fsize='+str(1920*MIB),'--']+plan['driver_argv']
    env=dict(os.environ)
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','RAYON_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='1'
    save(raw/'POST_CAP_SEGMENT_START.json',dict(status='PLANNED',argv=argv,cpu=cpu,binding_sha256=digest(ZERO_BINDING),review_sha256=digest(ZERO_REVIEW),original_costs='PRESERVED_ZERO_PREFIX',scientific_admission='NOT_ISSUED'))
    proc=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    with lock:active[SEGMENT]=dict(pid=proc.pid,cpu=cpu);launches[SEGMENT]=dict(pid=proc.pid,argv=argv,cpu=cpu)
    save(raw/'POST_CAP_SEGMENT_PROCESS.json',dict(pid=proc.pid,argv=argv,cpu=cpu,status='PROCESS_STARTED'))
    sel=selectors.DefaultSelector();logs={};started=time.monotonic();written=0;reason=None
    for pipe,name in [(proc.stdout,'stdout'),(proc.stderr,'stderr')]:
        logs[pipe.fileno()]=(raw/(name+'.log')).open('xb');os.set_blocking(pipe.fileno(),False);sel.register(pipe,selectors.EVENT_READ)
    try:
        while sel.get_map() or proc.poll() is None:
            for key,_ in sel.select(timeout=.1):
                chunk=os.read(key.fileobj.fileno(),min(65536,max(1,126*MIB-written)))
                if not chunk:sel.unregister(key.fileobj);continue
                if written+len(chunk)>126*MIB:reason='SEGMENT_LOG_CAP';break
                logs[key.fileobj.fileno()].write(chunk);logs[key.fileobj.fileno()].flush();written+=len(chunk)
            if ORIGINAL.total_bytes(out)+ORIGINAL.total_bytes(raw)+RECOVER.bytes_under(OWN)>2048*MIB:reason='SEGMENT_TOTAL_OUTPUT_CAP'
            if time.monotonic()-started>=10800:reason='SEGMENT_WALL_CAP'
            if reason:
                try:os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                break
        code=proc.wait()
    finally:
        for f in logs.values():f.close()
        sel.close()
        with lock:active.pop(SEGMENT,None)
    terminal=(out/'RETURN.txt').read_text() if (out/'RETURN.txt').exists() else None
    values=RECOVER.key_values(terminal or '')
    complete=code==0 and values.get('status')=='COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' and values.get('a')=='0.2'
    result=dict(case='ZERO',segment=SEGMENT,status='SUCCESS' if complete else reason or 'SEGMENT_STOPPED_PARTIAL',exit_code=code,driver_return=terminal,wall_s=time.monotonic()-started,raw=str(raw),scientific_admission='NOT_ISSUED')
    save(raw/'POST_CAP_SEGMENT_RECEIPT.json',result);return result

def observe():
    b,original,cases=validate();groups,old_observer=observer_state(os.getppid())
    if RUNTIME.exists():raise RuntimeError('POST_CAP_ALREADY_STARTED')
    RUNTIME.mkdir(parents=True);policy=Policy();active={};launches={};lock=threading.Lock();futures={};results=[];polls=0;terminal_cache={}
    with ThreadPoolExecutor(max_workers=2) as pool:
        while True:
            groups,old_observer=observer_state(os.getppid())
            observations=[];statuses=[]
            for name in ['ZERO','SHEAR_PLUS']:
                obs=RECOVER.observe_original(cases[name],ORIGINAL)
                if obs['occupied']:status='LIVE'
                elif obs['status']=='SUCCESS':status='SUCCESS'
                else:
                    status=terminal_cache.get(name)
                    if status is None:status='ACCEPTED_STEP_CAP' if typed_cap(cases[name],obs['external_exit_code'],groups) else 'BLOCKED_FAILURE';terminal_cache[name]=status
                observations.append(obs);statuses.append(status)
                if obs.get('resource_violation'):statuses.append('BLOCKED_RESOURCE_BREACH')
            for future in list(futures):
                if not future.done():continue
                name=futures.pop(future)
                try:result=future.result()
                except Exception as e:result=dict(case=name,status='LAUNCHER_FAILURE',error=repr(e))
                if name!=SEGMENT and result['status']!='COMPLETE_EXIT_0':
                    result['typed_stop']='ACCEPTED_STEP_CAP' if typed_cap(cases[name],result.get('exit_code'),RECOVER.process_groups()) else 'BLOCKED_FAILURE'
                results.append(result)
                if name==SEGMENT and result['status']!='SUCCESS':policy.blocked=True
                if name!=SEGMENT and result['status']!='COMPLETE_EXIT_0' and result.get('typed_stop')!='ACCEPTED_STEP_CAP':policy.blocked=True
            segment=segment_plan();reserved=set(futures.values())
            while True:
                groups,_=observer_state(os.getppid())
                with lock:known_new_groups={item['pid'] for item in active.values()}
                if scientific_groups(groups)-({396140,396141}|known_new_groups):raise RuntimeError('UNACCOUNTED_SCIENTIFIC_PROCESS_GROUP')
                occupied=sum(x['occupied'] for x in observations)+len(reserved)
                candidate=policy.next(statuses,occupied,segment is not None,lambda name:(segment['output'].exists() or (segment['output'].parent/'ZERO_continuation_001_raw').exists()) if name==SEGMENT else (cases[name]['output'].exists() or (cases[name]['output'].parent/(name+'_raw')).exists()))
                if candidate is None:break
                ORIGINAL.frozen_plan()
                used={x['cpu'] for x in observations if x['occupied']}
                with lock:used.update(x['cpu'] for x in active.values())
                used.update(cases[n]['assigned_cpu'] for n in reserved if n!=SEGMENT)
                if SEGMENT in reserved:used.add(segment_cpu)
                cpu=next(c for c in [0,1] if c not in used)
                if candidate==SEGMENT:segment_cpu=cpu;future=pool.submit(run_segment,segment,cpu,active,lock,launches)
                else:cases[candidate]['assigned_cpu']=cpu;future=pool.submit(ORIGINAL.run_case,cases[candidate],original,cpu,active,lock,launches)
                futures[future]=candidate;reserved.add(candidate)
            polls+=1
            with lock:starts={n:dict(v) for n,v in launches.items()}
            receipt=dict(status='STOPPED_FOR_CLASSIFICATION' if policy.blocked else 'OBSERVING',pid=os.getpid(),polls=polls,original_failure_preserved=True,original_observations=observations,original_typed_statuses=statuses,old_recovery_observer=old_observer,original_actual_starts=2+sum(n!=SEGMENT for n in starts),continuation_actual_starts=int(SEGMENT in starts),total_full_starts=2+len(starts),prior_and_current_starts=original['prior_costs']['runs_started']+2+len(starts),new_starts=starts,remaining_signed_queue=policy.queue,segment_ready=segment is not None,segment_dispatched=policy.segment_dispatched,results=results,max_total_concurrent=2,scientific_admission='NOT_ISSUED')
            save(RUNTIME/'POST_CAP_RECEIPT.json',receipt)
            if policy.blocked and not futures and not any(x['occupied'] for x in observations):return 2
            if not policy.queue and not futures and policy.segment_dispatched and not any(x['occupied'] for x in observations):return 0
            time.sleep(2)

def detached():
    validate();observer_state()
    if RUNTIME.exists():raise RuntimeError('POST_CAP_ALREADY_STARTED')
    with (OWN/'observer.stdout').open('xb') as out,(OWN/'observer.stderr').open('xb') as error:
        proc=subprocess.Popen([sys.executable,str(__file__),'--observe'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=error,start_new_session=True,close_fds=True)
    for _ in range(50):
        if proc.poll() is not None:raise RuntimeError('POST_CAP_EARLY_EXIT')
        file=RUNTIME/'POST_CAP_RECEIPT.json'
        if file.exists() and json.loads(file.read_text())['polls']>=2:
            save(OWN/'DETACHED_START.json',dict(pid=proc.pid,progress='TWO_HEARTBEATS',stdout=str(OWN/'observer.stdout'),stderr=str(OWN/'observer.stderr')));print(proc.pid);return
        time.sleep(.1)
    raise RuntimeError('POST_CAP_HEARTBEAT_NOT_OBSERVED')

def self_check():
    p=Policy();calls=[]
    def fake_launch(name):calls.append(name)
    name=p.next(['ACCEPTED_STEP_CAP','LIVE'],1,False,lambda _:False);assert name=='SHEAR_MINUS';fake_launch(name)
    assert p.next(['ACCEPTED_STEP_CAP','LIVE'],2,True,lambda _:False) is None
    name=p.next(['ACCEPTED_STEP_CAP','LIVE'],1,True,lambda _:False);assert name==SEGMENT;fake_launch(name)
    assert p.next(['ACCEPTED_STEP_CAP','LIVE'],2,True,lambda _:False) is None
    for expected in QUEUE[1:]:
        name=p.next(['ACCEPTED_STEP_CAP','SUCCESS'],0,True,lambda _:False);assert name==expected;fake_launch(name)
    assert p.next(['ACCEPTED_STEP_CAP','SUCCESS'],0,True,lambda _:False) is None
    assert len(p.dispatched)+2==5 and len(calls)+2==6 and calls.count(SEGMENT)==1
    q=Policy();assert q.next(['ACCEPTED_STEP_CAP','SUCCESS'],0,True,lambda _:False)==SEGMENT
    for failure in ['NUMERICAL_FAILURE','UNKNOWN_EXIT','UNVERIFIED_CAP']:
        q=Policy();assert q.next([failure,'LIVE'],1,False,lambda _:False) is None and q.blocked
    q=Policy()
    try:q.next(['ACCEPTED_STEP_CAP','LIVE'],1,False,lambda _:True)
    except RuntimeError:pass
    else:raise AssertionError('duplicate accepted')
    assert q.blocked
    global BINDING,DECISION
    old_binding,old_decision=BINDING,DECISION
    with tempfile.TemporaryDirectory() as name:
        root=pathlib.Path(name);out=root/'CASE';out.mkdir();raw=root/'CASE_raw';raw.mkdir();config=root/'case.cfg';config.write_text('frozen')
        (out/'config.cfg').write_text('frozen');(out/'source_identity.txt').write_text('same library');(out/'case_id.txt').write_text('CASE')
        values='status=STOPPED_CHECKPOINTED\nresult=Err(AXBI_RUNTIME_CAP)\na=0.1\naccepted=200000\nattempts=600054\nrhs_evaluations=4200402\nmax_newton_residual=2.7e-13\nlast_error=2.6e-6\n'
        (out/'RETURN.txt').write_text(values);(out/'checkpoint.txt').write_text('AXBI_CHECKPOINT_V2\n0.1 1 0 0 0 0 1 1 1 1 1\n200000 600054 18 0 4200402 1\n0\n0\n0\n')
        (out/'ledgers.csv').write_text('ledger,status\nenergy,PASS\n');(raw/'execution_start.json').write_text(json.dumps({'observed_process_pid':99,'binary_sha256':'ORIGINAL'}))
        BINDING=root/'binding.json';BINDING.write_text(json.dumps({'original_binary_sha256':'ORIGINAL'}));DECISION=root/'decision.json';DECISION.write_text(json.dumps({'actual_zero_stop':{'source_identity_sha256':digest(out/'source_identity.txt')}}))
        case={'case':'CASE','output':out,'config':config}
        try:
            assert typed_cap(case,101,{}) is True
            assert typed_cap(case,101,{99:[{'state':'R'}]}) is False
            assert typed_cap(case,1,{}) is False
            (out/'ledgers.csv').write_text('energy,FAIL\n');assert typed_cap(case,101,{}) is False
            (out/'ledgers.csv').write_text('energy,PASS\n');(out/'RETURN.txt').write_text(values.replace('AXBI_RUNTIME_CAP','AXBI_NEWTON_FAILURE'));assert typed_cap(case,101,{}) is False
        finally:BINDING,DECISION=old_binding,old_decision
    assert scientific_groups({10:[{'argv':['/x/axbi_reionization']}],11:[{'argv':['python3','recover_queue.py']}]})=={10}
    print('POST_CAP_FAKE_SHARED_SCHEDULER_PASS; typed caps only, max2/max5+1, ZERO priority, no duplicate/retry, zero scientific starts')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--self-check',action='store_true');parser.add_argument('--start-detached',action='store_true');parser.add_argument('--observe',action='store_true');a=parser.parse_args()
    if a.self_check:self_check()
    elif a.start_detached:detached()
    elif a.observe:raise SystemExit(observe())
    else:parser.error('Choose one action')
