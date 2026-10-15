#!/usr/bin/env python3
"""Fresh conditional two-case full campaign; no build and no old-output resume."""
import argparse, datetime, hashlib, json, math, os, re, shutil, signal, subprocess, time
from pathlib import Path
import ncp_helpers as H
STOP = False
GIB = 1024**3
def save(path,obj):
    with path.open('x') as f: json.dump(obj,f,indent=2,allow_nan=False); f.write('\n')
def fields(text):
    return dict(l.split('=',1) for l in text.splitlines() if l and not l.startswith('#'))
def checked_config(path,cells):
    text=path.read_text();v=fields(text)
    expected={'q_ref':0,'escape_fraction':.2,'initial_x_hii':.000210349192936,
      'initial_temperature_k':9.306042400380866,'energy_subdivisions':16,
      'transport_cells':cells,'n_mu':8,'background_panels':4096,'local_target':1e-5,
      'initial_dln_a':.0001,'spectra_every_accepted':2000,'end_zbar':4,
      'max_steps':800000,'max_attempts':2600000,'max_rhs':200000000,
      'max_wall_s':42880,'output_budget_mib':12288,'transport_threads':8}
    if set(v)!=set(expected)|{'same_h','inactive_hi_split'} or v['same_h']!='false' or v['inactive_hi_split']!='true':
        raise RuntimeError('unexpected full config fields')
    for k,x in expected.items():
        if not math.isfinite(float(v[k])) or float(v[k])!=x: raise RuntimeError('frozen full field mismatch '+k)
    return text
def finish(item,status,usage,identity,source,binary_sha,task):
    code=os.waitstatus_to_exitcode(status);item['proc'].returncode=code;item['terminal']=True
    item['log'].close();out=item['out'];native=None;parse_error=None
    try:
        native=fields((out/'RETURN.txt').read_text())
        for k in ['status','a','accepted','attempts','rejections','rhs_evaluations','wall_s','max_newton_residual','last_error','result']:native[k]
        for k in ['a','wall_s','max_newton_residual','last_error']:
            if not math.isfinite(float(native[k])):raise ValueError('nonfinite native return')
    except (OSError,KeyError,ValueError) as e:parse_error=str(e)
    sr=(out/'source_identity.txt').exists() and (out/'source_identity.txt').read_bytes()==identity
    cr=(out/'config.cfg').exists() and (out/'config.cfg').read_bytes()==item['runtime'].read_bytes()
    bound=sr and cr and H.sha(H.BINARY)==binary_sha
    complete=bool(native and not parse_error and native['status']=='COMPLETE_REPRESENTED_INTERVAL'
        and native['result']=='Ok(())' and float(native['a'])==.2 and code==0 and bound and item.get('stop_reason') is None)
    receipt={'case':item['case']['case'],'returncode':code,'wall_s':time.monotonic()-item['started'],
      'terminal_utc':H.utc(),'stop_reason':item.get('stop_reason'),'native_return':native,
      'terminal_parse_error':parse_error,'native_completion_proof':complete,
      'checkpoint':H.checkpoint(out/'checkpoint.txt'),'source_identity_sha256':source,
      'binary_sha256':binary_sha,'base_config_sha256':item['binding']['base_config_sha256'],
      'runtime_config_sha256':H.sha(item['runtime']),'source_identity_readback_equal':sr,
      'config_readback_equal':cr,'source_config_binary_bindings_match':bound,
      'peak_process_tree_rss_bytes':item['peak_rss'],'maximum_os_threads_observed':item['peak_threads'],
      'observed_process_tree_cpu_s':item['peak_cpu'],'native_cpu_user_s_exact_wait4':usage.ru_utime,
      'native_cpu_system_s_exact_wait4':usage.ru_stime,'native_cpu_s_exact_wait4':usage.ru_utime+usage.ru_stime,
      'native_peak_rss_bytes_wait4':usage.ru_maxrss*1024,'output_bytes':H.directory_bytes(out),
      'scientific_admission':'NOT_ISSUED_BY_CONTROLLER'}
    save(task/'launches'/(item['case']['case']+'.receipt.json'),receipt);item['receipt']=receipt
    print(json.dumps({'status':'CASE_TERMINAL','case':receipt['case'],'complete':complete,'native_return':native,'stop_reason':receipt['stop_reason']}),flush=True)
def host_ticks():
    v=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]))
    return sum(v[i] for i in [0,1,2,5,6]),v[7]
def host_memory():
    v=dict((l.split(':',1)[0],int(l.split(':',1)[1].split()[0])*1024) for l in Path('/proc/meminfo').read_text().splitlines())
    return {'mem_total_bytes':v['MemTotal'],'mem_available_bytes':v['MemAvailable'],'mem_used_from_available_bytes':v['MemTotal']-v['MemAvailable']}
def host_preflight():
    def sample():
        data={}
        for p in Path('/proc').iterdir():
            if not p.name.isdigit():continue
            try:
                q=(p/'stat').read_text().rsplit(')',1)[1].split()
                data[int(p.name)]=(int(q[11])+int(q[12]),(p/'comm').read_text().strip(),int(q[17]),sorted(os.sched_getaffinity(int(p.name))))
            except (OSError,ProcessLookupError):pass
        return data
    a=sample();started=time.monotonic();time.sleep(2);b=sample();wall=time.monotonic()-started;active=[]
    for pid,(ticks,name,threads,affinity) in b.items():
        if pid in a:
            cpu=(ticks-a[pid][0])/os.sysconf('SC_CLK_TCK')
            if cpu/wall>.02:active.append({'pid':pid,'comm':name,'cpu_s':cpu,'mean_busy_cores':cpu/wall,'os_threads':threads,'affinity':affinity})
    return {'sample_wall_s':wall,'active_processes':sorted(active,key=lambda x:-x['cpu_s']),
       'observed_other_mean_busy_cores':sum(x['mean_busy_cores'] for x in active),**host_memory(),'other_jobs_untouched':True}

def main(plan_path):
    plan=json.loads(plan_path.read_text());task=Path(plan['campaign_root']);epoch_root=Path(plan['source_epoch_root'])
    source=plan['source_identity_sha256'];binary_sha=plan['binary_sha256']
    H.TASK=task;H.STAGE=epoch_root/'stage';H.BINARY=Path(plan['binary'])
    H.SOURCE_SHA=source;H.BINARY_SHA=binary_sha
    H.verify_source();identity=H.source_identity();built=json.loads((epoch_root/'build_receipt.json').read_text())
    if hashlib.sha256(identity).hexdigest()!=source or H.sha(H.BINARY)!=binary_sha or built['returncode']!=0 or built['source_identity_sha256']!=source or built['binary_sha256']!=binary_sha:
        raise RuntimeError('full source/binary/build binding mismatch')
    cases=plan['cases']
    if len(cases)!=2 or {c['transport_cells'] for c in cases}!={512,1024} or sum(c['threads'] for c in cases)!=16:
        raise RuntimeError('two prescribed grid cases required')
    cpus=[q for c in cases for q in c['cpus']]
    if sorted(cpus)!=list(range(16)) or not set(cpus)<=os.sched_getaffinity(0):
        raise RuntimeError('disjoint available affinity0..15 required')
    if any(c['threads']!=8 or len(c['cpus'])!=8 or c['address_space_bytes']!=8*GIB or c['output_budget_bytes']!=12*GIB for c in cases):
        raise RuntimeError('fixed resource allocation mismatch')
    if shutil.disk_usage(task).free<32*GIB:raise RuntimeError('FULL_DISK_PREFLIGHT_BELOW32GiB')
    if (task/'campaign_epoch.json').exists():raise RuntimeError('campaign epoch already exists; never reset or silently restart')
    host=host_preflight();save(task/'host_preflight_before_launch.json',host)
    if host['observed_other_mean_busy_cores']>48 or host['mem_available_bytes']<24*GIB:raise RuntimeError('FULL_HOST_CAPACITY_PREFLIGHT')
    prepared=[]
    for c in cases:
        name=c['case'];base=task/'configs'/c['config'];out=task/'runs'/name
        if not re.fullmatch('[A-Za-z0-9_-]+',name) or out.exists():raise RuntimeError('fresh output required')
        if H.sha(base)!=c['config_sha256']:raise RuntimeError('prepared config identity mismatch')
        prepared.append((c,base,checked_config(base,c['transport_cells']),out))
    (task/'launches').mkdir(exist_ok=True);(task/'runs').mkdir(exist_ok=True)
    save(task/'full_campaign.binding.json',{'plan':plan,'plan_sha256':H.sha(plan_path),
      'controller_sha256':H.sha(Path(__file__)),'helpers_sha256':H.sha(Path(H.__file__)),
      'source_identity_sha256':source,'binary_sha256':binary_sha,'prepared_utc':H.utc(),
      'start_disk_free_bytes':shutil.disk_usage(task).free,'our_worker_allocation':16,
      'native_rss_cap_bytes_per_case':2*GIB,'other_jobs_untouched':True,
      'scientific_admission':'CONDITIONAL_FULL_EXECUTION_ONLY_NOT_FULL_ACCURACY_CERTIFICATE'})
    active=[];started=time.monotonic();last_status=-30;last_cpu=0.;last_sample=started;global_reason=None;last_host_busy,last_host_steal=host_ticks()
    epoch_now=time.time();epoch={'first_full_launch_epoch':epoch_now,'first_full_launch_utc':H.utc(),
      'deadline_epoch':epoch_now+43200,'cumulative_wall_cap_s':43200,'closeout_reserve_s':300,
      'never_reset_on_resume':True}
    save(task/'campaign_epoch.json',epoch)
    with (task/'full_campaign.telemetry.jsonl').open('x') as telemetry:
        try:
            for c,base,text,out in prepared:
                remaining=int(epoch['deadline_epoch']-time.time()-300)
                if remaining<=30:raise RuntimeError('FULL_CAMPAIGN_COMPUTE_DEADLINE')
                runtime=task/'launches'/(c['case']+'.runtime.cfg')
                modified,n=re.subn(r'(?m)^max_wall_s=42880$',f'max_wall_s={remaining-20}',text)
                if n!=1:raise RuntimeError('wall-only runtime binding failed')
                with runtime.open('x') as f:f.write(modified)
                cmd=['taskset','-c',','.join(map(str,c['cpus'])),'prlimit',
                  '--as='+str(c['address_space_bytes']),'--fsize='+str(c['output_budget_bytes']),
                  '--',str(H.BINARY),'--config',str(runtime),'--output',str(out),'--case',c['case']]
                binding={'case':c['case'],'command':cmd,'source_identity_sha256':source,
                  'binary_sha256':binary_sha,'base_config_sha256':H.sha(base),'runtime_config_sha256':H.sha(runtime),
                  'cpus':c['cpus'],'threads':8,'address_space_bytes':8*GIB,'output_budget_bytes':12*GIB,
                  'native_rss_cap_bytes':2*GIB,'native_max_wall_s':remaining-20,
                  'shared_campaign_deadline_epoch':epoch['deadline_epoch'],'closeout_reserve_s':300,
                  'checkpoint_wall_s':30,'spectra_every_accepted':2000,'start_utc':H.utc()}
                save(task/'launches'/(c['case']+'.binding.json'),binding)
                log=(task/'launches'/(c['case']+'.log')).open('x')
                proc=subprocess.Popen(cmd,env=H.environment(),stdout=log,stderr=subprocess.STDOUT,
                  stdin=subprocess.DEVNULL,start_new_session=True)
                active.append({'case':c,'out':out,'runtime':runtime,'binding':binding,'log':log,'proc':proc,
                  'started':time.monotonic(),'terminal':False,'term_at':None,'peak_rss':0,'peak_threads':0,'peak_cpu':0.})
                print(json.dumps({'status':'CASE_LAUNCHED','case':c['case'],'pid':proc.pid,'cpus':c['cpus'],'threads':8}),flush=True)
            while not all(x['terminal'] for x in active):
                now=time.monotonic();samples=[];output_total=0;rss_total=0;cpu_total=0.
                for item in active:
                    if not item['terminal']:
                        pid,status,usage=os.wait4(item['proc'].pid,os.WNOHANG)
                        if pid:finish(item,status,usage,identity,source,binary_sha,task)
                    if item['terminal']:
                        output_total+=item['receipt']['output_bytes'];cpu_total+=item['receipt']['native_cpu_s_exact_wait4'];continue
                    sample=H.process_sample(item['proc'].pid);sample.update(case=item['case']['case'],
                      wall_s=now-item['started'],output_bytes=H.directory_bytes(item['out']),
                      checkpoint=H.checkpoint(item['out']/'checkpoint.txt'))
                    item['peak_rss']=max(item['peak_rss'],sample['rss_bytes'])
                    item['peak_threads']=max(item['peak_threads'],sample['os_threads'])
                    item['peak_cpu']=max(item['peak_cpu'],sample['cpu_s'])
                    output_total+=sample['output_bytes'];rss_total+=sample['rss_bytes'];cpu_total+=sample['cpu_s'];samples.append(sample)
                    if STOP:H.stop_case(item,'OWNER_CONTROLLER_STOP')
                    elif time.time()>=epoch['deadline_epoch']-310:H.stop_case(item,'SHARED_CAMPAIGN_DEADLINE_TERM')
                    elif sample['output_bytes']>=12*GIB:H.stop_case(item,'CASE_OUTPUT12GiB_CAP')
                    if item.get('term_at') is not None and now-item['term_at']>=10:
                        try:os.killpg(item['proc'].pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                disk_free=shutil.disk_usage(task).free
                host_busy,host_steal=host_ticks();memory=host_memory()
                if output_total>=24*GIB or rss_total>=112*GIB or disk_free<8*GIB or memory['mem_used_from_available_bytes']>112*GIB:
                    global_reason='GLOBAL_OUTPUT24GiB_CAP' if output_total>=24*GIB else 'HOST_MEMORY112GiB_CAP' if rss_total>=112*GIB else 'HOST_DISK_FREE8GiB_FLOOR' if disk_free<8*GIB else 'HOST_GLOBAL_MEMORY112GiB_CAP'
                    for item in active:H.stop_case(item,global_reason)
                elapsed=now-started;delta=now-last_sample
                record={'wall_s':elapsed,'utc':H.utc(),'live_cases':len(samples),
                  'configured_workers_live':sum(x['case']['threads'] for x in active if not x['terminal']),
                  'rss_bytes':rss_total,'output_bytes':output_total,'disk_free_bytes':disk_free,
                  'total_process_cpu_s':cpu_total,'observed_average_busy_cores_since_previous_sample':max(0,cpu_total-last_cpu)/delta if delta>0 else 0,
                  'case_samples':samples,'campaign_deadline_epoch':epoch['deadline_epoch'],**memory,
                  'host_global_mean_busy_cores_since_previous_sample':max(0,host_busy-last_host_busy)/os.sysconf('SC_CLK_TCK')/delta if delta>0 else 0,
                  'host_steal_cores_since_previous_sample':max(0,host_steal-last_host_steal)/os.sysconf('SC_CLK_TCK')/delta if delta>0 else 0}
                telemetry.write(json.dumps(record,allow_nan=False)+'\n');telemetry.flush()
                last_cpu=cpu_total;last_sample=now;last_host_busy=host_busy;last_host_steal=host_steal
                if elapsed-last_status>=30:H.atomic(task/'full_campaign.status.json',record);print(json.dumps({'status':'FULL_PROGRESS',**record}),flush=True);last_status=elapsed
                if not all(x['terminal'] for x in active):time.sleep(1)
        except BaseException:
            for item in active:H.stop_case(item,'CONTROLLER_EXCEPTION')
            deadline=time.monotonic()+10
            while any(not x['terminal'] for x in active):
                for item in active:
                    if item['terminal']:continue
                    if time.monotonic()>=deadline:
                        try:os.killpg(item['proc'].pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                    pid,status,usage=os.wait4(item['proc'].pid,os.WNOHANG)
                    if pid:finish(item,status,usage,identity,source,binary_sha,task)
                time.sleep(.1)
            raise
    H.verify_source()
    summary={'status':'ALL_FULL_CASES_COMPLETE_PENDING_SCIENTIFIC_POSTPROCESS' if all(x['receipt']['native_completion_proof'] for x in active) else 'FULL_CASES_TERMINAL_INCOMPLETE',
      'wall_s':time.monotonic()-started,'source_identity_sha256':source,'binary_sha256':binary_sha,
      'source_unchanged':True,'global_stop_reason':global_reason,'campaign_epoch':epoch,
      'total_exact_process_cpu_s':sum(x['receipt']['native_cpu_s_exact_wait4'] for x in active),
      'output_bytes':sum(x['receipt']['output_bytes'] for x in active),'scientific_admission':'NOT_ISSUED_BY_CONTROLLER'}
    save(task/'full_campaign.receipt.json',summary);print(json.dumps(summary),flush=True)
    return 0 if all(x['receipt']['native_completion_proof'] for x in active) else 1
def handler(_signum,_frame):
    global STOP
    STOP=True
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);a=p.parse_args()
    signal.signal(signal.SIGTERM,handler);signal.signal(signal.SIGINT,handler)
    raise SystemExit(main(a.plan.resolve()))
