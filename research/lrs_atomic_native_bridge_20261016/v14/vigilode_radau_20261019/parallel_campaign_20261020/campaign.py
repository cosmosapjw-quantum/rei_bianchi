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
