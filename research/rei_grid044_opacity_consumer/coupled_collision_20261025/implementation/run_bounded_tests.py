"""One-worker, cumulative bounded test runner; no IVP or external writes.

The controller must bind RUN_AUTHORIZATION.json after freezing the contract.
Every executed attempt saves the exact candidate sources and input bytes.
The child process is reaped with os.wait4, retaining that child's raw rusage.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    auth_path = HERE / 'RUN_AUTHORIZATION.json'
    auth = json.loads(auth_path.read_text())
    if auth.get('authorized') is not True:
        raise SystemExit('CURRENT_ROOT_RUN_AUTHORIZATION_REQUIRED')
    ledger_path = HERE / 'TEST_BUDGET_LEDGER.json'
    records = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    carry = auth['carried_resources']
    carried_records = []
    for relative_ledger in carry['ledger_relative_paths']:
        carried_records.extend(json.loads((UNIT / relative_ledger).read_text()))
    carried_cpu = math.fsum(r['whole_child_cpu_s'] for r in carried_records)
    carried_wall = math.fsum(r['wall_s'] for r in carried_records)
    if carried_cpu != carry['CPU_s'] or carried_wall != carry['wall_s']:
        raise SystemExit('CARRIED_RESOURCE_RECEIPT_MISMATCH')
    used_cpu = carried_cpu + math.fsum(r['whole_child_cpu_s'] for r in records)
    used_wall = carried_wall + math.fsum(r['wall_s'] for r in records)
    remaining_cpu, remaining_wall = 10.0 - used_cpu, 20.0 - used_wall
    attempt_cpu = min(remaining_cpu, auth.get('attempt_limits', {}).get('CPU_s', remaining_cpu))
    attempt_wall = min(remaining_wall, auth.get('attempt_limits', {}).get('wall_s', remaining_wall))
    attempt = len(records) + 1
    if remaining_cpu < 1 or remaining_wall < 5:
        raise SystemExit('CUMULATIVE_TEST_BUDGET_EXHAUSTED')
    if attempt not in auth['authorized_attempts']:
        raise SystemExit('ATTEMPT_NOT_AUTHORIZED')
    mode = 'targeted' if '--targeted' in sys.argv else 'ordinary'
    suite = auth['suites'][mode]
    if auth['attempt_modes'].get(str(attempt)) != mode:
        raise SystemExit('ATTEMPT_MODE_NOT_AUTHORIZED')
    bindings = auth['sha256_bindings']
    for relative, expected in bindings.items():
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise SystemExit('NONPORTABLE_CURRENT_BINDING: '+relative)
        path = UNIT / relative
        if sha(path) != expected:
            raise SystemExit('INPUT_BYTE_IDENTITY_MISMATCH: ' + relative)
    attempt_dir = HERE / ('attempt%02d' % attempt)
    attempt_dir.mkdir(exist_ok=False)
    snapshot_locations = {}
    for index, relative in enumerate(bindings):
        path = UNIT / relative
        relative_path = Path(relative)
        snapshot_relative = (relative if not relative_path.is_absolute() and '..' not in relative_path.parts
                             else 'external_inputs/%02d_%s' % (index, path.name))
        destination = attempt_dir / 'snapshot' / snapshot_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        snapshot_locations[relative] = str(destination.relative_to(attempt_dir))
    (attempt_dir / 'RUN_AUTHORIZATION.json').write_bytes(auth_path.read_bytes())
    env = os.environ.copy()
    env['COUPLED_COLLISION_ATTEMPT'] = str(attempt)
    env['COUPLED_COLLISION_OUTPUT_DIR'] = str(attempt_dir)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    for key in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']:
        env[key] = '1'
    hard_cpu = 1
    soft_timer = auth['attempt_limits']['ITIMER_PROF_s']
    if attempt_cpu != 1 or attempt_wall != 5 or soft_timer != .8:
        raise SystemExit('FROZEN_SINGLE_ATTEMPT_LIMITS_REQUIRED')

    def caps():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (hard_cpu, hard_cpu))
        resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
        signal.signal(signal.SIGPROF, signal.SIG_DFL)
        signal.setitimer(signal.ITIMER_PROF, soft_timer)

    command = [sys.executable, str(HERE / suite)]
    start = time.monotonic()
    timed_out = False
    with (attempt_dir / 'stdout.log').open('wb') as out, (attempt_dir / 'stderr.log').open('wb') as err:
        child = subprocess.Popen(command, env=env, stdout=out, stderr=err,
                                 preexec_fn=caps, cwd=HERE)
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - start >= attempt_wall:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                pid, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(.005)
        exit_code = os.waitstatus_to_exitcode(status)
        child.returncode = exit_code
    wall = time.monotonic() - start
    raw_usage = {key: getattr(usage, key) for key in dir(usage) if key.startswith('ru_')}
    outputs = {str(p.relative_to(attempt_dir)): sha(p)
               for p in sorted(attempt_dir.rglob('*')) if p.is_file()}
    record = {'attempt': attempt, 'mode': mode, 'command': command,
              'exit_code': exit_code, 'timed_out': timed_out, 'wall_s': wall,
              'whole_child_cpu_s': usage.ru_utime + usage.ru_stime,
              'wait4_rusage': raw_usage, 'prior_CPU_s': used_cpu,
              'prior_wall_s': used_wall, 'carried_CPU_s': carried_cpu,
              'carried_wall_s': carried_wall, 'hard_RLIMIT_CPU_s': hard_cpu,
              'CPU_soft_timer_s': soft_timer, 'address_space_bytes': 1024 ** 3,
              'attempt_CPU_cap_s': attempt_cpu, 'attempt_wall_cap_s': attempt_wall,
              'authorization_sha256': sha(auth_path), 'input_sha256': bindings,
              'snapshot_locations': snapshot_locations,
              'post_run_input_sha256': {r: sha(UNIT / r) for r in bindings},
              'output_sha256': outputs, 'workers': 1, 'BLAS_threads': 1,
              'new_IVPs': 0, 'old_histories_rerun': 0, 'Git_writes': 0,
              'publication_actions': 0,
              'requested_execution_model': 'gpt-6.1-sol',
              'requested_reasoning_effort': 'high',
              'actual_runtime_model_identity': 'UNEXPOSED'}
    write_json(attempt_dir / 'RECEIPT.json', record)
    records.append(record)
    write_json(ledger_path, records)
    print(json.dumps(record, indent=2))
    return 0 if exit_code == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
