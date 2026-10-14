#!/usr/bin/env python3
"""Verify a bounded PHYS27 stage; optionally replay its frozen main once.

Only --replay launches physics code. Each invocation requires a previously
nonexistent destination and evidence prefix. The original first result is
expected output, never overwritten. No historical program is imported.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import time
import zipfile


HERE = Path(__file__).resolve().parent


def now():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': sha256(data).hexdigest()}


def write_json_new(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only', action='store_true')
    mode.add_argument('--replay', action='store_true')
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--record-prefix', required=True, type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    prefix = args.record_prefix.resolve()
    protocol_path = HERE / 'PORTABILITY_PROTOCOL.json'
    protocol = json.loads(protocol_path.read_bytes())
    archive = HERE / protocol['stage_archive']['filename']
    receipt_path = Path(str(prefix) + '_RECEIPT.json')
    stdout_path = Path(str(prefix) + '_STDOUT.txt')
    stderr_path = Path(str(prefix) + '_STDERR.txt')
    result_path = Path(str(prefix) + '_RESULT.json')
    started_path = Path(str(prefix) + '_STARTED.json')
    if destination.exists():
        parser.error('Destination must not exist; no reused extraction is permitted')
    if not prefix.parent.is_dir():
        parser.error('Record prefix parent must already exist')
    if any(path.exists() for path in [receipt_path, stdout_path, stderr_path,
                                       result_path, started_path]):
        parser.error('Refusing to overwrite any prior evidence for this prefix')
    mode_name = 'replay' if args.replay else 'verify-only'
    started = now()
    tick = time.monotonic()
    receipt = {
        'task': 'REI-PHYS27-20261011',
        'mode': mode_name,
        'evidence_class': 'implementation-verified reproducibility only',
        'operator_role': 'NONBLIND portability operator; not final decision reviewer',
        'independent_physics_evidence_credit': 0,
        'wrapper_command': [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        'wrapper_cwd': str(Path.cwd()),
        'started_utc': started,
        'python_executable': sys.executable,
        'python_version': platform.python_version(),
        'destination_existed_before_invocation': False,
        'destination': str(destination),
        'portability_protocol': identity(protocol_path),
        'wrapper': identity(Path(__file__).resolve()),
        'stage_archive': {'path': str(archive), **identity(archive)},
        'new_physics_evidence_main_invocations': 0,
        'portability_replay_main_invocations': 0,
        'old_program_imports_or_main_invocations': 0,
        'source_changes': 0,
        'tolerance_changes': 0,
        'automatic_retries': 0,
    }
    exit_code = 1
    try:
        if receipt['wrapper'] != protocol['wrapper_identity']:
            raise ValueError('Portability wrapper identity differs from frozen protocol')
        if identity(archive) != {k: protocol['stage_archive'][k]
                                  for k in ['bytes', 'sha256']}:
            raise ValueError('Stage archive identity differs from frozen protocol')
        with zipfile.ZipFile(archive) as stage:
            names = stage.namelist()
            if len(names) != len(set(names)) or any(
                    PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts
                    or '\\' in name or name.endswith('/') for name in names):
                raise ValueError('Unsafe or duplicated stage member')
            manifest_data = stage.read('MANIFEST.json')
            manifest = json.loads(manifest_data)
            if sha256(manifest_data).hexdigest() != protocol['stage_manifest']['sha256']:
                raise ValueError('Stage manifest identity differs from frozen protocol')
            records = manifest['files']
            if set(names) != {'MANIFEST.json', *(item['path'] for item in records)}:
                raise ValueError('Stage members do not exactly match manifest payload list')
            checked = []
            for item in records:
                data = stage.read(item['path'])
                observed = {'bytes': len(data), 'sha256': sha256(data).hexdigest()}
                if observed != {key: item[key] for key in ['bytes', 'sha256']}:
                    raise ValueError('Stage payload mismatch: ' + item['path'])
                checked.append({'path': item['path'], **observed, 'match': True})
            destination.mkdir(parents=True, exist_ok=False)
            for name in names:
                path = destination / name
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(stage.read(name))
        for item in records:
            if identity(destination / item['path']) != {
                    key: item[key] for key in ['bytes', 'sha256']}:
                raise ValueError('Restored payload mismatch: ' + item['path'])
        receipt['stage_verification'] = {
            'zip_member_count': len(names), 'payload_count': len(records),
            'manifest': {'bytes': len(manifest_data),
                         'sha256': sha256(manifest_data).hexdigest()},
            'all_payload_hashes_and_sizes_match_before_and_after_restore': True,
            'payloads': checked,
        }
        expected_path = destination / protocol['expected_first_result']['path']
        expected_bytes = expected_path.read_bytes()
        expected = json.loads(expected_bytes)
        receipt['original_first_result'] = {
            'path': str(expected_path), **identity(expected_path),
            'summary': expected['summary'],
            'classification': 'Inherited first execution output; no execution by this read',
        }
        if args.replay:
            script = destination / protocol['program_path']
            output_path = destination / 'contributions/numerics/FINITE_WIDTH_REPLAY.json'
            command = [sys.executable, str(script), '--output', str(output_path)]
            replay_started = now()
            write_json_new(started_path, {
                'task': receipt['task'], 'started_utc': replay_started,
                'command': command, 'cwd': str(destination),
                'attempt': 1, 'maximum_attempts_in_this_task': 1,
                'independent_physics_evidence_credit': 0,
            })
            replay_tick = time.monotonic()
            receipt['portability_replay_main_invocations'] = 1
            completed = subprocess.run(command, cwd=destination, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, check=False)
            elapsed = time.monotonic() - replay_tick
            with stdout_path.open('xb') as stream:
                stream.write(completed.stdout)
            with stderr_path.open('xb') as stream:
                stream.write(completed.stderr)
            receipt['replay_execution'] = {
                'command': command, 'cwd': str(destination),
                'started_utc': replay_started, 'finished_utc': now(),
                'wall_time_seconds': elapsed, 'exit_code': completed.returncode,
                'stdout': {'path': str(stdout_path), **identity(stdout_path)},
                'stderr': {'path': str(stderr_path), **identity(stderr_path)},
            }
            if output_path.exists():
                with result_path.open('xb') as stream:
                    stream.write(output_path.read_bytes())
                receipt['replay_result'] = {'path': str(result_path), **identity(result_path)}
            if completed.returncode != 0:
                raise RuntimeError('Frozen PHYS27 replay returned nonzero; evidence preserved')
            replay_bytes = result_path.read_bytes()
            replay = json.loads(replay_bytes)
            byte_equal = replay_bytes == expected_bytes
            parsed_equal = replay == expected
            receipt['comparison'] = {
                'byte_equal': byte_equal, 'parsed_json_equal': parsed_equal,
                'expected_sha256': sha256(expected_bytes).hexdigest(),
                'replay_sha256': sha256(replay_bytes).hexdigest(),
            }
            receipt['replay_counts_as_instrumented_by_frozen_program'] = replay['summary']['actual_counts']
            receipt['count_interpretation'] = {
                'original_first_science_main_count': 1,
                'this_portability_main_count': 1,
                'new_science_main_count_from_this_portability_action': 0,
                'independent_physics_evidence_credit': 0,
                'warning': 'The frozen program labels each invocation new_scientific_main_invocations=1; this second invocation is classified solely as portability replay.',
            }
            if not byte_equal or not parsed_equal:
                raise ValueError('Replay differs from first output; no automatic rerun permitted')
        receipt['status'] = 'PASS'
        exit_code = 0
    except Exception as exc:
        receipt['status'] = 'FAIL'
        receipt['failure'] = {'exception_type': type(exc).__name__, 'message': str(exc),
                              'first_failure_preserved': True, 'automatic_retry': False}
    receipt['finished_utc'] = now()
    receipt['total_wall_time_seconds'] = time.monotonic() - tick
    receipt['wrapper_exit_code'] = exit_code
    write_json_new(receipt_path, receipt)
    print(json.dumps({'status': receipt['status'], 'mode': mode_name,
                      'receipt': str(receipt_path), 'portability_replay_main_invocations':
                      receipt['portability_replay_main_invocations']}, ensure_ascii=False))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
