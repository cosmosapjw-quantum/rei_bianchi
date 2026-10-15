#!/usr/bin/env python3
"""One reviewed recovery of the charged PLUS pre-Popen reservation.

The historical PLUS observer supplies the solver argv, external caps, streaming
monitor and terminal classification. This wrapper changes only its metadata and
raw-log locations after validating the frozen failed reservation.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[6]
DRIVER = ROOT / 'research/axbi_goal_20261014/driver/full'
AUTHORITY = HERE / 'AUTHORITY.json'
BINDING = HERE / 'RECOVERY_BINDING.json'
RELEASE = HERE / 'RELEASE.json'
RUNTIME = HERE / 'runtime_001'
RAW = HERE / 'raw'
OLD_RUNTIME = DRIVER / 'epoch_recovery_001/plus/runtime_001/POST_PLUS_RECEIPT.json'
OLD_START = ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_PLUS_continuation_001_raw/POST_PLUS_SEGMENT_START.json'
OLD_PROCESS = OLD_START.parent / 'POST_PLUS_SEGMENT_PROCESS.json'
OUTPUT = ROOT / 'research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_PLUS_continuation_001'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ADAPTER = load(DRIVER / 'post_plus_epoch_dispatch.py', 'recovery_plus_adapter')
PLUS = ADAPTER.PLUS
EPOCH = ADAPTER.EPOCH
ORIGINAL_SAVE = PLUS.save


def validate_old_reservation(receipt, start, authority, solver_argv):
    """Only the exact consumed, unacknowledged pre-Popen attempt is eligible."""
    if receipt.get('status') != 'STOPPED_FOR_CLASSIFICATION' or receipt.get('error') != "RuntimeError('LIVE_WORKERS_OR_CHILDREN_HOLD')":
        raise RuntimeError('OLD_RESERVATION_NOT_EXACT_PRE_POPEN_FAILURE')
    if receipt.get('launch_attempt_reserved') is not True or receipt.get('automatic_retry') is not False:
        raise RuntimeError('OLD_RESERVATION_DISPOSITION_CHANGED')
    if receipt.get('observed_process_pid') is not None or receipt.get('pgid') is not None or receipt.get('polls') != 0:
        raise RuntimeError('OLD_SOLVER_ACKNOWLEDGEMENT_AMBIGUOUS')
    if [receipt.get(k) for k in ('PLUS_attempted_starts', 'total_full_starts', 'all_history_starts')] != [1, 7, 10]:
        raise RuntimeError('OLD_RESERVATION_ACCOUNTING_CHANGED')
    for key in ('argv', 'binding_sha256', 'dispatch_binding_sha256', 'old_receipt_sha256'):
        if start.get(key) != receipt.get(key):
            raise RuntimeError('OLD_START_RECEIPT_BINDING_CHANGED:' + key)
    if start.get('status') != 'RESERVED_BEFORE_SOLVER_LAUNCH' or start.get('observed_process_pid') is not None:
        raise RuntimeError('OLD_START_ACKNOWLEDGEMENT_AMBIGUOUS')
    if receipt.get('argv')[-len(solver_argv):] != solver_argv:
        raise RuntimeError('OLD_SOLVER_ARGV_CHANGED')
    if authority['accounting']['prior_PLUS_launch_attempts'] != 1 or authority['accounting']['prior_PLUS_observed_solver_starts'] != 0:
        raise RuntimeError('AUTHORITY_ACCOUNTING_CHANGED')


def exact_inputs():
    authority = read(AUTHORITY)
    binding = read(BINDING)
    if digest(AUTHORITY) != binding['authority_sha256']:
        raise RuntimeError('RECOVERY_AUTHORITY_CHANGED')
    if binding['old_receipt_sha256'] != digest(OLD_RUNTIME) or binding['old_start_sha256'] != digest(OLD_START):
        raise RuntimeError('FROZEN_FAILED_RESERVATION_CHANGED')
    for name, expected in authority['preserved_failure_sha256'].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('PRESERVED_FIRST_FAILURE_CHANGED:' + name)
    for name, expected in binding['immutable_sha256'].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError('IMMUTABLE_INPUT_CHANGED:' + name)
    decision, plus_binding = ADAPTER.validate()
    if plus_binding['driver_argv'] != binding['solver_argv']:
        raise RuntimeError('RECOVERY_SOLVER_ARGV_CHANGED')
    if decision['plus_continuation']['fresh_output'] != binding['science_output']:
        raise RuntimeError('RECOVERY_OUTPUT_CHANGED')
    validate_old_reservation(read(OLD_RUNTIME), read(OLD_START), authority, plus_binding['driver_argv'])
    if OLD_PROCESS.exists():
        raise RuntimeError('OLD_SOLVER_PROCESS_ACKNOWLEDGEMENT_EXISTS')
    if OUTPUT.exists():
        raise RuntimeError('SCIENCE_OUTPUT_ALREADY_EXISTS')
    return authority, binding, decision, plus_binding


def release_gate(binding):
    """Controller's post-review local/remote/pending-slot release is required."""
    release = read(RELEASE)
    if release.get('decision') != 'AUTHORIZE_ONE_RECOVERY_START':
        raise RuntimeError('INDEPENDENT_RELEASE_REQUIRED')
    if release.get('launcher_sha256') != digest(__file__) or release.get('binding_sha256') != digest(BINDING):
        raise RuntimeError('REVIEWED_LAUNCHER_BINDING_CHANGED')
    if release.get('old_receipt_sha256') != binding['old_receipt_sha256']:
        raise RuntimeError('REVIEWED_OLD_RESERVATION_CHANGED')
    if release.get('independent_review') != 'PASS_SCOPED_PRELAUNCH_RECOVERY' or not release.get('independent_review_sha256'):
        raise RuntimeError('FRESH_INDEPENDENT_REVIEW_REQUIRED')
    review_path = HERE / 'INDEPENDENT_REVIEW.json'
    if digest(review_path) != release['independent_review_sha256']:
        raise RuntimeError('INDEPENDENT_REVIEW_CHANGED')
    review = read(review_path)
    if review.get('decision') != 'PASS_SCOPED_PRELAUNCH_RECOVERY':
        raise RuntimeError('INDEPENDENT_REVIEW_NOT_PASS')
    if release.get('local_remote_pending_science_slots_at_most_two') is not True or release.get('remote_checked') is not True or release.get('pending_checked') is not True or release.get('no_other_PLUS_owner') is not True:
        raise RuntimeError('CONTROLLER_SLOT_RECONCILIATION_REQUIRED')
    return release


def inventory(groups, reason):
    """Preserve identities behind a refusal without changing the handoff rule."""
    return dict(reason=reason, groups=[dict(pgid=pgid, members=[dict(pid=m['pid'], pgid=pgid,
                 start_boot_s=m.get('start_boot_s'), argv=m['argv']) for m in members])
                 for pgid, members in sorted(groups.items())])


def handoff(allowed_group=None, allowed_parent=None):
    groups = EPOCH.RECOVER.process_groups()
    original_process_groups = EPOCH.RECOVER.process_groups
    try:
        EPOCH.RECOVER.process_groups = lambda: groups
        return ADAPTER.fresh_handoff(allowed_group=allowed_group, allowed_parent=allowed_parent)
    except Exception as error:
        refusal = RUNTIME / 'HANDOFF_REFUSAL.json' if RUNTIME.exists() else HERE / 'HANDOFF_REFUSAL.json'
        PLUS.save(refusal, inventory(groups, repr(error)))
        raise
    finally:
        EPOCH.RECOVER.process_groups = original_process_groups


def charged_save(path, value):
    if path.name in {'POST_PLUS_RECEIPT.json', 'POST_PLUS_SEGMENT_START.json', 'POST_PLUS_SEGMENT_RECEIPT.json'}:
        value = dict(value)
        value['PLUS_attempted_starts'] = 2
        value['PLUS_observed_solver_starts'] = 1 if value.get('observed_process_pid') is not None else 0
        value['total_full_starts'] = 7
        value['all_history_starts'] = 10
        value['campaign_observed_full_starts'] = 7 if value.get('observed_process_pid') is not None else 6
        value['launch_attempt_reserved'] = True
        value['automatic_retry'] = False
        value['prior_PLUS_launch_attempts'] = 1
        value['prior_PLUS_observed_solver_starts'] = 0
        value['old_failed_receipt_sha256'] = digest(OLD_RUNTIME)
        value['recovery_binding_sha256'] = digest(BINDING)
        value['start_ceilings'] = dict(value.get('start_ceilings', {}), PLUS=2, full=7, all_history=10)
    ORIGINAL_SAVE(path, value)


def configure():
    authority, binding, decision, _ = exact_inputs()
    release_gate(binding)
    if RUNTIME.exists() or RAW.exists():
        raise RuntimeError('RECOVERY_ALREADY_RESERVED_NO_RETRY')
    # Original reviewed validator still runs on every historical observer call.
    original_validate = ADAPTER.validate
    def validation():
        original_validate()
        exact_inputs()
        release_gate(binding)
        updated = copy.deepcopy(decision)
        updated['plus_continuation']['fresh_raw_output'] = str(RAW.relative_to(ROOT))
        return updated, read(PLUS.PLUS_BINDING)
    PLUS.validate = validation
    PLUS.fresh_handoff = handoff
    PLUS.save = charged_save
    # The old monitor's 1 MiB metadata cap must exclude the fresh science logs.
    PLUS.OWN = RUNTIME
    PLUS.RUNTIME = RUNTIME
    return authority, binding


def observe():
    configure()
    return PLUS.observe()


def detached():
    configure()
    handoff()
    with (HERE / 'observer.stdout').open('xb') as out, (HERE / 'observer.stderr').open('xb') as err:
        proc = subprocess.Popen([sys.executable, str(__file__), '--observe'], cwd=ROOT,
                                stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                start_new_session=True, close_fds=True)
    print(proc.pid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--start-detached', action='store_true')
    actions.add_argument('--observe', action='store_true')
    args = parser.parse_args()
    if args.start_detached:
        detached()
    else:
        raise SystemExit(observe())
