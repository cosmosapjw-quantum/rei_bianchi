#!/usr/bin/env python3
"""Run one bounded E13C4 work unit and preserve actual exit/stdout/stderr."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def dump(path, obj):
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w') as f:
        json.dump(obj, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', type=Path, required=True)
    ap.add_argument('--timeout', type=int, default=180)
    ap.add_argument('command', nargs=argparse.REMAINDER)
    a = ap.parse_args()
    command = a.command[1:] if a.command and a.command[0] == '--' else a.command
    if not command:
        raise ValueError('empty command')
    a.run_dir.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
              'timeout_seconds': a.timeout, 'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'status': 'RUNNING', 'actual_exit': None}
    dump(a.run_dir / 'RUN.json', record)
    with (a.run_dir / 'stdout.txt').open('w') as stdout, (a.run_dir / 'stderr.txt').open('w') as stderr:
        try:
            proc = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=a.timeout, check=False)
            record.update(actual_exit=proc.returncode, status='COMPLETE' if proc.returncode == 0 else 'FAILED')
        except subprocess.TimeoutExpired:
            record.update(status='TIMEOUT', actual_exit=None, failure_class='RUNTIME_RESOURCE')
        finally:
            stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
    record.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.perf_counter() - start)
    record['stdout_sha256'] = hashlib.sha256((a.run_dir / 'stdout.txt').read_bytes()).hexdigest()
    record['stderr_sha256'] = hashlib.sha256((a.run_dir / 'stderr.txt').read_bytes()).hexdigest()
    dump(a.run_dir / 'RUN.json', record)
    print(json.dumps(record))
    return 0 if record['status'] == 'COMPLETE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
