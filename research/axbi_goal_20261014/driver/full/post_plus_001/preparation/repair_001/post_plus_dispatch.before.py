#!/usr/bin/env python3
"""Serialized, one-shot PLUS successor; preparation never launches science."""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import selectors
import signal
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AREA = HERE / 'post_plus_001'
OWN = AREA / 'dispatch'
RUNTIME = OWN / 'runtime_001'
BINDING = AREA / 'POST_PLUS_DISPATCH_BINDING.json'
PLUS_BINDING = AREA / 'PLUS_CONTINUATION_BINDING.json'
REVIEW = ROOT / 'research/axbi_goal_20261014/reviews/POST_PLUS_DISPATCH_REVIEW.json'
PLUS_REVIEW = ROOT / 'research/axbi_goal_20261014/reviews/PLUS_CONTINUATION_REVIEW.json'
DECISION = ROOT / 'research/axbi_goal_20261014/scenario/POST_PLUS_CAP_EXECUTION_DECISION.json'
DECISION_SHA = '8731004f23be8d5ed4fddfeaf5400211f0012bcb0b420a4958f84b706fd10429'
OLD_RECEIPT = HERE / 'post_cap_001/dispatch/runtime_001/POST_CAP_RECEIPT.json'
SEGMENT = 'SHEAR_PLUS_RESOURCE_CONTINUATION_001'
MIB = 1024 * 1024
spec = importlib.util.spec_from_file_location('plus_original_observation', HERE / 'recover_queue.py')
RECOVER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RECOVER)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def save(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    # Atomic replacement and fsync retain reservation across observer death.
    size = RECOVER.bytes_under(OWN) - (path.stat().st_size if path.exists() else 0)
    if size + len(data) > MIB:
        raise RuntimeError('PLUS_METADATA_CAP')
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def scientific_groups(groups):
    return {pgid for pgid, members in groups.items() if any(
        any(pathlib.Path(arg).name.startswith('axbi_') for arg in member['argv'])
        for member in members)}


def handoff(receipt, groups, allowed_group=None, allowed_parent=None):
    for members in groups.values():
        for member in members:
            if member['pid'] == os.getpid():
                continue
            argv = member['argv']
            owners = {'run_campaign.py', 'recover_queue.py', 'post_cap_dispatch.py', 'post_plus_dispatch.py'}
            if any(pathlib.Path(arg).name in owners for arg in argv) and any(
                    flag in argv for flag in ['--run', '--observe', '--start-detached']):
                if member['pid'] == allowed_parent and any(
                        pathlib.Path(arg).name == 'post_plus_dispatch.py' for arg in argv) and '--start-detached' in argv:
                    continue
                raise RuntimeError('SHARED_OBSERVER_STILL_ACTIVE')
    live = scientific_groups(groups)
    if live - ({allowed_group} if allowed_group is not None else set()):
        raise RuntimeError('UNACCOUNTED_SCIENTIFIC_PROCESS_GROUP')
    if len(live) > 2:
        raise RuntimeError('SHARED_MAX_TWO')
    if receipt.get('status') != 'COMPLETED_POST_CAP_EXECUTION':
        raise RuntimeError('OLD_TERMINAL_CLASSIFICATION_REQUIRED')
    if receipt.get('remaining_signed_queue') != [] or receipt.get('segment_dispatched') is not True:
        raise RuntimeError('OLD_QUEUED_WORK')
    expected = {'ZERO_RESOURCE_CONTINUATION_001', 'SHEAR_MINUS', 'SHEAR_HALF_PLUS', 'SHEAR_HALF_MINUS'}
    if set(receipt.get('new_starts', {})) != expected:
        raise RuntimeError('OLD_START_ACCOUNTING_UNKNOWN')
    counts = [receipt.get(k) for k in ['original_actual_starts', 'continuation_actual_starts', 'total_full_starts', 'prior_and_current_starts']]
    if counts != [5, 1, 6, 9]:
        raise RuntimeError('OLD_CARRIED_COUNTS_UNKNOWN')
    originals = receipt.get('original_observations', [])
    if len(originals) != 2 or {x.get('case') for x in originals} != {'ZERO', 'SHEAR_PLUS'} or any(x.get('occupied') or x.get('missing_evidence') for x in originals):
        raise RuntimeError('OLD_ORIGINAL_OUTCOME_UNKNOWN')
    if receipt.get('original_typed_statuses') != ['ACCEPTED_STEP_CAP', 'ACCEPTED_STEP_CAP']:
        raise RuntimeError('OLD_ORIGINAL_CLASSIFICATION_UNKNOWN')
    results = receipt.get('results', [])
    if len(results) != 4 or {x.get('case') for x in results} != {'ZERO', 'SHEAR_MINUS', 'SHEAR_HALF_PLUS', 'SHEAR_HALF_MINUS'}:
        raise RuntimeError('OLD_PENDING_OR_UNACCOUNTED_RESULT')
    for result in results:
        if result.get('case') == 'ZERO':
            if result.get('segment') != 'ZERO_RESOURCE_CONTINUATION_001' or result.get('status') != 'SUCCESS' or result.get('exit_code') != 0:
                raise RuntimeError('OLD_ZERO_OUTCOME_UNKNOWN')
        elif not (result.get('status') == 'COMPLETE_EXIT_0' and result.get('exit_code') == 0) and not (
                result.get('typed_stop') == 'ACCEPTED_STEP_CAP' and result.get('exit_code') == 101):
            raise RuntimeError('OLD_ORIGINAL_OUTCOME_UNCLASSIFIED')
    return dict(original_actual_starts=5, ZERO_actual_starts=1, PLUS_attempted_starts=0,
                total_full_starts=6, prior_pilot_starts=3, all_history_starts=9,
                start_ceilings=dict(original=5, ZERO=1, PLUS=1, full=7, all_history=10),
                preserved_old_receipt=receipt)


def validate():
    if digest(DECISION) != DECISION_SHA:
        raise RuntimeError('PLUS_AUTHORITY_CHANGED')
    decision = json.loads(DECISION.read_text())
    for path, sha in {**decision['reviewed_immutable_evidence'], **decision['actual_plus_stop']['paths']}.items():
        if digest(ROOT / path) != sha:
            raise RuntimeError('IMMUTABLE_INPUT_CHANGED:' + path)
    b = json.loads(PLUS_BINDING.read_text())
    dispatch = json.loads(BINDING.read_text())
    required = {str(p.relative_to(ROOT)) for p in [pathlib.Path(__file__), PLUS_BINDING, BINDING, DECISION]}
    required.update(dispatch['execution_input_sha256'])
    for path, sha in dispatch['execution_input_sha256'].items():
        if digest(ROOT / path) != sha:
            raise RuntimeError('EXECUTION_INPUT_CHANGED:' + path)
    for path, field in [(REVIEW, 'dispatch_execution_authorized'), (PLUS_REVIEW, 'continuation_execution_authorized')]:
        review = json.loads(path.read_text())
        if review.get(field) is not True or not required.issubset(review.get('reviewed_input_sha256', {})):
            raise RuntimeError('FRESH_REVIEW_REQUIRED')
        for name, sha in review['reviewed_input_sha256'].items():
            if digest(ROOT / name) != sha:
                raise RuntimeError('REVIEWED_INPUT_CHANGED:' + name)
    review = json.loads(PLUS_REVIEW.read_text())
    argv = decision['scheduler_release']['solver_argv']
    if b['driver_argv'] != argv or review['authorized_driver_argv'] != argv or review['binary_sha256'] != b['new_binary_sha256']:
        raise RuntimeError('PLUS_ARGV_BINARY_SCOPE')
    if b['case_id'] != 'SHEAR_PLUS' or b['segment_id'] != SEGMENT or b['new_binary_path'] != argv[0] or digest(ROOT / argv[0]) != b['new_binary_sha256']:
        raise RuntimeError('PLUS_BINARY_IDENTITY')
    if b['predecessor_hashes'] != decision['actual_plus_stop']['paths'] or b['output_segment_path'] != decision['plus_continuation']['fresh_output']:
        raise RuntimeError('PLUS_PREDECESSOR_OUTPUT_SCOPE')
    if digest(ROOT / argv[2]) != decision['actual_plus_stop']['paths'][argv[4] + '/config.cfg']:
        raise RuntimeError('PLUS_CONFIG_CHANGED')
    original, _ = RECOVER.frozen_module().frozen_plan()
    if original['binary_sha256'] != decision['actual_plus_stop']['original_binary_sha256']:
        raise RuntimeError('ORIGINAL_BINARY_CHANGED')
    return decision, b


def fresh_handoff(allowed_group=None, allowed_parent=None):
    old = json.loads(OLD_RECEIPT.read_text())
    groups = RECOVER.process_groups()
    carried = handoff(old, groups, allowed_group, allowed_parent)
    carried['old_receipt_sha256'] = digest(OLD_RECEIPT)
    return carried, groups


def observe():
    decision, binding = validate()
    carried, _ = fresh_handoff(allowed_parent=os.getppid())
    out = ROOT / decision['plus_continuation']['fresh_output']
    raw = ROOT / decision['plus_continuation']['fresh_raw_output']
    if out.exists() or raw.exists() or RUNTIME.exists():
        raise RuntimeError('PLUS_EXISTING_OUTPUT_OR_RESERVATION_NO_RETRY')
    RUNTIME.mkdir(parents=True)  # Exclusive durable reservation; never reused.
    raw.mkdir()
    receipt = dict(status='RESERVED_BEFORE_SOLVER_LAUNCH', pid=os.getpid(), polls=0,
                   case='SHEAR_PLUS', segment=SEGMENT, scientific_admission='NOT_ISSUED', **carried)
    receipt.update(PLUS_attempted_starts=1, total_full_starts=7, all_history_starts=10)
    receipt.update(binding_sha256=digest(PLUS_BINDING), dispatch_binding_sha256=digest(BINDING),
                   continuation_review_sha256=digest(PLUS_REVIEW), dispatch_review_sha256=digest(REVIEW))
    save(RUNTIME / 'POST_PLUS_RECEIPT.json', receipt)
    argv = ['/usr/bin/time', '-v', '-o', str(raw / 'time.log'), '/usr/bin/timeout', '--foreground', '--signal=KILL', '10799s',
            '/usr/bin/taskset', '-c', '0', '/usr/bin/prlimit', '--as=2147483648', '--fsize=' + str(1920*MIB), '--'] + binding['driver_argv']
    env = dict(os.environ)
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'RAYON_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        env[key] = '1'
    receipt.update(argv=argv, cpu=0)
    save(raw / 'POST_PLUS_SEGMENT_START.json', receipt)
    proc = None
    logs = {}
    selector = selectors.DefaultSelector()
    started = time.monotonic()
    reason = None
    try:
        # Recheck ownership after durable reservation, immediately before Popen.
        validate()
        fresh_handoff(allowed_parent=os.getppid())
        proc = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        receipt.update(status='PROCESS_ACKNOWLEDGED', observed_process_pid=proc.pid, pgid=proc.pid)
        save(raw / 'POST_PLUS_SEGMENT_PROCESS.json', dict(pid=proc.pid, pgid=proc.pid, argv=argv, status='PROCESS_ACKNOWLEDGED'))
        save(RUNTIME / 'POST_PLUS_RECEIPT.json', receipt)
        for pipe, name in [(proc.stdout, 'stdout'), (proc.stderr, 'stderr')]:
            logs[pipe.fileno()] = (raw / (name + '.log')).open('xb')
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ)
        written = 0
        while selector.get_map() or proc.poll() is None:
            for key, _ in selector.select(timeout=.1):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                if written + len(chunk) > 126*MIB:
                    reason = 'SEGMENT_LOG_CAP'
                    break
                logs[key.fileobj.fileno()].write(chunk)
                logs[key.fileobj.fileno()].flush()
                written += len(chunk)
            _, groups = fresh_handoff(proc.pid, os.getppid())
            members = groups.get(proc.pid, [])
            if sum(x['rss_kib'] for x in members) > 2*1024*1024:
                reason = 'SEGMENT_RSS_CAP'
            if RECOVER.bytes_under(out) > 1920*MIB or RECOVER.bytes_under(out)+RECOVER.bytes_under(raw)+RECOVER.bytes_under(OWN) > 2048*MIB:
                reason = 'SEGMENT_TOTAL_OUTPUT_CAP'
            if time.monotonic()-started >= 10800:
                reason = 'SEGMENT_WALL_CAP'
            if reason:
                os.killpg(proc.pid, signal.SIGKILL)
                break
            receipt.update(status='OBSERVING', polls=receipt['polls']+1, wall_s=time.monotonic()-started)
            save(RUNTIME / 'POST_PLUS_RECEIPT.json', receipt)
        code = proc.wait()
        terminal = (out / 'RETURN.txt').read_text() if (out / 'RETURN.txt').exists() else None
        values = RECOVER.key_values(terminal or '')
        complete = code == 0 and values.get('status') == 'COMPLETE_SEGMENT_TO_SELECTED_ENDPOINT' and float(values.get('a', 'nan')) == .2
        receipt.update(status='COMPLETED_PLUS_EXECUTION' if complete else 'STOPPED_FOR_CLASSIFICATION',
                       exit_code=code, stop_reason=reason, driver_return=terminal, wall_s=time.monotonic()-started,
                       time_text=(raw/'time.log').read_text() if (raw/'time.log').exists() else None,
                       output_bytes=RECOVER.bytes_under(out)+RECOVER.bytes_under(raw)+RECOVER.bytes_under(OWN))
        save(raw / 'POST_PLUS_SEGMENT_RECEIPT.json', receipt)
        save(RUNTIME / 'POST_PLUS_RECEIPT.json', receipt)
        return 0 if complete else 2
    except Exception as error:
        if proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
        receipt.update(status='STOPPED_FOR_CLASSIFICATION', error=repr(error),
                       launch_attempt_reserved=True, automatic_retry=False)
        save(RUNTIME / 'POST_PLUS_RECEIPT.json', receipt)
        raise
    finally:
        for stream in logs.values():
            stream.close()
        selector.close()


def detached():
    validate()
    fresh_handoff()
    if RUNTIME.exists():
        raise RuntimeError('PLUS_ALREADY_RESERVED')
    OWN.mkdir(parents=True, exist_ok=True)
    with (OWN/'observer.stdout').open('xb') as out, (OWN/'observer.stderr').open('xb') as err:
        proc = subprocess.Popen([sys.executable, str(__file__), '--observe'], cwd=ROOT, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=err, start_new_session=True, close_fds=True)
    for _ in range(50):
        path = RUNTIME/'POST_PLUS_RECEIPT.json'
        if path.exists():
            receipt = json.loads(path.read_text())
            if receipt.get('observed_process_pid') and receipt['polls'] >= 2:
                save(OWN/'DETACHED_START.json', dict(pid=proc.pid, progress='ACKNOWLEDGED_AND_TWO_POLLS'))
                print(proc.pid)
                return
        if proc.poll() is not None:
            raise RuntimeError('PLUS_OBSERVER_EARLY_EXIT_NO_RETRY')
        time.sleep(.1)
    raise RuntimeError('PLUS_ACK_NOT_OBSERVED_NO_RETRY')


def self_check():
    receipt = dict(status='COMPLETED_POST_CAP_EXECUTION', remaining_signed_queue=[], segment_dispatched=True,
                   new_starts={n:{} for n in ['ZERO_RESOURCE_CONTINUATION_001','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS']},
                   original_actual_starts=5,continuation_actual_starts=1,total_full_starts=6,prior_and_current_starts=9,
                   original_observations=[dict(case=n,occupied=False,missing_evidence=None) for n in ['ZERO','SHEAR_PLUS']],
                   original_typed_statuses=['ACCEPTED_STEP_CAP','ACCEPTED_STEP_CAP'],
                   results=[dict(case='ZERO',segment='ZERO_RESOURCE_CONTINUATION_001',status='SUCCESS',exit_code=0)] +
                   [dict(case=n,status='STOPPED_CHECKPOINTED',typed_stop='ACCEPTED_STEP_CAP',exit_code=101) for n in ['SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS']])
    def refused(r, groups):
        try:
            handoff(r, groups)
        except RuntimeError:
            return
        raise AssertionError('unsafe handoff accepted')
    assert handoff(receipt,{})['all_history_starts'] == 9
    for status in ['OBSERVING','STOPPED_FOR_CLASSIFICATION','UNKNOWN']:
        refused(dict(receipt,status=status),{})
    refused(receipt,{9:[dict(pid=9,argv=['python3','/x/post_cap_dispatch.py','--observe'])]})
    refused(receipt,{9:[dict(pid=9,argv=['/x/axbi_reionization'])]})
    refused(receipt,{9:[dict(pid=9,argv=['/x/axbi_unknown'])],10:[dict(pid=10,argv=['/x/axbi_reionization'])]})
    refused(dict(receipt,remaining_signed_queue=['SHEAR_HALF_MINUS']),{})
    refused(dict(receipt,results=receipt['results'][:-1]),{})
    refused(dict(receipt,total_full_starts=5),{})
    attempted = 0
    reserved = False
    calls = []
    for _ in range(3):
        if not reserved:
            reserved = True
            attempted += 1
            calls.append(SEGMENT)
    assert calls == [SEGMENT] and attempted == 1 and 6+attempted == 7 and 9+attempted == 10
    assert handoff(receipt,{9:[dict(pid=9,argv=['/x/axbi_plus_resource_continuation'])]},allowed_group=9)
    print('POST_PLUS_FAKE_SERIALIZED_SCHEDULER_PASS; live-owner/unknown/queue refusal; one reservation, max2, original5+ZERO1+PLUS1/full7/pilot3/history10; zero scientific starts')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--self-check', action='store_true')
    actions.add_argument('--start-detached', action='store_true')
    actions.add_argument('--observe', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.start_detached:
        detached()
    else:
        raise SystemExit(observe())
