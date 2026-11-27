"""PWBE fresh-scope bounded executor; prior plumbing only, no repair authorization."""
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
PLAN=[('01_tests','test_pwbe.py',2,5),
      ('02_azimuth_analysis','run_azimuth_analysis.py',2,5),
      ('03_plot','plot_results.py',2,10)]


def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    b=path.read_bytes()
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


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
    r=resource.getrusage(kind)
    return r.ru_utime+r.ru_stime


def main():
    p=argparse.ArgumentParser()
    p.add_argument('run_id',choices=[x[0] for x in PLAN])
    p.add_argument('--repair-reason',choices=['C6-ASSERT-01'],help='explicit root-authorized two-method assertion repair')
    p.add_argument('--saved-plot-continuation',action='store_true',help='root-authorized one saved-output-only C8 continuation in same allocation')
    args=p.parse_args()
    if args.saved_plot_continuation and (args.run_id!='03_plot' or args.repair_reason):
        raise RuntimeError('continuation is plot-only and is not another repair reserve')
    EXEC.mkdir(parents=True,exist_ok=True)
    lock=EXEC/'RUN.lock'
    stale_cleanup=None
    if args.saved_plot_continuation and lock.exists():
        prior=json.loads(LEDGER.read_text())
        if lock.stat().st_size!=0 or len(prior['attempts'])!=4 or any(x['status']=='START' for x in prior['attempts']):
            raise RuntimeError('unexpected task lock or unfinished ledger; return to root')
        stale_cleanup={'path':str(lock),'bytes':0,'reason':'root native continuation GO; four known finished attempts; task-owned empty transient lock only','process_absence_claim':False}
        lock.unlink()
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    try:
        manifest=UNIT/'evidence/preparation/PREPARATION_MANIFEST.json'
        current_inputs={name:digest(UNIT/name) for name in json.loads(manifest.read_text())['frozen_inputs']}
        ledger=json.loads(LEDGER.read_text())
        attempts=ledger['attempts']
        if any(a['status']=='START' for a in attempts):raise RuntimeError('incomplete START: UNKNOWN_NOT_ZERO blocks launch')
        repair=None
        if args.saved_plot_continuation:
            if len(attempts)!=4 or [x['status'] for x in attempts]!=['FAIL','PASS','PASS','FAIL'] or ledger['diagnosed_repair_reserve']['used']!=1:
                raise RuntimeError('sole saved-output continuation requires the preserved four-attempt state')
            for name,expected in [('code/plot_results.py','bac815be2cacb9ed69a067a491b297e848c0f9ee5647f5402226ec9396395d68'),('results/AZIMUTH_ANALYSIS.json','fe6c23f3475ba9c50dd4c295ce0687f61db666babc04198a4a4faf7e35ae21e5')]:
                current_inputs[name]=digest(UNIT/name)
                if current_inputs[name]['sha256']!=expected:raise RuntimeError('saved-output continuation input identity changed')
        elif args.repair_reason:
            if args.run_id!='01_tests' or len(attempts)!=1 or attempts[0]['run_id']!='01_tests' or attempts[0]['status']!='FAIL':
                raise RuntimeError('C6-ASSERT-01 is the sole two-method reserve immediately after initial test FAIL')
            if ledger['diagnosed_repair_reserve']['used']:
                raise RuntimeError('reserve already consumed')
            repair={'reason':'C6-ASSERT-01','authority':'root explicit task; evidence/C6_ASSERT_REPAIR_AUTHORIZATION.json',
                    'scope':'test01 existing close comparison and test06 remove absolute0 override; two methods only; core/source/analysis unchanged'}
        else:
            if len(attempts)>=2 and attempts[0]['status']=='FAIL' and attempts[1].get('repair') and attempts[1]['status']=='PASS':
                if any(a['status']!='PASS' for a in attempts[2:]):
                    raise RuntimeError('post-repair failure blocks automatic continuation')
                index=len(attempts)-1
            else:
                if any(a['status']!='PASS' for a in attempts):
                    raise RuntimeError('failure requires explicit root diagnosis')
                index=len(attempts)
            if index>=len(PLAN) or PLAN[index][0]!=args.run_id:
                raise RuntimeError('planned sequential order required; no full suite replay')
        _,script,cap_cpu,cap_wall=next(x for x in PLAN if x[0]==args.run_id)
        if repair:cap_cpu,cap_wall=2,10
        if args.saved_plot_continuation:cap_cpu,cap_wall=3,10
        if (len(attempts)>=4 and not args.saved_plot_continuation) or ledger['cumulative_cpu_s']+cap_cpu>8 or ledger['cumulative_wall_s']+cap_wall>30:
            raise RuntimeError('fresh unit cumulative budget would be exceeded')
        identity=f'{len(attempts)+1:02d}_{args.run_id}'
        outdir=EXEC/identity;outdir.mkdir()
        env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1',
             'MKL_NUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','MPLBACKEND':'Agg',
             'PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':str(UNIT.parents[2]/'pwbe_ops/mplconfig')}
        Path(env['MPLCONFIGDIR']).mkdir(parents=True,exist_ok=True)
        command=[sys.executable,'-B','code/'+script]
        if repair:command+=['--repair-only','C6-ASSERT-01']
        start_wall=time.monotonic();start_parent=cpu(resource.RUSAGE_SELF);start_child=cpu(resource.RUSAGE_CHILDREN)
        row={'attempt_id':identity,'run_id':args.run_id,'command':command,'started_utc':stamp(),
             'status':'START','repair':repair,
             'continuation':{'id':'C8-SAVED-OUTPUT-01','authority':'root current native followup GO after fresh survey; renewed explicit user request; evidence/C8_SAVED_OUTPUT_CONTINUATION.json','old_no_fifth_rule':'historical four-attempt snapshot; prospectively amended for one saved-output-only render','new_budget_or_reserve':False,'stale_task_lock_cleanup':stale_cleanup} if args.saved_plot_continuation else None,'caps':{'cpu_s':cap_cpu,'wall_s':cap_wall,'memory_bytes':536870912,'threads':1},
             'remaining_before_cpu_s':8-ledger['cumulative_cpu_s'],'remaining_before_wall_s':30-ledger['cumulative_wall_s'],
             'incomplete_START_accounting':'UNKNOWN_NOT_ZERO; blocks replay',
             'preparation_manifest_sha256':digest(manifest)['sha256'], 'current_input_identities':current_inputs,
             'authority':'Astra root explicit native task GO after PWBE B1 dual-provider ACK and R7; no additional authorization gate'}
        if repair:
            ledger['diagnosed_repair_reserve']['used']=1
            ledger['diagnosed_repair_reserve']['remaining']=0
        if args.saved_plot_continuation:
            ledger['state']='C8_ONE_SAVED_OUTPUT_CONTINUATION_START_SAME_ALLOCATION'
            ledger['prospective_continuation']={'id':'C8-SAVED-OUTPUT-01','additional_render_max':1,'used':1,'cpu_s':3,'wall_s':10,'same_cumulative_allocation':[8,30],'reserve_used_remains':1,'reserve_remaining':0,'authority':'root current native followup GO; evidence/C8_SAVED_OUTPUT_CONTINUATION.json'}
        attempts.append(row);atomic(outdir/'START.json',row);atomic(LEDGER,ledger)
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU,(cap_cpu,cap_cpu))
            resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
        timed_out=False;launch_error=None;returncode=None
        try:
            with (outdir/'stdout.txt').open('wb') as out,(outdir/'stderr.txt').open('wb') as err:
                child=subprocess.Popen(command,cwd=UNIT,env=env,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits)
                try:returncode=child.wait(timeout=cap_wall)
                except subprocess.TimeoutExpired:
                    timed_out=True;os.killpg(child.pid,signal.SIGKILL);returncode=child.wait()
        except Exception as exc:
            launch_error=repr(exc)
        wall=time.monotonic()-start_wall
        parent_cpu=cpu(resource.RUSAGE_SELF)-start_parent
        child_cpu=cpu(resource.RUSAGE_CHILDREN)-start_child
        total_cpu=parent_cpu+child_cpu
        overshoot=total_cpu>cap_cpu or wall>cap_wall
        row.update(finished_utc=stamp(),returncode=returncode,child_cpu_s=child_cpu,parent_cpu_s=parent_cpu,
                   cpu_s=total_cpu,wall_s=wall,timed_out=timed_out,launch_error=launch_error,
                   measured_cap_overshoot=overshoot,
                   status='PASS' if returncode==0 and not timed_out and not launch_error and not overshoot else 'FAIL')
        row['outputs']={name:digest(outdir/name) for name in ('stdout.txt','stderr.txt') if (outdir/name).exists()}
        ledger['cumulative_cpu_s']+=total_cpu;ledger['cumulative_wall_s']+=wall
        atomic(outdir/'FINISH.json',row);atomic(LEDGER,ledger)
        print(json.dumps({'attempt':identity,'status':row['status'],'cpu_s':total_cpu,'wall_s':wall,
                          'cumulative_cpu_s':ledger['cumulative_cpu_s'],'cumulative_wall_s':ledger['cumulative_wall_s']}))
        return 0 if row['status']=='PASS' else 1
    finally:
        lock.unlink()


if __name__=='__main__':sys.exit(main())
