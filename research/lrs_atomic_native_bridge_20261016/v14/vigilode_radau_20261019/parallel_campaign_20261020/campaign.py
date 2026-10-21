#!/usr/bin/env python3
"""Bounded independent-process DAG execution. No native numerical code lives here."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import time
from datetime import datetime, timezone

THREADS = {k: '1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','RAYON_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')}

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def identity(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temp.replace(path)
def utc(): return datetime.now(timezone.utc).isoformat()

def resources(max_workers=64,memory_limit_mb=None,nominal_job_mb=512,cgroup_root=Path('/sys/fs/cgroup')):
    """Observed available bytes are separate from the explicitly nominal reservation."""
    if not 1<=max_workers<=64 or nominal_job_mb<=0: raise ValueError('positive worker limit <=64 and nominal memory required')
    affinity=sorted(os.sched_getaffinity(0));quota=None
    cpu_paths=[cgroup_root/'cpu.max',cgroup_root/'cpu/cpu.cfs_quota_us']
    try:
        q,p=(cgroup_root/'cpu.max').read_text().split()
        if q!='max':quota=float(q)/float(p)
    except (OSError,ValueError):
        try:
            q=float((cgroup_root/'cpu/cpu.cfs_quota_us').read_text());p=float((cgroup_root/'cpu/cpu.cfs_period_us').read_text())
            if q>0:quota=q/p
        except (OSError,ValueError):pass
    meminfo={}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key,value=line.split(':',1);meminfo[key]=int(value.strip().split()[0])*1024
    observed=meminfo['MemAvailable'];cgroup_remaining=None;cgroup_limit=None;cgroup_used=None;inactive_file=0;file_bytes=None
    try:
        memory_stat=dict(line.split()for line in(cgroup_root/'memory.stat').read_text().splitlines())
        inactive_file=int(memory_stat.get('inactive_file',0));file_bytes=int(memory_stat.get('file',0))
    except(OSError,ValueError):pass
    try:
        limit=(cgroup_root/'memory.max').read_text().strip();used=int((cgroup_root/'memory.current').read_text())
        if limit!='max':cgroup_limit=int(limit);cgroup_used=used;cgroup_remaining=max(0,int(limit)-used)
    except (OSError,ValueError):
        try:
            limit=int((cgroup_root/'memory/memory.limit_in_bytes').read_text());used=int((cgroup_root/'memory/memory.usage_in_bytes').read_text())
            if limit<2**60:cgroup_remaining=max(0,limit-used)
        except (OSError,ValueError):pass
    bounds=[observed]
    if cgroup_remaining is not None:bounds.append(cgroup_remaining+inactive_file)
    if memory_limit_mb is not None:
        if memory_limit_mb<=0:raise ValueError('memory limit must be positive')
        bounds.append(int(memory_limit_mb*1024**2))
    available=min(bounds);usable=int(available*.8)
    cpu_budget=min(max_workers,len(affinity),max(0,math.floor(quota)) if quota is not None else len(affinity))
    workers=min(cpu_budget,usable//int(nominal_job_mb*1024**2))
    return {'utc':utc(),'allowed_affinity':affinity,'cgroup_cpu_quota_cores':quota,'cpu_budget':cpu_budget,'requested_max_workers':max_workers,'mem_available_bytes':observed,'cgroup_remaining_bytes':cgroup_remaining,'cgroup_limit_bytes':cgroup_limit,'cgroup_current_bytes':cgroup_used,'cgroup_file_bytes':file_bytes,'observed_inactive_file_potentially_reclaimable_bytes':inactive_file,'cgroup_remaining_plus_inactive_file_estimate_bytes':None if cgroup_remaining is None else cgroup_remaining+inactive_file,'memory_admission_policy':'min(host MemAvailable, cgroup raw remaining plus observed inactive_file only, user cap), then reserve20%; estimate is not guaranteed allocation or measured RSS','user_memory_limit_mb':memory_limit_mb,'usable_memory_bytes_after_20_percent_headroom':usable,'nominal_job_memory_mb':nominal_job_mb,'nominal_memory_is_measured_peak_RSS':False,'admitted_workers':workers,'assigned_cpu_pool':affinity[:cpu_budget]}

def validate_manifest(manifest):
    jobs=manifest['jobs'];ids=[j['id']for j in jobs]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate job id')
    known=set(ids)
    for j in jobs:
        if not j['id'] or '/' in j['id'] or j['id']in('.', '..'):raise ValueError('job id must be a single path component')
        if not isinstance(j['argv'],list)or not j['argv']or not all(isinstance(x,str)for x in j['argv']):raise ValueError('argv must be string array')
        if j.get('timeout_s',0)<=0:raise ValueError('positive timeout required')
        if any(x not in known or x==j['id']for x in j.get('deps',[])):raise ValueError('invalid dependency')
        if any(g not in manifest.get('aggregate_caps_s',{})for g in j.get('budget_groups',[])):raise ValueError('unknown aggregate group')
    done=set()
    while len(done)<len(jobs):
        ready={j['id']for j in jobs if set(j.get('deps',[]))<=done}
        if ready<=done:raise ValueError('cyclic DAG')
        done|=ready
    if any(v<=0 for v in manifest.get('aggregate_caps_s',{}).values()):raise ValueError('positive aggregate cap required')

def file_outputs(job,attempt):
    result={}
    for item in job.get('outputs',[]):
        p=attempt/item['path']
        if not p.is_file():raise ValueError('missing output '+str(p))
        if item.get('kind')=='json':
            data=json.loads(p.read_text())
            if item.get('completed_required')and data.get('completed')is not True:raise ValueError('incomplete raw JSON')
        if item.get('kind')=='csv':
            with p.open(newline='')as f:
                reader=csv.DictReader(f);rows=list(reader);header=reader.fieldnames
            if not header or len(header)!=len(set(header)):raise ValueError('missing/duplicate CSV header')
            if 'rows'in item and len(rows)!=item['rows']:raise ValueError('CSV row count')
            if 'columns'in item and len(header)!=item['columns']:raise ValueError('CSV column count')
            for k,value in item.get('key_fields',{}).items():
                if any(row.get(k)!=str(value)for row in rows):raise ValueError('CSV key mismatch '+k)
            if item.get('step_column'):
                if [int(x[item['step_column']])for x in rows]!=list(range(1,len(rows)+1)):raise ValueError('CSV step coverage')
        result[item['path']]={'bytes':p.stat().st_size,'sha256':digest(p)}
    return result

def binding(job):
    """Recompute input and actual executable bytes, including after a dependent build."""
    files={str(Path(p).resolve()):digest(p)for p in job.get('identity_files',[])}
    for root in job.get('identity_roots',[]):
        root=Path(root)
        if not root.is_dir():raise FileNotFoundError('missing source root '+str(root))
        for p in sorted(root.rglob('*')):
            if p.is_file()and not any(x in('target','.git','__pycache__')for x in p.relative_to(root).parts):files[str(p.resolve())]=digest(p)
    executable=Path(job['argv'][0])
    if not executable.is_file():raise FileNotFoundError('missing executable '+str(executable))
    return {'job_identity':identity(job),'input_identity':files,'executable_sha256':digest(executable)}

def run(manifest,output,max_workers=64,memory_limit_mb=None,nominal_job_mb=512,poll_s=.01):
    if manifest.get("accounting_policy") == EXIT_ACCOUNTING_V1:
        return run_exit_observed(manifest,output,max_workers,memory_limit_mb,nominal_job_mb,poll_s)
    validate_manifest(manifest);output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    mid=identity(manifest);saved=output/'MANIFEST.json'
    if saved.exists()and identity(json.loads(saved.read_text()))!=mid:raise ValueError('MANIFEST_IDENTITY_MISMATCH: existing results preserved')
    if not saved.exists():write(saved,manifest)
    plan=resources(max_workers,memory_limit_mb,nominal_job_mb);write(output/'RESOURCE_PLAN.json',plan)
    jobs={j['id']:j for j in manifest['jobs']};states={k:{'status':'PENDING'}for k in jobs};active={};used=set();charged={k:0. for k in manifest.get('aggregate_caps_s',{})};caps=manifest.get('aggregate_caps_s',{})
    started=time.monotonic();invocation=output/f'invocations/{time.time_ns()}';invocation.mkdir(parents=True)
    def flush():
        record={'schema':'rei.lrs.parallel_campaign.v1','utc':utc(),'manifest_identity':mid,'states':states,'aggregate_charged_process_wall_s':charged,'active_jobs':list(active),'phase_wall_s':time.monotonic()-started,'resource_plan':plan,'native_numerical_source_changed':False}
        write(output/'CAMPAIGN_RECEIPT.json',record);write(invocation/'receipt.json',record)
    # Resume is per manifest, full input/executable binding, logs and output content.
    for jid,job in jobs.items():
        attempts=sorted((output/'jobs'/jid).glob('attempt_*'))
        if not attempts:continue
        latest=attempts[-1]/'outcome.json'
        if not latest.exists():continue
        old=json.loads(latest.read_text())
        if old.get('status')!='COMPLETED':continue
        try:
            now=binding(job)
            if old['binding']!=now:raise ValueError('INPUT_OR_EXECUTABLE_IDENTITY_MISMATCH')
            if file_outputs(job,latest.parent)!=old['outputs']:raise ValueError('OUTPUT_IDENTITY_MISMATCH')
            for name in ['stdout.txt','stderr.txt']:
                if digest(latest.parent/name)!=old['logs'][name]:raise ValueError('LOG_IDENTITY_MISMATCH')
            states[jid]={'status':'REUSED_COMPLETED','attempt':str(latest.parent),'binding':now}
        except (OSError,ValueError,KeyError)as exc:
            states[jid]={'status':'FAILED_IDENTITY_MISMATCH','reason':str(exc),'attempt':str(latest.parent)}
    for jid,job in jobs.items():
        for previous in (output/'jobs'/jid).glob('attempt_*/outcome.json'):
            history=json.loads(previous.read_text())
            for g in job.get('budget_groups',[]):charged[g]+=float(history.get('process_wall_s',0))
    # A changed restoration input invalidates the current dependent DAG even when
    # old produced bytes still exist. Preserve those old results without reusing them.
    changed=True
    while changed:
        changed=False
        for jid,job in jobs.items():
            if states[jid]['status']=='REUSED_COMPLETED'and any(states[d]['status']not in('PENDING','REUSED_COMPLETED','COMPLETED')for d in job.get('deps',[])):
                states[jid]={'status':'BLOCKED_DEPENDENCY_IDENTITY','deps':job.get('deps',[]),'historical_attempt':states[jid]['attempt']};changed=True
    flush()
    def group_total(g,now):return charged[g]+sum(now-a['start']for jid,a in active.items()if g in jobs[jid].get('budget_groups',[]))
    def finish(jid,reason=None):
        a=active.pop(jid);job=jobs[jid]
        if reason and a['process'].poll()is None:
            try:os.killpg(a['process'].pid,signal.SIGKILL)
            except ProcessLookupError:pass
        code=a['process'].wait();elapsed=time.monotonic()-a['start']
        a['stdout'].close();a['stderr'].close();used.difference_update(a['cpus'])
        for g in job.get('budget_groups',[]):charged[g]+=elapsed
        outputs={};error=reason
        if code==0 and not reason:
            try:outputs=file_outputs(job,a['attempt'])
            except (ValueError,OSError,KeyError)as exc:error=str(exc)
        status='COMPLETED'if code==0 and error is None else'FAILED'
        outcome={'status':status,'exit_code':code,'reason':error,'process_wall_s':elapsed,'binding':a['binding'],'outputs':outputs,'logs':{x:digest(a['attempt']/x)for x in ['stdout.txt','stderr.txt']},'assigned_cpus':a['cpus'],'timeout_s':job['timeout_s'],'aggregate_overshoot_s':{g:max(0,charged[g]-caps[g])for g in job.get('budget_groups',[])},'peak_RSS':'NOT_MEASURED;nominal admission reservation is not observed RSS'}
        write(a['attempt']/'outcome.json',outcome);(a['attempt']/'exit.txt').write_text(str(code)+'\n')
        states[jid]={'status':status,'attempt':str(a['attempt']),'outcome':outcome};flush()
    try:
        while True:
            now=time.monotonic()
            expired={g for g in caps if group_total(g,now)>=caps[g]}
            for jid in list(active):
                a=active[jid];job=jobs[jid]
                reason='AGGREGATE_CAP'if expired.intersection(job.get('budget_groups',[]))else('JOB_TIMEOUT'if now-a['start']>=job['timeout_s']else None)
                if a['process'].poll()is not None:finish(jid)
                elif reason:finish(jid,reason)
            pending=[j for j in jobs.values()if states[j['id']]['status']=='PENDING']
            for j in pending:
                deps=[states[x]['status']for x in j.get('deps',[])]
                if any(x not in ['PENDING','RUNNING','COMPLETED','REUSED_COMPLETED']for x in deps):states[j['id']]={'status':'BLOCKED_DEPENDENCY','deps':j.get('deps',[])}
                elif any(group_total(g,time.monotonic())>=caps[g]for g in j.get('budget_groups',[])):states[j['id']]={'status':'NOT_RUN_AGGREGATE_CAP'}
            pending=sorted([j for j in jobs.values()if states[j['id']]['status']=='PENDING'and all(states[d]['status']in('COMPLETED','REUSED_COMPLETED')for d in j.get('deps',[]))], key=lambda j:-float(j.get('estimated_duration_s',0)))
            for j in pending:
                need=int(j.get('cpu_slots',1));memory=int(j.get('nominal_memory_mb',nominal_job_mb)*1024**2)
                free=[c for c in plan['assigned_cpu_pool']if c not in used]
                live=resources(max_workers,memory_limit_mb,nominal_job_mb)
                reserved=sum(x['memory']for x in active.values())
                mem_ok=memory<=min(plan['usable_memory_bytes_after_20_percent_headroom']-reserved,live['usable_memory_bytes_after_20_percent_headroom'])
                if need<1 or need>plan['cpu_budget']or not mem_ok:
                    if not active:states[j['id']]={'status':'NOT_RUN_RESOURCE_ADMISSION','cpu_slots_required':need,'nominal_memory_bytes':memory,'live_resource_observation':live}
                    continue
                if len(free)<need or len(active)>=plan['admitted_workers']:continue
                cpus=free[:need];jobroot=output/'jobs'/j['id'];jobroot.mkdir(parents=True,exist_ok=True)
                attempts=list(jobroot.glob('attempt_*'));attempt=jobroot/f'attempt_{len(attempts)+1:04d}';attempt.mkdir()
                try:b= binding(j)
                except (OSError,ValueError)as exc:states[j['id']]={'status':'FAILED_INPUT_BINDING','reason':str(exc)};continue
                argv=[x.replace('{attempt}',str(attempt))for x in j['argv']]
                env=os.environ.copy();env.pop('CARGO_TARGET_DIR',None);env.update(THREADS);env.update(j.get('environment',{}))
                # Native jobs cannot override the single-thread contract; build jobs may set build concurrency only.
                env.update(THREADS)
                if j.get('kind')=='build':env['CARGO_BUILD_JOBS']=str(need)
                full=['taskset','-c',','.join(map(str,cpus)),*argv]
                write(attempt/'inputs.json',{'utc':utc(),'argv':full,'cwd':j.get('cwd'),'binding':b,'manifest_identity':mid,'assigned_cpus':cpus,'thread_environment':THREADS,'nominal_memory_mb':memory/1024**2,'nominal_memory_is_measured_peak_RSS':False,'timeout_s':j['timeout_s']})
                so=(attempt/'stdout.txt').open('wb');se=(attempt/'stderr.txt').open('wb');t=time.monotonic()
                try:child=subprocess.Popen(full,cwd=j.get('cwd'),env=env,stdout=so,stderr=se,start_new_session=True)
                except OSError as exc:
                    so.close();se.close();states[j['id']]={'status':'FAILED_LAUNCH','reason':str(exc),'attempt':str(attempt)};write(attempt/'outcome.json',states[j['id']]);continue
                used.update(cpus);active[j['id']]={'process':child,'attempt':attempt,'stdout':so,'stderr':se,'start':t,'cpus':cpus,'memory':memory,'binding':b};states[j['id']]={'status':'RUNNING','attempt':str(attempt),'assigned_cpus':cpus};flush()
            if not active and not any(s['status']=='PENDING'for s in states.values()):break
            if not active and pending and all(states[j['id']]['status']=='PENDING'for j in pending):
                for j in pending:states[j['id']]={'status':'NOT_RUN_RESOURCE_ADMISSION','reason':'No admitted worker slot'}
            flush();time.sleep(poll_s)
    finally:
        for jid in list(active):finish(jid,'SUPERVISOR_INTERRUPTION')
        flush()
    successful=all(s['status']in('COMPLETED','REUSED_COMPLETED')for s in states.values())
    result=json.loads((output/'CAMPAIGN_RECEIPT.json').read_text());result['overall_status']='COMPLETED'if successful else'INCOMPLETE_OR_FAILED';result['overall_exit_code']=0 if successful else 1;write(output/'CAMPAIGN_RECEIPT.json',result)
    return result

EXIT_ACCOUNTING_V1 = 'LRS_EXIT_OBSERVATION_PROSPECTIVE_V1_20261021'

def run_exit_observed(manifest, output, max_workers=64, memory_limit_mb=None, nominal_job_mb=512, poll_s=.01):
    """Opt-in launch-to-first-exit-observed accounting; persistence is uncharged.

    Observations have scheduling latency. poll_s is a requested sleep, not a
    maximum latency guarantee. Historical process_wall_s debits remain intact.
    """
    validate_manifest(manifest)
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    mid=identity(manifest);saved=output/'MANIFEST.json'
    if saved.exists() and identity(json.loads(saved.read_text()))!=mid:
        raise ValueError('MANIFEST_IDENTITY_MISMATCH: existing results preserved')
    if not saved.exists():write(saved,manifest)
    plan=resources(max_workers,memory_limit_mb,nominal_job_mb);write(output/'RESOURCE_PLAN.json',plan)
    jobs={j['id']:j for j in manifest['jobs']};states={k:{'status':'PENDING'}for k in jobs}
    active={};used=set();caps=manifest.get('aggregate_caps_s',{});charged={g:0. for g in caps};latched=set()
    started=time.monotonic();events=[];stop=False
    invocation=output/f'invocations/{time.time_ns()}';invocation.mkdir(parents=True)
    def flush():
        record={'schema':'rei.lrs.parallel_campaign.exit_observed.v1','utc':utc(),'manifest_identity':mid,
          'accounting_policy':EXIT_ACCOUNTING_V1,'charge_definition':'launch_to_first_exit_observed',
          'requested_poll_s':poll_s,'poll_s_is_latency_guarantee':False,'states':states,
          'aggregate_charged_process_wall_s':charged,'aggregate_caps_latched':sorted(latched),
          'active_jobs':list(active),'phase_wall_s':time.monotonic()-started,'resource_plan':plan,
          'observation_events':events,'native_numerical_source_changed':False}
        write(output/'CAMPAIGN_RECEIPT.json',record);write(invocation/'receipt.json',record)
    # Debit every old outcome once, including failed/partial attempts. Missing
    # charge is unknown, never silently zero or permission to launch more work.
    for jid,j in jobs.items():
        for oldpath in sorted((output/'jobs'/jid).glob('attempt_*/outcome.json')):
            old=json.loads(oldpath.read_text())
            if 'process_wall_s' not in old:
                if j.get('budget_groups'):stop=True;states[jid]={'status':'FAILED_HISTORICAL_DEBIT_UNKNOWN','attempt':str(oldpath.parent)}
            else:
                for g in j.get('budget_groups',[]):charged[g]+=float(old['process_wall_s'])
        attempts=sorted((output/'jobs'/jid).glob('attempt_*'))
        if not attempts:continue
        latest=attempts[-1]/'outcome.json'
        if not latest.exists():
            stop=True;states[jid]={'status':'FAILED_PARTIAL_DEBIT_UNKNOWN','attempt':str(latest.parent)};continue
        old=json.loads(latest.read_text())
        if old.get('status')!='COMPLETED':continue
        try:
            now=binding(j)
            if now!=old['binding']:raise ValueError('INPUT_OR_EXECUTABLE_IDENTITY_MISMATCH')
            if file_outputs(j,latest.parent)!=old['outputs']:raise ValueError('OUTPUT_IDENTITY_MISMATCH')
            if any(digest(latest.parent/n)!=old['logs'][n]for n in ['stdout.txt','stderr.txt']):raise ValueError('LOG_IDENTITY_MISMATCH')
            states[jid]={'status':'REUSED_COMPLETED','attempt':str(latest.parent),'binding':now}
        except (OSError,ValueError,KeyError)as exc:
            states[jid]={'status':'FAILED_IDENTITY_MISMATCH','reason':str(exc),'attempt':str(latest.parent)}
    # Identity failure is a supervisor stop, not permission to launch a fresh
    # independent or dependent process. Preserve historical cached evidence.
    if any(s['status']=='FAILED_IDENTITY_MISMATCH'for s in states.values()):
        stop=True
    changed=True
    while changed:
        changed=False
        for jid,j in jobs.items():
            if states[jid]['status']=='REUSED_COMPLETED'and any(states[d]['status']not in ('PENDING','REUSED_COMPLETED','COMPLETED')for d in j.get('deps',[])):
                states[jid]={'status':'BLOCKED_DEPENDENCY_IDENTITY','deps':j.get('deps',[]),'historical_attempt':states[jid]['attempt']}
                changed=True
    def observe():
        # Freeze ALL exit observations before any serialization/hash/validation.
        for jid,a in list(active.items()):
            if a.get('exit_observed') is not None:continue
            code=a['process'].poll();now=time.monotonic()
            previous=a['last_observation'];a['intervals'].append(now-previous);a['last_observation']=now
            if code is None:a['last_running_observed']=now
            else:a['exit_observed']=now;a['exit_code']=code
            events.append({'job':jid,'observed_monotonic':now,'exit_code':code})
    def total(g,now):
        return charged[g]+sum((a['exit_observed']if a.get('exit_observed')is not None else now)-a['start']for jid,a in active.items()if g in jobs[jid].get('budget_groups',[]))
    def request_kill(jid,reason):
        a=active[jid]
        if a.get('exit_observed')is not None or a.get('kill_request')is not None:return
        a['kill_request']=time.monotonic();a['reason']=reason
        try:os.killpg(a['process'].pid,signal.SIGKILL)
        except ProcessLookupError:pass
    def enforce():
        observe();now=time.monotonic()
        latched.update(g for g in caps if total(g,now)>=caps[g])
        # Signal every affected group member BEFORE persistence of any outcome.
        for jid,a in active.items():
            if latched.intersection(jobs[jid].get('budget_groups',[])):request_kill(jid,'AGGREGATE_CAP')
            elif a.get('exit_observed')is None and now-a['start']>=jobs[jid]['timeout_s']:request_kill(jid,'JOB_TIMEOUT')
    def persist(jid):
        nonlocal stop
        a=active[jid];j=jobs[jid];elapsed=a['exit_observed']-a['start']
        a['stdout'].close();a['stderr'].close();a['persistence_start']=time.monotonic()
        outputs={};error=a.get('reason');failure='EXIT_FAILURE'if a['exit_code']else None
        if a['exit_code']==0 and not error:
            try:outputs=file_outputs(j,a['attempt'])
            except (ValueError,OSError,KeyError)as exc:error=str(exc);failure='OUTPUT_VALIDATION_FAILURE'
        timing={k:a.get(k)for k in ['start','popen_returned','last_running_observed','exit_observed','exit_code','kill_request','persistence_start']}
        timing.update({'actual_observation_intervals_s':a['intervals'],'requested_poll_s':poll_s})
        outcome={'status':'COMPLETED'if a['exit_code']==0 and error is None else'FAILED','exit_code':a['exit_code'],
          'reason':error,'failure_kind':failure,'process_wall_s':elapsed,'accounting_policy':EXIT_ACCOUNTING_V1,
          'timing':timing,'binding':a['binding'],'outputs':outputs,'assigned_cpus':a['cpus'],
          'aggregate_overshoot_s':{g:max(0,total(g,time.monotonic())-caps[g])for g in j.get('budget_groups',[])}}
        try:
            outcome['logs']={n:digest(a['attempt']/n)for n in ['stdout.txt','stderr.txt']}
            # The outcome is written before its persistence end is knowable.
            # The final campaign receipt stores the measured end after both writes.
            timing['persistence_end']=None
            write(a['attempt']/'outcome.json',outcome);(a['attempt']/'exit.txt').write_text(str(a['exit_code'])+'\n')
            timing['persistence_end']=time.monotonic()
        except Exception as exc:
            stop=True;outcome.update(status='FAILED_PERSISTENCE',failure_kind='PERSISTENCE_FAILURE',persistence_error=repr(exc))
            timing['persistence_end']=time.monotonic()
            # Independent minimal partial record if the normal persistence failed.
            (a['attempt']/'partial_outcome.json').write_text(json.dumps(outcome,indent=2)+'\n')
        for g in j.get('budget_groups',[]):charged[g]+=elapsed
        used.difference_update(a['cpus']);active.pop(jid)
        states[jid]={'status':outcome['status'],'attempt':str(a['attempt']),'outcome':outcome}
    try:
        flush()
        while True:
            enforce()
            for jid in list(active):
                if active[jid].get('exit_observed')is not None:persist(jid)
            if stop:break
            for jid,j in jobs.items():
                if states[jid]['status']!='PENDING':continue
                deps=[states[d]['status']for d in j.get('deps',[])]
                if any(s not in ['PENDING','RUNNING','COMPLETED','REUSED_COMPLETED']for s in deps):states[jid]={'status':'BLOCKED_DEPENDENCY','deps':j.get('deps',[])}
                elif latched.intersection(j.get('budget_groups',[])):states[jid]={'status':'NOT_RUN_AGGREGATE_CAP'}
            pending=sorted([j for j in jobs.values()if states[j['id']]['status']=='PENDING'and all(states[d]['status']in ['COMPLETED','REUSED_COMPLETED']for d in j.get('deps',[]))],key=lambda j:-float(j.get('estimated_duration_s',0)))
            for j in pending:
                if stop:break
                enforce()
                if latched.intersection(j.get('budget_groups',[])):states[j['id']]={'status':'NOT_RUN_AGGREGATE_CAP'};continue
                need=int(j.get('cpu_slots',1));memory=int(j.get('nominal_memory_mb',nominal_job_mb)*1024**2)
                live=resources(max_workers,memory_limit_mb,nominal_job_mb);reserved=sum(a['memory']for a in active.values());free=[c for c in plan['assigned_cpu_pool']if c not in used]
                if need<1 or need>plan['cpu_budget']or memory>min(plan['usable_memory_bytes_after_20_percent_headroom']-reserved,live['usable_memory_bytes_after_20_percent_headroom']):
                    if not active:states[j['id']]={'status':'NOT_RUN_RESOURCE_ADMISSION'}
                    continue
                if len(free)<need or len(active)>=plan['admitted_workers']:continue
                jobroot=output/'jobs'/j['id'];jobroot.mkdir(parents=True,exist_ok=True)
                attempt=jobroot/f"attempt_{len(list(jobroot.glob('attempt_*')))+1:04d}";attempt.mkdir()
                try:b=binding(j)
                except (OSError,ValueError)as exc:states[j['id']]={'status':'FAILED_INPUT_BINDING','reason':str(exc)};continue
                cpus=free[:need];argv=[x.replace('{attempt}',str(attempt))for x in j['argv']];full=['taskset','-c',','.join(map(str,cpus)),*argv]
                env=os.environ.copy();env.pop('CARGO_TARGET_DIR',None);env.update(j.get('environment',{}));env.update(THREADS)
                if j.get('kind')=='build':env['CARGO_BUILD_JOBS']=str(need)
                write(attempt/'inputs.json',{'argv':full,'binding':b,'manifest_identity':mid,'accounting_policy':EXIT_ACCOUNTING_V1,'assigned_cpus':cpus,'thread_environment':THREADS,'timeout_s':j['timeout_s']})
                so=(attempt/'stdout.txt').open('wb');se=(attempt/'stderr.txt').open('wb')
                # Binding, input persistence and log opening can take time. Last
                # gate must observe again and enforce caps immediately before spawn.
                enforce()
                if latched.intersection(j.get('budget_groups',[])):
                    so.close();se.close()
                    no_launch={'status':'NOT_RUN_AGGREGATE_CAP','process_started':False,'process_wall_s':0.0,'accounting_policy':EXIT_ACCOUNTING_V1,'reason':'CAP_LATCHED_BEFORE_POPEN','binding':b}
                    write(attempt/'outcome.json',no_launch)
                    states[j['id']]={'status':'NOT_RUN_AGGREGATE_CAP','unlaunched_attempt':str(attempt),'outcome':no_launch};continue
                t=time.monotonic()
                try:child=subprocess.Popen(full,cwd=j.get('cwd'),env=env,stdout=so,stderr=se,start_new_session=True)
                except OSError as exc:
                    so.close();se.close();states[j['id']]={'status':'FAILED_LAUNCH','reason':str(exc),'attempt':str(attempt)};stop=True;break
                popen_returned=time.monotonic()
                used.update(cpus);active[j['id']]={'process':child,'start':t,'popen_returned':popen_returned,'last_observation':t,'last_running_observed':None,'exit_observed':None,'exit_code':None,'kill_request':None,'intervals':[],'stdout':so,'stderr':se,'attempt':attempt,'binding':b,'cpus':cpus,'memory':memory}
                states[j['id']]={'status':'RUNNING','attempt':str(attempt)}
            observe()
            # No receipt persistence while exited children remain unobserved.
            flush()
            if not active and not any(s['status']=='PENDING'for s in states.values()):break
            time.sleep(poll_s)
    except BaseException as exc:
        stop=True;events.append({'supervisor_exception':repr(exc),'observed_monotonic':time.monotonic()})
    finally:
        # Observe all, signal all, then reap/observe all before individual writes.
        observe()
        for jid in active:request_kill(jid,'SUPERVISOR_INTERRUPTION')
        for a in active.values():a['process'].wait()
        observe()
        for jid in list(active):persist(jid)
        if stop:
            for jid,s in states.items():
                if s['status']=='PENDING':states[jid]={'status':'NOT_RUN_SUPERVISOR_STOP'}
        flush()
    result=json.loads((output/'CAMPAIGN_RECEIPT.json').read_text());ok=all(s['status']in ['COMPLETED','REUSED_COMPLETED']for s in states.values())
    result.update(overall_status='COMPLETED'if ok else'INCOMPLETE_OR_FAILED',overall_exit_code=0 if ok else 1)
    write(output/'CAMPAIGN_RECEIPT.json',result);return result


def merge_csv(paths,output,keys,expected_keys,expected_steps,columns=None):
    """Validate exact finite coverage, then emit in declared original key/step order."""
    expected=[tuple(str(v)for v in key)for key in expected_keys]
    if len(expected)!=len(set(expected)):raise ValueError('duplicate expected key')
    groups={};header=None
    for path in paths:
        with Path(path).open(newline='')as f:
            reader=csv.DictReader(f)
            if header is None:header=reader.fieldnames
            if reader.fieldnames!=header or not header or len(header)!=len(set(header)):raise ValueError('CSV header mismatch')
            if columns and len(header)!=columns:raise ValueError('CSV column count')
            for row in reader:
                if None in row or any(v is None for v in row.values()):raise ValueError('malformed CSV row')
                key=tuple(row[k]for k in keys);step=int(row['step'])
                if key not in expected:raise ValueError('unexpected CSV key '+str(key))
                bucket=groups.setdefault(key,{})
                if step in bucket:raise ValueError('duplicate CSV key/step')
                bucket[step]=row
    if set(groups)!=set(expected):raise ValueError('missing CSV keys')
    for key in expected:
        n=expected_steps(key)
        if set(groups[key])!=set(range(1,n+1)):raise ValueError('CSV step coverage '+str(key))
    output=Path(output)
    if output.exists():raise FileExistsError('merged output exists; original preserved')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=header);writer.writeheader()
        for key in expected:
            for step in sorted(groups[key]):writer.writerow(groups[key][step])
    return {'histories':len(expected),'rows':sum(len(x)for x in groups.values()),'columns':len(header),'sha256':digest(output),'path':str(output)}
