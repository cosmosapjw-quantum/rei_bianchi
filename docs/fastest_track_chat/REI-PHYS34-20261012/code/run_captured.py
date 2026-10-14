#!/usr/bin/env python3
"""Capture the single authorized PHYS34 child process for a named ledger role.

No scientific module is imported here. stdout/stderr and wrapper markers are
created exclusively; a failed or timed-out attempt is never overwritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', choices=('first', 'replay'), required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--ledger', required=True)
    parser.add_argument('--capture-dir', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    frozen_path = root/'evidence/PREEXECUTION_FREEZE.json'
    frozen = json.loads(frozen_path.read_text())
    for relative, expected in frozen['sha256'].items():
        if sha(root/relative) != expected:
            raise RuntimeError('PREEXECUTION_IDENTITY_MISMATCH: '+relative)
    ledger = Path(args.ledger).resolve()
    ledger.mkdir(parents=True, exist_ok=True)
    if args.role == 'replay':
        prior = ledger/'first.finished.json'
        if not prior.exists() or json.loads(prior.read_text())['status'] != 'PASS_SCOPED':
            raise RuntimeError('Replay requires completed passing first receipt')
    output = Path(args.output).resolve()
    if output.exists():
        raise FileExistsError('Refuse to replace scientific output: '+str(output))
    capture = Path(args.capture_dir).resolve()
    capture.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, '-B', str(root/'code/certify_lower_branch.py'),
               '--role', args.role, '--output', str(output), '--ledger', str(ledger)]
    start = datetime.now(timezone.utc).isoformat()
    marker = ledger/(args.role+'.wrapper.started.json')
    with marker.open('x') as f:
        json.dump({'role': args.role, 'started_utc': start, 'command': command,
                   'preexecution_freeze_sha256': sha(frozen_path)}, f, indent=2)
        f.write('\n')
    stdout_path = capture/(args.role+'.stdout.txt')
    stderr_path = capture/(args.role+'.stderr.txt')
    timed_out = False
    wall0 = time.monotonic()
    with stdout_path.open('xb') as out, stderr_path.open('xb') as err:
        child = subprocess.Popen(command, cwd=str(root), stdout=out, stderr=err,
                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        try:
            returncode = child.wait(timeout=45)
        except subprocess.TimeoutExpired:
            timed_out = True
            child.kill()
            returncode = child.wait()
    receipt = {
        'task': 'REI-PHYS34-20261012', 'role': args.role,
        'record_type': 'ACTUAL_PARENT_OBSERVED_CHILD_PROCESS_RECEIPT',
        'command': command, 'source_root': str(root), 'ledger': str(ledger),
        'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'observed_returncode': returncode, 'timed_out': timed_out,
        'timeout_seconds': 45, 'wall_seconds': time.monotonic()-wall0,
        'stdout': {'path': str(stdout_path), 'bytes': stdout_path.stat().st_size,
                   'sha256': sha(stdout_path)},
        'stderr': {'path': str(stderr_path), 'bytes': stderr_path.stat().st_size,
                   'sha256': sha(stderr_path)},
        'scientific_output': {'path': str(output), 'exists': output.exists(),
                              'sha256': sha(output) if output.exists() else None},
        'preexecution_freeze_sha256': sha(frozen_path),
    }
    receipt_path = capture/(args.role+'.process.json')
    with receipt_path.open('x') as f:
        json.dump(receipt, f, indent=2)
        f.write('\n')
    print(json.dumps(receipt, indent=2), flush=True)
    return 0 if returncode == 0 and not timed_out else 1


if __name__ == '__main__':
    raise SystemExit(main())
