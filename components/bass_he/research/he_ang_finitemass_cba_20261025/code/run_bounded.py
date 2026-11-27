"""Once-only new 12CPU/35wall increment; explicit root GO required."""
import argparse
import datetime
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from io_utils import atomic_json, identity

UNIT = Path(__file__).resolve().parents[1]
WORKSPACE = UNIT.parents[2]
EXEC = UNIT/'evidence/execution'
LEDGER = EXEC/'RESOURCE_LEDGER.json'
PLAN = [('01_tests', 'test_fm_cba.py', 2, 5), ('02_analysis', 'run_analysis.py', 6, 18),
        ('03_plot', 'plot_results.py', 3, 10)]


def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()


def cpu(kind):
    usage = resource.getrusage(kind)
    return usage.ru_utime+usage.ru_stime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', choices=[x[0] for x in PLAN])
    args = parser.parse_args()
    EXEC.mkdir(parents=True, exist_ok=True)
    # A preexisting lock is preserved and reported before entering this try.
    lock = EXEC/'RUN.lock'
    descriptor = os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'created_utc': stamp()})); stream.flush(); os.fsync(stream.fileno())
        manifest_path = UNIT/'evidence/preparation/PREPARATION_MANIFEST.json'
        manifest = json.loads(manifest_path.read_bytes().decode('utf-8'))
        go = json.loads((EXEC/'ROOT_GO.json').read_bytes().decode('utf-8'))
        if not (go.get('scientific_start_authorized') is True
                and go.get('preparation_manifest_sha256') == identity(manifest_path)['sha256']
                and go.get('R6_receipt') and go.get('R7_receipt') and go.get('B1_dual_provider_ACK')):
            raise RuntimeError('root GO with bound preparation/R6/R7/B1 dual ACK is required before START')
        current = {name: identity(UNIT/name) for name in manifest['frozen_inputs']}
        for name, expected in manifest['frozen_inputs'].items():
            if current[name] != expected: raise RuntimeError('frozen input changed: '+name)
        for name, expected in manifest['external_inputs'].items():
            if identity(WORKSPACE/name) != expected: raise RuntimeError('immutable parent/dependency changed: '+name)
        ledger = json.loads(LEDGER.read_bytes().decode('utf-8'))
        attempts = ledger['attempts']
        if any(a['status'] != 'PASS' for a in attempts):
            raise RuntimeError('failure/incomplete START retained; return to root; no automatic retry')
        index = len(attempts)
        if index >= len(PLAN) or PLAN[index][0] != args.run_id:
            raise RuntimeError('once-only planned order; repair needs separate root diagnosis and amendment')
        _, script, cap_cpu, cap_wall = PLAN[index]
        if ledger['new_science_cpu_s']+cap_cpu > 12 or ledger['new_science_wall_s']+cap_wall > 35:
            raise RuntimeError('new increment cap would be exceeded')
        if ledger['lineage_cpu_s']+cap_cpu > 20 or ledger['lineage_wall_s']+cap_wall > 60:
            raise RuntimeError('additional CBA lineage cap would be exceeded')
        wheel = WORKSPACE/'finitemass_ops/dependencies/mpmath-1.3.0-py3-none-any.whl'
        env = {**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
               'NUMEXPR_NUM_THREADS': '1', 'MPLBACKEND': 'Agg', 'PYTHONDONTWRITEBYTECODE': '1',
               'PYTHONPATH': str(wheel)+os.pathsep+os.environ.get('PYTHONPATH', ''),
               'MPLCONFIGDIR': str(WORKSPACE/'next5_ops_20261025/mplconfig')}
        Path(env['MPLCONFIGDIR']).mkdir(parents=True, exist_ok=True)
        attempt_id = f'{index+1:02d}_{args.run_id}'
        directory = EXEC/attempt_id; directory.mkdir()
        command = [sys.executable, '-B', 'code/'+script]
        started_wall, parent_cpu_before, child_cpu_before = time.monotonic(), cpu(resource.RUSAGE_SELF), cpu(resource.RUSAGE_CHILDREN)
        row = {'attempt_id': attempt_id, 'run_id': args.run_id, 'started_utc': stamp(), 'status': 'START',
               'command': command, 'caps': {'CPU_s': cap_cpu, 'wall_s': cap_wall, 'memory_bytes': 536870912, 'threads': 1},
               'preparation_manifest_sha256': identity(manifest_path)['sha256'], 'current_inputs': current,
               'external_inputs': manifest['external_inputs'], 'root_GO': go,
               'incomplete_START_cost': 'UNKNOWN_NOT_ZERO; blocks replay',
               'requested_model': 'gpt-6.1-sol', 'observed_runtime_model': 'NOT_OBSERVABLE'}
        attempts.append(row); ledger['state'] = 'ACTUAL_START'
        atomic_json(directory/'START.json', row); atomic_json(LEDGER, ledger)
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (cap_cpu, cap_cpu))
            resource.setrlimit(resource.RLIMIT_AS, (536870912, 536870912))
        timed_out, launch_error, returncode = False, None, None
        try:
            with (directory/'stdout.txt').open('wb') as out, (directory/'stderr.txt').open('wb') as err:
                child = subprocess.Popen(command, cwd=UNIT, env=env, stdout=out, stderr=err,
                                         start_new_session=True, preexec_fn=limits)
                try: returncode = child.wait(timeout=cap_wall)
                except subprocess.TimeoutExpired:
                    timed_out = True; os.killpg(child.pid, signal.SIGKILL); returncode = child.wait()
        except Exception as exc: launch_error = repr(exc)
        elapsed = time.monotonic()-started_wall
        parent_cpu, child_cpu = cpu(resource.RUSAGE_SELF)-parent_cpu_before, cpu(resource.RUSAGE_CHILDREN)-child_cpu_before
        total_cpu = parent_cpu+child_cpu
        overshoot = total_cpu > cap_cpu or elapsed > cap_wall
        row.update(finished_utc=stamp(), returncode=returncode, child_cpu_s=child_cpu, parent_cpu_s=parent_cpu,
                   cpu_s=total_cpu, wall_s=elapsed, timed_out=timed_out, launch_error=launch_error,
                   measured_cap_overshoot=overshoot,
                   status='PASS' if returncode == 0 and not timed_out and not launch_error and not overshoot else 'FAIL')
        row['outputs'] = {name: identity(directory/name) for name in ['stdout.txt', 'stderr.txt'] if (directory/name).exists()}
        ledger['new_science_cpu_s'] += total_cpu; ledger['new_science_wall_s'] += elapsed
        ledger['lineage_cpu_s'] += total_cpu; ledger['lineage_wall_s'] += elapsed
        ledger['state'] = 'ACTUAL_'+str(len(attempts))+'_CHILDREN_FINISHED_'+row['status']
        atomic_json(directory/'FINISH.json', row); atomic_json(LEDGER, ledger)
        print(json.dumps({key: row[key] for key in ['attempt_id', 'status', 'cpu_s', 'wall_s']}))
        return 0 if row['status'] == 'PASS' else 1
    finally:
        # Only this process's successfully created lock is removed. Historical
        # parent pre-START failures and unrelated existing locks are untouched.
        lock.unlink()


if __name__ == '__main__': raise SystemExit(main())
