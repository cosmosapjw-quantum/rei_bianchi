"""Single root-diagnosed combined repair; preserves original failure and costs."""
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
REPAIR_MANIFEST = UNIT/'evidence/preparation/REPAIR01_MANIFEST.json'


def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()


def cpu(kind):
    r = resource.getrusage(kind)
    return r.ru_utime+r.ru_stime


def main():
    contract = json.loads((UNIT/'REPAIR_CONTRACT_01.json').read_bytes().decode('utf-8'))
    manifest = json.loads(REPAIR_MANIFEST.read_bytes().decode('utf-8'))
    go = json.loads((EXEC/'ROOT_REPAIR_GO.json').read_bytes().decode('utf-8'))
    if not (go.get('scientific_start_authorized') is True
            and go.get('repair_manifest_sha256') == identity(REPAIR_MANIFEST)['sha256']
            and go.get('static_review_receipt') and go.get('B1R_dual_provider_ACK')):
        raise RuntimeError('root repair GO bound to manifest/static review/actual B1R dual ACK required')
    original_path = UNIT/'evidence/preparation/PREPARATION_MANIFEST.json'
    if identity(original_path)['sha256'] != contract['reuse']['original_preparation_manifest_sha256']:
        raise RuntimeError('original preparation manifest changed')
    original = json.loads(original_path.read_bytes().decode('utf-8'))
    for name, expected in original['frozen_inputs'].items():
        if identity(UNIT/name) != expected: raise RuntimeError('original frozen input changed: '+name)
    for name, expected in original['external_inputs'].items():
        if identity(WORKSPACE/name) != expected: raise RuntimeError('immutable external input changed: '+name)
    for name, expected in manifest['repair_inputs'].items():
        if identity(UNIT/name) != expected: raise RuntimeError('new repair input changed: '+name)
    prior = manifest['prior_failed_ledger']
    if identity(LEDGER) != prior['identity'] or identity(UNIT/prior['snapshot_path']) != prior['identity']:
        raise RuntimeError('prior failed ledger differs from frozen snapshot')
    ledger = json.loads(LEDGER.read_bytes().decode('utf-8'))
    if not (len(ledger['attempts']) == 2 and ledger['attempts'][0]['status'] == 'PASS'
            and ledger['attempts'][1]['status'] == 'FAIL' and ledger['attempts'][1]['returncode'] == -9):
        raise RuntimeError('repair only follows the exact initial PASS/FAIL sequence; no retries')
    reserve = ledger['new_targeted_repair_reserve']
    if reserve['remaining'] != 1 or reserve['used'] != 0:
        raise RuntimeError('exactly one unconsumed new-unit repair reserve is required')
    cfg = contract['resources']; cap_cpu, cap_wall = cfg['repair_child_CPU_cap_s'], cfg['repair_child_wall_cap_s']
    if ledger['new_science_cpu_s']+cap_cpu > cfg['new_unit_original_CPU_cap_s'] or ledger['new_science_wall_s']+cap_wall > cfg['new_unit_original_wall_cap_s']:
        raise RuntimeError('original new-unit cumulative cap would be exceeded')
    if ledger['lineage_cpu_s']+cap_cpu > cfg['lineage_CPU_ceiling_s'] or ledger['lineage_wall_s']+cap_wall > cfg['lineage_wall_ceiling_s']:
        raise RuntimeError('original lineage cumulative cap would be exceeded')
    if (EXEC/'RUN.lock').exists():
        raise RuntimeError('existing original-run lock preserved; return to root')
    lock = EXEC/'REPAIR01.lock'
    descriptor = os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'created_utc': stamp()})); stream.flush(); os.fsync(stream.fileno())
        directory = EXEC/'03_REPAIR01_COMBINED'; directory.mkdir()
        wheel = WORKSPACE/'finitemass_ops/dependencies/mpmath-1.3.0-py3-none-any.whl'
        env = {**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
               'NUMEXPR_NUM_THREADS': '1', 'MPLBACKEND': 'Agg', 'PYTHONDONTWRITEBYTECODE': '1',
               'PYTHONPATH': str(wheel)+os.pathsep+os.environ.get('PYTHONPATH', ''),
               'MPLCONFIGDIR': str(WORKSPACE/'next5_ops_20261025/mplconfig')}
        Path(env['MPLCONFIGDIR']).mkdir(parents=True, exist_ok=True)
        command = [sys.executable, '-B', 'code/resume_analysis_repair01.py']
        start_wall, before_parent, before_child = time.monotonic(), cpu(resource.RUSAGE_SELF), cpu(resource.RUSAGE_CHILDREN)
        row = {'attempt_id': '03_REPAIR01_COMBINED', 'run_id': contract['repair_id'], 'status': 'START',
            'started_utc': stamp(), 'command': command,
            'caps': {'CPU_s': cap_cpu, 'wall_s': cap_wall, 'memory_bytes': cfg['memory_bytes'], 'threads': 1},
            'repair_manifest_identity': identity(REPAIR_MANIFEST), 'root_repair_GO': go,
            'prior_failed_ledger': prior, 'reserve_consumed_at_START': 1,
            'completed_cases_reexecution_authorized': False, 'separate_original03_plot': False,
            'incomplete_START_cost': 'UNKNOWN_NOT_ZERO; no further retry',
            'requested_model': 'gpt-6.1-sol', 'observed_runtime_model': 'NOT_OBSERVABLE'}
        ledger['attempts'].append(row); reserve['remaining'] = 0; reserve['used'] = 1
        ledger['zero_scope'] = 'Initial zero applied only before START; actual attempt costs are in this ledger'
        ledger['state'] = 'ACTUAL_REPAIR01_START'
        atomic_json(directory/'START.json', row); atomic_json(LEDGER, ledger)
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (cap_cpu, cap_cpu))
            resource.setrlimit(resource.RLIMIT_AS, (cfg['memory_bytes'], cfg['memory_bytes']))
        timed_out, launch_error, returncode = False, None, None
        try:
            with (directory/'stdout.txt').open('wb') as out, (directory/'stderr.txt').open('wb') as err:
                child = subprocess.Popen(command, cwd=UNIT, env=env, stdout=out, stderr=err,
                                         start_new_session=True, preexec_fn=limits)
                try: returncode = child.wait(timeout=cap_wall)
                except subprocess.TimeoutExpired:
                    timed_out = True; os.killpg(child.pid, signal.SIGKILL); returncode = child.wait()
        except Exception as exc: launch_error = repr(exc)
        wall = time.monotonic()-start_wall
        parent_cpu, child_cpu = cpu(resource.RUSAGE_SELF)-before_parent, cpu(resource.RUSAGE_CHILDREN)-before_child
        total_cpu = parent_cpu+child_cpu
        overshoot = total_cpu > cap_cpu or wall > cap_wall
        ledger['new_science_cpu_s'] += total_cpu; ledger['new_science_wall_s'] += wall
        ledger['lineage_cpu_s'] += total_cpu; ledger['lineage_wall_s'] += wall
        cumulative_overshoot = (ledger['new_science_cpu_s'] > cfg['new_unit_original_CPU_cap_s']
            or ledger['new_science_wall_s'] > cfg['new_unit_original_wall_cap_s']
            or ledger['lineage_cpu_s'] > cfg['lineage_CPU_ceiling_s']
            or ledger['lineage_wall_s'] > cfg['lineage_wall_ceiling_s'])
        row.update(finished_utc=stamp(), returncode=returncode, parent_cpu_s=parent_cpu, child_cpu_s=child_cpu,
            cpu_s=total_cpu, wall_s=wall, timed_out=timed_out, launch_error=launch_error,
            measured_cap_overshoot=overshoot, cumulative_cap_overshoot=cumulative_overshoot,
            status='PASS' if returncode == 0 and not timed_out and not launch_error and not overshoot and not cumulative_overshoot else 'FAIL')
        row['outputs'] = {name: identity(directory/name) for name in ['stdout.txt', 'stderr.txt'] if (directory/name).exists()}
        ledger['state'] = 'ACTUAL_REPAIR01_FINISHED_'+row['status']
        ledger['prior_FAIL_preserved'] = True
        ledger['repair_resolution'] = {'original_attempt': '02_02_analysis', 'original_status': 'FAIL',
            'repair_attempt': row['attempt_id'], 'repair_status': row['status'],
            'further_science_authorization': 'NONE; reserve exhausted, stop'}
        atomic_json(directory/'FINISH.json', row); atomic_json(LEDGER, ledger)
        print(json.dumps({key: row[key] for key in ['attempt_id', 'status', 'cpu_s', 'wall_s']}))
        return 0 if row['status'] == 'PASS' else 1
    finally:
        lock.unlink()


if __name__ == '__main__': raise SystemExit(main())
