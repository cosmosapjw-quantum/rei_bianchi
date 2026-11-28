"""Mechanical create-only resource boundary; imports no scientific module."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def save(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.link(tmp,path);tmp.unlink()

def manifest():
    files=sorted(list((ROOT/'src').glob('*.py'))+list((ROOT/'tests').glob('*.py'))+list((ROOT/'scripts').glob('*.py'))+[ROOT/'CONTRACT.md'])
    files += [ROOT.parent/name/'src'/file for name,file in [('continuation_harmonic_20261028','harmonic.py'),('continuation_azimuth_20261028','azimuth.py'),('continuation_kinematic_20261028','kinematic.py'),('continuation_aperture_20261027','aperture.py')]]
    # New src included by both globs; deterministic dictionary removes duplicate.
    return {str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['validate','plot'],required=True);p.add_argument('--source-commit',required=True);p.add_argument('--pin',required=True);p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--saved-json');p.add_argument('--cpu-cap',type=float);p.add_argument('--wall-cap',type=float);p.add_argument('--test-name',action='append',default=[]);a=p.parse_args()
    pin=json.loads(Path(a.pin).read_text());observed=manifest()
    if pin['source_commit']!=a.source_commit or pin['source_sha256']!=observed:raise SystemExit('authorized publication/source manifest differs')
    if hashlib.sha256(Path(a.source).read_bytes()).hexdigest()!=pin['input_sha256']:raise SystemExit('immutable input differs')
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    cpu,wall=(60,180) if a.mode=='validate' else (10,30);cpu=min(cpu,a.cpu_cap) if a.cpu_cap else cpu;wall=min(wall,a.wall_cap) if a.wall_cap else wall
    if cpu<1 or wall<=0:raise SystemExit('budget exhausted')
    if a.mode=='validate':cmd=[sys.executable,'-B',str(ROOT/'scripts/validate_once.py'),'--saved-json',str(out/'SAVED_PLOT_DATA.json'),'--report-json',str(out/'TEST_REPORT.json'),'--source',str(Path(a.source).resolve())]
    else:
        if not a.saved_json:raise SystemExit('plot requires saved JSON')
        cmd=[sys.executable,'-B',str(ROOT/'scripts/plot_saved.py'),'--saved-json',str(Path(a.saved_json).resolve()),'--output',str(out)]
    for name in a.test_name:cmd+=['--test-name',name]
    env=os.environ.copy();env.update({k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')});env.update(PYTHONDONTWRITEBYTECODE='1',MPLBACKEND='Agg',MPLCONFIGDIR='/tmp/exfor11-mpl')
    record={'mode':a.mode,'source_commit':a.source_commit,'source_sha256':observed,'command':cmd,'start':datetime.now(timezone.utc).isoformat(),'limits':{'cpu_s':cpu,'wall_s':wall,'memory_bytes':768*1024**2,'threads':1}}
    save(out/'START.json',record)
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(int(cpu),int(cpu)));resource.setrlimit(resource.RLIMIT_AS,(768*1024**2,768*1024**2));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    before=resource.getrusage(resource.RUSAGE_CHILDREN);t=time.perf_counter();own=time.process_time()
    with (out/'stdout.log').open('x') as stdout,(out/'stderr.log').open('x') as stderr:
        child=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,env=env,cwd=ROOT,preexec_fn=limits,start_new_session=True);timed=False
        try:code=child.wait(timeout=wall)
        except subprocess.TimeoutExpired:timed=True;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
    after=resource.getrusage(resource.RUSAGE_CHILDREN);used=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime+time.process_time()-own;elapsed=time.perf_counter()-t
    record.update(exit_code=code,timed_out=timed,cpu_s=used,wall_s=elapsed,maxrss_kib=after.ru_maxrss,status='PASS' if code==0 and not timed and used<=cpu and elapsed<=wall else 'FAIL')
    save(out/'RESOURCE_RESULT.json',record);print(json.dumps(record));sys.exit(0 if record['status']=='PASS' else 1)
