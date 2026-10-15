#!/usr/bin/env python3
"""Five finite full AX07/08 primary cases after exact changed-resource review.

Driver prewrite ceiling1920MiB; launcher envelope<=127MiB plus1MiB allocation reserve.
No resume/retry, arbitrary case, remote executor or scientific admission.
"""
import argparse, hashlib, json, os, pathlib, resource, selectors, signal
import subprocess, tempfile, time, re
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
ROOT=pathlib.Path(__file__).resolve().parents[4]
BINDING=ROOT/'research/axbi_goal_20261014/driver/full/FULL_DRIVER_BINDING.json'
REVIEW=ROOT/'research/axbi_goal_20261014/reviews/FULL_RESOURCE_REVIEW.json'
FULL=ROOT/'research/axbi_goal_20261014/driver/full'
MIB=1024*1024
ENVELOPE=127*MIB
LOG_BUDGET=126*MIB
DRIVER_BUDGET=1920*MIB

def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def total_bytes(path):
    return sum(p.stat().st_size for p in pathlib.Path(path).rglob('*') if p.is_file())

def save(path,value,envelope):
    data=(json.dumps(value,indent=2)+'\n').encode()
    old=path.stat().st_size if path.exists() else 0
    if total_bytes(envelope)-old+len(data)>ENVELOPE:
        raise RuntimeError('LAUNCHER_TOTAL_OUTPUT_LIMIT')
    path.write_bytes(data)

def parse_config(path):
    return dict(line.strip().split('=',1) for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#'))

def frozen_plan():
    b=json.loads(BINDING.read_text())
    binary=ROOT/b['compiled_binary_path']
    if not b.get('binary_sha256') or digest(binary)!=b['binary_sha256']:
        raise RuntimeError('FINAL_RELEASE_BINARY_IDENTITY_MISSING_OR_CHANGED')
    for name,sha in b['source_sha256'].items():
        if digest(ROOT/name)!=sha: raise RuntimeError('FROZEN_SOURCE_CHANGED:'+name)
    for name,sha in b['config_sha256'].items():
        if digest(ROOT/name)!=sha: raise RuntimeError('FROZEN_CONFIG_CHANGED:'+name)
    review=json.loads(REVIEW.read_text())
    if review.get('full_execution_authorized') is not True:
        raise RuntimeError('EXPLICIT_FULL_RESOURCE_REVIEW_REQUIRED')
    for name,sha in review['reviewed_input_sha256'].items():
        if digest(ROOT/name)!=sha:raise RuntimeError('REVIEWED_INPUT_CHANGED:'+name)
    if review['reviewed_input_sha256'].get(str(pathlib.Path(__file__).resolve().relative_to(ROOT)))!=digest(__file__):
        raise RuntimeError('LAUNCHER_REVIEW_IDENTITY_MISSING')
    if review.get('driver_output_limit_bytes')!=DRIVER_BUDGET:raise RuntimeError('EXACT_FULL_DRIVER_CAP_REVIEW_REQUIRED')
    cases=[]
    for case in b['cases']:
        config=ROOT/case['config'];c=parse_config(config)
        expected={'q_ref':str(case['q_ref']),'same_h':'false','end_zbar':'4.0','max_steps':'200000','max_attempts':'650000','max_rhs':'20000000','max_wall_s':'10800','output_budget_mib':'2048','spectra_every_accepted':'60'}
        if any(c.get(k)!=v for k,v in expected.items()):raise RuntimeError('FULL_CONFIG_SCOPE:'+case['case'])
        cases.append(dict(case=case['case'],config=config,output=ROOT/case['output'],binary=binary))
    if len(cases)!=5 or len({c['case'] for c in cases})!=5:raise RuntimeError('FROZEN_FIVE_CASES_REQUIRED')
    return b,cases

def run_case(case,binding,cpu,active,active_lock,launches):
    case_root=case['output'];raw=case_root.parent/(case['case']+'_raw')
    if case_root.exists() or raw.exists(): raise RuntimeError('EXISTING_ATTEMPT_NO_RESTART:'+str(case_root))
    # Driver requires an absent output directory. Raw lives alongside it and
    # remains included in per-case aggregate receipts and launcher envelope.
    raw.mkdir(parents=True)
    argv=['/usr/bin/time','-v','-o',str(raw/'time.log'),'/usr/bin/timeout','--foreground','--signal=KILL','10799s','/usr/bin/taskset','-c',str(cpu),'/usr/bin/prlimit','--as=2147483648','--fsize='+str(DRIVER_BUDGET),'--',str(case['binary']),'--config',str(case['config']),'--output',str(case_root),'--case',case['case']]
    env=dict(os.environ)
    for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','RAYON_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[k]='1'
    pre=dict(node_id='AX07' if case['case']=='ZERO' else 'AX08',case=case['case'],argv=argv,cwd=str(ROOT),source_sha256=binding['source_sha256'],binary_sha256=binding['binary_sha256'],config_sha256=digest(case['config']),review_sha256=digest(REVIEW),launcher_sha256=digest(__file__),requested_executor_identity={'model':'gpt-6.1-sol','reasoning_effort':'medium'},observed_executor_identity_or_null=None,limits={'wall_seconds':10800,'timeout_seconds':10799,'cpu_threads':1,'CPU_affinity':cpu,'virtual_address_space_bytes':2*1024**3,'RSS_ceiling_bytes':2*1024**3,'RSS_kind':'observed by externaltime; AS cap is stronger distinct mechanism','driver_aggregate_output_bytes':DRIVER_BUDGET,'launcher_output_bytes':ENVELOPE,'combined_output_bytes':2048*MIB,'allocation_receipt_reserve_bytes':MIB,'automatic_retries':0},status='STARTING')
    save(raw/'execution_plan.json',pre,raw)
    before=resource.getrusage(resource.RUSAGE_CHILDREN);t0=time.monotonic()
    proc=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    with active_lock:
        active[case['case']]=dict(pid=proc.pid,output=case_root,cpu=cpu)
        launches[case['case']]=dict(pid=proc.pid,argv=argv,config_sha256=pre['config_sha256'],raw=str(raw))
    save(raw/'execution_start.json',dict(pre,status='PROCESS_STARTED',observed_process_pid=proc.pid),raw)
    sel=selectors.DefaultSelector();files={}
    for stream,name in [(proc.stdout,'stdout'),(proc.stderr,'stderr')]:
        files[stream.fileno()]=open(raw/(name+'.log'),'xb');os.set_blocking(stream.fileno(),False);sel.register(stream,selectors.EVENT_READ)
    reason=None;log_bytes=0;peak_total=0
    def stop(why):
        nonlocal reason
        if reason is None:reason=why
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    try:
        while sel.get_map() or proc.poll() is None:
            for key,_ in sel.select(timeout=0.05):
                fd=key.fileobj.fileno();remaining=LOG_BUDGET-log_bytes
                if remaining<=0:
                    stop('LAUNCHER_LOG_CAP');sel.unregister(key.fileobj);continue
                data=os.read(fd,min(65536,remaining))
                if not data:sel.unregister(key.fileobj);continue
                files[fd].write(data);files[fd].flush();log_bytes+=len(data)
            current=total_bytes(case_root)+total_bytes(raw);peak_total=max(peak_total,current)
            if current>=2048*MIB:stop('COMBINED_OUTPUT_CAP')
            if total_bytes(case_root)>DRIVER_BUDGET:stop('DRIVER_OUTPUT_CAP_DEFECT')
            if time.monotonic()-t0>=10800:stop('WALL_CAP')
            if reason and proc.poll() is not None:
                # At the log cap close unread pipe tails; record explicitly.
                if reason=='LAUNCHER_LOG_CAP':break
        exit_code=proc.wait()
    finally:
        for f in files.values():f.close()
        sel.close()
        with active_lock:active.pop(case['case'],None)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    time_text=(raw/'time.log').read_text() if (raw/'time.log').exists() else ''
    match=re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',time_text)
    measured_rss=int(match.group(1)) if match else None
    terminal_path=case_root/'RETURN.txt'
    terminal_text=terminal_path.read_text() if terminal_path.exists() else None
    elapsed=time.monotonic()-t0
    user=re.search(r'User time \(seconds\):\s*([0-9.]+)',time_text)
    system=re.search(r'System time \(seconds\):\s*([0-9.]+)',time_text)
    per_case_cpu=float(user.group(1))+float(system.group(1)) if user and system else None
    status='COMPLETE_EXIT_0' if exit_code==0 else 'FAILED_EXIT_'+str(exit_code)
    if reason:status=reason
    counters={}
    checkpoint=case_root/'checkpoint.txt'
    if checkpoint.exists():
        try:
            counters={'raw_text':checkpoint.read_text()}
        except OSError:pass
    result=dict(pre,status=status,exit_code=exit_code,wall_seconds=elapsed,cpu_seconds=per_case_cpu,cpu_seconds_scope='external GNU time per-case; global children accounting not used under parallel execution',peak_RSS_kib=measured_rss,resource_children_cumulative_max_RSS_kib=after.ru_maxrss,driver_terminal_record=terminal_text,peak_RSS_scope='external GNU time per-case measurement; cumulative children fallback separately labelled',external_resource_capture=str(raw/'time.log'),peak_recursively_observed_output_bytes=peak_total,final_output_bytes=total_bytes(case_root)+total_bytes(raw),stdout_path=str(raw/'stdout.log'),stderr_path=str(raw/'stderr.log'),checkpoint_path=str(checkpoint) if checkpoint.exists() else None,checkpoint=counters,raw_stream_tail_status='NOT_CAPTURED_AFTER_CAP_KILL' if reason=='LAUNCHER_LOG_CAP' else 'CAPTURED_UNTIL_PROCESS_EXIT',scientific_admission='NOT_ISSUED')
    save(raw/'execution_receipt.json',result,raw)
    return result

def self_check():
    with tempfile.TemporaryDirectory() as name:
        p=pathlib.Path(name);(p/'nested').mkdir();(p/'nested/a').write_bytes(b'abc')
        assert total_bytes(p)==3
        save(p/'r.json',{'mechanical_only':True},p)
        assert json.loads((p/'r.json').read_text())['mechanical_only']
        assert DRIVER_BUDGET+ENVELOPE+MIB==2048*MIB and LOG_BUDGET+MIB==ENVELOPE
    print('MECHANICAL_SELF_CHECK_PASS; no driver process started')

def memory_available_kib():
    for line in pathlib.Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'):return int(line.split()[1])
    return 0

def current_group_rss_kib(pgid):
    total=0
    for entry in pathlib.Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])==pgid:total+=int(fields[21])*os.sysconf('SC_PAGE_SIZE')//1024
        except (OSError,ValueError,IndexError):pass
    return total

def checkpoint_progress(path):
    try:
        lines=(path/'checkpoint.txt').read_text().splitlines()
        return int(lines[2].split()[0])>=60
    except (OSError,ValueError,IndexError):return False

def run_campaign():
    import threading
    binding,cases=frozen_plan();cpus=sorted(os.sched_getaffinity(0))
    max_parallel_authorized=json.loads(REVIEW.read_text()).get('max_parallel_authorized',2)
    if max_parallel_authorized not in [2,4]:raise RuntimeError('INVALID_PARALLEL_ALLOCATION')
    if len(cpus)<2:raise RuntimeError('TWO_DISTINCT_ALLOWED_CPUS_REQUIRED')
    group=FULL/'allocations'/binding['binary_sha256'][:12]
    if group.exists():raise RuntimeError('EXISTING_FULL_ALLOCATION_NO_RETRY')
    group.mkdir(parents=True);active={};launches={};lock=threading.Lock();queue=list(cases);results=[];events=[]
    baseline=dict(node_ids=['AX07','AX08'],status='STARTING',binding_sha256=digest(BINDING),review_sha256=digest(REVIEW),binary_sha256=binding['binary_sha256'],prior_costs=binding['prior_costs'],cases=[],solver_runs_started=0,parallel_limit=2,max_parallel_authorized=max_parallel_authorized,phase1_limits=binding['phase1_limits'],scientific_admission='NOT_ISSUED')
    save(group/'FULL_CAMPAIGN_RECEIPT.json',baseline,group)
    parallel=2;failed=False;started=0;futures={};had_checkpoint=False
    with ThreadPoolExecutor(max_workers=4) as pool:
        while queue or futures:
            with lock:observed=[dict(v) for v in active.values()]
            had_checkpoint=had_checkpoint or any(checkpoint_progress(x['output']) for x in observed)
            avail=memory_available_kib()
            rss=[current_group_rss_kib(x['pid']) for x in observed]
            if parallel==2 and max_parallel_authorized>=4 and had_checkpoint and avail>=10*1024*1024 and len(cpus)>=4 and all(x<=2*1024*1024 for x in rss):
                parallel=4;events.append(dict(event='INCREASE_PARALLEL_TO4',mem_available_kib=avail,current_process_group_rss_kib=rss,checkpoint_observed=True))
            while queue and len(futures)<parallel and not failed:
                used={x['cpu'] for x in futures.values()};cpu=next(x for x in cpus if x not in used)
                case=queue.pop(0);future=pool.submit(run_case,case,binding,cpu,active,lock,launches);futures[future]=dict(cpu=cpu,case=case['case']);started+=1
                events.append(dict(event='CASE_DISPATCH',case=case['case'],cpu=cpu,jobs_dispatched_cumulative=started))
                print('START',case['case'],'CPU',cpu,flush=True)
            if not futures:break
            done,_=wait(list(futures),timeout=1,return_when=FIRST_COMPLETED)
            for future in done:
                info=futures.pop(future)
                try:result=future.result()
                except Exception as exception:result=dict(case=info['case'],status='LAUNCHER_FAILURE',exception=repr(exception),scientific_admission='NOT_ISSUED')
                results.append(result);print('FINISH',info['case'],result['status'],flush=True)
                if result['status']!='COMPLETE_EXIT_0':failed=True
            with lock:observed_launches={name:dict(value) for name,value in launches.items()}
            payload=dict(baseline,status='RUNNING' if futures or (queue and not failed) else 'STOPPED' if failed else 'COMPLETE_PHASE1',cases=results,solver_runs_started=len(observed_launches),jobs_dispatched=started,observed_run_starts=observed_launches,parallel_limit=parallel,events=events,not_started_cases=[x['case'] for x in queue],current_resources=dict(mem_available_kib=avail,process_group_rss_kib=rss),prior_and_current_started_runs=binding['prior_costs']['runs_started']+len(observed_launches))
            if len((json.dumps(payload,indent=2)+'\n').encode())>MIB:raise RuntimeError('ALLOCATION_RECEIPT_SIZE')
            save(group/'FULL_CAMPAIGN_RECEIPT.json',payload,group)
            if failed and not futures:break
    print('RECEIPT',group/'FULL_CAMPAIGN_RECEIPT.json',flush=True)
    return 1 if failed or queue else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--self-check',action='store_true');parser.add_argument('--run',action='store_true');args=parser.parse_args()
    if args.self_check:
        self_check()
        assert pathlib.Path(__file__).resolve().parents[4]==ROOT
        for tool in ['/usr/bin/time','/usr/bin/timeout','/usr/bin/taskset','/usr/bin/prlimit']:
            assert os.access(tool,os.X_OK),tool
        assert memory_available_kib()>0
        print('FULL_LAUNCHER_MECHANICAL_CHECK_PASS; no driver process started')
    elif args.run:raise SystemExit(run_campaign())
    else:parser.error('Choose --self-check or --run')
