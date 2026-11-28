#!/usr/bin/env python3
"""Preserve immutable owner source, raw process output, and actual exit per attempt."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def atomic_bytes(path, payload):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('wb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def identity(path):
    payload = path.read_bytes()
    return {'path': str(path.resolve()), 'bytes': len(payload),
            'sha256': hashlib.sha256(payload).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--script', required=True, type=Path)
    parser.add_argument('--interval', required=True, type=Path)
    args, extra = parser.parse_known_args()
    home = Path(__file__).resolve().parent
    folder = home / args.attempt
    folder.mkdir(exist_ok=False)
    owner_bytes = args.interval.read_bytes()
    owner_snapshot = folder / 'owner_directed_interval_as_run.py'
    atomic_bytes(owner_snapshot, owner_bytes)
    command = [sys.executable, str(args.script.resolve()), '--interval',
               str(owner_snapshot), '--output', str(folder / 'RESULTS.json'), *extra]
    sources = [identity(Path(__file__)), identity(args.script), identity(owner_snapshot)]
    rational = home / 'rational_reference.py'
    if rational.is_file():
        sources.append(identity(rational))
    started = datetime.now(timezone.utc).isoformat()
    before = time.perf_counter()
    run = subprocess.run(command, text=True, capture_output=True, check=False)
    elapsed = time.perf_counter() - before
    atomic_bytes(folder / 'stdout.txt', run.stdout.encode())
    atomic_bytes(folder / 'stderr.txt', run.stderr.encode())
    record = {'schema': 'BASS_HE_E13C4_CONTROL_RUN_V1',
              'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': elapsed, 'command': command, 'actual_exit_code': run.returncode,
              'python': sys.version, 'platform': platform.platform(),
              'owner_source_original_path': str(args.interval.resolve()),
              'owner_source_captured_sha256': hashlib.sha256(owner_bytes).hexdigest(),
              'sources_before_execution': sources,
              'output_identities': [identity(folder / 'stdout.txt'), identity(folder / 'stderr.txt')],
              'failure_class': 'IMPLEMENTATION' if run.returncode else None}
    if (folder / 'RESULTS.json').is_file():
        record['output_identities'].append(identity(folder / 'RESULTS.json'))
    atomic_bytes(folder / 'RUN.json', (json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps({'attempt': str(folder), 'actual_exit_code': run.returncode,
                      'elapsed_seconds': elapsed, 'owner_source_sha256': record['owner_source_captured_sha256']}))
    if run.stdout:
        print(run.stdout, end='')
    if run.stderr:
        print(run.stderr, end='', file=sys.stderr)
    return run.returncode


if __name__ == '__main__':
    raise SystemExit(main())
