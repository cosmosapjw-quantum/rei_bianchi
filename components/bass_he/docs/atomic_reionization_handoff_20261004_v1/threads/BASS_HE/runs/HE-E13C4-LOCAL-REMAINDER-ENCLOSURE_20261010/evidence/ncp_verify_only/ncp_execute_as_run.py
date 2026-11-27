#!/usr/bin/env python3
"""One host-compatibility execution of the sealed E13C4 local work unit.

Default: verify lock and record host, without scientific execution.
--execute: fresh six-control N512/P60 calculation exactly once, then compare
the complete deterministic numerical projection with reviewed saved evidence.
Does not solve the old photon ODE, run gas/native campaigns, publish or merge.
"""
import argparse
from datetime import datetime, timezone
import decimal
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time


def atomic(path, obj):
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('x') as f:
        json.dump(obj, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numerical_projection(result):
    rows = []
    for row in result['controls']:
        rows.append({k: v for k, v in row.items() if k != 'elapsed_seconds'})
    return {'controls': rows, 'rounding_operation_counts': result['rounding_operation_counts'],
            'source_unchanged_during_run': result['source_unchanged_during_run'],
            'compatibility_failures': result['compatibility_failures'],
            'saved_firstvariation_containment_failures': result['saved_firstvariation_containment_failures']}


def numerical_digest(result):
    payload = json.dumps(numerical_projection(result), sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest()


def optional_text(path):
    p = Path(path)
    return p.read_text().strip() if p.is_file() else None


def host_inventory():
    memory = {}
    meminfo = optional_text('/proc/meminfo')
    if meminfo:
        memory = {line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                  for line in meminfo.splitlines() if line.startswith(('MemTotal:', 'MemAvailable:'))}
    try:
        cpu = subprocess.run(['lscpu'], text=True, capture_output=True, check=False, timeout=10)
        lscpu = {'actual_exit': cpu.returncode, 'stdout': cpu.stdout, 'stderr': cpu.stderr}
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        lscpu = {'status': 'UNAVAILABLE', 'reason': type(error).__name__}
    return {'recorded_utc': datetime.now(timezone.utc).isoformat(),
            'python': sys.version, 'executable': sys.executable,
            'implementation': platform.python_implementation(), 'platform': platform.platform(),
            'decimal_libmpdec_version': decimal.__libmpdec_version__,
            'logical_cpu_count': os.cpu_count(),
            'cpu_affinity': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
            'cgroup_cpu_max': optional_text('/sys/fs/cgroup/cpu.max'),
            'cgroup_cpuset_effective': optional_text('/sys/fs/cgroup/cpuset.cpus.effective'),
            'cgroup_memory_max': optional_text('/sys/fs/cgroup/memory.max'),
            'cgroup_memory_current': optional_text('/sys/fs/cgroup/memory.current'),
            'memory': memory, 'lscpu': lscpu,
            'selected_layout': {'processes': 1, 'threads': 1, 'MPI': False,
                                'reason': 'six local validated Decimal tasks; no unmeasured native substitution'}}


def arithmetic_smoke(package):
    sys.path.insert(0, str(package / 'code'))
    import directed_interval as di
    di.configure(60)
    tests = []
    def check(name, ok):
        tests.append({'id': name, 'pass': bool(ok)})
        if not ok:
            raise ArithmeticError('host arithmetic check failed: ' + name)
    x = di.IV(1) / di.IV(3)
    check('rational_division_inclusion', Fraction(x.lo) <= Fraction(1, 3) <= Fraction(x.hi))
    x = di.IV(2).sqrt()
    check('sqrt_rational_square_inclusion', Fraction(x.lo) ** 2 <= 2 <= Fraction(x.hi) ** 2)
    x = di.IV('0.125').exp()
    # Independent exact positive Taylor series and geometric tail enclosure.
    term = total = Fraction(1)
    for k in range(1, 100):
        term *= Fraction(1, 8 * k); total += term
    next_term = term * Fraction(1, 800)
    upper = total + next_term / (1 - Fraction(1, 808))
    check('exp_exact_rational_series_inclusion', Fraction(x.lo) <= total and upper <= Fraction(x.hi))
    check('captured_binary64_lift', Fraction(di.IV.from_binary64(0.1).lo) == Fraction.from_float(0.1))
    failed_domain = False
    try:
        di.response_j(di.IV(0), di.IV(-1))
    except ArithmeticError:
        failed_domain = True
    check('zero_rate_negative_width_rejected', failed_domain)
    return tests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 180:
        parser.error('timeout must be in 1..180 seconds; no implicit budget expansion')
    package = args.package.resolve()
    out = args.out.absolute()
    # Reject an existing directory or symlink before any output is mutated.
    out.mkdir(parents=True, exist_ok=False)
    report = {'task': 'NCP_E13C4_SIX_LOCAL_HOST_PARITY', 'execute_requested': args.execute,
              'started_utc': datetime.now(timezone.utc).isoformat(), 'status': 'INTAKE',
              'new_host_scientific_runs': 0, 'old_continuous_solves': 0, 'native_runs': 0,
              'gas_advances': 0, 'physical': 'HOLD', 'production': 'HOLD',
              'first2_enclosure': 'NOT_IMPLEMENTED_NOT_AUTHORIZED_BY_THIS_RUNNER'}
    atomic(out / 'NCP_RESULT.json', report)
    try:
        lock_path = package / 'EXECUTION_LOCK.json'
        lock = json.loads(lock_path.read_text())
        checks = []
        for row in lock['files']:
            path = (package / row['path']).resolve()
            if not path.is_relative_to(package) or not path.is_file():
                raise ValueError('invalid or missing locked file: ' + row['path'])
            actual = digest(path)
            ok = actual == row['sha256'] and path.stat().st_size == row['bytes']
            checks.append({'path': row['path'], 'actual_sha256': actual, 'pass': ok})
            if not ok:
                raise ValueError('locked source/input mismatch: ' + row['path'])
        atomic(out / 'IDENTITY_CHECK.json', {'lock_sha256': digest(lock_path), 'checks': checks, 'pass': True})
        if platform.python_implementation() != 'CPython' or sys.version_info[:2] != (3, 12):
            raise RuntimeError('host contract requires CPython3.12.x; select an available matching interpreter without changing science')
        atomic(out / 'HOST.json', host_inventory())
        atomic(out / 'ARITHMETIC_SMOKE.json', {'checks': arithmetic_smoke(package), 'scope': 'targeted host diagnostics; reviewed interval proof remains separately required'})
        baseline = json.loads((package / 'evidence/N512_P60.json').read_text())
        baseline_digest = numerical_digest(baseline)
        if baseline_digest != lock['baseline_numerical_sha256']:
            raise ValueError('baseline numerical projection mismatch')
        if not args.execute:
            report.update(status='VERIFY_ONLY_PASS', scientific_execution='NOT_RUN', new_result_accuracy='NOT_EVALUATED')
        else:
            env = os.environ.copy()
            for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
                env[key] = '1'
            command = [sys.executable, str(package / 'code/local_enclosure.py'), '--package', str(package),
                       '--subdivisions', '512', '--precision', '60', '--output', str(out / 'RESULTS.json')]
            report.update(status='RUNNING', command=command, timeout_seconds=args.timeout,
                          memory_limit_bytes=1073741824, new_host_scientific_runs=1)
            atomic(out / 'NCP_RESULT.json', report)
            def limits():
                resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
                resource.setrlimit(resource.RLIMIT_CPU, (180, 185))
            start = time.perf_counter()
            with (out / 'stdout.txt').open('x') as stdout, (out / 'stderr.txt').open('x') as stderr:
                try:
                    process = subprocess.run(command, stdout=stdout, stderr=stderr, env=env,
                                             timeout=args.timeout, check=False, preexec_fn=limits)
                    report['actual_exit'] = process.returncode
                except subprocess.TimeoutExpired:
                    report.update(status='TIMEOUT', actual_exit=None, failure_class='RUNTIME_RESOURCE')
                    raise RuntimeError('bounded scientific process timed out')
                finally:
                    stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
                    report['wall_seconds'] = time.perf_counter() - start
            if process.returncode != 0:
                raise RuntimeError('scientific process failed; inspect preserved stderr/checkpoint')
            fresh = json.loads((out / 'RESULTS.json').read_text())
            locked = {row['path']: row['sha256'] for row in lock['files']}
            as_run = fresh['identity']['source_sha256_before_run']
            required = ['code/local_enclosure.py', 'code/directed_interval.py',
                        'PLAN.json', 'inputs/SIX_CONTROLS.json']
            as_run_matches_lock = all(as_run.get(name) == locked[name] for name in required)
            if not as_run_matches_lock:
                raise RuntimeError('fresh producer/input identities differ from the validated execution lock')
            actual_digest = numerical_digest(fresh)
            parity = {'comparison': 'all deterministic controls, bounds, intervals, derivatives, saved comparisons and rounding counts',
                      'ignored': ['environment/path/start-finish/elapsed/RSS metadata'],
                      'expected_numerical_sha256': baseline_digest, 'actual_numerical_sha256': actual_digest,
                      'fresh_as_run_source_matches_execution_lock': as_run_matches_lock,
                      'fresh_output_compared': True, 'bitwise_numerical_json_parity': actual_digest == baseline_digest,
                      'fresh_reference_compatibility_failures': fresh['compatibility_failures']}
            atomic(out / 'PARITY.json', parity)
            if actual_digest != baseline_digest:
                report['failure_class'] = 'NUMERICAL_OR_RUNTIME_DIAGNOSE_BEFORE_CHANGE'
                raise RuntimeError('host numerical parity mismatch; no tolerance relaxation or baseline replacement')
            report.update(status='PASS_SCOPED_HOST_PARITY', scientific_execution='ACTUALLY_EXECUTED',
                          new_result_accuracy='SCOPED_PARITY_PASS', new_output_parity_checked=True,
                          peak_RSS_KiB=fresh['peak_RSS_KiB'])
    except Exception as error:
        report.setdefault('failure_class', 'RUNTIME_OR_IDENTITY_INTAKE')
        report.update(status='FAILED' if report['status'] != 'TIMEOUT' else 'TIMEOUT',
                      error_type=type(error).__name__, error=str(error))
        raise
    finally:
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        atomic(out / 'NCP_RESULT.json', report)
        print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
