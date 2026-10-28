"""Approved one-shot 36-test runner; authoring is not execution."""
import resource
import signal
import os
import sys


def self_cpu():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


class BudgetStop(Exception):
    pass


def stop(signum, frame):
    raise BudgetStop('wrapper CPU allowance reached')


signal.signal(signal.SIGPROF, stop)
signal.setitimer(signal.ITIMER_PROF, max(0.000001, 0.20 - self_cpu()))

import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/scratch/52cc495a5f0a/rei_finite_history_unit')
OUTPUT = BASE / 'execution/approved_first_run_20261027'
EXPECTED = {
    'cohort': {'cohort_bounds.py': 'd9d9a435d43fdffa099f0bcdd07890c835a1184d',
               'test_cohort_bounds.py': '0b7d410fa8cc3543adc5047954e16a9aec300d1d'},
    'affine': {'history_bounds.py': '9dac2505626386917d36b85037e3d0686d19d913',
               'test_history_bounds.py': '50e287438ccdc56a714158ceaa43d79430d6a020'},
}
ACTIVE = None
RESULT = {'status': 'NOT_RUN', 'source_head': 'd91de6299e614520949c5873a9378000ceb1f85c',
          'approval': 'User explicitly approved planning cap16, presentation46 and bounded0.80 CPU jobs.',
          'planning_prior': '15.077490885', 'presentation_prior': '44.990767494',
          'unmeasured_tool_cost': 'UNKNOWN_NOT_ZERO', 'jobs': [],
          'reservation': {'each_child': 0.25, 'wrapper': 0.20, 'tail': 0.10, 'total': 0.80}}


def verify(directory, expected):
    verified = {}
    for filename, wanted in expected.items():
        data = (directory / filename).read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        verified[filename] = actual
        if actual != wanted:
            raise ValueError('source blob mismatch: ' + filename)
    return verified


def run_job(name, directory, module, expected_count):
    global ACTIVE
    if self_cpu() >= 0.20 or self_cpu() + sum(item.get('cpu_total', 0) for item in RESULT['jobs']) >= 0.70:
        raise BudgetStop('refusing new child at wrapper or combined CPU threshold')
    record = {'name': name, 'cwd': str(directory), 'module': module,
              'expected_tests': expected_count, 'status': 'NOT_RUN',
              'source_blobs': verify(directory, EXPECTED[name]),
              'argv': [sys.executable, '-S', '-B', '-m', 'unittest', '-v', module]}
    RESULT['jobs'].append(record)
    stdout = os.open(str(OUTPUT / (name + '.stdout.txt')), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        stderr = os.open(str(OUTPUT / (name + '.stderr.txt')), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except BaseException:
        os.close(stdout)
        raise
    try:
        if self_cpu() >= 0.20 or self_cpu() + sum(item.get('cpu_total', 0) for item in RESULT['jobs']) >= 0.70:
            raise BudgetStop('refusing fork at wrapper or combined CPU threshold')
        pid = os.fork()
        if pid == 0:
            try:
                signal.signal(signal.SIGPROF, signal.SIG_DFL)
                remaining = 0.25 - self_cpu()
                if remaining <= 0:
                    os._exit(125)
                signal.setitimer(signal.ITIMER_PROF, remaining)
                os.dup2(stdout, 1)
                os.dup2(stderr, 2)
                os.close(stdout)
                os.close(stderr)
                os.chdir(directory)
                os.execv(sys.executable, record['argv'])
            except BaseException:
                os._exit(126)
        ACTIVE = pid
    finally:
        os.close(stdout)
        os.close(stderr)
    waited, status, usage = os.wait4(pid, 0)
    ACTIVE = None
    record.update({'wait_status': status, 'user_cpu': usage.ru_utime,
                   'system_cpu': usage.ru_stime,
                   'cpu_total': usage.ru_utime + usage.ru_stime,
                   'exit_code': os.waitstatus_to_exitcode(status)})
    text = (OUTPUT / (name + '.stderr.txt')).read_text(encoding='utf-8', errors='replace')
    summary = '\nRan ' + str(expected_count) + ' tests in '
    record['count_summary_verified'] = summary in text
    record['ok_summary_verified'] = text.rstrip().endswith('\nOK')
    record['status'] = ('PASS' if record['exit_code'] == 0
                        and record['cpu_total'] <= 0.25
                        and record['count_summary_verified']
                        and record['ok_summary_verified'] else 'FAIL')
    return record['status'] == 'PASS'


def main():
    global ACTIVE
    try:
        if len(sys.argv) != 2:
            raise ValueError('one absolute canonical affine implementation directory required')
        affine = Path(sys.argv[1])
        if not affine.is_absolute() or not affine.resolve().is_relative_to(BASE.resolve()):
            raise ValueError('affine source must be supplied within existing scratch unit')
        if (OUTPUT / 'result.json').exists():
            raise ValueError('one-shot result already exists; retry refused')
        RESULT['python'] = sys.version
        RESULT['interpreter'] = sys.executable
        RESULT['status'] = 'FAIL'
        if run_job('cohort', BASE / 'implementation', 'test_cohort_bounds', 20):
            if run_job('affine', affine, 'test_history_bounds', 16):
                RESULT['status'] = 'PASS'
    except BaseException as error:
        RESULT['status'] = 'BUDGET_STOP' if isinstance(error, BudgetStop) else 'FAIL'
        RESULT['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0.10)
        tail_start = self_cpu()
        if ACTIVE is not None:
            try:
                os.kill(ACTIVE, signal.SIGKILL)
            except ProcessLookupError:
                pass
            waited, status, usage = os.wait4(ACTIVE, 0)
            record = RESULT['jobs'][-1]
            record.update({'status': 'BUDGET_STOP', 'wait_status': status,
                           'exit_code': os.waitstatus_to_exitcode(status),
                           'user_cpu': usage.ru_utime, 'system_cpu': usage.ru_stime,
                           'cpu_total': usage.ru_utime + usage.ru_stime})
            ACTIVE = None
        RESULT['wrapper_cpu_before_tail'] = tail_start
        RESULT['tail_cpu_before_final_serialization'] = self_cpu() - tail_start
        RESULT['parent_cpu_before_final_serialization'] = self_cpu()
        RESULT['child_cpu_total'] = sum(item.get('cpu_total', 0) for item in RESULT['jobs'])
        RESULT['measured_total_before_final_serialization'] = self_cpu() + RESULT['child_cpu_total']
        RESULT['final_tail_note'] = 'Final serialization/process exit remains within reserved tail; external final process CPU must be preserved.'
        with (OUTPUT / 'result.json').open('x', encoding='utf-8') as stream:
            json.dump(RESULT, stream, indent=2)
            stream.write('\n')
        sys.stdout.write(json.dumps(RESULT) + '\n')
        sys.stdout.flush()
    return 0 if RESULT['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
