"""Single-use parent runner for the authorized CPU1s/wall5s scientific child."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
RAW = HERE / 'raw'
PREFLIGHT = HERE / 'preflight.json'
CPU_LIMIT_S = 1
WALL_LIMIT_S = 5


def cpu_limit():
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT_S, CPU_LIMIT_S))


def main():
    preflight = json.loads(PREFLIGHT.read_text())
    for filename, expected in preflight['file_sha256'].items():
        actual = hashlib.sha256((HERE / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f'Preflight byte identity mismatch for {filename}: {actual}')
    RAW.mkdir(exist_ok=True)
    # Exclusive marker records the only attempt. A failed attempt is never retried.
    with (RAW / 'attempt.json').open('x') as handle:
        json.dump({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'single_child_attempt': 1, 'cpu_limit_s': CPU_LIMIT_S,
                   'wall_timeout_s': WALL_LIMIT_S}, handle, indent=2)
        handle.write('\n')
    command = [sys.executable, '-B', str(HERE / 'focused_fixture.py')]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    stdout = b''
    stderr = b''
    process = None
    timeout = False
    launch_error = None
    returncode = None
    try:
        process = subprocess.Popen(command, cwd=HERE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, preexec_fn=cpu_limit)
        try:
            remaining_wall_s = max(0.0, WALL_LIMIT_S - (time.monotonic() - start))
            stdout, stderr = process.communicate(timeout=remaining_wall_s)
        except subprocess.TimeoutExpired:
            timeout = True
            process.kill()
            stdout, stderr = process.communicate()
        returncode = process.returncode
    except BaseException:
        launch_error = traceback.format_exc()
        if process is not None and process.poll() is None:
            process.kill()
            stdout, stderr = process.communicate()
            returncode = process.returncode
    finally:
        wall_s = time.monotonic() - start
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        (RAW / 'stdout.jsonl').write_bytes(stdout)
        (RAW / 'stderr.txt').write_bytes(stderr)
        receipt = {
            'schema': 'REI_L0_SRC01_SINGLE_CHILD_RECEIPT_V1',
            'command': command, 'scientific_child_attempts': 1,
            'cpu_rlimit_soft_s': CPU_LIMIT_S, 'cpu_rlimit_hard_s': CPU_LIMIT_S,
            'wall_timeout_s': WALL_LIMIT_S, 'wall_elapsed_s': wall_s,
            'child_user_cpu_s': after.ru_utime - before.ru_utime,
            'child_system_cpu_s': after.ru_stime - before.ru_stime,
            'child_total_cpu_s': (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime),
            'returncode': returncode, 'timed_out': timeout, 'launch_error': launch_error,
            'python_version': sys.version, 'python_executable': sys.executable,
            'executor': preflight['executor'],
            'preflight_sha256': hashlib.sha256(PREFLIGHT.read_bytes()).hexdigest(),
            'file_sha256': preflight['file_sha256'],
            'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
            'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
            'parent_io_review_remote_cas_cpu': 'SEPARATE_UNMEASURED_NOT_ZERO',
            'historical_whole_L0_cpu': 'UNKNOWN_NOT_ZERO',
            'automatic_retry': False,
        }
        (RAW / 'resource_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if returncode == 0 and not timeout and launch_error is None else 1


if __name__ == '__main__':
    sys.exit(main())
