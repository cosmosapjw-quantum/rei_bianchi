#!/usr/bin/env python3
"""One manufactured, no-solver recovery gate fixture."""
import copy
import json
import os
import pathlib
import tempfile
from unittest import mock

import recover_plus as recovery


def expect_refusal(label, function, expected):
    try:
        function()
    except RuntimeError as error:
        if expected not in str(error):
            raise AssertionError((label, repr(error), expected)) from error
        return dict(case=label, result='EXPECTED_REFUSAL', error=str(error))
    raise AssertionError(label + ' unexpectedly accepted')


def main():
    authority, binding, _, plus_binding = recovery.exact_inputs()
    receipt = recovery.read(recovery.OLD_RUNTIME)
    start = recovery.read(recovery.OLD_START)
    argv = plus_binding['driver_argv']
    recovery.validate_old_reservation(receipt, start, authority, argv)
    results = [dict(case='exact_pre_Popen_reservation', result='ACCEPTED_FOR_PREPARATION')]

    acknowledged = copy.deepcopy(receipt)
    acknowledged['observed_process_pid'] = 12345
    results.append(expect_refusal('acknowledged_process', lambda: recovery.validate_old_reservation(acknowledged, start, authority, argv), 'ACKNOWLEDGEMENT_AMBIGUOUS'))
    ambiguous = copy.deepcopy(receipt)
    ambiguous['polls'] = 1
    results.append(expect_refusal('ambiguous_start', lambda: recovery.validate_old_reservation(ambiguous, start, authority, argv), 'ACKNOWLEDGEMENT_AMBIGUOUS'))
    changed = copy.deepcopy(start)
    changed['binding_sha256'] = '0' * 64
    results.append(expect_refusal('changed_binding', lambda: recovery.validate_old_reservation(receipt, changed, authority, argv), 'BINDING_CHANGED'))
    changed_argv = copy.deepcopy(receipt)
    changed_argv['argv'][-1] = 'OTHER'
    results.append(expect_refusal('changed_solver_argv', lambda: recovery.validate_old_reservation(changed_argv, start, authority, argv), 'BINDING_CHANGED'))
    group = {987654: [dict(pid=987655, argv=['/tmp/axbi_fixture_solver'], start_boot_s=12.5, rss_kib=1)]}
    results.append(expect_refusal('live_group', lambda: recovery.EPOCH.handoff(group), 'LIVE_WORKERS_OR_CHILDREN_HOLD'))
    with tempfile.TemporaryDirectory() as temp:
        occupied = pathlib.Path(temp) / 'science_output'
        occupied.mkdir()
        with mock.patch.object(recovery, 'OUTPUT', occupied):
            results.append(expect_refusal('existing_output', recovery.exact_inputs, 'SCIENCE_OUTPUT_ALREADY_EXISTS'))
        reserved = pathlib.Path(temp) / 'runtime_001'
        reserved.mkdir()
        with mock.patch.object(recovery, 'RUNTIME', reserved), mock.patch.object(recovery, 'release_gate', return_value={}):
            results.append(expect_refusal('repeated_reservation', recovery.configure, 'RECOVERY_ALREADY_RESERVED_NO_RETRY'))
    result = dict(schema='rei.axbi.plus_prelaunch_recovery_fixture.v1', status='PASS',
                  cases=results, fake_popen_calls=0, scientific_starts=0,
                  authority_sha256=recovery.digest(recovery.AUTHORITY),
                  binding_sha256=recovery.digest(recovery.BINDING))
    path = recovery.HERE / 'FIXTURE_RESULT.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status='PASS', cases=len(results), fake_popen_calls=0, scientific_starts=0)))


if __name__ == '__main__':
    main()
