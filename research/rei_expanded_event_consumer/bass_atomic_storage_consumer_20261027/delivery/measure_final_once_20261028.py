"""Prepared only: launch one approved worker, measure its complete CPU via wait4.

No retry or packaging occurs without all explicit approval guards. Those guards
do not substitute for the owner's newly explicit quantified authorization.
"""
import argparse
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

PRIOR_LOWER = 48.263016494
CACHE = Path('/workspace/scratch/52cc495a5f0a/rei_bass_storage_unit')
WORKER = Path(__file__).resolve().with_name('package_final_reuse_once_20261028.py')
SUPERVISOR_ALLOWANCE = 2.0
CPU_GUARD = {'expired': False, 'first_signal': None}
CLEANUP_WALL_BOUND = 1.0


def cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def cleanup_expired(signum, frame):
    # A fixed wall bound prevents an indefinite signal-ignore/cleanup path.
    os._exit(124)


def stop(signum, frame):
    if CPU_GUARD['expired']:
        # Simultaneous PROF/XCPU must not interrupt kill/reap or the receipt.
        # This state is bounded by the one-shot wall alarm below.
        return
    CPU_GUARD['expired'] = True
    CPU_GUARD['first_signal'] = signum
    signal.setitimer(signal.ITIMER_REAL, CLEANUP_WALL_BOUND)
    raise TimeoutError('supervisor CPU allowance exhausted')


def destination(path, root):
    if (not path.is_absolute() or path.resolve().parent != root
            or path.exists() or path.is_symlink()):
        raise ValueError('new absolute direct-child output path required: ' + str(path))
    return path


def main(argv=None):
    wall_start = time.monotonic()
    # Fixed supervisor-only timer; blocked wait4 consumes no supervisor CPU.
    signal.signal(signal.SIGPROF, stop)
    signal.signal(signal.SIGXCPU, stop)
    signal.signal(signal.SIGALRM, cleanup_expired)
    remaining = SUPERVISOR_ALLOWANCE - cpu()
    if remaining > 0:
        signal.setitimer(signal.ITIMER_PROF, remaining)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--explicit-approved-launch', action='store_true', required=True)
    p.add_argument('--approved-absolute-cap', type=float, required=True)
    p.add_argument('--approved-reservation', type=float, required=True)
    p.add_argument('--output-root', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('archive', type=Path)
    p.add_argument('worker_result', type=Path)
    p.add_argument('supervisor_result', type=Path)
    a = p.parse_args(sys.argv[1:] if argv is None else argv)
    if (a.approved_absolute_cap != 60 or a.approved_reservation != 8
            or PRIOR_LOWER + a.approved_reservation > a.approved_absolute_cap):
        p.error('only separately approved absolute cap 60 / reservation 8 accepted')
    receipt = {'status': 'FAIL', 'claim_admission': 'NOT_RUN',
               'historical_cpu_lower_bound': PRIOR_LOWER,
               'historical_unmeasured_cpu': 'UNKNOWN_NOT_ZERO',
               'approved_cap_argument': 60, 'reservation_argument': 8,
               'approval_flag_is_authorization': False,
               'worker_launches': 0, 'automatic_retries': 0,
               'supervisor_exit_tail': 'UNKNOWN_NOT_ZERO',
               'complete_global_cpu_measured': False,
               'guard_limitations': 'CPU timers/RLIMIT are not an exact subsecond global hard bound'}
    child = None
    waited = False
    result_stream = None
    try:
        root = a.output_root.resolve()
        if (not a.output_root.is_absolute() or not root.is_dir()
                or root.is_relative_to(CACHE.resolve())):
            raise ValueError('existing writable output root outside cached source required')
        logs = (a.supervisor_result.with_name(a.supervisor_result.name + '.stdout.log'),
                a.supervisor_result.with_name(a.supervisor_result.name + '.stderr.log'))
        paths = [destination(x, root) for x in
                 (a.archive, a.worker_result, a.supervisor_result, *logs)]
        if len({x.resolve() for x in paths}) != len(paths):
            raise ValueError('all output paths must differ')
        result_stream = a.supervisor_result.open('x', encoding='utf-8')
        if remaining <= 0 or cpu() >= SUPERVISOR_ALLOWANCE:
            raise TimeoutError('supervisor entered after CPU deadline')
        # Handled soft CPU limit and CPU timer guard supervisor SELF usage.
        # Their one-shot expiry permits only nonrenewed, wall-bounded cleanup.
        # Retain the hard ceiling so the worker can set its own 6-second limit.
        old_soft, old_hard = resource.getrlimit(resource.RLIMIT_CPU)
        if old_hard != resource.RLIM_INFINITY and old_hard < 6:
            raise ValueError('inherited hard CPU limit cannot accommodate worker 6')
        resource.setrlimit(resource.RLIMIT_CPU, (2, old_hard))
        command = [sys.executable, str(WORKER), '--explicit-approved-launch',
                   '--approved-absolute-cap', '60', '--approved-reservation', '8',
                   '--output-root', str(root), '--manifest', str(a.manifest),
                   str(a.archive), str(a.worker_result)]
        with logs[0].open('xb') as stdout, logs[1].open('xb') as stderr:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            receipt['worker_launches'] = 1
            _, status, child_usage = os.wait4(child.pid, 0)
            waited = True
            child.returncode = os.waitstatus_to_exitcode(status)
        worker_cpu = child_usage.ru_utime + child_usage.ru_stime
        receipt.update({'worker_exitcode': child.returncode,
                        'worker_cpu': {'kind': 'ACTUAL_MEASURED',
                                       'user': child_usage.ru_utime,
                                       'system': child_usage.ru_stime,
                                       'total': worker_cpu},
                        'worker_accounted_cpu': worker_cpu,
                        'worker_full_exit_cpu_measured': True,
                        'stdout_log': str(logs[0]), 'stderr_log': str(logs[1])})
        internal = 0.0
        if a.worker_result.exists():
            with a.worker_result.open('r', encoding='utf-8') as stream:
                worker = json.load(stream)
            raw_internal = worker.get('process_cpu_before_final_serialization', 0.0)
            receipt['worker_internal_cpu_raw'] = raw_internal
            internal = float(raw_internal)
            if not math.isfinite(internal) or internal < 0:
                raise ValueError('worker internal CPU snapshot must be finite and nonnegative')
            # Preserve every valid larger observation before discrepancy failure.
            receipt['worker_internal_lower_bound'] = internal
            receipt['worker_accounted_cpu'] = max(worker_cpu, internal)
            if not internal <= worker_cpu + 0.02:
                raise ValueError('worker internal CPU snapshot inconsistent with wait4')
            receipt['worker_reported_status'] = worker.get('status')
        else:
            receipt['worker_reported_status'] = 'MISSING'
        receipt['worker_internal_lower_bound'] = internal
        receipt['worker_accounted_cpu'] = max(worker_cpu, internal)
        receipt['status'] = ('PASS' if child.returncode == 0
                             and receipt['worker_reported_status'] == 'PASS'
                             and worker_cpu <= 6 else 'FAIL')
    except BaseException as error:
        receipt['status'] = 'FAIL'
        receipt['error'] = type(error).__name__ + ': ' + str(error)
        if child is not None and not waited:
            # Exactly one launch, no retry. Reap even on supervisor interruption.
            try:
                os.kill(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, status, child_usage = os.wait4(child.pid, 0)
            child.returncode = os.waitstatus_to_exitcode(status)
            actual = child_usage.ru_utime + child_usage.ru_stime
            receipt.update({'worker_exitcode': child.returncode,
                            'worker_full_exit_cpu_measured': True,
                            'worker_cpu': {'kind': 'ACTUAL_MEASURED',
                                           'user': child_usage.ru_utime,
                                           'system': child_usage.ru_stime,
                                           'total': actual},
                            'worker_accounted_cpu': actual})
    try:
        prefix = cpu()
        tail_reserve = max(0.0, SUPERVISOR_ALLOWANCE - prefix)
        receipt.update({'supervisor_prefix_cpu': {'kind': 'ACTUAL_MEASURED_PARTIAL', 'total': prefix},
                        'supervisor_remaining_tail': {'kind': 'RESERVED', 'cpu': tail_reserve},
                        'supervisor_total_planned_allowance': SUPERVISOR_ALLOWANCE,
                        'supervisor_cpu_guard_triggered': CPU_GUARD['expired'],
                        'supervisor_cpu_guard_first_signal': CPU_GUARD['first_signal'],
                        'post_guard_cleanup_wall_bound': CLEANUP_WALL_BOUND,
                        'post_guard_cleanup_cpu_exactly_bounded': False,
                        'wall_before_final_serialization': time.monotonic() - wall_start})
        if 'worker_accounted_cpu' in receipt:
            receipt['known_cpu_lower_bound_after_measured_prefix'] = (
                PRIOR_LOWER + receipt['worker_accounted_cpu'] + prefix)
            receipt['known_lower_plus_remaining_reserve'] = (
                PRIOR_LOWER + receipt['worker_accounted_cpu'] + prefix + tail_reserve)
        if prefix >= SUPERVISOR_ALLOWANCE:
            receipt['status'] = 'FAIL'
            receipt['supervisor_budget_exhausted'] = True
        receipt['accounting_note'] = ('Historical unknown and final supervisor tail remain unknown; '
                                      'reserve is not actual CPU. External measurement must include '
                                      'supervisor serialization/exit. No cumulative ledger reset.')
        serialized = json.dumps(receipt, ensure_ascii=False, indent=2) + '\n'
        if result_stream is not None:
            result_stream.write(serialized)
            result_stream.close()
        sys.stdout.write(serialized)
        sys.stdout.flush()
    except BaseException as error:
        try:
            sys.stderr.write('FAIL supervisor receipt: ' + type(error).__name__ + ': ' + str(error) + '\n')
        except BaseException:
            pass
        return 1
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
