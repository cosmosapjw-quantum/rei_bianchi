"""Separate resource-accounted raw-result analysis/plotting, zero IVPs."""
from pathlib import Path
import json
import os
import resource
import signal
import subprocess
import sys
import time

BASE=Path(__file__).resolve().parents[1]
R=BASE/'results'


def limits(cpu):
    resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
    resource.setrlimit(resource.RLIMIT_AS,(int(1.5*1024**3),int(1.5*1024**3)))


def main():
    budget=json.loads((R/'execution_budget.json').read_text())
    cpu=budget['cumulative_child_cpu_s'];wall=budget['cumulative_child_wall_s']
    assert cpu<300 and wall<420
    cap=min(60,max(1,int(300-cpu)))
    env=os.environ.copy()
    env['MPLCONFIGDIR']='/tmp/angtherm01_mpl_cache'
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
        env[key]='1'
    command=[sys.executable,str(BASE/'code/analyze_results.py')]
    before=resource.getrusage(resource.RUSAGE_CHILDREN);stamp=time.perf_counter()
    with (R/'analysis_stdout.log').open('w') as out,(R/'analysis_stderr.log').open('w') as err:
        proc=subprocess.Popen(command,cwd=BASE,env=env,stdout=out,stderr=err,preexec_fn=lambda:limits(cap),start_new_session=True)
        try:
            code=proc.wait(timeout=min(90,420-wall))
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM);code=proc.wait(timeout=5)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    result={'phase':'analysis_and_plotting','new_IVPs':0,'command':command,'returncode':code,
            'whole_child_wall_s':time.perf_counter()-stamp,
            'whole_child_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            'whole_child_maxRSS_KiB':after.ru_maxrss}
    (R/'analysis_execution.json').write_text(json.dumps(result,indent=2)+'\n')
    budget.setdefault('postprocessing',[]).append(result)
    budget['cumulative_child_cpu_s']+=result['whole_child_cpu_s']
    budget['cumulative_child_wall_s']+=result['whole_child_wall_s']
    (R/'execution_budget.json').write_text(json.dumps(budget,indent=2)+'\n')
    print(json.dumps(result,indent=2));sys.exit(0 if code==0 else 1)


if __name__=='__main__':
    main()
