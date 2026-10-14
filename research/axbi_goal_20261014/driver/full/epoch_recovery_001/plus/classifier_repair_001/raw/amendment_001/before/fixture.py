#!/usr/bin/env python3
"""One fake-only replay of the preserved handoff and classifier boundaries."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import process_identity as identity
import repaired_adapter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
REFUSAL = HERE.parent / 'recovery_001/runtime_001/HANDOFF_REFUSAL.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refuse(label, call, expected, outcomes):
    try:
        call()
    except (RuntimeError, identity.IdentityAmbiguous) as error:
        if expected not in str(error):
            raise AssertionError((label, repr(error), expected)) from error
        outcomes.append({'case': label, 'result': 'EXPECTED_REFUSAL', 'error': str(error)})
        return
    raise AssertionError(label + ' unexpectedly accepted')


def group(pgid, argv, pid=None, start=700000.0):
    return [{'pid': pgid if pid is None else pid, 'state': 'S', 'argv': argv,
             'start_boot_s': start, 'rss_kib': 1}]


def main():
    binding = json.loads((HERE / 'BINDING.json').read_text())
    if binding['authority_sha256'] != sha(HERE / 'AUTHORITY.json') or \
       binding['refusal_sha256'] != sha(REFUSAL) or \
       binding['process_identity_sha256'] != sha(HERE / 'process_identity.py') or \
       binding['repaired_adapter_sha256'] != sha(HERE / 'repaired_adapter.py'):
        raise AssertionError('BINDING_CHANGED')
    saved = json.loads(REFUSAL.read_text())
    groups = {g['pgid']: g['members'] for g in saved['groups']}
    tracked = identity.TrackedLauncher(**binding['observed_owned_launcher'])
    adapter = repaired_adapter.install((tracked,))
    original_kill = os.killpg
    original_popen = subprocess.Popen
    calls = {'kill': 0, 'popen': 0}
    def fake_kill(*_args, **_kwargs):
        calls['kill'] += 1
        raise AssertionError('kill attempted in classifier fixture')
    def fake_popen(*_args, **_kwargs):
        calls['popen'] += 1
        raise AssertionError('Popen attempted in classifier fixture')
    os.killpg = fake_kill
    subprocess.Popen = fake_popen
    outcomes = []
    try:
        adapter.EPOCH.handoff(groups, allowed_group=tracked.pgid)
        assert adapter.PLUS.scientific_groups(groups) == {tracked.pgid}
        assert 1911669 not in adapter.PLUS.scientific_groups(groups)
        outcomes.append({'case': 'preserved_false_positive_replay', 'result': 'PASS',
                         'scientific_groups': [tracked.pgid]})

        with_operand = dict(groups)
        with_operand[900001] = group(900001, ['rg', '-n', 'needle', '/tmp/axbi_fake'])
        with_operand[900002] = group(900002, ['/bin/bash', '-c',
                                            'python3 post_plus_epoch_dispatch.py --observe; axbi_fake'])
        with_operand[900003] = group(900003, ['python3', '-c',
                                            'print("post_plus_dispatch.py --observe axbi_fake")'])
        adapter.EPOCH.handoff(with_operand, allowed_group=tracked.pgid)
        assert adapter.PLUS.scientific_groups(with_operand) == {tracked.pgid}
        outcomes.append({'case': 'operands_and_shell_text_ignored', 'result': 'PASS'})

        foreign = dict(groups)
        foreign[900004] = group(900004, ['/tmp/axbi_foreign'])
        refuse('foreign_native_solver', lambda: adapter.EPOCH.handoff(foreign, allowed_group=tracked.pgid),
               'LIVE_WORKERS_OR_CHILDREN_HOLD', outcomes)
        assert adapter.PLUS.scientific_groups(foreign) == {tracked.pgid, 900004}

        owner = dict(groups)
        owner[900005] = group(900005, ['python3', '-u', '/tmp/post_plus_epoch_dispatch.py', '--observe'])
        refuse('active_python_owner', lambda: adapter.EPOCH.handoff(owner, allowed_group=tracked.pgid),
               'OWNER_LIFECYCLE_HOLD', outcomes)
        assert identity.member_identity(owner[900005][0]) == ('owner', 'post_plus_epoch_dispatch.py', '--observe')

        wrapper = identity.TrackedLauncher(pid=900006, pgid=900006, start_boot_s=700000.0,
                                           native_basename='axbi_tracked')
        leader = group(900006, ['/usr/bin/time', '-v', '-o', '/tmp/time.log',
                                '/usr/bin/timeout', '--foreground', '10799s',
                                '/usr/bin/taskset', '-c', '0', '/usr/bin/prlimit',
                                '--as=2147483648', '--', '/tmp/axbi_tracked'])
        assert identity.scientific_groups({900006: leader}, (wrapper,)) == {900006}
        child = group(900006, ['/tmp/axbi_tracked'], pid=900007, start=700000.01)
        assert identity.scientific_groups({900006: leader + child}, (wrapper,)) == {900006}
        assert identity.scientific_groups({900006: leader}, (wrapper,)) == {900006}
        assert identity.scientific_groups({900006: child}, (wrapper,)) == {900006}
        assert identity.scientific_groups({}, (wrapper,)) == set()
        outcomes.append({'case': 'tracked_wrapper_child_transitions', 'result': 'PASS'})

        altered = copy.deepcopy(leader)
        altered[0]['start_boot_s'] += 1
        refuse('leader_pid_reuse', lambda: identity.project_groups({900006: altered}, (wrapper,), 900006),
               'TRACKED_LAUNCHER_START_IDENTITY_CHANGED', outcomes)
        refuse('unbound_allowed_group', lambda: identity.project_groups({900006: leader}, (), 900006),
               'ALLOWED_GROUP_START_IDENTITY_REQUIRED', outcomes)
        refuse('unknown_wrapper_option', lambda: identity.member_identity(group(900008, ['/usr/bin/time',
               '--unknown-option', '/tmp/axbi_foreign'])[0]), 'UNRECOGNIZED_WRAPPER_OPTION', outcomes)

        # Original duplicate reservation guard remains active, before any Popen.
        with tempfile.TemporaryDirectory() as temp:
            occupied = Path(temp) / 'runtime'
            occupied.mkdir()
            previous = (adapter.PLUS.validate, adapter.PLUS.fresh_handoff, adapter.PLUS.RUNTIME)
            try:
                adapter.PLUS.validate = lambda: ({'plus_continuation': {
                    'fresh_output': str(Path(temp) / 'output'),
                    'fresh_raw_output': str(Path(temp) / 'raw')}}, {})
                adapter.PLUS.fresh_handoff = lambda **_kwargs: ({}, {})
                adapter.PLUS.RUNTIME = occupied
                refuse('duplicate_reservation', adapter.PLUS.observe,
                       'PLUS_EXISTING_OUTPUT_OR_RESERVATION_NO_RETRY', outcomes)
            finally:
                adapter.PLUS.validate, adapter.PLUS.fresh_handoff, adapter.PLUS.RUNTIME = previous

        # Non-classification validation failures remain uncaught by the adapter.
        old_validate = adapter.EPOCH.validate
        old_groups = adapter.EPOCH.RECOVER.process_groups
        try:
            adapter.EPOCH.RECOVER.process_groups = lambda: groups
            for kind in ('NUMERICAL_FAILURE', 'RESOURCE_FAILURE', 'IMMUTABLE_IDENTITY_FAILURE'):
                def fail(*_args, **_kwargs):
                    raise RuntimeError(kind)
                adapter.EPOCH.validate = fail
                refuse(kind.lower(), lambda: adapter.fresh_handoff(allowed_group=tracked.pgid),
                       kind, outcomes)
        finally:
            adapter.EPOCH.validate = old_validate
            adapter.EPOCH.RECOVER.process_groups = old_groups
        assert calls == {'kill': 0, 'popen': 0}
    finally:
        os.killpg = original_kill
        subprocess.Popen = original_popen
    result = {'schema': 'rei.axbi.process_classifier_repair_fixture.v1',
              'status': 'PASS', 'cases': outcomes, 'fake_calls': calls,
              'scientific_starts': 0, 'refusal_sha256': sha(REFUSAL),
              'classifier_sha256': sha(HERE / 'process_identity.py'),
              'adapter_sha256': sha(HERE / 'repaired_adapter.py')}
    (HERE / 'raw/FIXTURE_RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'cases': len(outcomes), 'fake_calls': calls,
                      'scientific_starts': 0}))


if __name__ == '__main__':
    main()
