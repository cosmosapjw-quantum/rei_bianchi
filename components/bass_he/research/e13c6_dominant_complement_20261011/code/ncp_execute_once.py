#!/usr/bin/env python3
"""One new E13C6 N512/P60 execution, then one exact saved-result analysis.

This stdlib-only wrapper never imports a scientific kernel. The externally
pinned EXECUTION_LOCK closes the source, selected inputs and completed
baseline. A launch reservation consumes the one work-unit slot even if
process creation fails; no path in this program retries a child process.
"""
import argparse
from datetime import datetime, timezone
import decimal
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import resource
import signal
import stat
import subprocess
import sys
import time
import traceback
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_LOCK_SHA = '0b4688c61c6070e0663fa78043a4ff3c37af2250f1e9d98d1e5485f568efaf47'
NUMERICAL_SHA = 'c9321b00102920e8aedbcc2f9f5cdcd374e67742f346754b928cc873d0e25f23'
ANALYSIS_SHA = 'd975525df1f0d3a1cc18a254c05cc92d36677e2538438e71a420644ab46a7db2'
WORK_UNIT = {'N': 512, 'precision': 60, 'nodes': [101, 102, 410, 413], 'mode': 'OFF'}
MEMORY_BYTES = 1024 ** 3
NUMERICAL_PREFIX = b'bass-he-e13c6-off4-semantic-v1\n'
ANALYSIS_PREFIX = b'bass-he-e13c6-budget-semantic-v1\n'
BASE_NUM = 'runs/N512_P60'
BASE_ANALYSIS = 'analysis/N512_P60'
REQUIRED = {
    'SOURCE_LOCK.json', 'code/ncp_execute_once.py', 'code/analyze_refinement.py',
    *(BASE_NUM + '/' + x for x in ('RESULTS.json', 'NUMERICAL_PROJECTION.json',
                                  'NUMERICAL_IDENTITY.json', 'START.json', 'RESOURCE_RECEIPT.json')),
    *(BASE_ANALYSIS + '/' + x for x in ('GLOBAL_ANALYSIS.json', 'ANALYSIS_IDENTITY.json', 'GLOBAL_WIDTHS.csv')),
}
FORBIDDEN = dict(ODE_solves=0, native_runs=0, gas_advances=0,
                 full_first2_reruns=0, old_budget_reruns=0,
                 E13C5_transport_replays=0, automatic_retries=0)


def utc():
    return datetime.now(timezone.utc).isoformat()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def read(path):
    def nonfinite(value):
        raise ValueError('nonfinite JSON literal: ' + value)
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream, object_pairs_hook=no_duplicates,
                         parse_constant=nonfinite)


def save_new(path, obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True,
                     indent=2, allow_nan=False).encode('utf-8') + b'\n'
    with Path(path).open('xb') as stream:
        if stream.write(raw) != len(raw):
            raise OSError('short write')
        stream.flush()
        os.fsync(stream.fileno())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_file(root, name):
    require(isinstance(name, str) and name and '\\' not in name,
            'invalid inventory path')
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and
            all(part not in ('', '.', '..') for part in name.split('/')),
            'non-canonical or escaping inventory path: ' + name)
    current = root
    for part in relative.parts:
        current = current / part
        require(not current.is_symlink(), 'symlink in pinned path: ' + name)
    require(current.is_file() and stat.S_ISREG(current.stat().st_mode),
            'missing/non-regular pinned file: ' + name)
    return current


def verify_inventory(root, records):
    require(isinstance(records, dict) and records, 'empty/malformed file inventory')
    actual = {}
    for name, pin in sorted(records.items()):
        require(isinstance(pin, dict) and type(pin.get('bytes')) is int and
                pin['bytes'] >= 0 and isinstance(pin.get('sha256'), str) and
                re.fullmatch('[0-9a-f]{64}', pin['sha256']),
                'malformed file pin: ' + str(name))
        path = safe_file(root, name)
        observed = {'bytes': path.stat().st_size, 'sha256': sha(path)}
        require(observed == {'bytes': pin['bytes'], 'sha256': pin['sha256']},
                'pinned file mismatch: ' + name)
        actual[name] = observed
    return actual


def verify_closure(expected_execution_sha):
    lock_path = safe_file(ROOT, 'EXECUTION_LOCK.json')
    require(sha(lock_path) == expected_execution_sha, 'EXECUTION_LOCK SHA mismatch')
    lock = read(lock_path)
    require(lock.get('schema') == 'bass-he-e13c6-execution-lock-v1',
            'unsupported EXECUTION_LOCK schema')
    files = lock.get('files')
    require(isinstance(files, dict) and REQUIRED <= set(files),
            'EXECUTION_LOCK omits a required runtime/baseline file')
    observed = verify_inventory(ROOT, files)
    require(observed['SOURCE_LOCK.json']['sha256'] == SOURCE_LOCK_SHA,
            'different scientific SOURCE_LOCK')
    source_lock = read(ROOT / 'SOURCE_LOCK.json')
    require(source_lock.get('schema') == 'bass-he-e13c6-source-lock-v1' and
            isinstance(source_lock.get('files'), dict) and len(source_lock['files']) == 15,
            'unexpected scientific source inventory')
    source_actual = verify_inventory(ROOT, source_lock['files'])
    require(set(source_actual) <= set(files) and
            all(source_actual[k] == observed[k] for k in source_actual),
            'execution/source inventories disagree or lack source closure')
    expected_baseline = {'numerical_semantic_sha256': NUMERICAL_SHA,
                         'analysis_semantic_sha256': ANALYSIS_SHA}
    require(isinstance(lock.get('baseline'), dict) and
            all(lock['baseline'].get(k) == v for k, v in expected_baseline.items()),
            'EXECUTION_LOCK selects a different numerical/analysis baseline')
    return {'execution_lock_sha256': expected_execution_sha,
            'source_lock_sha256': SOURCE_LOCK_SHA,
            'files': observed, 'source_files': source_actual}


def numerical_identity(directory):
    result = read(directory / 'RESULTS.json')
    supplied = read(directory / 'NUMERICAL_PROJECTION.json')
    identity = read(directory / 'NUMERICAL_IDENTITY.json')
    keys = ('schema', 'work_unit', 'input_checks', 'new_coefficient_evaluations',
            'new_local_enclosures', 'reused_local_enclosures', 'rounding_operation_counts',
            'source_unchanged_during_run', 'source_lock_sha256', 'forbidden_invocations')
    projection = {k: result[k] for k in keys}
    projection['tracks'] = [{k: v for k, v in t.items() if k != 'elapsed_seconds'}
                            for t in result['tracks']]
    require(supplied == projection, 'actual RESULTS disagrees with full numerical projection')
    raw = canonical(projection)
    digest = hashlib.sha256(NUMERICAL_PREFIX + raw).hexdigest()
    require(result['work_unit'] == WORK_UNIT, 'different N/P/mode/target work unit')
    require(result['new_local_enclosures'] == 8 and result['reused_local_enclosures'] == 0 and
            result['new_coefficient_evaluations'] == 8192,
            'different enclosure/coefficient invocation budget')
    require(result['source_lock_sha256'] == SOURCE_LOCK_SHA and
            result['source_unchanged_during_run'] is True, 'scientific source identity changed')
    require(result['forbidden_invocations'] == {k: 0 for k in
            ('ODE_solves', 'native_runs', 'gas_advances', 'full_first2_reruns', 'old_budget_reruns')},
            'forbidden scientific invocation is not exactly zero')
    require(all(result.get(k) == 'HOLD' for k in ('physical', 'continuum', 'production', 'receiver')),
            'unreviewed claim promotion')
    require(identity.get('projection_version') == 1 and
            identity.get('semantic_sha256') == digest and
            identity.get('canonical_object_sha256') == hashlib.sha256(raw).hexdigest() and
            identity.get('projection_file_sha256') == sha(directory / 'NUMERICAL_PROJECTION.json') and
            identity.get('result_file_sha256') == sha(directory / 'RESULTS.json'),
            'actual numerical identity/file evidence mismatch')
    require(digest == NUMERICAL_SHA, 'whole numerical semantic parity failed')
    return {'semantic_sha256': digest,
            'canonical_object_sha256': hashlib.sha256(raw).hexdigest(),
            'result_file_sha256': sha(directory / 'RESULTS.json'),
            'projection_file_sha256': sha(directory / 'NUMERICAL_PROJECTION.json')}


def analysis_identity(directory):
    analysis = read(directory / 'GLOBAL_ANALYSIS.json')
    identity = read(directory / 'ANALYSIS_IDENTITY.json')
    raw = canonical(analysis)
    digest = hashlib.sha256(ANALYSIS_PREFIX + raw).hexdigest()
    require(analysis.get('work_unit') == WORK_UNIT and
            analysis.get('source_numerical_semantic_sha256') == NUMERICAL_SHA and
            analysis.get('source_lock_sha256') == SOURCE_LOCK_SHA,
            'analysis is attached to a different numerical target')
    require(analysis.get('analysis_scientific_kernel_calls') == 0 and
            identity.get('analysis_scientific_kernel_calls') == 0,
            'analysis unexpectedly invokes a scientific kernel')
    require(identity.get('schema') == 'bass-he-e13c6-analysis-identity-v1' and
            identity.get('exclusions') == [] and
            identity.get('semantic_sha256') == digest and
            identity.get('canonical_object_sha256') == hashlib.sha256(raw).hexdigest() and
            identity.get('analysis_file_sha256') == sha(directory / 'GLOBAL_ANALYSIS.json'),
            'actual full analysis identity/file evidence mismatch')
    require(digest == ANALYSIS_SHA, 'whole analysis semantic parity failed')
    return {'semantic_sha256': digest,
            'canonical_object_sha256': hashlib.sha256(raw).hexdigest(),
            'analysis_file_sha256': sha(directory / 'GLOBAL_ANALYSIS.json'),
            'csv_file_sha256': sha(directory / 'GLOBAL_WIDTHS.csv')}


def host_preflight(evidence):
    require(platform.system() == 'Linux' and platform.python_implementation() == 'CPython',
            'execution requires Linux CPython; no installation or environment repair is attempted')
    require(sys.version_info[:2] == (3, 12), 'declared reproduction runtime is CPython 3.12.x')
    affinity = sorted(os.sched_getaffinity(0))
    require(bool(affinity), 'no available CPU affinity')
    as_limit = resource.getrlimit(resource.RLIMIT_AS)
    require(as_limit[1] == resource.RLIM_INFINITY or as_limit[1] >= MEMORY_BYTES,
            'inherited hard address-space limit cannot permit the declared 1 GiB cap')
    cgroup = {}
    for name in ('memory.max', 'memory.current', 'memory.high', 'cpu.max', 'cpuset.cpus.effective'):
        path = Path('/sys/fs/cgroup') / name
        try:
            cgroup[name] = path.read_text().strip()
        except OSError as exc:
            cgroup[name] = {'available': False, 'error_type': type(exc).__name__}
    attestation = {'status': 'NOT_ASSERTED', 'scope': 'No provider identity is inferred from hostname or a successful run.'}
    if evidence is not None:
        evidence = evidence.resolve(strict=True)
        require(evidence.is_file() and not evidence.is_symlink(), 'provider evidence is not a regular file')
        attestation = {'status': 'USER_SUPPLIED_EVIDENCE_RECORDED_NOT_INDEPENDENTLY_VERIFIED',
                       'evidence_filename': evidence.name, 'bytes': evidence.stat().st_size,
                       'sha256': sha(evidence)}
    return {'hostname': platform.node(), 'platform': platform.platform(), 'python': sys.version,
            'decimal_libmpdec_version': decimal.__libmpdec_version__,
            'cpu_affinity_available': affinity, 'scientific_child_affinity': [affinity[0]],
            'inherited_RLIMIT_AS': list(as_limit), 'cgroup_observation': cgroup,
            'provider_attestation': attestation,
            'limits': {'scientific_workers': 1, 'threads_per_worker': 1,
                       'address_space_bytes': MEMORY_BYTES, 'primary_inner_seconds': 300,
                       'primary_outer_timeout_seconds': 310, 'analysis_timeout_seconds': 60,
                       'automatic_retries': 0}}


def run_child(command, output, label, timeout, cpu, counters, reservation_key, invocation_key):
    # Reserve before Popen; an OS-level launch failure still consumes this slot.
    counters[reservation_key] = 1
    save_new(output / (label + '_LAUNCH_RESERVED.json'),
             {'utc': utc(), 'argv': command, 'timeout_seconds': timeout,
              'counters': dict(counters), 'no_retry': True})
    environment = os.environ.copy()
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
        environment[key] = '1'
    def constrain_child():
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
        os.sched_setaffinity(0, {cpu})
    child = None
    started = time.perf_counter()
    status = 'LAUNCH_FAILED'
    code = None
    try:
        with (output / (label + '.stdout.log')).open('xb') as stdout, \
             (output / (label + '.stderr.log')).open('xb') as stderr:
            child = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=stdout,
                                     stderr=stderr, start_new_session=True, preexec_fn=constrain_child)
            counters[invocation_key] += 1
            save_new(output / (label + '_PROCESS_STARTED.json'),
                     {'utc': utc(), 'pid': child.pid, 'counters': dict(counters)})
            code = child.wait(timeout=timeout)
            status = 'EXIT_ZERO' if code == 0 else 'NONZERO_EXIT'
        require(code == 0, label + ' failed with exit ' + str(code))
    except BaseException:
        if child is not None and child.poll() is None:
            status = 'TIMEOUT_OR_INTERRUPTION'
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            code = child.returncode
        raise
    finally:
        save_new(output / (label + '_PROCESS_RECEIPT.json'),
                 {'status': status, 'exit_code': code, 'elapsed_seconds': time.perf_counter() - started,
                  'spawned': child is not None, 'counters': dict(counters), 'automatic_retries': 0})


def package_return(output):
    files = []
    for path in sorted(output.rglob('*')):
        require(not path.is_symlink(), 'symlink encountered in return output')
        if path.is_file():
            require(stat.S_ISREG(path.stat().st_mode), 'non-regular return output')
            files.append(path)
    manifest = {'schema': 'bass-he-e13c6-return-manifest-v1',
                'files': {p.relative_to(output).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                          for p in files},
                'self_exclusion': 'This manifest and subsequently written ZIP/ZIP identity are not self-hashed.'}
    save_new(output / 'RETURN_MANIFEST.json', manifest)
    files.append(output / 'RETURN_MANIFEST.json')
    archive = output / 'NCP_RETURN.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in files:
            zf.write(path, arcname=path.relative_to(output).as_posix())
    identity = {'archive_name': archive.name, 'bytes': archive.stat().st_size,
                'sha256': sha(archive), 'members': len(files),
                'scope': 'Actual new execution output; this identity is a sidecar outside its own ZIP.'}
    save_new(output / 'RETURN_ARCHIVE_IDENTITY.json', identity)
    return identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True,
                        help='Fresh directory outside the immutable package; it must not already exist.')
    parser.add_argument('--execution-lock-sha256', required=True,
                        help='Externally supplied immutable EXECUTION_LOCK SHA from the handoff.')
    parser.add_argument('--provider-evidence', type=Path,
                        help='Optional user-supplied existing provider evidence; no provider is inferred.')
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise InterruptedError('wrapper interrupted by signal ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGHUP, interrupted)
    output = args.output_root.absolute()
    # Reject a pre-existing symlink even when resolve() would hide it.
    if output.exists() or output.is_symlink():
        print(json.dumps({'status': 'NOT_RUN_OUTPUT_COLLISION', 'output_root': str(output),
                          'new_N512_work_unit_invocations': 0, 'automatic_retries': 0,
                          'prior_output_untouched': True}), file=sys.stderr)
        return 2
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        print(json.dumps({'status': 'NOT_RUN_OUTPUT_INSIDE_IMMUTABLE_PACKAGE',
                          'new_N512_work_unit_invocations': 0, 'automatic_retries': 0}), file=sys.stderr)
        return 2
    try:
        output.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        print(json.dumps({'status': 'NOT_RUN_OUTPUT_CREATION_FAILED', 'error_type': type(exc).__name__,
                          'message': str(exc), 'new_N512_work_unit_invocations': 0,
                          'automatic_retries': 0}), file=sys.stderr)
        return 2
    started = time.perf_counter()
    counters = {'consumed_N512_slots': 0, 'new_N512_work_unit_invocations': 0,
                'consumed_analysis_slots': 0, 'new_exact_analysis_invocations': 0, **FORBIDDEN}
    phase = 'INITIAL_RECEIPT'
    status = 'FAIL_PRESERVED_NO_RETRY'
    failure = None
    before = None
    parity = None
    save_new(output / 'RUN_ONCE.lock', {'schema': 'bass-he-e13c6-one-shot-v1', 'created_utc': utc(),
                                      'execution_lock_sha256': args.execution_lock_sha256,
                                      'work_unit': WORK_UNIT, 'automatic_retries': 0})
    try:
        phase = 'EXECUTION_SOURCE_AND_BASELINE_CLOSURE'
        require(re.fullmatch('[0-9a-f]{64}', args.execution_lock_sha256) is not None,
                'expected execution SHA must be 64 lowercase hexadecimal characters')
        before = verify_closure(args.execution_lock_sha256)
        save_new(output / 'SOURCE_AND_INPUT_BEFORE.json', before)
        base_num = numerical_identity(ROOT / BASE_NUM)
        base_analysis = analysis_identity(ROOT / BASE_ANALYSIS)
        save_new(output / 'BASELINE_PARITY_GATES.json', {'numerical': base_num, 'analysis': base_analysis})
        phase = 'HOST_PREFLIGHT'
        host = host_preflight(args.provider_evidence)
        save_new(output / 'START.json', {'started_utc': utc(), 'host': host, 'argv': sys.argv,
                                       'work_unit': WORK_UNIT, 'counters': dict(counters),
                                       'execution_lock_sha256': args.execution_lock_sha256,
                                       'claim_ceiling': 'same-code recorded-host reproduction; physical/continuum/production/receiver HOLD'})
        if args.provider_evidence is not None:
            evidence = args.provider_evidence.resolve(strict=True)
            with (output / 'USER_SUPPLIED_PROVIDER_EVIDENCE.bin').open('xb') as stream:
                with evidence.open('rb') as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b''):
                        stream.write(chunk)
        phase = 'NEW_N512_P60_EXECUTION'
        python = [sys.executable, '-E', '-s', '-S', '-B']
        run_child(python + [str(ROOT / 'code/dominant_complement.py'), '--subdivisions', '512',
                           '--precision', '60', '--output-dir', str(output / 'N512_P60')],
                  output, 'N512', 310, host['scientific_child_affinity'][0], counters,
                  'consumed_N512_slots', 'new_N512_work_unit_invocations')
        phase = 'NEW_NUMERICAL_WHOLE_PROJECTION_PARITY'
        fresh_num = numerical_identity(output / 'N512_P60')
        phase = 'NEW_EXACT_SAVED_RESULT_ANALYSIS'
        run_child(python + [str(ROOT / 'code/analyze_refinement.py'), '--result',
                           str(output / 'N512_P60/RESULTS.json'), '--output-dir', str(output / 'ANALYSIS')],
                  output, 'ANALYSIS', 60, host['scientific_child_affinity'][0], counters,
                  'consumed_analysis_slots', 'new_exact_analysis_invocations')
        phase = 'NEW_ANALYSIS_WHOLE_OBJECT_AND_CSV_PARITY'
        fresh_analysis = analysis_identity(output / 'ANALYSIS')
        require(fresh_analysis['csv_file_sha256'] == base_analysis['csv_file_sha256'],
                'deterministic GLOBAL_WIDTHS CSV byte parity failed')
        require(canonical(read(output / 'N512_P60/NUMERICAL_PROJECTION.json')) ==
                canonical(read(ROOT / BASE_NUM / 'NUMERICAL_PROJECTION.json')),
                'full numerical projection object differs from baseline')
        require(canonical(read(output / 'ANALYSIS/GLOBAL_ANALYSIS.json')) ==
                canonical(read(ROOT / BASE_ANALYSIS / 'GLOBAL_ANALYSIS.json')),
                'full exact analysis object differs from baseline')
        parity = {'status': 'PASS_SCOPED_NEW_OFF4_N512_AND_EXACT_ANALYSIS_PARITY',
                  'actual_numerical': fresh_num, 'actual_analysis': fresh_analysis,
                  'whole_numerical_projection_equal': True, 'whole_analysis_object_equal': True,
                  'CSV_byte_equal': True,
                  'RESULTS_byte_equality_required': False,
                  'host_time_paths_are_receipts_not_numerical_parity_fields': True,
                  'same_code_reproduction_is_independent_physics_validation': False}
        save_new(output / 'PARITY.json', parity)
        phase = 'SOURCE_AND_INPUT_AFTER'
        after = verify_closure(args.execution_lock_sha256)
        require(after == before, 'source/input/lock/baseline changed during execution')
        save_new(output / 'SOURCE_AND_INPUT_AFTER.json', after)
        status = 'PASS_SCOPED_NEW_OFF4_N512_AND_EXACT_ANALYSIS_PARITY'
        phase = 'COMPLETE'
    except BaseException as exc:
        failure = {'status': 'NOT_RUN' if counters['consumed_N512_slots'] == 0 else 'FAIL_PRESERVED_NO_RETRY',
                   'failing_phase': phase, 'error_type': type(exc).__name__, 'message': str(exc),
                   'traceback': traceback.format_exc(), 'counters': dict(counters),
                   'automatic_retries': 0, 'failed_evidence_preserved': True}
        status = failure['status']
        save_new(output / 'FAILURE.json', failure)
        if before is not None and not (output / 'SOURCE_AND_INPUT_AFTER.json').exists():
            try:
                after = verify_closure(args.execution_lock_sha256)
                save_new(output / 'SOURCE_AND_INPUT_AFTER.json',
                         {'verification_after_failure': 'PASS', 'unchanged_from_before': after == before, **after})
            except BaseException as post_exc:
                save_new(output / 'SOURCE_AND_INPUT_AFTER_FAILURE.json',
                         {'verification_after_failure': 'FAIL', 'error_type': type(post_exc).__name__,
                          'message': str(post_exc)})
    receipt = {'schema': 'bass-he-e13c6-ncp-one-shot-receipt-v1', 'status': status,
               'finished_utc': utc(), 'elapsed_seconds': time.perf_counter() - started,
               'last_phase': phase, 'failure': failure, 'counters': counters,
               'work_unit': WORK_UNIT, 'execution_lock_sha256': args.execution_lock_sha256,
               'source_lock_sha256': SOURCE_LOCK_SHA,
               'numerical_semantic_sha256_expected': NUMERICAL_SHA,
               'analysis_semantic_sha256_expected': ANALYSIS_SHA,
               'child_peak_RSS_KiB': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
               'byte_identity_vs_semantic_parity': 'Host-dependent RESULTS bytes are recorded, never substituted for whole numerical semantic parity.',
               'physical': 'HOLD', 'continuum': 'HOLD', 'production': 'HOLD', 'receiver': 'HOLD'}
    save_new(output / 'EXECUTION_RECEIPT.json', receipt)
    try:
        archive = package_return(output)
    except BaseException as exc:
        save_new(output / 'RETURN_PACKAGING_FAILURE.json',
                 {'status': 'RETURN_PACKAGING_FAILED', 'error_type': type(exc).__name__,
                  'message': str(exc), 'scientific_status': status, 'counters': counters,
                  'automatic_retries': 0})
        print(json.dumps({'status': 'RETURN_PACKAGING_FAILED', 'scientific_status': status,
                          'output_root': str(output), 'counters': counters}), flush=True)
        return 1
    print(json.dumps({'status': status, 'output_root': str(output), 'return_archive': archive,
                      'counters': counters}), flush=True)
    return 0 if status.startswith('PASS_') else 1


if __name__ == '__main__':
    raise SystemExit(main())
