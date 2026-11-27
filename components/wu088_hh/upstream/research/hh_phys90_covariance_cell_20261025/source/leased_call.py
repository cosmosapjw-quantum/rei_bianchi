#!/usr/bin/env python3
"""PHYS90 one-child wrapper: original cooperative gate, fresh memory, fixed CPUs.

No scientific code is imported by this wrapper. The pinned gate module defines
its old runner but only original resource/lease APIs are called. No peer is killed.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import resource
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parents[1]
GATE_SHA = '76ff57ba687fd9830b84c3fcff69eb8ed0e9f6ceab4551e61c67c84d3ea65124'
CONTRACT_SHA = '45d7b94544cf801619aa723c79be35c05e3ca2b023e2e94e8985f4c20758a20c'
SCIENTIFIC_CPU, COORDINATOR_CPU = 0, 8
CAPS = {'primary': (20, 45), 'reference': (20, 45)}
LEASE_DIRECTORY = '/tmp/rei-bianchi-cooperative-leases'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def raw_memory_before_launch(gate):
    """Read actual available memory and every original gate cgroup ancestor."""
    info = {k: int(v.split()[0])*1024 for k, v in
            (line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())}
    available = info['MemAvailable']; capacity = min(info['MemTotal'], 8*1024**3)
    records = []
    for path in gate._cgroups():
        try:
            limit_text = (path/'memory.max').read_text().strip()
            used = int((path/'memory.current').read_text())
            limit = None if limit_text == 'max' else int(limit_text)
            records.append({'path': str(path), 'memory_max_bytes': limit, 'memory_current_bytes': used})
            if limit is not None:
                available = min(available, max(0, limit-used)); capacity = min(capacity, limit)
        except (OSError, ValueError):
            records.append({'path': str(path), 'status': 'UNREADABLE_OR_INVALID; original gate semantics retained'})
    required = 2*1024**3
    return {'observed_utc': now(), 'available_bytes': available, 'capacity_bytes': capacity,
            'required_reserve_plus_job_bytes': required, 'reserve_GiB': 1.5, 'job_GiB': 0.5,
            'cgroups': records, 'memory_admissible': available >= required and capacity >= required}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kind', choices=tuple(CAPS), required=True)
    p.add_argument('--label', required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--admission-receipt', type=Path, help='Optional distinct create-only actual prelaunch admission JSON')
    p.add_argument('command', nargs=argparse.REMAINDER)
    args = p.parse_args()
    command = args.command[1:] if args.command and args.command[0] == '--' else args.command
    if not command:
        raise ValueError('COMMAND_REQUIRED')
    if args.receipt.exists():
        raise FileExistsError('CREATE_ONLY_ATTEMPT_RECEIPT_EXISTS')
    if args.admission_receipt is not None:
        if args.admission_receipt.exists() or args.admission_receipt.resolve() == args.receipt.resolve():
            raise FileExistsError('DISTINCT_CREATE_ONLY_ADMISSION_RECEIPT_REQUIRED')
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    cpu, wall = CAPS[args.kind]
    rec = {'schema': 'PHYS90_BOUNDED_LEASED_CHILD_ATTEMPT_V1', 'kind': args.kind, 'label': args.label,
           'command': command, 'started_utc': now(), 'cpu_limit_s': cpu, 'wall_limit_s': wall,
           'threads': 1, 'workers': 1, 'reserve_GiB': 1.5, 'job_GiB': 0.5,
           'scientific_CPU': SCIENTIFIC_CPU, 'coordinator_CPU': COORDINATOR_CPU,
           'gate_source_sha256': GATE_SHA, 'child_invocations': 0, 'automatic_retries': 0,
           'old_PHYS78_87_science_calls': 0, 'other_processes_terminated': 0,
           'cache_manipulation': False, 'lease': None,
           'HH_R10': 'OFF', 'production_admission': 'NOT_ISSUED'}
    gate = None; lease = None; original_affinity = None
    wrapper_start = time.monotonic(); self_usage_start = resource.getrusage(resource.RUSAGE_SELF)
    child_usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    exit_code = 1
    try:
        if hashlib.sha256((UNIT/'CONTRACT.json').read_bytes()).hexdigest() != CONTRACT_SHA:
            raise ValueError('FROZEN_CONTRACT_REVISION1_MISMATCH')
        source = UNIT.parent/'hh_phys88_atomic_bare_remap_20261024/source/vendor/phys78_run_pilot.py'
        if hashlib.sha256(source.read_bytes()).hexdigest() != GATE_SHA:
            raise ValueError('ORIGINAL_FULL_LEASE_SOURCE_SHA_MISMATCH')
        if not hasattr(os, 'sched_getaffinity') or not hasattr(os, 'sched_setaffinity'):
            raise RuntimeError('FROZEN_CPU_AFFINITY_API_UNAVAILABLE')
        original_affinity = set(os.sched_getaffinity(0))
        rec['original_allowed_affinity'] = sorted(original_affinity)
        if not {SCIENTIFIC_CPU, COORDINATOR_CPU} <= original_affinity:
            raise RuntimeError('FROZEN_CPU0_CPU8_MAPPING_UNAVAILABLE; NO_CPU55_FALLBACK')
        # Importing this exact original gate only sets thread env and defines its
        # routines. It never invokes the historical scientific runner here.
        spec = importlib.util.spec_from_file_location('_phys90_original_lease_only', source)
        gate = importlib.util.module_from_spec(spec); sys.modules[spec.name] = gate
        spec.loader.exec_module(gate)
        pool = gate.LeasePool(LEASE_DIRECTORY, site='local')
        with gate._lease_lock(LEASE_DIRECTORY):
            peers_before = gate._live_leases(LEASE_DIRECTORY, pool.boot)
        rec['live_leases_before_acquire'] = peers_before
        if peers_before:
            rec['status'] = 'WAITING_OTHER_LIVE_LEASE_CPU_MAPPING_NOT_GRANTED'; exit_code = 75
        else:
            lease, observation = pool.acquire('PHYS90:'+args.kind+':'+args.label)
            rec['lease'] = lease; rec['observation'] = observation
            if lease is None:
                rec['status'] = 'WAITING_FOR_PINNED_SHARED_RESOURCE_LEASE'; exit_code = 75
            else:
                with gate._lease_lock(LEASE_DIRECTORY):
                    live_after = gate._live_leases(LEASE_DIRECTORY, pool.boot)
                rec['live_leases_after_acquire'] = live_after
                peers = [r for r in live_after if r.get('owner') != lease['owner']]
                own = [r for r in live_after if r.get('owner') == lease['owner']]
                if peers or len(own) != 1:
                    rec['status'] = 'WAITING_OBSERVED_LEASE_CONFLICT_NO_CHILD'; exit_code = 75
                else:
                    memory = raw_memory_before_launch(gate)
                    rec['fresh_memory_before_launch'] = memory
                    if not memory['memory_admissible']:
                        rec['status'] = 'WAITING_FRESH_MEMORY_RESERVE_PLUS_JOB'; exit_code = 75
                    else:
                        env = os.environ.copy()
                        for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                                    'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
                            env[key] = '1'
                        env['PYTHONDONTWRITEBYTECODE'] = '1'
                        def child_limits():
                            resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
                            os.sched_setaffinity(0, {SCIENTIFIC_CPU})
                        os.sched_setaffinity(0, {COORDINATOR_CPU})
                        rec['actual_coordinator_affinity'] = sorted(os.sched_getaffinity(0))
                        if args.admission_receipt is not None:
                            admission = {'schema': 'PHYS90_ACTUAL_PRELAUNCH_RESOURCE_LEASE_V1',
                                         'status': 'ADMITTED_FRESH_PINNED_RESOURCE_LEASE',
                                         'observed_utc': now(), 'kind': args.kind, 'label': args.label,
                                         'command': command, 'gate_source_sha256': GATE_SHA,
                                         'lease': lease, 'actual_post_acquire_live_leases': live_after,
                                         'other_live_leases_observed': 0,
                                         'fresh_memory_before_launch': memory,
                                         'original_gate_observation': observation,
                                         'cpu_limit_s': cpu, 'wall_limit_s': wall,
                                         'threads': 1, 'workers': 1,
                                         'actual_coordinator_affinity': rec['actual_coordinator_affinity'],
                                         'scientific_CPU_to_enforce_in_child_preexec': SCIENTIFIC_CPU,
                                         'child_started': False,
                                         'scope': 'Actual fresh prelaunch observation; child caps/affinity enforced by wrapper preexec, not yet a child outcome'}
                            args.admission_receipt.parent.mkdir(parents=True, exist_ok=True)
                            raw_admission = (json.dumps(admission, indent=2, allow_nan=False)+'\n').encode()
                            with args.admission_receipt.open('xb') as f:
                                f.write(raw_admission)
                            rec['prelaunch_admission_receipt'] = {'path': str(args.admission_receipt.resolve()),
                                'bytes': len(raw_admission), 'sha256': hashlib.sha256(raw_admission).hexdigest()}
                        rec['child_launch_utc'] = now(); launch_start = time.monotonic()
                        rec['child_invocations'] = 1
                        try:
                            result = subprocess.run(command, env=env, capture_output=True, text=True,
                                                    timeout=wall, preexec_fn=child_limits)
                            rec.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr,
                                       status='CHILD_COMPLETED' if result.returncode == 0 else 'CHILD_FAILED_PRESERVED')
                            exit_code = result.returncode
                        except subprocess.TimeoutExpired as exc:
                            def text(value):
                                return value.decode(errors='replace') if isinstance(value, bytes) else value or ''
                            rec.update(status='CHILD_WALL_LIMIT_EXCEEDED_PRESERVED', exit_code=124,
                                       stdout=text(exc.stdout), stderr=text(exc.stderr))
                            exit_code = 124
                        rec['launch_inclusive_child_wall_s'] = time.monotonic()-launch_start
                        rec['child_return_utc'] = now()
    except BaseException as exc:
        rec.update(status='WRAPPER_FAILURE_PRESERVED', exception=type(exc).__name__,
                   reason=str(exc), traceback=traceback.format_exc(), exit_code=1)
        exit_code = 1
    finally:
        if original_affinity is not None:
            try:
                os.sched_setaffinity(0, original_affinity)
                rec['coordinator_affinity_restored'] = True
            except OSError as exc:
                rec['coordinator_affinity_restore_error'] = str(exc)
        if lease is not None and gate is not None:
            try:
                gate.release_lease(lease); rec['own_lease_released'] = True
            except BaseException as exc:
                rec['own_lease_release_error'] = {'exception': type(exc).__name__, 'reason': str(exc)}
                exit_code = 1
        child_usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        self_usage = resource.getrusage(resource.RUSAGE_SELF)
        rec.update(completed_utc=now(), wrapper_wall_s=time.monotonic()-wrapper_start,
                   child_user_cpu_s=child_usage.ru_utime-child_usage_start.ru_utime,
                   child_system_cpu_s=child_usage.ru_stime-child_usage_start.ru_stime,
                   child_cpu_s=child_usage.ru_utime+child_usage.ru_stime-child_usage_start.ru_utime-child_usage_start.ru_stime,
                   coordinator_cpu_s=self_usage.ru_utime+self_usage.ru_stime-self_usage_start.ru_utime-self_usage_start.ru_stime,
                   wrapper_exit_code=exit_code)
        with args.receipt.open('x') as f:
            json.dump(rec, f, indent=2, allow_nan=False); f.write('\n')
    print(json.dumps({'status': rec['status'], 'receipt': str(args.receipt),
                      'child_invocations': rec['child_invocations'], 'exit_code': exit_code,
                      'scientific_CPU': SCIENTIFIC_CPU, 'coordinator_CPU': COORDINATOR_CPU}))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
