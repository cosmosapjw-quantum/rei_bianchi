"""PROPOSED_NOT_AUTHORIZED pressure runner: prepared only; do not execute yet.

This wrapper inherits the reviewed one-child CPU1s/wall5s pattern. Its exclusive
attempt marker preserves reproducibility and prevents accidental reruns; it is
not a security mechanism or an approval token. Future execution needs root's
separate authorization. The parent never imports pressure_interval or focused_check.
"""
import datetime
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
RAW = HERE / 'raw'
PROPOSAL = HERE / 'PROPOSED_EXECUTION.json'
CPU_LIMIT_S = 1
WALL_LIMIT_S = 5


def cpu_limit():
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT_S, CPU_LIMIT_S))


def main():
    proposal = json.loads(PROPOSAL.read_text(encoding='utf-8'))
    for filename in ('pressure_interval.py', 'focused_check.py'):
        expected = proposal['file_sha256'][filename]
        actual = hashlib.sha256((HERE / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f'Proposed input byte identity mismatch for {filename}: {actual}')
    command = [sys.executable, '-B', str(HERE / 'focused_check.py')]
    RAW.mkdir(exist_ok=True)
    # One attempt, including a failed launch. No retry after this marker exists.
    with (RAW / 'attempt.json').open('x', encoding='utf-8') as handle:
        json.dump({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'single_child_attempt': 1, 'command': command,
                   'cpu_limit_s': CPU_LIMIT_S, 'wall_timeout_s': WALL_LIMIT_S,
                   'file_sha256': proposal['file_sha256']}, handle, indent=2)
        handle.write('\n')
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
            'schema': 'REI_PRESSURE_SINGLE_CHILD_RECEIPT_V1',
            'command': command, 'scientific_child_attempts': 1,
            'cpu_rlimit_soft_s': CPU_LIMIT_S, 'cpu_rlimit_hard_s': CPU_LIMIT_S,
            'wall_timeout_s': WALL_LIMIT_S, 'wall_elapsed_s': wall_s,
            'child_user_cpu_s': after.ru_utime - before.ru_utime,
            'child_system_cpu_s': after.ru_stime - before.ru_stime,
            'child_total_cpu_s': (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime),
            'returncode': returncode, 'timed_out': timeout, 'launch_error': launch_error,
            'python_version': sys.version, 'python_executable': sys.executable,
            'executor': proposal['executor'],
            'proposal_sha256': hashlib.sha256(PROPOSAL.read_bytes()).hexdigest(),
            'proposal_preparation_status': proposal['status'],
            'file_sha256': proposal['file_sha256'],
            'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
            'stderr_sha256': hashlib.sha256(stderr).hexdigest(),
            'parent_io_review_remote_cas_cpu': 'SEPARATE_UNMEASURED_NOT_ZERO',
            'historical_whole_L0_cpu': 'UNKNOWN_NOT_ZERO',
            'allocation_transfer_from_current_L1': False,
            'automatic_retry': False,
            'scientific_admission': 'ROOT_DECISION_REQUIRED_NO_ADMISSION_BY_RUNNER',
        }
        (RAW / 'resource_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if returncode == 0 and not timeout and launch_error is None else 1


if __name__ == '__main__':
    sys.exit(main())
