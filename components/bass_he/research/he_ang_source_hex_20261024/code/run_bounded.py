"""One-shot owner-authorized HE-ANG-SOURCE-HEX-INTAKE execution ledger.

Existing ledger => refuse replay. Preserve interrupted START as unknown, never zero.
Only the three approved children below may run. No automatic retry is implemented.
"""
from datetime import datetime, timezone
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

UNIT = Path(__file__).resolve().parents[1]
OUT = UNIT / 'evidence' / 'execution'
LEDGER = OUT / 'bounded_ledger.json'
LIMITS = {'cpu_s': 20, 'wall_s': 60, 'per_child_cpu_s': 8,
          'per_child_wall_s': 20, 'address_space_MiB': 256,
          'kind_caps': {'algebra': 3, 'catalogue': 1, 'plot': 2}}


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    with open(temporary, 'w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def file_identity(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            digest.update(block)
    return {'sha256': digest.hexdigest(), 'bytes': path.stat().st_size}


def freeze():
    files = sorted(list((UNIT/'code').glob('*.py')) + list((UNIT/'tests').glob('*.py')) + [UNIT/'code'/'README.md', UNIT/'CONTRACT.json'])
    manifest = {str(p.relative_to(UNIT)): file_identity(p) for p in files}
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'manifest_sha256': digest, 'files': manifest}


def usage_cpu():
    used = resource.getrusage(resource.RUSAGE_CHILDREN)
    return used.ru_utime + used.ru_stime


def catalogue_validation(stdout):
    result = json.loads(stdout.read_text())
    if result['status'] not in ('SOURCE_INPUT_PENDING', 'RAW_H1_IONF_PRESENT_ABI_UNCONFIRMED'):
        raise ValueError('unexpected catalogue availability status')
    if result['sql_executed'] or result['physical_provider_values_inferred']:
        raise ValueError('catalogue crossed the approved raw-intake boundary')
    return {'availability_status': result['status'], 'ionf_rows': result['ionf_rows']}


def plot_validation(_stdout):
    path = UNIT/'figures'/'synthetic_tail.png'
    identity = file_identity(path)
    if not identity['bytes']:
        raise ValueError('plot output is empty')
    return {'plot': str(path.relative_to(UNIT)), **identity}


def run_child(ledger, kind, command, extra_env=None, validation=None):
    used_cpu = sum(item.get('cpu_s', 0) for item in ledger['attempts'])
    used_wall = sum(item.get('wall_s', 0) for item in ledger['attempts'])
    if any(item['status'] != 'FINISH' for item in ledger['attempts']):
        raise RuntimeError('prior failed/interrupted child; replay is prohibited')
    if sum(item['kind'] == kind for item in ledger['attempts']) >= LIMITS['kind_caps'][kind]:
        raise RuntimeError('kind invocation cap reached')
    cpu_limit = min(8, math.floor(LIMITS['cpu_s']-used_cpu))
    wall_limit = min(20, LIMITS['wall_s']-used_wall)
    if cpu_limit < 1 or wall_limit <= 0:
        raise RuntimeError('cumulative budget exhausted')
    index = len(ledger['attempts'])+1
    stem = f'{index:02d}_{kind}'
    stdout, stderr = OUT/(stem+'.stdout.txt'), OUT/(stem+'.stderr.txt')
    item = {'index': index, 'kind': kind, 'status': 'START', 'started_utc': now(),
            'command': command, 'cwd': str(UNIT), 'environment_overrides': extra_env or {},
            'caps': {'cpu_s': cpu_limit, 'wall_s': wall_limit, 'address_space_MiB': 256},
            'stdout': str(stdout.relative_to(UNIT)), 'stderr': str(stderr.relative_to(UNIT)),
            'source_manifest_sha256': ledger['freeze']['manifest_sha256'],
            'interrupted_START_accounting': 'UNKNOWN_NOT_ZERO until a final receipt exists'}
    ledger['attempts'].append(item)
    atomic_json(LEDGER, ledger)
    atomic_json(OUT/(stem+'.START.json'), item)
    print(f'START {index} {kind}: {command}', flush=True)

    def child_caps():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
        resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))

    environment = os.environ.copy()
    environment.update(extra_env or {})
    before_cpu, started = usage_cpu(), time.monotonic()
    process, failure, returncode = None, None, None
    try:
        with open(stdout, 'wb') as out, open(stderr, 'wb') as err:
            try:
                process = subprocess.Popen(command, cwd=UNIT, env=environment, stdout=out, stderr=err,
                                           preexec_fn=child_caps, start_new_session=True)
                try:
                    returncode = process.wait(timeout=wall_limit)
                except subprocess.TimeoutExpired:
                    failure = 'WALL_LIMIT'
                    os.killpg(process.pid, signal.SIGKILL)
                    returncode = process.wait()
            finally:
                out.flush(); err.flush()
                os.fsync(out.fileno()); os.fsync(err.fileno())
        if returncode != 0:
            failure = failure or 'CHILD_NONZERO_EXIT'
        elif validation is not None:
            item['validation'] = validation(stdout)
    except Exception as error:
        failure = 'ENVIRONMENT_OR_VALIDATION_FAILURE'
        item['exception'] = repr(error)
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            returncode = process.wait()
    item.update({'status': 'FAIL' if failure else 'FINISH', 'failure_reason': failure,
                 'finished_utc': now(), 'returncode': returncode,
                 'cpu_s': usage_cpu()-before_cpu, 'wall_s': time.monotonic()-started})
    item['stdout_identity'] = file_identity(stdout)
    item['stderr_identity'] = file_identity(stderr)
    ledger['cumulative_cpu_s'] = sum(entry.get('cpu_s', 0) for entry in ledger['attempts'])
    ledger['cumulative_wall_s'] = sum(entry.get('wall_s', 0) for entry in ledger['attempts'])
    if ledger['cumulative_cpu_s'] > 20 or ledger['cumulative_wall_s'] > 60:
        item['status'], item['failure_reason'] = 'FAIL', 'CUMULATIVE_BUDGET_EXCEEDED'
    atomic_json(OUT/(stem+'.'+item['status']+'.json'), item)
    atomic_json(LEDGER, ledger)
    print(f"{item['status']} {index} {kind}: rc={returncode}, cpu={item['cpu_s']:.6f}s, wall={item['wall_s']:.6f}s", flush=True)
    return item['status'] == 'FINISH'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Exclusive creation is a no-replay guard even if another runner starts now.
    try:
        descriptor = os.open(LEDGER, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SystemExit('REFUSED: existing execution ledger; no automatic replay')
    os.close(descriptor)
    ledger = {'unit_id': 'HE-ANG-SOURCE-HEX-INTAKE', 'created_utc': now(),
              'limits': LIMITS, 'freeze': freeze(), 'attempts': [],
              'cumulative_cpu_s': 0, 'cumulative_wall_s': 0,
              'accounting': 'Measured direct child RUSAGE_CHILDREN CPU deltas; sequential wall intervals include child launch/wait/validation. Failed attempts included. Interrupted START stays unknown and blocks replay.'}
    atomic_json(LEDGER, ledger)
    atomic_json(OUT/'source_freeze.json', ledger['freeze'])
    if not run_child(ledger, 'algebra', ['python', '-B', 'tests/test_hex_intake.py']):
        return 1
    if not run_child(ledger, 'catalogue', ['python', '-B', 'code/hex_intake.py', '/workspace/scratch/47d8070ffff8/source_intake/Hex-170210.sql.xz'], validation=catalogue_validation):
        return 1
    if not run_child(ledger, 'plot', ['python', '-B', 'code/plot_synthetic_tail.py', 'figures/synthetic_tail.png'],
                     {'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MPLCONFIGDIR': '/tmp/he_hex_mpl'}, plot_validation):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
