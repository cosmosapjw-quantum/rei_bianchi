#!/usr/bin/env python3
"""Two finite AX06 pilots, after explicit changed-driver execution review.

Driver prewrite aggregate ceiling is224MiB. Launcher owns<=32MiB remaining.
No resume/retry, arbitrary case, remote executor or scientific admission.
"""
import argparse, hashlib, json, os, pathlib, resource, selectors, signal
import subprocess, tempfile, time, re
ROOT=pathlib.Path(__file__).resolve().parents[3]
BINDING=ROOT/'research/axbi_goal_20261014/driver/DRIVER_BINDING.json'
REVIEW=ROOT/'research/axbi_goal_20261014/reviews/DRIVER_PILOT_REVIEW.json'
PILOTS=ROOT/'research/axbi_goal_20261014/runs/pilot'
MIB=1024*1024
ENVELOPE=31*MIB
LOG_BUDGET=30*MIB
DRIVER_BUDGET=224*MIB

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
    if review.get('pilot_execution_authorized') is not True:
        raise RuntimeError('EXPLICIT_PILOT_EXECUTION_REVIEW_REQUIRED')
    for name,sha in review['reviewed_input_sha256'].items():
        if digest(ROOT/name)!=sha: raise RuntimeError('REVIEWED_INPUT_CHANGED:'+name)
    if review['reviewed_input_sha256'].get(str(pathlib.Path(__file__).resolve().relative_to(ROOT)))!=digest(__file__):
        raise RuntimeError('LAUNCHER_REVIEW_IDENTITY_MISSING')
    if review.get('driver_output_limit_bytes')!=DRIVER_BUDGET:
        raise RuntimeError('EXACT_DRIVER_AGGREGATE_CAP_REVIEW_REQUIRED')
    cases=[]
    for case,name,q in [('FLRW','pilot_flrw.cfg','0'),('SHEAR_PLUS','pilot_plus.cfg','0.01')]:
        config=ROOT/'research/axbi_goal_20261014/driver'/name
        c=parse_config(config)
        expected={'q_ref':q,'same_h':'false','end_zbar':'19.8','max_steps':'10000','max_attempts':'30000','max_rhs':'2000000','max_wall_s':'1200'}
        if REVIEW.name=='PILOT_CADENCE_REVIEW.json':expected['spectra_every_accepted']='60'
        if any(c.get(k)!=v for k,v in expected.items()): raise RuntimeError('PILOT_CONFIG_SCOPE:'+case)
        out=PILOTS/b['binary_sha256'][:12]/case
        cases.append(dict(case=case,config=config,output=out,binary=binary))
    return b,cases

def apply_limits():
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE,(DRIVER_BUDGET,DRIVER_BUDGET))
    allowed=os.sched_getaffinity(0)
    os.sched_setaffinity(0,{min(allowed)})

def run_case(case,binding):
    case_root=case['output'];raw=case_root.parent/(case['case']+'_raw')
    if case_root.exists() or raw.exists(): raise RuntimeError('EXISTING_ATTEMPT_NO_RESTART:'+str(case_root))
    # Driver requires an absent output directory. Raw lives alongside it and
    # remains included in per-case aggregate receipts and launcher envelope.
    raw.mkdir(parents=True)
    argv=['/usr/bin/time','-v','-o',str(raw/'time.log'),'/usr/bin/timeout','--foreground','--signal=KILL','1199s',str(case['binary']),'--config',str(case['config']),'--output',str(case_root),'--case',case['case']]
    env=dict(os.environ)
    for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','RAYON_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[k]='1'
    pre=dict(node_id='AX06',case=case['case'],argv=argv,cwd=str(ROOT),source_sha256=binding['source_sha256'],binary_sha256=binding['binary_sha256'],config_sha256=digest(case['config']),review_sha256=digest(REVIEW),launcher_sha256=digest(__file__),requested_executor_identity={'model':'gpt-6.1-sol','reasoning_effort':'medium'},observed_executor_identity_or_null=None,limits={'wall_seconds':1200,'timeout_seconds':1199,'cpu_threads':1,'CPU_affinity':'one currently allowed CPU','virtual_address_space_bytes':2*1024**3,'RSS_ceiling_bytes':2*1024**3,'RSS_kind':'observed by externaltime; AS cap is stronger distinct mechanism','driver_aggregate_output_bytes':DRIVER_BUDGET,'launcher_output_bytes':ENVELOPE,'combined_output_bytes':256*MIB,'allocation_receipt_reserve_bytes':MIB,'automatic_retries':0},status='STARTING')
    save(raw/'execution_start.json',pre,raw)
    before=resource.getrusage(resource.RUSAGE_CHILDREN);t0=time.monotonic()
    proc=subprocess.Popen(argv,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,preexec_fn=apply_limits)
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
            if current>=256*MIB:stop('COMBINED_OUTPUT_CAP')
            if total_bytes(case_root)>DRIVER_BUDGET:stop('DRIVER_OUTPUT_CAP_DEFECT')
            if time.monotonic()-t0>=1200:stop('WALL_CAP')
            if reason and proc.poll() is not None:
                # At the log cap close unread pipe tails; record explicitly.
                if reason=='LAUNCHER_LOG_CAP':break
        exit_code=proc.wait()
    finally:
        for f in files.values():f.close()
        sel.close()
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    time_text=(raw/'time.log').read_text() if (raw/'time.log').exists() else ''
    match=re.search(r'Maximum resident set size \(kbytes\):\s*(\d+)',time_text)
    measured_rss=int(match.group(1)) if match else None
    terminal_path=case_root/'RETURN.txt'
    terminal_text=terminal_path.read_text() if terminal_path.exists() else None
    elapsed=time.monotonic()-t0
    status='COMPLETE_EXIT_0' if exit_code==0 else 'FAILED_EXIT_'+str(exit_code)
    if reason:status=reason
    counters={}
    checkpoint=case_root/'checkpoint.txt'
    if checkpoint.exists():
        try:
            counters={'raw_text':checkpoint.read_text()}
        except OSError:pass
    result=dict(pre,status=status,exit_code=exit_code,wall_seconds=elapsed,cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,peak_RSS_kib=measured_rss,resource_children_cumulative_max_RSS_kib=after.ru_maxrss,driver_terminal_record=terminal_text,peak_RSS_scope='external GNU time per-case measurement; cumulative children fallback separately labelled',external_resource_capture=str(raw/'time.log'),peak_recursively_observed_output_bytes=peak_total,final_output_bytes=total_bytes(case_root)+total_bytes(raw),stdout_path=str(raw/'stdout.log'),stderr_path=str(raw/'stderr.log'),checkpoint_path=str(checkpoint) if checkpoint.exists() else None,checkpoint=counters,raw_stream_tail_status='NOT_CAPTURED_AFTER_CAP_KILL' if reason=='LAUNCHER_LOG_CAP' else 'CAPTURED_UNTIL_PROCESS_EXIT',scientific_admission='NOT_ISSUED')
    save(raw/'execution_receipt.json',result,raw)
    return result

def self_check():
    with tempfile.TemporaryDirectory() as name:
        p=pathlib.Path(name);(p/'nested').mkdir();(p/'nested/a').write_bytes(b'abc')
        assert total_bytes(p)==3
        save(p/'r.json',{'mechanical_only':True},p)
        assert json.loads((p/'r.json').read_text())['mechanical_only']
        assert DRIVER_BUDGET+ENVELOPE+MIB==256*MIB and LOG_BUDGET+MIB==ENVELOPE
    print('MECHANICAL_SELF_CHECK_PASS; no driver process started')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--self-check',action='store_true');parser.add_argument('--run',action='store_true');parser.add_argument('--review',choices=['DRIVER_PILOT_REVIEW.json','PILOT_CADENCE_REVIEW.json'],default='DRIVER_PILOT_REVIEW.json');args=parser.parse_args()
    REVIEW=ROOT/'research/axbi_goal_20261014/reviews'/args.review
    if args.self_check:self_check()
    elif args.run:
        binding,cases=frozen_plan();results=[]
        group=PILOTS/binding['binary_sha256'][:12]
        if (group/'PILOT_RECEIPT.json').exists():raise RuntimeError('EXISTING_ALLOCATION_NO_RETRY')
        for case in cases:
            result=run_case(case,binding);results.append(result)
            print(case['case'],result['status'],flush=True)
            if result['status']!='COMPLETE_EXIT_0':break
        group.mkdir(parents=True,exist_ok=True)
        # Small top-level allocation receipt has its own <=1MiB reserve,
        # included in group total, distinct from per-case32MiB envelopes.
        payload=json.dumps({'node_id':'AX06','cases':results,'solver_runs_started':len(results),'next_case_status':'NOT_STARTED_AFTER_FAILURE' if len(results)<2 else 'BOTH_ATTEMPTS_COMPLETE','scientific_admission':'NOT_ISSUED'},indent=2)+'\n'
        if len(payload.encode())>MIB:raise RuntimeError('ALLOCATION_RECEIPT_SIZE')
        (group/'PILOT_RECEIPT.json').write_text(payload)
    else:parser.error('Choose --self-check or --run')
