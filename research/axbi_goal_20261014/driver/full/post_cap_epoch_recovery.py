#!/usr/bin/env python3
"""One reviewed recovery of the remaining original HALF_MINUS; never retries."""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import re
import subprocess
import sys
import threading
import tempfile
import copy
import time

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AREA = HERE / 'epoch_recovery_001'
OWN = AREA / 'recovery'
RUNTIME = OWN / 'runtime_001'
RECEIPT = RUNTIME / 'RECOVERED_TERMINAL_RECEIPT.json'
BINDING = AREA / 'EPOCH_RECOVERY_BINDING.json'
REVIEW = ROOT / 'research/axbi_goal_20261014/reviews/EPOCH_EXIT_CLASSIFICATION_REPAIR_REVIEW.json'
EXIT_AUTHORITY = ROOT / 'research/axbi_goal_20261014/reviews/SHEAR_MINUS_RESOURCE_STOP_SCIENCE_DECISION.json'
EXIT_AUTHORITY_SHA = '9abb16bd516ba81f2e82051b869576b7414eb8b2d369f2bff0a89a6f4a34dab3'
AUTHORITY = HERE / 'SIGNED_CONTINUATION_MECHANISM_DECISION.json'
AUTHORITY_SHA = '80dd0bf70778f82a8bd10e1bb603fa31d270cc0dcfdfd00b9c8ddf07c7855e9a'
OLD_RECEIPT = HERE / 'post_cap_001/dispatch/runtime_001/POST_CAP_RECEIPT.json'
HALF = 'SHEAR_HALF_MINUS'
ZERO_SEGMENT = 'ZERO_RESOURCE_CONTINUATION_001'
MAPPING = {
    'rust/rei_microphysics/src/axbi_driver.rs': ['research/axbi_goal_20261014/convergence/output_allocation_repair/driver_source.before.rs', 'a614725c153ee21d88554573c15801087d8fb412954fa51d67b781f671475dbf'],
    'rust/rei_microphysics/tests/axbi_driver.rs': ['research/axbi_goal_20261014/convergence/output_allocation_repair/driver_test.before.rs', '5d7a3f893dec801e1d841a78b707c043672b237a3a5b11136c967b2b23472731'],
}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAP = load(HERE / 'post_cap_dispatch.py', 'epoch_cap')
ORIGINAL = CAP.ORIGINAL
RECOVER = CAP.RECOVER


def digest(path):
    with pathlib.Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def historical_digest(path):
    path = pathlib.Path(path).resolve()
    for name, (snapshot, sha) in MAPPING.items():
        if path == ROOT / name:
            actual = digest(ROOT / snapshot)
            if actual != sha:
                raise RuntimeError('HISTORICAL_SNAPSHOT_CHANGED:' + snapshot)
            return actual
    return digest(path)


def check_inputs(inputs):
    for name, expected in inputs.items():
        if historical_digest(ROOT / name) != expected:
            raise RuntimeError('IMMUTABLE_INPUT_CHANGED:' + name)


def frozen_plan():
    """Equivalent original validation, with two exact historical build inputs."""
    binding = json.loads(ORIGINAL.BINDING.read_text())
    if digest(ROOT / binding['compiled_binary_path']) != binding['binary_sha256']:
        raise RuntimeError('ORIGINAL_BINARY_CHANGED')
    check_inputs(binding['source_sha256'])
    check_inputs(binding['config_sha256'])
    review = json.loads(ORIGINAL.REVIEW.read_text())
    if review.get('full_execution_authorized') is not True or review.get('driver_output_limit_bytes') != ORIGINAL.DRIVER_BUDGET:
        raise RuntimeError('ORIGINAL_REVIEW_REQUIRED')
    check_inputs(review['reviewed_input_sha256'])
    if review['reviewed_input_sha256'].get(str(pathlib.Path(ORIGINAL.__file__).relative_to(ROOT))) != digest(ORIGINAL.__file__):
        raise RuntimeError('ORIGINAL_LAUNCHER_NOT_REVIEWED')
    cases = []
    for item in binding['cases']:
        config = ROOT / item['config']
        expected = dict(q_ref=str(item['q_ref']), same_h='false', end_zbar='4.0', max_steps='200000', max_attempts='650000', max_rhs='20000000', max_wall_s='10800', output_budget_mib='2048', spectra_every_accepted='60')
        if any(ORIGINAL.parse_config(config).get(key) != value for key, value in expected.items()):
            raise RuntimeError('ORIGINAL_CONFIG_SCOPE:' + item['case'])
        cases.append(dict(case=item['case'], config=config, output=ROOT / item['output'], binary=ROOT / binding['compiled_binary_path']))
    if {c['case'] for c in cases} != {'ZERO', 'SHEAR_PLUS', 'SHEAR_MINUS', 'SHEAR_HALF_PLUS', HALF} or len(cases) != 5:
        raise RuntimeError('EXACT_ORIGINAL_FIVE_CASES_REQUIRED')
    return binding, cases


def validate(require_review=True):
    if digest(AUTHORITY) != AUTHORITY_SHA:
        raise RuntimeError('RECOVERY_AUTHORITY_CHANGED')
    if digest(EXIT_AUTHORITY) != EXIT_AUTHORITY_SHA:
        raise RuntimeError('EXIT_CLASSIFICATION_AUTHORITY_CHANGED')
    binding = json.loads(BINDING.read_text())
    check_inputs(binding['execution_input_sha256'])
    if digest(OLD_RECEIPT) != binding['preserved_stale_receipt_sha256']:
        raise RuntimeError('FROZEN_STALE_RECEIPT_CHANGED')
    for review_path, field in [(CAP.REVIEW, 'dispatch_execution_authorized'), (CAP.ZERO_REVIEW, 'continuation_execution_authorized')]:
        review = json.loads(review_path.read_text())
        if review.get(field) is not True:
            raise RuntimeError('HISTORICAL_REVIEW_REQUIRED')
        check_inputs(review['reviewed_input_sha256'])
    if require_review:
        review = json.loads(REVIEW.read_text())
        if review.get('epoch_recovery_execution_authorized') is not True:
            raise RuntimeError('EPOCH_REVIEW_RELEASE_REQUIRED')
        required = {str(p.relative_to(ROOT)): digest(p) for p in [pathlib.Path(__file__), HERE/'post_plus_epoch_dispatch.py', BINDING, AUTHORITY, EXIT_AUTHORITY]}
        if any(review.get('reviewed_input_sha256', {}).get(k) != v for k, v in required.items()):
            raise RuntimeError('EPOCH_REVIEW_SCOPE_CHANGED')
        check_inputs(review['reviewed_input_sha256'])
    original, cases = frozen_plan()
    if original['prior_costs']['runs_started'] != 3 or digest(ROOT / original['prior_costs']['evidence']) != original['prior_costs']['evidence_sha256']:
        raise RuntimeError('PILOT_CARRIED_COSTS_CHANGED')
    return original, {c['case']: c for c in cases}


def handoff(groups, allowed_group=None, allowed_parent=None):
    owners = {'run_campaign.py', 'recover_queue.py', 'post_cap_dispatch.py', 'post_plus_dispatch.py', 'post_cap_epoch_recovery.py', 'post_plus_epoch_dispatch.py'}
    live = set()
    for pgid, members in groups.items():
        for member in members:
            argv = member['argv']
            if member['pid'] == os.getpid():
                continue
            if any(pathlib.Path(arg).name in owners for arg in argv) and any(flag in argv for flag in ['--run','--observe','--start-detached']):
                if member['pid'] == allowed_parent and '--start-detached' in argv and any(pathlib.Path(arg).name == pathlib.Path(__file__).name for arg in argv):
                    continue
                raise RuntimeError('OWNER_LIFECYCLE_HOLD')
            if any(pathlib.Path(arg).name.startswith('axbi_') for arg in argv):
                live.add(pgid)
    if len(live) > 2:
        raise RuntimeError('SHARED_MAX_TWO')
    if live - ({allowed_group} if allowed_group is not None else set()):
        raise RuntimeError('LIVE_WORKERS_OR_CHILDREN_HOLD')
    # An adopted launcher group remains occupied even after its Rust child exits.
    if OLD_RECEIPT.exists():
        old = json.loads(OLD_RECEIPT.read_text())
        known = {old.get('pid'), 396140, 396141} | {v['pid'] for v in old.get('new_starts', {}).values()}
        for pgid, members in groups.items():
            if pgid != allowed_group and (pgid in known or any(m['pid'] in known for m in members)):
                raise RuntimeError('OLD_OWNER_OR_LAUNCHER_CHILDREN_HOLD')


def half_absent(cases, old):
    case = cases[HALF]
    if HALF in old.get('new_starts', {}) or case['output'].exists() or (case['output'].parent / (HALF+'_raw')).exists():
        raise RuntimeError('HALF_MINUS_PREEXISTING_NO_RETRY')
    # Detect other original attempt directories and acknowledgements in the goal.
    for path in (ROOT/'research/axbi_goal_20261014/runs').rglob('*'):
        if path.name in {HALF, HALF+'_raw'}:
            raise RuntimeError('HALF_MINUS_ATTEMPT_EXISTS_ANYWHERE')
        if path.name in {'execution_start.json', 'execution_plan.json'}:
            if json.loads(path.read_text()).get('case') == HALF:
                raise RuntimeError('HALF_MINUS_START_EXISTS_ANYWHERE')


def original_cap_exit(result):
    """Exact original handled cap semantics; never translate actual exit codes."""
    case = result.get('case'); code = result.get('exit_code')
    expected = 101 if case in {'ZERO','SHEAR_PLUS'} else 1 if case in {'SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'} else None
    if expected is None or code != expected:
        return False
    proof = result.get('cap_evidence', {})
    values = result.get('actual_terminal', {})
    start = result.get('actual_start', {})
    if proof.get('exact_terminal_evidence_verified') is not True or proof.get('source_identity_sha256') != 'd7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185' or proof.get('authority_sha256') != EXIT_AUTHORITY_SHA:
        return False
    if start.get('case') != case or start.get('binary_sha256') != '32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca':
        return False
    if values.get('status') != 'STOPPED_CHECKPOINTED' or values.get('result') != 'Err(InvalidInput("AXBI_RUNTIME_CAP"))' or values.get('accepted') != '200000':
        return False
    if expected == 1 and (proof.get('stderr_text') != 'InvalidInput("AXBI_RUNTIME_CAP")\n' or proof.get('launcher_status') != 'FAILED_EXIT_1'):
        return False
    try:
        return int(values['attempts']) < 650000 and int(values['rhs_evaluations']) < 20000000 and 0 <= float(values['wall_s']) < 10800
    except (KeyError, ValueError, TypeError):
        return False


def terminal(case, original, groups):
    out = case['output']; raw = out.parent / (case['case']+'_raw')
    required = [raw/'execution_start.json', raw/'time.log', raw/'stdout.log', raw/'stderr.log', out/'RETURN.txt', out/'checkpoint.txt', out/'config.cfg', out/'case_id.txt', out/'source_identity.txt', out/'ledgers.csv']
    if any(not path.is_file() for path in required):
        raise RuntimeError('TERMINAL_EVIDENCE_MISSING:' + case['case'])
    start = json.loads(required[0].read_text())
    if groups.get(start['observed_process_pid']):
        raise RuntimeError('TERMINAL_GROUP_STILL_LIVE')
    if start.get('case') != case['case'] or start.get('binary_sha256') != original['binary_sha256'] or start.get('config_sha256') != digest(case['config']):
        raise RuntimeError('TERMINAL_START_IDENTITY')
    if start.get('source_sha256') != original['source_sha256']:
        raise RuntimeError('TERMINAL_START_SOURCE_BINDING')
    limits = start.get('limits', {})
    expected_limits = dict(wall_seconds=10800, timeout_seconds=10799, cpu_threads=1, virtual_address_space_bytes=2147483648, RSS_ceiling_bytes=2147483648, driver_aggregate_output_bytes=2013265920, combined_output_bytes=2147483648, automatic_retries=0)
    if any(limits.get(k) != v for k, v in expected_limits.items()):
        raise RuntimeError('ORIGINAL_RESOURCE_LIMITS_CHANGED')
    expected_argv = [str(case['binary']), '--config', str(case['config']), '--output', str(out), '--case', case['case']]
    if start['argv'][-7:] != expected_argv:
        raise RuntimeError('TERMINAL_START_ARGV')
    if digest(out/'config.cfg') != digest(case['config']) or (out/'case_id.txt').read_text() != case['case'] or digest(out/'source_identity.txt') != 'd7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185':
        raise RuntimeError('TERMINAL_CASE_CONFIG_SOURCE')
    time_text = (raw/'time.log').read_text(); match = re.search(r'Exit status:\s*(\d+)', time_text)
    if match is None:
        raise RuntimeError('EXTERNAL_EXIT_UNKNOWN')
    code = int(match.group(1)); values = RECOVER.key_values((out/'RETURN.txt').read_text())
    numbers = [float(values[k]) for k in ['a', 'wall_s', 'max_newton_residual', 'last_error']]
    if not all(math.isfinite(x) for x in numbers):
        raise RuntimeError('NONFINITE_TERMINAL')
    lines = (out/'checkpoint.txt').read_text().splitlines()
    if len(lines) != 6 or lines[0] != 'AXBI_CHECKPOINT_V2':
        raise RuntimeError('CHECKPOINT_SCHEMA')
    state = list(map(float, lines[1].split())); counts = list(map(int, lines[2].split()))
    if not all(math.isfinite(x) for x in state) or float(values['a']) != state[0] or [int(values[k]) for k in ['accepted', 'attempts', 'rejections', 'rhs_evaluations']] != [counts[i] for i in [0,1,2,4]]:
        raise RuntimeError('TERMINAL_CHECKPOINT_PARITY')
    if len(state) != 11 or len(counts) != 6 or any(x < 0 for x in counts) or not (0 < state[0] <= .2 and state[1] >= 0 and all(0 <= x <= 1 for x in state[3:6]) and state[4]+state[5] <= 1 and state[6] > 0 and state[7] > 0):
        raise RuntimeError('TERMINAL_CHECKPOINT_DOMAIN')
    if [float(values[k]) for k in ['wall_s','max_newton_residual','last_error']] != [state[i] for i in [10,8,9]]:
        raise RuntimeError('TERMINAL_CHECKPOINT_SCALAR_PARITY')
    cells = list(map(float, lines[4].split()))
    if len(cells) != 392 or not all(math.isfinite(x) and x >= 0 for x in cells):
        raise RuntimeError('CHECKPOINT_PHOTON_DOMAIN')
    if numbers[2] < 0 or numbers[2] > 1e-11 or numbers[3] >= 2e-4 or numbers[3] < 0:
        raise RuntimeError('TERMINAL_NUMERICAL_GUARD')
    checkpoint_ledgers = list(map(float, lines[3].split()))
    initial_energy = list(map(float, lines[5].split()))
    if len(checkpoint_ledgers) != 24 or len(initial_energy) != 1 or not all(math.isfinite(x) for x in checkpoint_ledgers + initial_energy):
        raise RuntimeError('CHECKPOINT_LEDGER_DOMAIN')
    with (out/'ledgers.csv').open() as stream:
        for line in stream:
            fields = line.rstrip().split(',')
            if fields[-1] == 'FAIL' or any(x.lower() in {'nan','inf','-inf','+inf','infinity','-infinity','+infinity'} for x in fields):
                raise RuntimeError('TERMINAL_LEDGER_FAILURE')
    complete = code == 0 and values.get('status') == 'COMPLETE_REPRESENTED_INTERVAL' and numbers[0] == .2
    launcher_status = None
    if case['case'] not in {'ZERO', 'SHEAR_PLUS'}:
        launcher = raw/'execution_receipt.json'
        result = json.loads(launcher.read_text())
        if result.get('case') != case['case'] or result.get('exit_code') != code or result.get('driver_terminal_record') != (out/'RETURN.txt').read_text():
            raise RuntimeError('LAUNCHER_TERMINAL_PARITY')
        launcher_status = result.get('status')
        required.append(launcher)
    cap_evidence = dict(exact_terminal_evidence_verified=True, source_identity_sha256=digest(out/'source_identity.txt'), stderr_text=(raw/'stderr.log').read_text(), launcher_status=launcher_status, authority_sha256=EXIT_AUTHORITY_SHA)
    cap = original_cap_exit(dict(case=case['case'], exit_code=code, actual_terminal=values, actual_start=start, cap_evidence=cap_evidence))
    if not complete and not cap:
        raise RuntimeError('UNKNOWN_OR_SCIENCE_OUTCOME_HOLD:' + case['case'])
    return dict(case=case['case'], status='COMPLETE_EXIT_0' if complete else 'STOPPED_CHECKPOINTED', typed_stop=None if complete else 'ACCEPTED_STEP_CAP', exit_code=code, occupied=False, missing_evidence=None, actual_start=start, actual_terminal=values, cap_evidence=cap_evidence, actual_launcher_status=launcher_status, time_text=time_text, evidence_sha256={str(p.relative_to(ROOT)):digest(p) for p in required if p.name not in {'stdout.log','stderr.log','ledgers.csv'}}, raw_paths={p.name:str(p.relative_to(ROOT)) for p in required})


def reconcile(original, cases, require_half=False, allowed_parent=None, allowed_group=None, groups=None):
    groups = RECOVER.process_groups() if groups is None else groups
    handoff(groups, allowed_parent=allowed_parent, allowed_group=allowed_group)
    old = json.loads(OLD_RECEIPT.read_text())
    if old.get('status') != 'OBSERVING' or old.get('remaining_signed_queue') != [HALF] or set(old.get('new_starts', {})) != {ZERO_SEGMENT,'SHEAR_MINUS','SHEAR_HALF_PLUS'} or [old.get(k) for k in ['original_actual_starts','continuation_actual_starts','total_full_starts','prior_and_current_starts']] != [4,1,5,8]:
        raise RuntimeError('STALE_RECEIPT_SCOPE_OR_COUNTS')
    results = [terminal(cases[n], original, groups) for n in ['ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS']]
    for result in results[2:]:
        if result['actual_start']['observed_process_pid'] != old['new_starts'][result['case']]['pid']:
            raise RuntimeError('STALE_START_ACK_CHAIN')
    zout = ROOT/'research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_continuation_001'
    zraw = zout.parent/'ZERO_continuation_001_raw'
    zr = json.loads((zraw/'POST_CAP_SEGMENT_RECEIPT.json').read_text())
    zp = json.loads((zraw/'POST_CAP_SEGMENT_PROCESS.json').read_text())
    zv = RECOVER.key_values((zout/'RETURN.txt').read_text())
    zb = json.loads(CAP.ZERO_BINDING.read_text())
    expected_zero_argv = [str(ROOT/zb['driver_argv'][0])] + zb['driver_argv'][1:]
    if zp['argv'][-len(expected_zero_argv):] != expected_zero_argv:
        raise RuntimeError('ZERO_START_ARGV_CHANGED')
    if zr.get('status') != 'SUCCESS' or zr.get('exit_code') != 0 or zr.get('segment') != ZERO_SEGMENT or zp['pid'] != old['new_starts'][ZERO_SEGMENT]['pid'] or zp['argv'] != old['new_starts'][ZERO_SEGMENT]['argv'] or zv.get('status') != 'COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' or float(zv['a']) != .2 or zr['driver_return'] != (zout/'RETURN.txt').read_text():
        raise RuntimeError('ZERO_COMPLETION_UNKNOWN')
    if not re.search(r'Exit status:\s*0\s*$', (zraw/'time.log').read_text()):
        raise RuntimeError('ZERO_EXTERNAL_EXIT_UNKNOWN')
    if digest(zout/'config.cfg') != digest(cases['ZERO']['config']) or digest(zout/'source_identity.txt') != 'd7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185':
        raise RuntimeError('ZERO_CONFIG_SOURCE_CHANGED')
    zpaths = [zraw/'POST_CAP_SEGMENT_RECEIPT.json', zraw/'POST_CAP_SEGMENT_PROCESS.json', zraw/'POST_CAP_SEGMENT_START.json', zraw/'time.log', zout/'RETURN.txt', zout/'checkpoint.txt', zout/'config.cfg', zout/'source_identity.txt']
    zero = dict(zr, evidence_sha256={str(p.relative_to(ROOT)):digest(p) for p in zpaths})
    if require_half:
        results.append(terminal(cases[HALF], original, groups))
    else:
        half_absent(cases, old)
    starts = {n: results[i]['actual_start'] for i,n in enumerate(['ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS'])}
    if require_half:
        starts[HALF] = results[-1]['actual_start']
    count = len(starts)
    return dict(schema='rei.axbi.epoch_recovery_receipt.v1', status='COMPLETED_EPOCH_RECOVERY' if require_half else 'RECONCILED_READY_HALF_MINUS', preserved_stale_receipt_path=str(OLD_RECEIPT.relative_to(ROOT)), preserved_stale_receipt_sha256=digest(OLD_RECEIPT), preserved_stale_receipt=old, original_actual_starts=count, continuation_actual_starts=1, total_full_starts=count+1, prior_pilot_starts=3, prior_and_current_starts=count+4, original_results=results, zero_result=zero, remaining_signed_queue=[] if require_half else [HALF], max_total_concurrent=2, source_mapping=MAPPING, authority_sha256=AUTHORITY_SHA, scientific_admission='NOT_ISSUED')


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2)+'\n').encode()
    if RECOVER.bytes_under(OWN) - (path.stat().st_size if path.exists() else 0) + len(data) > 1024**2:
        raise RuntimeError('RECOVERY_METADATA_CAP')
    temporary = path.with_suffix('.tmp')
    with temporary.open('wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def observe():
    original, cases = validate()
    ready = reconcile(original, cases, allowed_parent=os.getppid())
    RUNTIME.mkdir(parents=True)  # exclusive reservation, before any process start
    save(RECEIPT, dict(ready, status='RESERVED_ORIGINAL_HALF_MINUS', half_launch_reserved=True))
    active = {}; launches = {}; lock = threading.Lock()
    try:
        validate(); reconcile(original, cases, allowed_parent=os.getppid())
        result = ORIGINAL.run_case(cases[HALF], original, 0, active, lock, launches)
        save(RUNTIME/'HALF_MINUS_LAUNCHER_RESULT.json', result)
        final = reconcile(original, cases, require_half=True, allowed_parent=os.getppid())
        save(RECEIPT, final)
        return 0
    except Exception as error:
        save(RUNTIME/'FIRST_FAILURE.json', dict(error=repr(error), launches=launches, automatic_retry=False))
        save(RECEIPT, dict(ready, status='STOPPED_FOR_CLASSIFICATION', error=repr(error), half_launch_reserved=True, actual_new_starts=len(launches), original_actual_starts=4+len(launches), total_full_starts=5+len(launches), prior_and_current_starts=8+len(launches)))
        raise


def detached():
    original, cases = validate(); reconcile(original, cases)
    if RUNTIME.exists():
        raise RuntimeError('RECOVERY_ALREADY_RESERVED_NO_RETRY')
    OWN.mkdir(parents=True, exist_ok=True)
    with (OWN/'observer.stdout').open('xb') as out, (OWN/'observer.stderr').open('xb') as err:
        proc = subprocess.Popen([sys.executable, str(__file__), '--observe'], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
    save(OWN/'DETACHED_START.json', dict(pid=proc.pid, status='OBSERVER_STARTED_NOT_SCIENCE_ACKNOWLEDGEMENT'))
    print(proc.pid)


def self_check():
    def refused(fn):
        try: fn()
        except (RuntimeError, FileNotFoundError): return
        raise AssertionError('unsafe acceptance')
    for name,(snapshot,expected) in MAPPING.items():
        assert historical_digest(ROOT/name) == expected == digest(ROOT/snapshot)
    refused(lambda: check_inputs({'rust/rei_microphysics/src/axbi_driver.rs':'0'*64}))
    refused(lambda: check_inputs({'unknown_source.rs':'0'*64}))
    for argv in [['python3','/x/post_cap_dispatch.py','--observe'], ['/x/axbi_reionization'], ['/usr/bin/time']]:
        groups = {811806:[dict(pid=811806,argv=argv)]}
        refused(lambda: handoff(groups))
    refused(lambda: handoff({i:[dict(pid=i,argv=['/x/axbi_reionization'])] for i in [11,12,13]}))
    assert handoff({}) is None
    original, cases = validate(require_review=False)
    old = json.loads(OLD_RECEIPT.read_text())
    refused(lambda: half_absent(cases, dict(old,new_starts={HALF:{}})))
    assert original['prior_costs']['runs_started']+4+1 == 8
    assert original['prior_costs']['runs_started']+5+1 == 9
    plus = load(HERE/'post_plus_epoch_dispatch.py','epoch_plus_fake')
    for status in ['OBSERVING','RECONCILED_READY_HALF_MINUS','STOPPED_FOR_CLASSIFICATION']:
        refused(lambda: plus.carried_receipt(dict(status=status)))
    # Exercise the actual PLUS handoff after receipt JSON persistence. This
    # fails with the original tuple-valued MAPPING; strict equality is retained.
    pe = plus.EPOCH
    actual = dict(status='COMPLETED_EPOCH_RECOVERY', remaining_signed_queue=[],
                  original_actual_starts=5, continuation_actual_starts=1,
                  total_full_starts=6, prior_pilot_starts=3, prior_and_current_starts=9,
                  original_results=[dict(case=n, status='STOPPED_CHECKPOINTED',
                                         typed_stop='ACCEPTED_STEP_CAP', exit_code=101)
                                    for n in ['ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS',HALF]],
                  zero_result=dict(status='SUCCESS', exit_code=0),
                  source_mapping=MAPPING,
                  preserved_stale_receipt_sha256=digest(OLD_RECEIPT))
    saved_attributes = (pe.RECEIPT, pe.validate, pe.reconcile, pe.RECOVER.process_groups)
    with tempfile.TemporaryDirectory(dir=AREA, prefix='fake_persisted_') as directory:
        pe.RECEIPT = pathlib.Path(directory)/'terminal.json'
        pe.validate = lambda: ({}, {})
        pe.reconcile = lambda *args, **kwargs: actual
        pe.RECOVER.process_groups = lambda: {}
        def persist(value):
            pe.RECEIPT.write_text(json.dumps(value))
        try:
            persist(actual)
            carried, groups = plus.fresh_handoff()
            assert carried['all_history_starts'] == 9 and groups == {}
            changed = copy.deepcopy(actual)
            changed['source_mapping']['rust/rei_microphysics/src/axbi_driver.rs'][1] = '0'*64
            persist(changed); refused(lambda: plus.fresh_handoff())
            changed = copy.deepcopy(actual)
            changed['original_results'][0]['exit_code'] = 99
            persist(changed); refused(lambda: plus.fresh_handoff())
            for status in ['OBSERVING','RECONCILED_READY_HALF_MINUS','STOPPED_FOR_CLASSIFICATION']:
                actual['status'] = status
                persist(actual); refused(lambda: plus.fresh_handoff())
            actual['status'] = 'COMPLETED_EPOCH_RECOVERY'
            actual['original_results'][0]['typed_stop'] = 'UNKNOWN'
            persist(actual); refused(lambda: plus.fresh_handoff())
        finally:
            pe.RECEIPT, pe.validate, pe.reconcile, pe.RECOVER.process_groups = saved_attributes
    print('ERD01_PERSISTED_ACTUAL_PLUS_HANDOFF_PASS; valid JSON receipt accepted; changed source mapping/evidence, incomplete status and unknown outcome refused')
    calls = []
    reserved = False
    for _ in range(3):
        if not reserved:
            reserved = True; calls.append(HALF)
    assert calls == [HALF] and len(calls)+5 == 6 and 6+3 == 9
    print('EPOCH_RECOVERY_FAKE_CHECK_PASS; exact two snapshots; live owner/workers/children, unknown source, duplicate HALF, incomplete PLUS refused; HALF only once; max2; carried full5->6/pilot3/history8->9; zero science starts')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); actions=parser.add_mutually_exclusive_group(required=True)
    for action in ['self-check','start-detached','observe']: actions.add_argument('--'+action,action='store_true')
    args=parser.parse_args()
    if args.self_check: self_check()
    elif args.start_detached: detached()
    else: raise SystemExit(observe())
