"""One explicitly authorized diagnostic, linked to the immutable failed ledger."""
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
from run_bounded import atomic_json, file_identity, now, usage_cpu

UNIT = Path(__file__).resolve().parents[1]
OUT = UNIT/'evidence'/'execution'
OLD = OUT/'bounded_ledger.json'
RECEIPT = OUT/'03_diagnostic.receipt.json'


def main():
    baseline = json.loads(OLD.read_text())
    old_cpu, old_wall = baseline['cumulative_cpu_s'], baseline['cumulative_wall_s']
    if len(baseline['attempts']) != 2 or baseline['attempts'][1]['kind'] != 'catalogue' or baseline['attempts'][1]['status'] != 'FAIL':
        raise SystemExit('REFUSED: legacy ledger does not match approved failed intake')
    cpu_limit, wall_limit = min(8, math.floor(20-old_cpu)), min(20, 60-old_wall)
    if cpu_limit < 1 or wall_limit <= 0:
        raise SystemExit('REFUSED: same-unit cumulative budget exhausted')
    try:
        descriptor = os.open(RECEIPT, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SystemExit('REFUSED: diagnostic count1 already consumed/reserved')
    os.close(descriptor)
    stdout, stderr = OUT/'03_diagnostic.stdout.txt', OUT/'03_diagnostic.stderr.txt'
    command = ['python', '-B', 'code/diagnose_input_format.py']
    item = {'unit_id': baseline['unit_id'], 'status': 'START', 'kind': 'input_format_diagnostic',
            'diagnostic_count': 1, 'diagnostic_cap': 1, 'catalogue_count_unchanged': 1,
            'authorization': 'Explicit root/Astra bounded prefix diagnostic after failed catalogue; no retry or cap change',
            'started_utc': now(), 'command': command, 'cwd': str(UNIT),
            'legacy_ledger': str(OLD.relative_to(UNIT)), 'legacy_ledger_identity': file_identity(OLD),
            'previous_cumulative_cpu_s': old_cpu, 'previous_cumulative_wall_s': old_wall,
            'caps': {'cpu_s': cpu_limit, 'wall_s': wall_limit, 'address_space_MiB': 256, 'decoded_bytes': 65536},
            'source_identities': {str(path.relative_to(UNIT)): file_identity(path) for path in
                [UNIT/'code'/'diagnose_input_format.py', UNIT/'code'/'run_diagnostic_once.py', UNIT/'code'/'run_bounded.py']},
            'interrupted_START_accounting': 'UNKNOWN_NOT_ZERO; blocks repetition'}
    atomic_json(RECEIPT, item)
    atomic_json(OUT/'03_diagnostic.START.json', item)
    print('START diagnostic count1; legacy accounting preserved', flush=True)

    def caps():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
        resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))

    before, started = usage_cpu(), time.monotonic()
    process, returncode, failure = None, None, None
    try:
        with open(stdout, 'wb') as out, open(stderr, 'wb') as err:
            try:
                process = subprocess.Popen(command, cwd=UNIT, stdout=out, stderr=err, preexec_fn=caps, start_new_session=True)
                try:
                    returncode = process.wait(timeout=wall_limit)
                except subprocess.TimeoutExpired:
                    failure = 'WALL_LIMIT'
                    os.killpg(process.pid, signal.SIGKILL)
                    returncode = process.wait()
            finally:
                out.flush(); err.flush(); os.fsync(out.fileno()); os.fsync(err.fileno())
        if returncode != 0:
            failure = failure or 'CHILD_NONZERO_EXIT'
        else:
            result = json.loads(stdout.read_text())
            if result['decoded_bytes_read'] > 65536 or result['sql_executed'] or result['catalogue_completed']:
                raise ValueError('diagnostic scope exceeded')
    except Exception as error:
        failure = 'ENVIRONMENT_OR_VALIDATION_FAILURE'
        item['exception'] = repr(error)
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            returncode = process.wait()
    cpu, wall = usage_cpu()-before, time.monotonic()-started
    item.update({'status': 'FAIL' if failure else 'FINISH', 'failure_reason': failure, 'returncode': returncode,
                 'finished_utc': now(), 'cpu_s': cpu, 'wall_s': wall,
                 'cumulative_cpu_s': old_cpu+cpu, 'cumulative_wall_s': old_wall+wall,
                 'stdout_identity': file_identity(stdout), 'stderr_identity': file_identity(stderr),
                 'stdout': str(stdout.relative_to(UNIT)), 'stderr': str(stderr.relative_to(UNIT))})
    if old_cpu+cpu > 20 or old_wall+wall > 60:
        item['status'], item['failure_reason'] = 'FAIL', 'CUMULATIVE_BUDGET_EXCEEDED'
    atomic_json(RECEIPT, item)
    atomic_json(OUT/('03_diagnostic.'+item['status']+'.json'), item)
    print(json.dumps(item, indent=2, sort_keys=True))
    return 0 if item['status'] == 'FINISH' else 1


if __name__ == '__main__':
    sys.exit(main())
