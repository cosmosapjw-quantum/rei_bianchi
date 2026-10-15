"""Mechanical frozen-contract runner; manufactured-rate benchmark only."""
from pathlib import Path
import datetime, hashlib, json, os, platform, re, shutil, signal, subprocess, time

BASE = Path('/root/REI_C16B_NATIVE_20261016')
HERE = BASE / 'benchmark'
PKG = HERE / 'package'
SOURCE = BASE / 'REI_C16B_THERMAL_REACTION_HANDOFF_20261016'
PYTHON = str(BASE / 'venv/bin/python')
OUT = HERE / 'runs'
OUT.mkdir(exist_ok=True)
start = time.monotonic()
deadline = start + 300
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def sources(root):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
source_hashes = sources(SOURCE)
assert sources(PKG) == source_hashes
receipt = {
    'schema':'rei.c16b.bounded_manufactured_benchmark.v1',
    'utc_started':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'claim_scope':'MANUFACTURED_RATE_ONLY; mechanical deterministic worker-count parity, no scientific admission',
    'selected_stages':['C6','C8'],
    'executor':'native delegated coding worker; observed model identity unavailable',
    'hardware':{'platform':platform.platform(),'cpu_count':os.cpu_count(), 'intake_resources':'intake/resources_initial.json'},
    'limits':{'total_wall_seconds':300,'aggregate_rss_bytes':8*1024**3,'pool_worker_processes':8,'process_interpretation':'jobs8 explicitly requires eight workers plus one Python orchestrator; time wrapper separately counted'},
    'environment':{k:env[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','PYTHONDONTWRITEBYTECODE')},
    'python':subprocess.check_output([PYTHON,'--version'],text=True).strip(),
    'source_sha256':source_hashes,'runs':[],'repairs':[],
    'checkpoint':'Isolated package byte-matched to restored source before execution; serial then jobs8 frozen workload.'
}
def save():
    (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
save()
def proc_snapshot(root_pid):
    stats={}
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            row=path.read_text(); rest=row[row.rfind(')')+2:].split()
            pid=int(path.parent.name); stats[pid]=(int(rest[1]),int(rest[21])*os.sysconf('SC_PAGE_SIZE'),row[row.find('(')+1:row.rfind(')')])
        except (ValueError,FileNotFoundError,ProcessLookupError,PermissionError,IndexError):
            continue
    selected={root_pid}
    changed=True
    while changed:
        old=len(selected); selected.update(pid for pid,st in stats.items() if st[0] in selected); changed=len(selected)!=old
    rows=[(pid,*stats[pid]) for pid in selected if pid in stats]
    return {'aggregate_rss_bytes':sum(row[2] for row in rows), 'process_count':len(rows), 'python_process_count':sum('python' in row[3] for row in rows)}
for jobs,label in [(1,'serial'),(8,'jobs8')]:
    directory=OUT/label; directory.mkdir(exist_ok=True)
    command=['/usr/bin/time','-v','-o',str(directory/'time_verbose.log'),PYTHON,'hpc_sweep.py','--cases','64','--substeps','64','--jobs',str(jobs),'--out',str(directory)]
    record={'label':label,'jobs':jobs,'command':command,'cwd':str(PKG),'utc_started':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    begun=time.monotonic(); peak_rss=peak_procs=peak_python=0; stopped=None
    with (directory/'stdout.log').open('w') as stdout, (directory/'stderr.log').open('w') as stderr:
        process=subprocess.Popen(command,cwd=PKG,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        while process.poll() is None:
            snap=proc_snapshot(process.pid)
            peak_rss=max(peak_rss,snap['aggregate_rss_bytes']); peak_procs=max(peak_procs,snap['process_count']); peak_python=max(peak_python,snap['python_process_count'])
            if time.monotonic()>deadline:
                stopped='TOTAL_WALL_LIMIT'
            elif snap['aggregate_rss_bytes']>8*1024**3:
                stopped='AGGREGATE_RSS_LIMIT'
            if stopped:
                os.killpg(process.pid,signal.SIGTERM)
                try: process.wait(timeout=3)
                except subprocess.TimeoutExpired: os.killpg(process.pid,signal.SIGKILL); process.wait()
                break
            time.sleep(0.05)
        exit_code=process.wait()
    record.update(exit_code=exit_code,wall_seconds=time.monotonic()-begun,peak_sampled_aggregate_rss_bytes=peak_rss,peak_sampled_tree_processes_including_time=peak_procs,peak_sampled_python_processes=peak_python,stop_reason=stopped)
    (directory/'exit.txt').write_text(str(exit_code)+'\n')
    timelog=(directory/'time_verbose.log').read_text()
    for key,pattern in [('time_maximum_rss_kib',r'Maximum resident set size \(kbytes\): (\d+)'),('time_user_seconds',r'User time \(seconds\): ([\d.]+)'),('time_system_seconds',r'System time \(seconds\): ([\d.]+)')]:
        match=re.search(pattern,timelog)
        if match: record[key]=float(match.group(1))
    if (directory/'timing.json').exists(): record['sweep_timing']=json.loads((directory/'timing.json').read_text())
    if (directory/'results.json').exists(): record['result_sha256']=sha(directory/'results.json')
    receipt['runs'].append(record); save()
    if exit_code:
        shutil.copy2(directory/'stderr.log',HERE/'first_failure.log')
        receipt['first_failure']={'run':label,'exit_code':exit_code,'log':'first_failure.log'}; save()
        break
if len(receipt['runs'])==2 and all(r['exit_code']==0 for r in receipt['runs']):
    command=['cmp',str(OUT/'serial/results.json'),str(OUT/'jobs8/results.json')]
    compared=subprocess.run(command,capture_output=True,text=True)
    (HERE/'cmp.log').write_text(compared.stdout+compared.stderr)
    (HERE/'cmp.exit').write_text(str(compared.returncode)+'\n')
    receipt['parity']={'comparison':'EXACT_RESULT_BYTES','command':command,'exit_code':compared.returncode,'equal':compared.returncode==0}
    if compared.returncode==0:
        receipt['observed_sweep_speed_ratio_serial_over_jobs8']=receipt['runs'][0]['sweep_timing']['wall_seconds']/receipt['runs'][1]['sweep_timing']['wall_seconds']
receipt['source_unchanged']=sources(SOURCE)==source_hashes
receipt['isolated_source_unchanged']=all(sha(PKG/p)==digest for p,digest in source_hashes.items())
receipt['total_runner_wall_seconds']=time.monotonic()-start
receipt['utc_finished']=datetime.datetime.now(datetime.timezone.utc).isoformat()
save()
print(json.dumps({'runs':receipt['runs'],'parity':receipt.get('parity'),'source_unchanged':receipt['source_unchanged'],'total_wall_seconds':receipt['total_runner_wall_seconds']},indent=2))
