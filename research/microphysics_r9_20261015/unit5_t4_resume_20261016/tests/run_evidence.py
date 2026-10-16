"""Execute the frozen bounded local suite and preserve commands/exit/timing."""
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/final_run';OUT.mkdir(exist_ok=False)
records=[]
env=os.environ|{'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','UNIT5_OBSERVATIONS':str(OUT/'dense_observations.json')}

def run(name,cmd):
    start=time.monotonic();utc=dt.datetime.now(dt.timezone.utc).isoformat()
    p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=30)
    (OUT/(name+'.stdout.log')).write_text(p.stdout);(OUT/(name+'.stderr.log')).write_text(p.stderr)
    record={'name':name,'command':cmd,'cwd':str(Path.cwd()),'started_utc':utc,'elapsed_s':time.monotonic()-start,'exit_code':p.returncode,
            'stdout':name+'.stdout.log','stderr':name+'.stderr.log','timeout_s':30}
    records.append(record);return p

run('tests',[sys.executable,str(ROOT/'tests/test_resume.py')])
run('exact',[sys.executable,str(ROOT/'tests/exact_resolvent_check.py')])
primary='/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3'
run('exact_primary',[primary,str(ROOT/'tests/exact_resolvent_check.py')])
run('exact_fraction',[sys.executable,str(ROOT/'tests/exact_fraction_check.py')])
run('prepare',[sys.executable,str(ROOT/'code/t4_resume.py'),'prepare','--out',str(OUT/'prepared')])
# Build the synthetic exact legacy-format fixture. This invokes only a 96D toy K.
spec=importlib.util.spec_from_file_location('fixture_helpers',ROOT/'tests/test_resume.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
K,g,u=t.fixture();old,_,bu=t.legacy(OUT/'native_fixture_input',K,g,u,64)
now=dt.datetime.now(dt.timezone.utc)
allocation={'authorized':True,'allocation_id':'SYNTHETIC_LOCAL_ONLY','issued_utc':(now-dt.timedelta(seconds=1)).isoformat(),
  'absolute_deadline_utc':(now+dt.timedelta(seconds=25)).isoformat(),'wall_s':7200,'memory_gib':24,
  'omp_threads':12,'blas_threads':1,'maximum_new_Hamiltonian_actions':70}
worker_out=OUT/'native_fixture_worker';worker_out.mkdir()
config={'out':str(worker_out),'receipt':'SYNTHETIC','data':'SYNTHETIC','v6_source':'SYNTHETIC',
        'checkpoint':str(OUT/'native_fixture_input/checkpoint.npz'),'allocation':allocation}
t.b.dump(OUT/'native_fixture_config.json',config)
command=[sys.executable,str(ROOT/'tests/native_fixture_worker.py'),str(OUT/'native_fixture_config.json')]
started=time.monotonic()
result=t.b.supervise(command,worker_out,25,24.,env=env,headroom_gib=0)
records.append({'name':'synthetic_native_worker','command':command,'cwd':str(Path.cwd()),'elapsed_s':time.monotonic()-started,
    'exit_code':result['supervisor_exit_code'],'stdout':'native_fixture_worker/stdout.log','stderr':'native_fixture_worker/stderr.log',
    'supervised_wall_cap_s':25,'supervised_memory_cap_gib':24,'headroom_check':'disabled for small toy supervisor only; toy worker budget also disables headroom; production default unchanged',
    'fixture':'injected toy loader/reconstruction; actual acquisition identity check replaced only for toy checkpoint'})
import numpy as np
versions={'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'executable':sys.executable,'sympy':'unavailable in both tested runtimes'}
t.b.dump(OUT/'execution.json',{'unit':t.r.UNIT,'requested_executor_model':'gpt-6.1-sol','observed_runtime_model':'UNKNOWN',
    'versions':versions,'commands':records,'actual_checkpoint_compatibility':'NOT_RUN','actual_physical_H_actions':0,
    'NCP_actions':0,'actual_refinement':'HOLD','historical_actions':t.r.HISTORY,
    'native_PySCF_reconstruction':'NOT_RUN','scientific_admission':'PENDING independent Astra review'})
print(json.dumps({'commands':[(x['name'],x['exit_code']) for x in records],
    'native_fixture_status':result['status'],'native_fixture_actions':result.get('new_Hamiltonian_actions'),
    'native_fixture_length':result.get('last_length')},indent=2))
assert records[0]['exit_code']==0 and records[3]['exit_code']==0 and records[4]['exit_code']==0
assert result['status']=='success' and result['new_Hamiltonian_actions']==37 and result['last_length']==95
