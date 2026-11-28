"""Root execution supervisor: consumes one recorded allowance before launching.

This module performs no scientific computation. It retains subprocess exit,
stdout/stderr, operating-system child CPU, and wall duration, including output
serialization. It never retries a failed run or overwrites an existing result.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time

LEAF = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=('primary', 'reference'))
    args = parser.parse_args()
    kind = args.kind
    ledger_path = LEAF / 'EXECUTION_LEDGER.json'
    ledger = json.loads(ledger_path.read_text())
    output = LEAF / ('raw/' + kind.upper() + '_RESULTS.json')
    process_output = LEAF / ('raw/' + kind.upper() + '_PROCESS.json')
    if ledger['remaining'][kind] != 1 or output.exists() or process_output.exists():
        parser.error('Allowance consumed or original output exists; replay refused')
    frozen = json.loads((LEAF / 'verification/PREEXECUTION_FREEZE.json').read_text())
    for record in frozen['files']:
        if digest(LEAF / record['path']) != record['sha256']:
            parser.error('Frozen input/code changed: ' + record['path'])
    runner = LEAF / ('verification/run_primary.py' if kind == 'primary'
                     else 'verification/reference_r7.py')
    input_path = LEAF / ('verification/' + kind.upper() + '_INPUT.json')
    command = [sys.executable, str(runner), '--input', str(input_path),
               '--output', str(output)]
    if kind == 'reference':
        primary = LEAF / 'raw/PRIMARY_RESULTS.json'
        if not primary.is_file() or json.loads(primary.read_text())['status'] != 'PASS':
            parser.error('Successful retained primary result required')
        command += ['--primary', str(primary), '--primary-sha256', digest(primary)]
    entry = {'id': 'R7_' + kind.upper(), 'status': 'RUNNING',
             'started_utc': now(), 'command': command, 'CPU_limit_s': 60,
             'wall_emergency_limit_s': 90, 'input_sha256': digest(input_path),
             'runner_sha256': digest(runner), 'old_science_replay': 0}
    ledger['remaining'][kind] = 0
    ledger['science_runs'].append(entry)
    save(ledger_path, ledger)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    wall_start = time.monotonic()
    try:
        process = subprocess.run(command, cwd=LEAF, capture_output=True, text=True,
                                 timeout=90, check=False)
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as error:
        code = 124
        stdout = error.stdout or ''
        stderr = error.stderr or ''
        if isinstance(stdout, bytes):
            stdout = stdout.decode('utf-8', errors='replace')
        if isinstance(stderr, bytes):
            stderr = stderr.decode('utf-8', errors='replace')
        stderr += '\nEmergency wall limit reached; no retry.'
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    record = {'schema': 'WU_R7_ACTUAL_SUBPROCESS_V1', 'kind': kind,
              'finished_utc': now(), 'command': command, 'exit_code': code,
              'stdout': stdout, 'stderr': stderr, 'OS_child_CPU_seconds': cpu,
              'wall_seconds': time.monotonic() - wall_start,
              'CPU_includes_imports_and_serialization': True,
              'supervisor_sha256': digest(Path(__file__)),
              'output_exists': output.exists(),
              'result_sha256': digest(output) if output.exists() else None,
              'science_runs': 1, 'old_science_replay': 0}
    save(process_output, record)
    entry.update(status='COMPLETED_PASS' if code == 0 else 'FAILED_RETAINED',
                 finished_utc=record['finished_utc'], exit_code=code,
                 CPU_seconds=cpu, wall_seconds=record['wall_seconds'],
                 result=str(output.relative_to(LEAF)),
                 result_sha256=record['result_sha256'],
                 process_record=str(process_output.relative_to(LEAF)))
    save(ledger_path, ledger)
    print(json.dumps({k: v for k, v in record.items()
                      if k not in ('command', 'stdout', 'stderr')}, sort_keys=True))
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
