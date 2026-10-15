#!/usr/bin/env python3
"""Bounded continuation of the original five-case queue; never restarts a case."""
import argparse, hashlib, importlib.util, json, os, pathlib, re, subprocess
import sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
DECISION=ROOT/'research/axbi_goal_20261014/scenario/SUPERVISOR_LOSS_RECOVERY_DECISION.json'
BINDING=HERE/'recovery/RECOVERY_BINDING.json'
REVIEW=ROOT/'research/axbi_goal_20261014/reviews/SUPERVISOR_RECOVERY_REVIEW.json'
EVIDENCE=HERE/'recovery/runtime_001'
ORIGINAL=HERE/'allocations/32d11e733155'
ORPHANS={'ZERO':396140,'SHEAR_PLUS':396141}
QUEUE=['SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS']
MIB=1024*1024

def frozen_module():
    spec=importlib.util.spec_from_file_location('axbi_original_campaign',HERE/'run_campaign.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def digest(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def bytes_under(path):return sum(p.stat().st_size for p in path.rglob('*') if p.is_file()) if path.exists() else 0

def save(path,value):
    data=(json.dumps(value,indent=2)+'\n').encode()
    # Same allocation reserve, including preparation and original handoffs.
    if bytes_under(ORIGINAL)+bytes_under(HERE/'recovery')+len(data)>MIB:
        raise RuntimeError('ORIGINAL_PLUS_RECOVERY_ALLOCATION_RESERVE')
    temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(data);temporary.replace(path)

def process_groups():
    groups={}
    for proc in pathlib.Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:
            fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
            if fields[0] in ['Z','X']:continue
            argv=[x.decode() for x in (proc/'cmdline').read_bytes().split(bytes([0])) if x]
            member=dict(pid=int(proc.name),state=fields[0],argv=argv,start_boot_s=int(fields[19])/os.sysconf('SC_CLK_TCK'),rss_kib=int(fields[21])*os.sysconf('SC_PAGE_SIZE')//1024)
            groups.setdefault(int(fields[2]),[]).append(member)
        except (OSError,ValueError,IndexError,UnicodeDecodeError):pass
    return groups

def key_values(text):return dict(line.split('=',1) for line in text.splitlines() if '=' in line)

def observe_original(case,module):
    group=ORPHANS[case['case']];members=process_groups().get(group,[])
    raw=case['output'].parent/(case['case']+'_raw')
    start=json.loads((raw/'execution_start.json').read_text())
    if start['observed_process_pid']!=group or start['case']!=case['case']:
        raise RuntimeError('ORIGINAL_START_IDENTITY')
    identity=['--config',str(case['config']),'--output',str(case['output']),'--case',case['case']]
    match=lambda member: any(member['argv'][i:i+6]==identity for i in range(len(member['argv'])))
    output_bytes=module.total_bytes(case['output'])+module.total_bytes(raw)
    if members:
        if not any(match(member) for member in members):raise RuntimeError('LIVE_ORIGINAL_GROUP_IDENTITY_UNKNOWN')
        outer=next((member for member in members if member['pid']==group),None)
        if outer is None:raise RuntimeError('ORIGINAL_DEADLINE_START_UNKNOWN')
        uptime=float(pathlib.Path('/proc/uptime').read_text().split()[0])
        elapsed=uptime-outer['start_boot_s']
        return dict(case=case['case'],occupied=True,status='ADOPTED_LIVE',pgid=group,cpu=start['limits']['CPU_affinity'],elapsed_since_original_start_s=elapsed,remaining_original_wall_s=max(0,10800-elapsed),members=members,output_bytes=output_bytes,resource_violation=(output_bytes>2048*MIB or sum(x['rss_kib'] for x in members)>2*1024*1024 or elapsed>10800),monitor_gap='Original Python monitor absent; external timeout/prlimit and driver remain active. Gap duration/current peak unknown; no clocks reset.')
    timefile=raw/'time.log';terminal=case['output']/'RETURN.txt'
    external=timefile.read_text() if timefile.exists() else None
    returned=terminal.read_text() if terminal.exists() else None
    status_match=re.search(r'Exit status:\s*(\d+)',external or '')
    code=int(status_match.group(1)) if status_match else None
    values=key_values(returned or '')
    success=code==0 and values.get('status')=='COMPLETE_REPRESENTED_INTERVAL' and values.get('a')=='0.2'
    elapsed_match=re.search(r'Elapsed .*\):\s*([0-9:.]+)',external or '')
    elapsed_wall=None
    if elapsed_match:
        elapsed_wall=0.0
        for part in elapsed_match.group(1).split(':'):elapsed_wall=elapsed_wall*60+float(part)
    status='SUCCESS' if success else 'FAILED' if code is not None and (code!=0 or returned is not None) else 'UNKNOWN_EXIT'
    def metric(pattern):
        match=re.search(pattern,external or '');return float(match.group(1)) if match else None
    return dict(case=case['case'],occupied=False,status=status,pgid=group,external_exit_code=code,external_time_text=external,driver_return_text=returned,wall_s=elapsed_wall,CPU_user_s=metric(r'User time \(seconds\):\s*([0-9.]+)'),CPU_system_s=metric(r'System time \(seconds\):\s*([0-9.]+)'),peak_RSS_kib=metric(r'Maximum resident set size \(kbytes\):\s*(\d+)'),output_bytes=output_bytes,non_child_waitpid='NOT_USED',missing_evidence='UNKNOWN' if code is None or returned is None else None)

class QueuePolicy:
    """Pure accounting/dispatch policy; fake observations exercise it."""
    def __init__(self):self.queue=list(QUEUE);self.dispatched=[];self.stopped=False
    def next_case(self,original,new_active,exists):
        if any((not x['occupied'] and x['status']!='SUCCESS') or x.get('resource_violation') for x in original):self.stopped=True
        if self.stopped:return None
        occupied=sum(x['occupied'] for x in original)+len(new_active)
        if occupied>=2 or not self.queue or 2+len(self.dispatched)>=5:return None
        case=self.queue[0]
        if case in ORPHANS or exists(case):self.stopped=True;raise RuntimeError('PREVIOUSLY_EXISTING_QUEUED_CASE')
        self.queue.pop(0);self.dispatched.append(case);return case

def validated():
    binding=json.loads(BINDING.read_text());review=json.loads(REVIEW.read_text())
    if review.get('recovery_execution_authorized') is not True:raise RuntimeError('RECOVERY_REVIEW_REQUIRED')
    for name,sha in review['reviewed_input_sha256'].items():
        if digest(ROOT/name)!=sha:raise RuntimeError('RECOVERY_REVIEWED_INPUT_CHANGED:'+name)
    if review['reviewed_input_sha256'].get(str(pathlib.Path(__file__).relative_to(ROOT)))!=digest(__file__):raise RuntimeError('RECOVERY_ENTRYPOINT_NOT_REVIEWED')
    module=frozen_module();original,cases=module.frozen_plan()
    if original['binary_sha256']!=binding['binary_sha256']:raise RuntimeError('RECOVERY_BINARY_MISMATCH')
    if digest(ORIGINAL/'FULL_CAMPAIGN_RECEIPT.json')!=binding['original_receipt_sha256']:raise RuntimeError('ORIGINAL_RECEIPT_CHANGED')
    decision=json.loads(DECISION.read_text())
    if decision['preserved_authorization']['queue_order']!=QUEUE:raise RuntimeError('RECOVERY_QUEUE_SCOPE')
    return binding,module,original,{case['case']:case for case in cases}

def observe():
    binding,module,original,cases=validated()
    if EVIDENCE.exists():raise RuntimeError('EXISTING_RECOVERY_NO_RESTART')
    EVIDENCE.mkdir(parents=True);save(EVIDENCE/'observer_start.json',dict(pid=os.getpid(),sid=os.getsid(0),argv=sys.argv,binding_sha256=digest(BINDING),review_sha256=digest(REVIEW),original_starts=2,prior_pilot_costs=original['prior_costs'],scientific_admission='NOT_ISSUED'))
    policy=QueuePolicy();active={};launches={};lock=threading.Lock();futures={};results=[];polls=0
    with ThreadPoolExecutor(max_workers=2) as pool:
        while True:
            old=[observe_original(cases[name],module) for name in ORPHANS]
            for future in list(futures):
                if future.done():
                    case=futures.pop(future)
                    try:result=future.result()
                    except Exception as error:result=dict(case=case,status='LAUNCHER_FAILURE',error=repr(error))
                    results.append(result)
                    if result['status']!='COMPLETE_EXIT_0':policy.stopped=True
            new_active=set(futures.values())
            def exists(name):
                case=cases[name];return case['output'].exists() or (case['output'].parent/(name+'_raw')).exists()
            # Refresh exact frozen identity and group observations at every dispatch.
            while True:
                old=[observe_original(cases[name],module) for name in ORPHANS]
                candidate=policy.next_case(old,new_active,exists)
                if candidate is None:break
                module.frozen_plan()
                used={x['cpu'] for x in old if x['occupied']}
                with lock:used.update(x['cpu'] for x in active.values())
                used.update(cases[name].get('assigned_cpu') for name in new_active)
                cpu=next(cpu for cpu in [0,1] if cpu not in used)
                cases[candidate]['assigned_cpu']=cpu
                future=pool.submit(module.run_case,cases[candidate],original,cpu,active,lock,launches);futures[future]=candidate;new_active.add(candidate)
            polls+=1
            with lock:observed_starts={name:dict(value) for name,value in launches.items()}
            receipt=dict(status='STOPPED_AFTER_FAILURE' if policy.stopped else 'COMPLETE_ORIGINAL_PHASE1' if not policy.queue and not futures and all(x['status']=='SUCCESS' for x in old) else 'OBSERVING',pid=os.getpid(),polls=polls,adopted_original_cases=old,original_phase1_starts=2,new_actual_starts=len(observed_starts),phase1_actual_starts=2+len(observed_starts),prior_and_current_actual_starts=original['prior_costs']['runs_started']+2+len(observed_starts),observed_new_starts=observed_starts,jobs_dispatched=policy.dispatched,remaining_queue=policy.queue,new_results=results,max_concurrent_cases=2,scientific_admission='NOT_ISSUED')
            save(EVIDENCE/'RECOVERY_RECEIPT.json',receipt)
            if policy.stopped and not futures and not any(x['occupied'] for x in old):return 2
            if not policy.queue and not futures and all(x['status']=='SUCCESS' for x in old):return 0
            time.sleep(2)

def detached():
    validated()
    if EVIDENCE.exists():raise RuntimeError('RECOVERY_ALREADY_STARTED')
    logdir=HERE/'recovery';stdout=logdir/'observer.stdout';stderr=logdir/'observer.stderr'
    with stdout.open('xb') as out,stderr.open('xb') as error:
        process=subprocess.Popen([sys.executable,str(__file__),'--observe'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=error,start_new_session=True,close_fds=True)
    for _ in range(50):
        if process.poll() is not None:raise RuntimeError('DETACHED_RECOVERY_EARLY_EXIT')
        heartbeat=EVIDENCE/'RECOVERY_RECEIPT.json'
        if heartbeat.exists() and json.loads(heartbeat.read_text())['polls']>=2:
            record=dict(pid=process.pid,observed_progress='TWO_MONITOR_POLLS',stdout=str(stdout),stderr=str(stderr),independent_session=True)
            save(logdir/'DETACHED_START.json',record);print(json.dumps(record));return
        time.sleep(0.1)
    raise RuntimeError('DETACHED_MONITOR_PROGRESS_NOT_OBSERVED')

def self_check():
    live=[dict(occupied=True,status='ADOPTED_LIVE'),dict(occupied=True,status='ADOPTED_LIVE')]
    p=QueuePolicy();assert p.next_case(live,set(),lambda name:False) is None and p.dispatched==[]
    one=[dict(occupied=False,status='SUCCESS'),live[1]]
    first=p.next_case(one,set(),lambda name:False);assert first=='SHEAR_MINUS'
    assert p.next_case(one,{first},lambda name:False) is None
    # One completed original slot can dispatch one next case, never a duplicate.
    second=p.next_case(one,set(),lambda name:False);assert second=='SHEAR_HALF_PLUS'
    assert p.next_case(one,{second},lambda name:False) is None
    third=p.next_case(one,set(),lambda name:False);assert third=='SHEAR_HALF_MINUS'
    assert p.next_case(one,set(),lambda name:False) is None and len(p.dispatched)+2==5
    q=QueuePolicy()
    try:q.next_case(one,set(),lambda name:True)
    except RuntimeError:pass
    else:raise AssertionError('existing case not refused')
    assert q.stopped
    for failure in ['FAILED','UNKNOWN_EXIT']:
        q=QueuePolicy();assert q.next_case([dict(occupied=False,status=failure),live[1]],set(),lambda name:False) is None and q.stopped
    q=QueuePolicy();assert q.next_case([dict(occupied=True,status='ADOPTED_LIVE',resource_violation=True),live[1]],set(),lambda name:False) is None
    # Fake launch calls and detached observer Popen: no real process is started.
    calls=[]
    def fake_launch(case):calls.append(case);return dict(pid=9000+len(calls),case=case)
    for name in p.dispatched:fake_launch(name)
    assert calls==QUEUE and len(calls)+2==5
    global HERE,ORIGINAL,EVIDENCE
    saved=(HERE,ORIGINAL,EVIDENCE,subprocess.Popen,globals()['validated'])
    with tempfile.TemporaryDirectory() as directory:
        HERE=pathlib.Path(directory);ORIGINAL=HERE/'original';ORIGINAL.mkdir();EVIDENCE=HERE/'recovery/runtime_001';EVIDENCE.parent.mkdir()
        captured={}
        class FakeProcess:
            pid=9999
            def poll(self):return None
        def fake_popen(argv,**kwargs):
            captured.update(kwargs);captured['argv']=argv;EVIDENCE.mkdir();(EVIDENCE/'RECOVERY_RECEIPT.json').write_text(json.dumps({'polls':2}));return FakeProcess()
        subprocess.Popen=fake_popen;globals()['validated']=lambda:None
        try:
            detached()
            assert captured['start_new_session'] is True and captured['stdin']==subprocess.DEVNULL
            assert captured['stdout'].name.endswith('observer.stdout') and captured['stderr'].name.endswith('observer.stderr')
            assert captured['argv'][-1]=='--observe'
        finally:
            HERE,ORIGINAL,EVIDENCE,subprocess.Popen,globals()['validated']=saved
    print('FAKE_PROCESS_QUEUE_CHECK_PASS; adopted occupancy, max2/max5, exact order, no duplicate/retry, stop on failure; zero scientific process starts')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--self-check',action='store_true');parser.add_argument('--start-detached',action='store_true');parser.add_argument('--observe',action='store_true');args=parser.parse_args()
    if args.self_check:self_check()
    elif args.start_detached:detached()
    elif args.observe:raise SystemExit(observe())
    else:parser.error('Choose one action')
