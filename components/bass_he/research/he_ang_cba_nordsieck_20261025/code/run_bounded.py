"""CBA Nordsieck distinct20CPU/60wall increment; planned runs once only."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time

UNIT=Path(__file__).resolve().parents[1]
EXEC=UNIT/'evidence/execution'
LEDGER=EXEC/'RESOURCE_LEDGER.json'
PLAN=[('01_tests','test_cba.py',3,10),('02_analysis','run_analysis.py',10,25),('03_plot','plot_results.py',3,10)]


def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    b=path.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def atomic(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.')
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
        fd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def cpu(kind):
    r=resource.getrusage(kind);return r.ru_utime+r.ru_stime


def main():
    p=argparse.ArgumentParser();p.add_argument('run_id',choices=[r[0] for r in PLAN]);args=p.parse_args()
    EXEC.mkdir(parents=True,exist_ok=True);lock=EXEC/'RUN.lock'
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    try:
        manifest=UNIT/'evidence/preparation/PREPARATION_MANIFEST.json'
        prep=json.loads(manifest.read_text());current={name:digest(UNIT/name) for name in prep['frozen_inputs']}
        for name, expected in prep['frozen_inputs'].items():
            if current[name]!=expected:raise RuntimeError('frozen input changed: '+name)
        wheel=UNIT.parents[2]/prep['dependency']['wheel_relative_to_workspace']
        if digest(wheel)!=prep['dependency']['wheel_identity']:raise RuntimeError('pinned dependency wheel changed')
        ledger=json.loads(LEDGER.read_text());attempts=ledger['attempts']
        if any(a['status']!='PASS' for a in attempts):raise RuntimeError('failure/incomplete START: preserve and return to root; no automatic retry')
        index=len(attempts)
        if index>=3 or PLAN[index][0]!=args.run_id:raise RuntimeError('planned order once only; reserve needs diagnosed native root amendment')
        _,script,cap_cpu,cap_wall=PLAN[index]
        if ledger['cumulative_cpu_s']+cap_cpu>20 or ledger['cumulative_wall_s']+cap_wall>60:
            raise RuntimeError('same increment cumulative limit would be exceeded')
        identity=f'{index+1:02d}_{args.run_id}';outdir=EXEC/identity;outdir.mkdir()
        env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1',
             'NUMEXPR_NUM_THREADS':'1','MPLBACKEND':'Agg','PYTHONDONTWRITEBYTECODE':'1',
             'PYTHONPATH':str(wheel)+os.pathsep+os.environ.get('PYTHONPATH',''),
             'MPLCONFIGDIR':str(UNIT.parents[2]/'cba_nordsieck_ops_20261025/mplconfig')}
        Path(env['MPLCONFIGDIR']).mkdir(parents=True,exist_ok=True)
        command=[sys.executable,'-B','code/'+script]
        start_wall=time.monotonic();start_parent=cpu(resource.RUSAGE_SELF);start_child=cpu(resource.RUSAGE_CHILDREN)
        row={'attempt_id':identity,'run_id':args.run_id,'command':command,'started_utc':stamp(),
             'status':'START','caps':{'cpu_s':cap_cpu,'wall_s':cap_wall,'memory_bytes':536870912,'threads':1},
             'remaining_before_cpu_s':20-ledger['cumulative_cpu_s'],'remaining_before_wall_s':60-ledger['cumulative_wall_s'],
             'preparation_manifest_sha256':digest(manifest)['sha256'],'current_input_identities':current,
             'dependency_wheel_identity':digest(wheel),'dependency_mode':'Existing pinned pure-Python wheel via PYTHONPATH zip import; no installation',
             'authority':'Execution invoked only under root explicit GO after R6/R7 and actual B1 dual ACK; invocation itself does not admit science',
             'incomplete_START_accounting':'UNKNOWN_NOT_ZERO; blocks automatic replay'}
        attempts.append(row);ledger['state']='ACTUAL_CHILD_START';atomic(outdir/'START.json',row);atomic(LEDGER,ledger)
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU,(cap_cpu,cap_cpu));resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
        timed_out=False;launch_error=None;returncode=None
        try:
            with (outdir/'stdout.txt').open('wb') as out,(outdir/'stderr.txt').open('wb') as err:
                child=subprocess.Popen(command,cwd=UNIT,env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits)
                try:returncode=child.wait(timeout=cap_wall)
                except subprocess.TimeoutExpired:
                    timed_out=True;os.killpg(child.pid,signal.SIGKILL);returncode=child.wait()
        except Exception as exc:launch_error=repr(exc)
        wall=time.monotonic()-start_wall;parent_cpu=cpu(resource.RUSAGE_SELF)-start_parent;child_cpu=cpu(resource.RUSAGE_CHILDREN)-start_child
        total_cpu=parent_cpu+child_cpu;overshoot=total_cpu>cap_cpu or wall>cap_wall
        row.update(finished_utc=stamp(),returncode=returncode,child_cpu_s=child_cpu,parent_cpu_s=parent_cpu,
                   cpu_s=total_cpu,wall_s=wall,timed_out=timed_out,launch_error=launch_error,measured_cap_overshoot=overshoot,
                   status='PASS' if returncode==0 and not timed_out and not launch_error and not overshoot else 'FAIL')
        row['outputs']={name:digest(outdir/name) for name in ('stdout.txt','stderr.txt') if (outdir/name).exists()}
        ledger['cumulative_cpu_s']+=total_cpu;ledger['cumulative_wall_s']+=wall
        ledger['state']='ACTUAL_'+str(len(attempts))+'_CHILDREN_FINISHED_'+row['status']
        ledger['zero_scope']='Current attempts contains actual completed/failed costs; host preparation/provider/model/IO costs remain separate UNKNOWN_NOT_ZERO'
        atomic(outdir/'FINISH.json',row);atomic(LEDGER,ledger)
        print(json.dumps({'attempt':identity,'status':row['status'],'cpu_s':total_cpu,'wall_s':wall,
                          'cumulative_cpu_s':ledger['cumulative_cpu_s'],'cumulative_wall_s':ledger['cumulative_wall_s']}))
        return 0 if row['status']=='PASS' else 1
    finally:lock.unlink()


if __name__=='__main__':raise SystemExit(main())
