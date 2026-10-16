#!/usr/bin/env python3
"""Five fresh, source-bound cases under one explicit 64-worker allocation.
This controller changes only transport_threads in each runtime config.
"""
import argparse,datetime,hashlib,json,math,os,re,signal,subprocess,time
from pathlib import Path
TASK=Path('/root/REI_FLRW_COVARIANT_20261015_003')
STAGE=TASK/'stage'
BINARY=TASK/'target/release/examples/axbi_reionization'
TC=Path('/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001/toolchain')
SOURCE_SHA='63899f056e57de9a9bcfe0e33ef0d61e73434e080f31c2838f8950025ba83529'
BINARY_SHA='408c76fdcb472f4ed47f5e115a946d5dc5cc198fe79878893b432a25bd1200d4'
GIB=1024**3
STOP=False

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_new(path,data):
    with path.open('x') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def atomic(path,data):
    temp=path.with_name(path.name+'.tmp');temp.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');os.replace(temp,path)
def environment():
    env=os.environ.copy();env.update(LD_LIBRARY_PATH=str(TC/'lib'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',RAYON_NUM_THREADS='1');return env

def source_identity():
    driver=STAGE/'rust/rei_microphysics/src/axbi_driver.rs'
    body=driver.read_text().split('pub fn compiled_identity() -> String {',1)[1].split('fn ledger_values',1)[0]
    return '\nAXBI_SOURCE_BOUNDARY\n'.join((driver.parent/p).read_text() for p in re.findall(r'include_str!\(\s*"([^"]+)"\s*\)',body)).encode()
def verify_source():
    for line in (STAGE/'SOURCE_SHA256SUMS.txt').read_text().splitlines():
        expected,name=line.split('  ',1)
        if sha(STAGE/name)!=expected:raise RuntimeError('staged source mismatch: '+name)

def directory_bytes(path):
    total=0
    if path.exists():
        for f in path.rglob('*'):
            try:
                if f.is_file():total+=f.stat().st_size
            except FileNotFoundError:pass
    return total

def process_sample(pid):
    pending=[pid];cpu=0;rss=0;threads=0;seen=[]
    while pending:
        current=pending.pop()
        try:
            values=Path(f'/proc/{current}/stat').read_text().rsplit(')',1)[1].split()
            cpu+=int(values[11])+int(values[12]);rss+=int(values[21])*os.sysconf('SC_PAGE_SIZE');threads+=int(values[17]);seen.append(current)
            pending.extend(map(int,Path(f'/proc/{current}/task/{current}/children').read_text().split()))
        except (FileNotFoundError,ProcessLookupError):pass
    return dict(cpu_s=cpu/os.sysconf('SC_CLK_TCK'),rss_bytes=rss,os_threads=threads,pids=seen)

def checkpoint(path):
    if not path.exists():return None
    try:
        rows=path.read_text().splitlines();v=list(map(float,rows[1].split()));c=list(map(int,rows[2].split()))
        if len(v)!=11 or len(c)!=6 or not all(math.isfinite(x) for x in v):raise ValueError('shape or nonfinite')
        return dict(version=rows[0],a=v[0],zbar=1/v[0]-1,accepted=c[0],attempts=c[1],rejections=c[2],rhs_evaluations=c[4],comparisons=c[5],next_dln_a=v[7],last_error=v[9],native_wall_s=v[10])
    except (ValueError,IndexError,FileNotFoundError) as e:return dict(read_error=str(e))

def config_fields(text):
    return dict(line.split('=',1) for line in text.splitlines() if line and not line.startswith('#'))
def checked_config(path,label,threads):
    original=path.read_text();v=config_fields(original)
    expected={'q_ref':0.0,'escape_fraction':0.2,'initial_x_hii':0.000210349192936,'initial_temperature_k':9.306042400380866,'energy_subdivisions':16,'background_panels':4096,'initial_dln_a':0.0001,'spectra_every_accepted':60,'end_zbar':19.8,'max_steps':80000,'max_attempts':260000,'max_rhs':20000000,'max_wall_s':1800,'output_budget_mib':2048,'transport_cells':128 if label=='q128' else 256 if label=='q256' else 512,'local_target':2.5e-6 if label=='q512_time' else 1e-5,'n_mu':16 if label=='q512_angle' else 8,'transport_threads':1}
    if set(v)!=set(expected)|{'same_h','inactive_hi_split'} or v['same_h']!='false' or v['inactive_hi_split']!='true':raise RuntimeError('unexpected config fields: '+label)
    for key,value in expected.items():
        if not math.isfinite(float(v[key])) or float(v[key])!=value:raise RuntimeError('frozen config mismatch '+label+':'+key)
    runtime,n=re.subn(r'(?m)^transport_threads=1$',f'transport_threads={threads}',original)
    if n!=1:raise RuntimeError('thread-only substitution failed')
    if {k:x for k,x in config_fields(runtime).items() if k!='transport_threads'}!={k:x for k,x in v.items() if k!='transport_threads'}:raise RuntimeError('non-thread config changed')
    return original,runtime

def stop_case(item,reason):
    if item.get('terminal') or item.get('term_at') is not None:return
    item['stop_reason']=reason;item['term_at']=time.monotonic()
    try:os.killpg(item['proc'].pid,signal.SIGTERM)
    except ProcessLookupError:pass

def final_receipt(item,status,usage,identity):
    item['proc'].returncode=os.waitstatus_to_exitcode(status)
    item['terminal']=True;item['log'].close();out=item['out'];native=None;parse_error=None
    if (out/'RETURN.txt').exists():
        try:
            native=config_fields((out/'RETURN.txt').read_text())
            for key in ['status','a','accepted','attempts','rejections','rhs_evaluations','wall_s','max_newton_residual','last_error','result']:native[key]
            if not all(math.isfinite(float(native[k])) for k in ['a','wall_s','max_newton_residual','last_error']):raise ValueError('nonfinite native return')
        except (KeyError,ValueError) as e:parse_error=str(e)
    else:parse_error='RETURN.txt absent'
    read_source=(out/'source_identity.txt').exists() and (out/'source_identity.txt').read_bytes()==identity
    read_config=(out/'config.cfg').exists() and (out/'config.cfg').read_bytes()==item['runtime'].read_bytes()
    bound=read_source and read_config and sha(BINARY)==BINARY_SHA
    complete=bool(native and not parse_error and native['status']=='COMPLETE_REPRESENTED_INTERVAL' and native['result']=='Ok(())' and float(native['a'])==1/(1+19.8) and item['proc'].returncode==0 and bound and item.get('stop_reason') is None)
    receipt=dict(case=item['case']['case'],returncode=item['proc'].returncode,wall_s=time.monotonic()-item['started'],terminal_utc=utc(),stop_reason=item.get('stop_reason'),native_return=native,terminal_parse_error=parse_error,native_completion_proof=complete,checkpoint=checkpoint(out/'checkpoint.txt'),source_identity_sha256=SOURCE_SHA,binary_sha256=BINARY_SHA,base_config_sha256=item['binding']['base_config_sha256'],runtime_config_sha256=sha(item['runtime']),source_identity_readback_equal=read_source,config_readback_equal=read_config,source_config_binary_bindings_match=bound,peak_process_tree_rss_bytes=item['peak_rss'],maximum_os_threads_observed=item['peak_threads'],observed_process_tree_cpu_s=item['peak_cpu'],native_cpu_user_s_exact_wait4=usage.ru_utime,native_cpu_system_s_exact_wait4=usage.ru_stime,native_cpu_s_exact_wait4=usage.ru_utime+usage.ru_stime,native_peak_rss_bytes_wait4=usage.ru_maxrss*1024,output_bytes=directory_bytes(out),sample_count=item['samples'],scientific_admission='NOT_ISSUED_BY_CONTROLLER')
    write_new(TASK/'launches'/(item['case']['case']+'.receipt.json'),receipt);item['receipt']=receipt
    print(json.dumps(dict(status='CASE_TERMINAL',case=receipt['case'],returncode=receipt['returncode'],complete=complete,stop_reason=receipt['stop_reason'],wall_s=receipt['wall_s'],native=native)),flush=True)

def main(plan_path,config_dir):
    plan=json.loads(plan_path.read_text());verify_source();identity=source_identity();built=json.loads((TASK/'build_receipt.json').read_text())
    if plan['source_identity_sha256']!=SOURCE_SHA or plan['binary_sha256']!=BINARY_SHA or hashlib.sha256(identity).hexdigest()!=SOURCE_SHA or sha(BINARY)!=BINARY_SHA or built['returncode']!=0 or built['source_identity_sha256']!=SOURCE_SHA or built['binary_sha256']!=BINARY_SHA:raise RuntimeError('immutable stage003 source/binary/build binding mismatch')
    cases=plan['cases'];labels={'q128','q256','q512','q512_time','q512_angle'}
    if len(cases)!=5 or {c['label'] for c in cases}!=labels:raise RuntimeError('five prescribed cases required')
    cpus=[v for c in cases for v in c['cpus']]
    if len(set(cpus))!=len(cpus) or set(cpus)!=set(range(64)) or not set(cpus)<=os.sched_getaffinity(0):raise RuntimeError('CPU sets must disjointly cover available0..63')
    if sum(c['threads'] for c in cases)!=64 or any(c['threads']!=len(c['cpus']) or not 1<=c['threads']<=64 for c in cases) or sum(c['memory_gib'] for c in cases)!=112 or plan['aggregate_output_gib']!=10:raise RuntimeError('aggregate resource binding mismatch')
    prepared=[]
    for c in cases:
        case=c['case'];out=TASK/'runs'/case
        if not re.fullmatch(r'[A-Za-z0-9_-]+',case) or out.exists() or any((TASK/'launches'/(case+suffix)).exists() for suffix in ['.binding.json','.receipt.json','.log','.runtime.cfg']):raise RuntimeError('fresh case paths required: '+case)
        base=config_dir/c['config'];original,runtime=checked_config(base,c['label'],c['threads']);prepared.append((c,out,base,original,runtime))
    (TASK/'launches').mkdir(exist_ok=True);(TASK/'runs').mkdir(exist_ok=True)
    write_new(TASK/'matrix003.binding.json',dict(plan=plan,plan_sha256=sha(plan_path),controller_sha256=sha(Path(__file__).resolve()),source_identity_sha256=SOURCE_SHA,binary_sha256=BINARY_SHA,source_manifest_sha256=sha(STAGE/'SOURCE_SHA256SUMS.txt'),start_utc=utc(),allocation=dict(workers=64,address_space_gib=112,output_gib=10,native_wall_s=1800,external_term_s=1820,external_kill_s=1830),cpu_accounting='Process utime/stime already includes all pthreads; descendants counted once, no /task double count; exact terminal wait4 also recorded'))
    active=[];started=time.monotonic();last_status=-30.0;last_cpu=0.0;last_sample=started;global_reason=None
    with (TASK/'matrix003.telemetry.jsonl').open('x') as telemetry:
        try:
            for c,out,base,original,runtime_text in prepared:
                name=c['case'];runtime=TASK/'launches'/(name+'.runtime.cfg');runtime.write_text(runtime_text)
                command=['taskset','-c',','.join(map(str,c['cpus'])),'prlimit',f"--as={c['memory_gib']*GIB}",f'--fsize={2*GIB}','--',str(BINARY),'--config',str(runtime),'--output',str(out),'--case',name]
                binding=dict(case=name,label=c['label'],command=command,source_identity_sha256=SOURCE_SHA,binary_sha256=BINARY_SHA,base_config_sha256=sha(base),runtime_config_sha256=sha(runtime),base_config=str(base),runtime_config=str(runtime),plan_sha256=sha(plan_path),threads=c['threads'],cpus=c['cpus'],address_space_bytes=c['memory_gib']*GIB,output_bytes=2*GIB,native_wall_s=1800,external_term_s=1820,external_kill_s=1830,start_utc=utc())
                write_new(TASK/'launches'/(name+'.binding.json'),binding)
                log=(TASK/'launches'/(name+'.log')).open('x');proc=subprocess.Popen(command,env=environment(),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                active.append(dict(case=c,out=out,runtime=runtime,binding=binding,log=log,proc=proc,started=time.monotonic(),peak_rss=0,peak_threads=0,peak_cpu=0.0,samples=0,term_at=None,terminal=False))
                print(json.dumps(dict(status='CASE_LAUNCHED',case=name,pid=proc.pid,threads=c['threads'],cpus=c['cpus'])),flush=True)
            while not all(x['terminal'] for x in active):
                now=time.monotonic();samples=[];output_total=0;rss_total=0;cpu_total=0.0
                for item in active:
                    if not item['terminal']:
                        pid,status,usage=os.wait4(item['proc'].pid,os.WNOHANG)
                        if pid:final_receipt(item,status,usage,identity)
                    if item['terminal']:
                        output_total+=item['receipt']['output_bytes'];cpu_total+=item['receipt']['native_cpu_s_exact_wait4'];continue
                    sample=process_sample(item['proc'].pid);sample.update(case=item['case']['case'],wall_s=now-item['started'],output_bytes=directory_bytes(item['out']),checkpoint=checkpoint(item['out']/'checkpoint.txt'))
                    item['peak_rss']=max(item['peak_rss'],sample['rss_bytes']);item['peak_threads']=max(item['peak_threads'],sample['os_threads']);item['peak_cpu']=max(item['peak_cpu'],sample['cpu_s']);item['samples']+=1
                    output_total+=sample['output_bytes'];rss_total+=sample['rss_bytes'];cpu_total+=sample['cpu_s'];samples.append(sample)
                    if STOP:stop_case(item,'OWNER_CONTROLLER_STOP')
                    elif sample['wall_s']>=1820:stop_case(item,'EXTERNAL_WALL_TERM_1820')
                    elif sample['output_bytes']>=2*GIB:stop_case(item,'CASE_OUTPUT_CAP')
                    if item.get('term_at') is not None and now-item['term_at']>=10:
                        try:os.killpg(item['proc'].pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                if output_total>=10*GIB or rss_total>=112*GIB:
                    global_reason='AGGREGATE_OUTPUT_CAP' if output_total>=10*GIB else 'AGGREGATE_RSS_CAP'
                    for item in active:stop_case(item,global_reason)
                elapsed=now-started;delta_wall=now-last_sample;busy=max(0.0,cpu_total-last_cpu)/delta_wall if delta_wall>0 else 0.0
                record=dict(wall_s=elapsed,utc=utc(),live_cases=len(samples),configured_workers_live=sum(x['case']['threads'] for x in active if not x['terminal']),rss_bytes=rss_total,output_bytes=output_total,total_process_cpu_s=cpu_total,observed_average_busy_cores_since_previous_sample=busy,case_samples=samples)
                telemetry.write(json.dumps(record,allow_nan=False)+'\n');telemetry.flush();last_cpu=cpu_total;last_sample=now
                if elapsed-last_status>=30:
                    atomic(TASK/'matrix003.status.json',record);print(json.dumps(dict(status='MATRIX_PROGRESS',**record)),flush=True);last_status=elapsed
                if not all(x['terminal'] for x in active):time.sleep(1)
        except BaseException:
            for item in active:stop_case(item,'CONTROLLER_EXCEPTION')
            deadline=time.monotonic()+10
            while any(not x['terminal'] for x in active):
                for item in active:
                    if item['terminal']:continue
                    if time.monotonic()>=deadline:
                        try:os.killpg(item['proc'].pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                    pid,status,usage=os.wait4(item['proc'].pid,os.WNOHANG)
                    if pid:final_receipt(item,status,usage,identity)
                time.sleep(.1)
            raise
    verify_source()
    summary=dict(status='ALL_CASES_COMPLETE_PENDING_SCIENTIFIC_SCREEN' if all(x['receipt']['native_completion_proof'] for x in active) else 'TERMINAL_CASES_SCREEN_INCOMPLETE',wall_s=time.monotonic()-started,global_stop_reason=global_reason,source_identity_sha256=SOURCE_SHA,binary_sha256=BINARY_SHA,source_unchanged=True,worker_allocation=64,memory_allocation_gib=112,output_allocation_gib=10,total_exact_process_cpu_s=sum(x['receipt']['native_cpu_s_exact_wait4'] for x in active),output_bytes=sum(x['receipt']['output_bytes'] for x in active),receipts=[str(TASK/'launches'/(x['case']['case']+'.receipt.json')) for x in active],scientific_admission='NOT_ISSUED_BY_CONTROLLER')
    write_new(TASK/'matrix003.receipt.json',summary);print(json.dumps(summary),flush=True)
    return 0 if all(x['receipt']['native_completion_proof'] for x in active) else 1

def handler(_signum,_frame):
    global STOP
    STOP=True
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--config-dir',type=Path,required=True);args=parser.parse_args();signal.signal(signal.SIGTERM,handler);signal.signal(signal.SIGINT,handler);raise SystemExit(main(args.plan.resolve(),args.config_dir.resolve()))
