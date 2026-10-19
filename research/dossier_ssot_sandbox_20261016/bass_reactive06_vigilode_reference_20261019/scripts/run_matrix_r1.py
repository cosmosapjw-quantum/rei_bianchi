#!/usr/bin/env python3
"""Execute the fixed nine BR06 recovery controls; never classify convergence.

Every process gets a new output directory, a pre-execution intent, a wall-time
budget and raw stdout/stderr. Timeouts remain work-budget outcomes. This script
does not change any physics, source, controller, Git ref or cloud object.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

CASES = [
    ('fitted_r4_m4_o4_e8', 'SIGNED_MINUS', 'fitted', 4, 2, 4, 4, 8, 'original'),
    ('fitted_r4_m4_o8_e8', 'SIGNED_MINUS', 'fitted', 4, 2, 4, 8, 8, 'original'),
    ('fitted_r4_m4_o8_e16', 'SIGNED_MINUS', 'fitted', 4, 2, 4, 8, 16, 'original'),
    ('fitted_r8_m4_o8_e16', 'SIGNED_MINUS', 'fitted', 8, 2, 4, 8, 16, 'original'),
    ('gauss_r1_d8_m4_o8_e16', 'SIGNED_MINUS', 'gauss', 1, 8, 4, 8, 16, 'original'),
    ('gauss_r1_d16_m4_o8_e16', 'SIGNED_MINUS', 'gauss', 1, 16, 4, 8, 16, 'original'),
    ('plus_gauss_r1_d8_m4_o8_e16', 'SIGNED_PLUS', 'gauss', 1, 8, 4, 8, 16, 'original'),
    ('split_gauss_r1_d8_m4_o8_e16', 'SIGNED_MINUS', 'gauss', 1, 8, 4, 8, 16, 'split'),
    ('gauss_r1_d8_m8_o8_e16', 'SIGNED_MINUS', 'gauss', 1, 8, 8, 8, 16, 'original'),
]

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def identity(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(chunk)
    return {'bytes': path.stat().st_size, 'sha256': sha.hexdigest()}

def new_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=3, choices=[1, 2, 3])
    parser.add_argument('--timeout', type=float, default=600.0)
    parser.add_argument('--source-identity', type=Path, required=True)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    source = args.source_identity.resolve(strict=True)
    output = args.output.resolve()
    if args.timeout <= 0 or output.exists():
        raise ValueError('positive work budget and a new output directory required')
    output.mkdir(parents=True)
    run_identity = {'binary': str(binary), 'binary_identity': identity(binary),
                    'source_identity_path': str(source), 'source_identity': identity(source)}
    plan = {'schema': 'rei.br06.recovery_matrix.v1', 'scope': 'Frozen recorded gas inventory; no new nonlinear history',
            'recovery': 'R1 actual post-interruption executions; prior PASS not inherited',
            'created_utc': utc(), 'workers': args.workers, 'timeout_per_case_s': args.timeout,
            'case_count': len(CASES), 'cases': CASES, **run_identity}
    new_json(output / 'MATRIX_INTENT.json', plan)

    def execute(case):
        name, *controls = case
        directory = output / name
        directory.mkdir()
        data = directory / 'data'
        command = [str(binary), 'run', *map(str, controls), '0', str(data)]
        intent = {'case': name, 'command': command, 'started_utc': utc(),
                  'timeout_s': args.timeout, **run_identity}
        new_json(directory / 'EXECUTION_INTENT.json', intent)
        start = time.monotonic()
        timed_out = False
        with (directory / 'stdout.log').open('xb') as out, (directory / 'stderr.log').open('xb') as err:
            try:
                process = subprocess.run(command, stdout=out, stderr=err,
                                         timeout=args.timeout, check=False)
                code = process.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                code = None
        status = 'WORK_BUDGET_TIMEOUT' if timed_out else ('PROGRAM_COMPLETED' if code == 0 else 'PROGRAM_DIAGNOSTIC_OR_FAILURE')
        receipt = {**intent, 'completed_utc': utc(), 'wall_s': time.monotonic() - start,
                   'exit_code': code, 'status': status, 'convergence_classification': 'NOT_ASSIGNED_BY_RUNNER',
                   'files': {p.relative_to(directory).as_posix(): identity(p)
                             for p in sorted(directory.rglob('*')) if p.is_file()}}
        new_json(directory / 'EXECUTION.json', receipt)
        print(json.dumps({'case': name, 'status': status, 'wall_s': receipt['wall_s']}), flush=True)
        return receipt

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(execute, CASES))
    final = {**plan, 'completed_utc': utc(), 'completed_programs': sum(r['exit_code'] == 0 for r in results),
             'results': results, 'binary_unchanged': identity(binary) == run_identity['binary_identity'],
             'source_identity_unchanged': identity(source) == run_identity['source_identity']}
    new_json(output / 'MATRIX_EXECUTION.json', final)
    if not final['binary_unchanged'] or not final['source_identity_unchanged']:
        raise RuntimeError('source/build identity changed during execution')
    return 0 if final['completed_programs'] == len(CASES) else 1

if __name__ == '__main__':
    raise SystemExit(main())
