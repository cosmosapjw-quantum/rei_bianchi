"""One create-only launch per declared endpoint phase; no HH integration.

Reuses the pinned, previously lifecycle-tested process host. A STARTED file is
an invocation claim, including failures: this script never retries a phase.
"""
from pathlib import Path
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
LADDER = HERE.parent
PINS = {
    'w1_parallel_20261002_v1/process_host/host.py': '1274f166132e0fed8af61b71db00f1f4bacae2e9fea1b8c97ba33599dd808c5e',
    'production_solver_20261001_v1/endpoint_tasks/planner.py': '53fe8cea32fb24efe9ef2682f480d63595db2bf32525ed57f46df391fe3eb4e6',
    'w3_design_20261002_v1/tail_bound/select_cutoff.py': '7a8a4d9fc10d79ba08d7c9eb015bd814559d9c970ec008404b7e45d1a055a759',
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value):
    with path.open('x') as f: json.dump(value, f, indent=2, sort_keys=True); f.write('\n')
def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec); sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj
def ref(path):
    return {'namespace':'continuation', 'path':str(path.relative_to(HERE)), 'sha256':sha(path)}

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('phase', choices=('selection','crosscheck')); args = cli.parse_args()
    for rel, pin in PINS.items():
        if sha(LADDER / rel) != pin: raise ValueError('source pin mismatch: '+rel)
    phase = args.phase.upper(); runtime = HERE / 'runtime'; runtime.mkdir(exist_ok=True)
    out = runtime / (phase+'_RESULT.json')
    if any(runtime.glob(phase+'_*')): raise ValueError('phase already claimed; no retry')
    host = module(LADDER/'w1_parallel_20261002_v1/process_host/host.py','_w3_host')
    authority = host.identity()
    python = str(Path(sys.executable).resolve())
    cap = 60 if phase == 'SELECTION' else 30
    if phase == 'SELECTION':
        command = [python,'-B',str(HERE/'tail_bound/select_cutoff.py'),'--execute-pinned-endpoint','--output',str(out)]
    else:
        selection = json.loads((runtime/'SELECTION_RESULT.json').read_bytes())
        receipt = json.loads((runtime/'SELECTION_RECEIPT.json').read_bytes())
        if not receipt['accepted'] or receipt['output'] != ref(runtime/'SELECTION_RESULT.json'):
            raise ValueError('accepted source-bound selection required')
        exponent = selection['selected_upper_exponent']
        if type(exponent) is not int or exponent not in (32,40,48,56,64): raise ValueError('unselected cutoff')
        p = module(LADDER/'production_solver_20261001_v1/endpoint_tasks/planner.py','_w3_planner')
        raw = (LADDER/'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz').read_bytes()
        record = p.adapter.decode_npz(raw, expected_archive_sha256='8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c', scope='FROZEN107_PINNED')
        plan = p.build_plan(record, {'l_t':'1/512','l_u':'1/512','T_t':str(1<<exponent),'T_u':str(1<<exponent)},precision_bits=128,panels=4,caps={'wall_seconds':30,'memory_bytes':512*1024**2},source_archive_bytes=raw)
        write(runtime/'CROSSCHECK_PLAN.json', plan)
        command = [python,'-B',str(HERE/'crosscheck_worker.py')]
    started = {'schema':'WU088_W3_PHASE_STARTED_V1','phase':phase,'command':command,'controller_sha256':sha(Path(__file__)),'worker_sha256':sha(Path(command[2])),'source_pins':PINS,'host_identity':authority,'wall_seconds':cap,'memory_mib':512,'cpu_seconds':cap,'creation_syscalls_denied':True,'utc_started':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    write(runtime/(phase+'_STARTED.json'),started)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    timed_out=False; child=None; launch_error=None; t0=time.monotonic_ns()
    with (runtime/(phase+'_STDOUT.txt')).open('xb') as so, (runtime/(phase+'_STDERR.txt')).open('xb') as se:
        try:
            child=host._launch(command,stdout=so,stderr=se,env=env,memory_mib=512,cpu_seconds=cap,nofork=True)
            try: child.wait(timeout=cap)
            except subprocess.TimeoutExpired: timed_out=True; child.kill(); child.wait()
        except BaseException as exc:
            launch_error=repr(exc)
            if child is not None and child.poll() is None: child.kill(); child.wait()
    elapsed=time.monotonic_ns()-t0
    result=json.loads(out.read_bytes()) if out.exists() else None
    accepted=bool(child and child.returncode==0 and not timed_out and launch_error is None and result)
    if accepted:
        if phase=='SELECTION':
            accepted=(result['status']=='FIRST_TESTED_CUTOFF_SELECTED' and result['term_count']==107 and result['budget_strictly_less_than_baseline_bound'] and result['native_integrations']==0)
        else:
            accepted=(result['status']=='CONDITIONAL_TAIL_BOUND' and Q(result['endpoint_radius'])<=Q(1,1<<21) and len(result['terms'])==107)
    record={'schema':'WU088_W3_BOUNDED_ENDPOINT_RECEIPT_V1','record_id':phase.lower(),'kind':'ACTUAL_ENDPOINT_SELECTION' if phase=='SELECTION' else 'ACTUAL_ENDPOINT_CROSSCHECK','primitive_index':0,'accepted':accepted,'status':result['status'] if result else 'NO_RESULT','actual_worker_observed':child is not None,'native_integration_invocations':0,'candidate_polynomial_evaluations':len(result['candidates']) if phase=='SELECTION' and result else 0,'output':ref(out) if result else None,'started':ref(runtime/(phase+'_STARTED.json')),'stdout':ref(runtime/(phase+'_STDOUT.txt')),'stderr':ref(runtime/(phase+'_STDERR.txt')),'returncode':child.returncode if child else None,'worker_pid':child.pid if child else None,'wait_completed':child is not None and child.poll() is not None,'timed_out':timed_out,'launch_error':launch_error,'elapsed_ns':elapsed,'wall_seconds':cap,'cpu_seconds':cap,'memory_mib':512,'host_identity':authority,'PDEATHSIG':'SIGKILL','creation_syscalls_denied':True,'NCP_or_MPI_execution':False,'scientific_admission':False,'production_admission':False}
    write(runtime/(phase+'_RECEIPT.json'),record)
    print(json.dumps(record))
    return 0 if accepted else 2

if __name__=='__main__': raise SystemExit(main())
