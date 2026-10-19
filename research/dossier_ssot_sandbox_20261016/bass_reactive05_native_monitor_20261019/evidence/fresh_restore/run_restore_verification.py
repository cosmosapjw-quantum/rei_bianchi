#!/usr/bin/env python3
"""BR05 isolated source-copy restore, scoped tests, and small-fixture replay.

No longspan native case is executed by this script.  The one requested replay
is the already published implementation fixture: one step, T=1e9 s, r=1.
"""
import csv
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

WORKSPACE = Path('/workspace/scratch/996fc62899da')
UNIT = WORKSPACE / 'repo/research/dossier_ssot_sandbox_20261016/bass_reactive05_native_monitor_20261019'
WORK = WORKSPACE / 'br05_work/fresh_restore'
PACKAGE = WORK / 'crate_package'
EVIDENCE = UNIT / 'evidence/fresh_restore'
BASELINE = WORKSPACE / 'br05_work/implementation/sample_final'
IMPLEMENTATION = WORKSPACE / 'br05_work/implementation'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def save(path, data):
    create(path, (json.dumps(data, indent=2) + '\n').encode())


def copy_pinned(source, destination, expected):
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('source identity mismatch: ' + str(source))
    create(destination, data)
    destination.chmod(0o444)
    if sha(destination) != expected:
        raise ValueError('restore copy identity mismatch: ' + str(destination))


def rows(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream)
        result = list(reader)
        if any(None in row or None in row.values() for row in result):
            raise ValueError('partial CSV: ' + str(path))
        return reader.fieldnames, result


def main():
    started = now()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if PACKAGE.exists() or (EVIDENCE / 'FRESH_RESTORE_VERIFICATION.json').exists():
        raise RuntimeError('refusing to reuse prior restore source/output')
    parent = json.loads((UNIT / 'contracts/PARENT_INPUT_SHA256.json').read_text())
    frozen = json.loads((IMPLEMENTATION / 'SOURCE_IDENTITY_FINAL.json').read_text())
    expected = {**parent, **frozen['new_files']}
    assert len(parent) == 125 and len(frozen['new_files']) == 8 and len(expected) == 133
    for relative, digest in expected.items():
        copy_pinned(UNIT / relative, PACKAGE / relative, digest)
    baseline_verification = json.loads((IMPLEMENTATION / 'IMPLEMENTATION_VERIFICATION.json').read_text())
    expected_args = ['SIGNED_MINUS', '121', '1', '0', '1e9', 'false', 'false', '2', '4', '1e-12', '1']
    if 'native_birth_monitor_driver ' + ' '.join(expected_args) + ' ' not in (BASELINE / 'RUN.log').read_text():
        raise RuntimeError('baseline fixture command mismatch')
    baseline_hashes = {'native.csv': sha(BASELINE / 'native.csv'), 'RUN.log': sha(BASELINE / 'RUN.log')}
    for filename, item in baseline_verification['sample_final_schema'].items():
        path = BASELINE / 'monitor' / filename
        if sha(path) != item['sample_sha256']:
            raise RuntimeError('baseline monitor identity changed: ' + filename)
        baseline_hashes['monitor/' + filename] = sha(path)
    script_hashes = {}
    for name in ['audit_native_monitor.py', 'monitor_reference.py']:
        original = UNIT / 'scripts' / name
        script_hashes[name] = sha(original)
        copy_pinned(original, WORK / 'audit_scripts' / name, script_hashes[name])
    save(EVIDENCE / 'FRESH_INPUT_IDENTITY.json', {
        'started_utc': started,
        'parent_inputs': 125,
        'new_sources': 8,
        'fresh_package_files': 133,
        'package': str(PACKAGE),
        'source_sha256': expected,
        'baseline_sample_sha256': baseline_hashes,
        'copied_auditor_sha256': script_hashes,
        'runner_sha256': sha(Path(__file__)),
        'scope': 'Exactly 133 original crate/manifest/donor files copied. Auditor scripts are a separate read-only snapshot. Cargo target directory is new and outside the package.'
    })
    env = os.environ.copy()
    env['CARGO_TARGET_DIR'] = str(WORK / 'target')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    target = Path(env['CARGO_TARGET_DIR'])
    if target.exists():
        raise RuntimeError('fresh target path already exists')
    executions = []

    def run(name, command, *, stdout_path=None, timeout=300):
        print(json.dumps({'stage': name, 'status': 'STARTED', 'utc': now()}), flush=True)
        start = time.perf_counter()
        log = EVIDENCE / (name + '.log')
        with log.open('xb') as stderr:
            if stdout_path is None:
                result = subprocess.run(command, cwd=PACKAGE, env=env, stdout=stderr,
                                        stderr=subprocess.STDOUT, timeout=timeout)
            else:
                stdout_path.parent.mkdir(parents=True, exist_ok=True)
                with stdout_path.open('xb') as out:
                    result = subprocess.run(command, cwd=PACKAGE, env=env, stdout=out,
                                            stderr=stderr, timeout=timeout)
                    out.flush()
                    os.fsync(out.fileno())
            stderr.flush()
            os.fsync(stderr.fileno())
        receipt = {'name': name, 'command': command, 'exit_code': result.returncode,
                   'wall_s': time.perf_counter() - start, 'completed_utc': now(),
                   'log': str(log.relative_to(UNIT)), 'log_sha256': sha(log)}
        if stdout_path is not None:
            receipt['stdout'] = str(stdout_path.relative_to(UNIT))
            receipt['stdout_sha256'] = sha(stdout_path)
        executions.append(receipt)
        with (EVIDENCE / 'EXECUTIONS.jsonl').open('a') as stream:
            stream.write(json.dumps(receipt) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps(receipt), flush=True)
        if result.returncode:
            raise RuntimeError(name + ' returned ' + str(result.returncode))

    manifest = str(PACKAGE / 'br05/Cargo.toml')
    common = ['--manifest-path', manifest, '--offline', '--locked']
    run('FRESH_NEW_RUST_TESTS', ['cargo', 'test', *common, '--test', 'native_birth_monitor', '--jobs', '2', '--', '--test-threads', '2'])
    run('FRESH_STRICT_CLIPPY', ['cargo', 'clippy', *common, '--all-targets', '--jobs', '2', '--', '-D', 'warnings'])
    run('FRESH_RELEASE_DRIVER_BUILD', ['cargo', 'build', *common, '--release', '--example', 'native_birth_monitor_driver', '--jobs', '2'])
    test_counts = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;', (EVIDENCE / 'FRESH_NEW_RUST_TESTS.log').read_text())
    assert test_counts == [('9', '0')]
    binary = target / 'release/examples/native_birth_monitor_driver'
    binary_before = sha(binary)
    sample = EVIDENCE / 'sample'
    monitor = sample / 'monitor'
    if monitor.exists():
        raise RuntimeError('fresh monitor output already exists')
    run('FRESH_SMALL_NATIVE_FIXTURE', [str(binary), *expected_args, str(monitor)], stdout_path=sample / 'native.csv', timeout=60)
    original_header, original_rows = rows(BASELINE / 'native.csv')
    replay_header, replay_rows = rows(sample / 'native.csv')
    assert replay_header == original_header and len(replay_header) == 54
    assert len(original_rows) == len(replay_rows) == 1
    different_fields = [key for key in replay_header if key != 'wall_s' and original_rows[0][key] != replay_rows[0][key]]
    if different_fields:
        raise RuntimeError('fresh serialized state mismatch: ' + repr(different_fields))
    monitor_parity = {}
    for filename in baseline_verification['sample_final_schema']:
        monitor_parity[filename] = {
            'expected_sha256': baseline_hashes['monitor/' + filename],
            'replay_sha256': sha(monitor / filename),
            'bytes': (monitor / filename).stat().st_size,
        }
        if monitor_parity[filename]['expected_sha256'] != monitor_parity[filename]['replay_sha256']:
            raise RuntimeError('fresh monitor raw-byte mismatch: ' + filename)
    run('FRESH_INDEPENDENT_PYTHON_AUDIT', [sys.executable, str(WORK / 'audit_scripts/audit_native_monitor.py'), '--monitor', str(monitor), '--native', str(sample / 'native.csv'), '--output', str(EVIDENCE / 'independent_audit')])
    independent_path = EVIDENCE / 'independent_audit/MONITOR_INDEPENDENT_VERIFICATION.json'
    independent = json.loads(independent_path.read_text())
    original_mismatches = [key for key, digest in expected.items() if sha(UNIT / key) != digest]
    restored_mismatches = [key for key, digest in expected.items() if sha(PACKAGE / key) != digest]
    auditor_mismatches = [key for key, digest in script_hashes.items() if sha(WORK / 'audit_scripts' / key) != digest]
    baseline_mismatches = [key for key, digest in baseline_hashes.items() if sha(BASELINE / key) != digest]
    binary_after = sha(binary)
    if original_mismatches or restored_mismatches or auditor_mismatches or baseline_mismatches or binary_before != binary_after:
        raise RuntimeError('fresh verification input/binary changed')
    if not str(independent['status']).startswith('PASS'):
        raise RuntimeError('independent small fixture audit not PASS')
    result = {
        'status': 'PASS_SCOPED_FRESH_RESTORE',
        'started_utc': started,
        'completed_utc': now(),
        'fresh_package_files': 133,
        'inherited_inputs': 125,
        'new_sources': 8,
        'copied_source_hashes_match': True,
        'original_source_unchanged': not original_mismatches,
        'restored_source_unchanged': not restored_mismatches,
        'read_only_auditor_copy_unchanged': not auditor_mismatches,
        'baseline_sample_unchanged': not baseline_mismatches,
        'fresh_tests': {'passed': 9, 'failed': 0, 'scope': 'native_birth_monitor target only'},
        'fresh_strict_clippy': 'PASS_ALL_TARGETS',
        'fresh_native_fixture_invocations': 1,
        'longspan_native_reruns': 0,
        'fixture_arguments': expected_args,
        'normal_columns': 54,
        'normal_rows': 1,
        'exact_serialized_parity_excluding_wall_s': {'checked_columns': 53, 'differing_columns': different_fields},
        'monitor_raw_byte_parity': monitor_parity,
        'binary_sha256_before': binary_before,
        'binary_sha256_after': binary_after,
        'source_identity_receipt': 'FRESH_INPUT_IDENTITY.json',
        'source_identity_receipt_sha256': sha(EVIDENCE / 'FRESH_INPUT_IDENTITY.json'),
        'independent_audit': {'status': independent['status'], 'path': str(independent_path.relative_to(UNIT)), 'sha256': sha(independent_path), 'birth_rows_all': independent['birth_rows_all'], 'rules_all': independent['rules_all'], 'panels_all': independent['panels_all']},
        'executions': executions,
        'scope': 'Fresh isolated source-copy restore with a fresh Cargo target; 9 new tests and all-target strict Clippy. One small 1e9-s implementation fixture was replayed. Original full 233-test verification is separate. The 8e12-s study was not rerun. This is not a fresh archive/provider download restoration.',
    }
    output = EVIDENCE / 'FRESH_RESTORE_VERIFICATION.json'
    save(output, result)
    print(json.dumps({'status': result['status'], 'receipt': str(output), 'sha256': sha(output)}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if EVIDENCE.exists():
            failure = EVIDENCE / 'FRESH_RESTORE_FAILURE.json'
            if not failure.exists():
                save(failure, {'status': 'FAILED_SCOPE_PENDING_CLASSIFICATION', 'utc': now(), 'exception': repr(error), 'runner_sha256': sha(Path(__file__)), 'longspan_native_reruns': 0})
        raise
