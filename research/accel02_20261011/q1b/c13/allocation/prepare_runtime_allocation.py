#!/usr/bin/env python3
"""Create an explicitly reviewed runtime-only child of a committed full history.

No map is evaluated here. Parent evidence is read only; the child is create only.
The parent journal determines the latest checkpoint, never an observed generation
constant. Diagnostic maps have a separate allowance and never reset/debit the
production controller cursor. A production failure requires another repair lane.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
Q1B = HERE.parents[1]
REPO = HERE.parents[4]
C11 = Q1B / 'c11'
sys.path.insert(0, str(C11 / 'integration/production'))
sys.path.insert(0, str(Q1B / 'c12/repair/production_v2'))
from production_journal import AttemptJournal, durable_json, sha, validate_cursor
from prepare_failure_transition import copy_initial_output

TARGET = 4.011926941800233e16
PARENT_REL = Path('research/accel02_20261011/q1b/c12/evidence/C2_FULL004')
SOURCE_REL = Path('research/accel02_20261011/q1b/c12/repair/source_candidate/source_precision_v2.py')
SOURCE_SHA = 'a29207b6ebee37024c35b87723dd64516e528a4f0a160b17ce9965b8dd7e0779'
ABSORPTION_REL = Path('research/accel02_20261011/q1b/c12/repair/opacity_candidate_v3/positive_absorption_v3.py')
ABSORPTION_SHA = '48df7043fb2b974bac3cf196ea488d45eb9afbfb16ee5a757d7f0cfc275147fb'
TRANSITION_KEY = 'production_runtime_allocation_transitions'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def inside(repo, path, *, strict=True):
    path = Path(path)
    if not path.is_absolute():
        path = repo / path
    path = path.resolve(strict=strict)
    require(path.is_relative_to(repo), 'PATH_OUTSIDE_REPO')
    return path


def allocation_controls(original, cursor, parent_allocation, additional_physical_attempts=100):
    """Only cumulative runtime caps change; numerical controls stay byte-semantic."""
    validate_cursor(cursor)
    require(type(additional_physical_attempts) is int and additional_physical_attempts > 0,
            'POSITIVE_INTEGER_ADDITIONAL_ALLOCATION_REQUIRED')
    debit = parent_allocation['external_failed_attempt_debit']
    require(type(debit) is int and debit >= 0, 'EXTERNAL_FAILURE_DEBIT')
    old_cap = parent_allocation.get('all_physical_attempt_cap', parent_allocation.get('original_all_attempt_cap'))
    require(type(old_cap) is int and original['max_attempts'] + debit == old_cap,
            'PARENT_CUMULATIVE_ALLOCATION_IDENTITY')
    require(cursor['attempts'] <= original['max_attempts'] and
            cursor['accepted_macros'] <= original['max_accepted_macros'], 'PARENT_ALLOCATION_OVERRUN')
    require(cursor['attempts'] == original['max_attempts'] or
            cursor['accepted_macros'] == original['max_accepted_macros'], 'PARENT_ALLOCATION_NOT_EXHAUSTED')
    # This lane admits no new failure. Every previously debited incident remains
    # explicit and is neither discarded nor counted again.
    failed = parent_allocation['failed_lanes']
    require(len(failed) == debit and len({(x['run'], x['attempt']) for x in failed}) == debit,
            'FAILURE_DEBIT_RECEIPT_CARDINALITY')
    new_cap = old_cap + additional_physical_attempts
    controls = copy.deepcopy(original)
    controls['max_attempts'] = new_cap - debit
    controls['max_accepted_macros'] = cursor['accepted_macros'] + additional_physical_attempts
    allocation = dict(
        schema='rei.c13.cumulative_runtime_allocation.v1',
        original_all_attempt_cap=parent_allocation.get('original_all_attempt_cap', old_cap),
        parent_all_physical_attempt_cap=old_cap,
        additional_physical_attempt_allowance=additional_physical_attempts,
        all_physical_attempt_cap=new_cap,
        external_failed_attempt_debit=debit,
        failed_lanes=copy.deepcopy(failed),
        parent_completed_attempts=cursor['attempts'],
        parent_accepted_macros=cursor['accepted_macros'],
        child_completed_attempt_cap=controls['max_attempts'],
        child_accepted_macro_cap=controls['max_accepted_macros'],
        remaining_completed_attempts=controls['max_attempts'] - cursor['attempts'],
        remaining_accepted_macros=controls['max_accepted_macros'] - cursor['accepted_macros'],
        next_child_attempt_number=cursor['attempts'] + 1,
        next_physical_attempt_ordinal=cursor['attempts'] + debit + 1,
        counters_reset=False,
        numerical_controller_parameters_changed=False,
        scientific_tolerances_changed=False,
        source_identity_changed=False,
        absorption_arithmetic_identity_changed=False,
        old_failed_attempt_resolved=False,
        controller_count_identity='attempts=accepted_macros+rejected_macros',
        total_budget_identity=f'completed_attempts + external_failed_attempt_debit <= {new_cap}',
        diagnostic_runtime_accounting='SEPARATE_REVIEWED_ALLOWANCE_NO_MAIN_CURSOR_OR_DEBIT_CHANGE',
    )
    return controls, allocation


def committed_head(journal_directory, expected_cursor, expected_checkpoint):
    """Read-only lineage scan; reject even uncommitted/orphan tail receipts."""
    directory = Path(journal_directory)
    seed_path = directory / 'SEED.json'
    seed = json.loads(seed_path.read_text())
    require(seed['cursor'] == expected_cursor and seed['checkpoint'] == expected_checkpoint,
            'JOURNAL_SEED_BUNDLE_MISMATCH')
    validate_cursor(seed['cursor'])
    head = copy.deepcopy(seed)
    consumed = {seed_path.name}
    evidence = [seed_path]
    validator = AttemptJournal.__new__(AttemptJournal)
    while True:
        number = head['cursor']['attempts'] + 1
        begin_path = directory / f'attempt-{number:08d}.begin.json'
        commit_path = directory / f'attempt-{number:08d}.commit.json'
        failure_path = directory / f'attempt-{number:08d}.failure.json'
        if not begin_path.exists():
            break
        require(not failure_path.exists(), 'FAILED_ATTEMPT_REQUIRES_EXPLICIT_REPAIR')
        require(commit_path.exists(), 'UNRESOLVED_INFLIGHT_NO_ALLOCATION_ADOPTION')
        begin = json.loads(begin_path.read_text())
        row = json.loads(commit_path.read_text())
        require(begin['attempt'] == number and begin['cursor'] == head['cursor'] and
                begin['checkpoint'] == head['checkpoint'], 'JOURNAL_BROKEN_LINEAGE')
        require(row['begin_sha256'] == sha(begin_path), 'JOURNAL_BEGIN_HASH')
        validator._validate_commit(begin, row['receipt'])
        head = copy.deepcopy(row['receipt'])
        consumed.update((begin_path.name, commit_path.name))
        evidence.extend((begin_path, commit_path))
        exception = directory / f'attempt-{number:08d}.exception.json'
        if exception.exists():
            require(row.get('reconciled_from_atomic_checkpoint') is True,
                    'UNCLASSIFIED_JOURNAL_EXCEPTION')
            consumed.add(exception.name)
            evidence.append(exception)
    actual = {p.name for p in directory.glob('*.json')}
    require(actual == consumed, 'UNRESOLVED_OR_ORPHAN_JOURNAL_RECORD')
    require(not list(directory.glob('*.tmp-*')), 'INCOMPLETE_JOURNAL_PUBLICATION')
    return head, evidence


def inspect_parent(repo, parent_root=PARENT_REL):
    """Validate immutable restore identity without replaying any numerical map."""
    repo = Path(repo).resolve(strict=True)
    require(repo == REPO, 'EXECUTING_CHECKOUT_IDENTITY')
    parent = inside(repo, parent_root)
    bundle_path = parent / 'TRANSITION_RESULT.json'
    bundle = json.loads(bundle_path.read_text())
    seed_checkpoint = dict(generation=bundle['generation'], manifest_sha256=bundle['manifest_sha256'])
    head, journal_paths = committed_head(parent / 'RUN/JOURNAL', bundle['cursor'], seed_checkpoint)
    checkpoint = head['checkpoint']
    gp = parent / 'CHECKPOINTS' / f'gen-{checkpoint["generation"]:08d}'
    require(sha(gp / 'manifest.json') == checkpoint['manifest_sha256'], 'LATEST_PARENT_MANIFEST')
    # A checkpoint beyond the committed head could contain an accepted inflight
    # transaction. Such a state must be reconciled in its own lane first.
    for path in (parent / 'CHECKPOINTS').glob('gen-*'):
        require(path.is_dir() and int(path.name.removeprefix('gen-')) <= checkpoint['generation'],
                'UNCOMMITTED_LATER_CHECKPOINT')
    sys.path.insert(0, str(C11 / 'restart'))
    from adaptive_checkpoint import load_adaptive_checkpoint
    loaded = load_adaptive_checkpoint(gp.parent, checkpoint['generation'], bundle['identity'],
                                      expected_manifest_sha256=checkpoint['manifest_sha256'])
    metadata = loaded['metadata']
    # A pure runtime transition copies the whole saved cursor. A rejection-only
    # tail would require separately specified cursor adoption; fail closed here.
    require(metadata['adaptive_cursor'] == head['cursor'], 'JOURNAL_CURSOR_NOT_SAVED_IN_ACCEPTED_CHECKPOINT')
    binding = metadata['restart_binding']
    require(bundle['controls'] == binding['controls'] and bundle['dependency_closure'] == binding['dependency_closure'],
            'PARENT_BUNDLE_BINDING')
    require(bundle['identity']['source'] == SOURCE_SHA and sha(repo / SOURCE_REL) == SOURCE_SHA,
            'UNCHANGED_SOURCE_IDENTITY')
    require(bundle['source_module_path'] == str(SOURCE_REL) and bundle['absorption_module_path'] == str(ABSORPTION_REL) and
            bundle['absorption_sha256'] == ABSORPTION_SHA and sha(repo / ABSORPTION_REL) == ABSORPTION_SHA,
            'UNCHANGED_ABSORPTION_IDENTITY')
    schedule = json.loads((parent / 'SCHEDULE.json').read_text())
    require(bundle['target_time_s'] == binding['end_time_s'] == schedule['target_time_s'] == TARGET and
            schedule['hard_events_s'] == binding['hard_events_s'], 'FULL_TARGET_SCHEDULE_CHANGED')
    require(head['cursor']['accepted_clock_s'] < TARGET, 'FULL_TARGET_ALREADY_REACHED')
    # Verify every existing output row; migration does not regenerate h0.
    for record in metadata['production_output_records']:
        require(record['time_s'] == schedule['output_epochs_s'][record['epoch_index']], 'OUTPUT_EPOCH_BINDING')
        path = parent / 'RUN/OUTPUT24' / f'epoch-{record["epoch_index"]:03d}.json'
        require(json.loads(path.read_text()) == record, 'OUTPUT_HISTORY_CONTENT')
    # All failure receipts must remain physically present and identity-bound.
    failure_paths = []
    for item in bundle['allocation']['failed_lanes']:
        lane = Q1B / 'c12/evidence' / item['run']
        for kind in ('begin', 'failure'):
            path = lane / 'RUN/JOURNAL' / f'attempt-{item["attempt"]:08d}.{kind}.json'
            key = 'dependency:' + str(path.relative_to(repo))
            require(binding['dependency_closure'].get(key) == sha(path), 'PRIOR_FAILURE_RECEIPT_IDENTITY')
            failure_paths.append(path)
        require(not (lane / 'RUN/JOURNAL' / f'attempt-{item["attempt"]:08d}.commit.json').exists(),
                'PRIOR_FAILED_ATTEMPT_WAS_MUTATED')
    return dict(repo=repo, parent=parent, bundle=bundle, loaded=loaded, checkpoint=checkpoint,
                cursor=head['cursor'], generation_path=gp, schedule=schedule,
                journal_paths=journal_paths, failure_paths=failure_paths)


def validate_adoption_review(review, checkpoint, cursor, allowance):
    require(review.get('status') == 'ALLOW_BOUNDED_RUNTIME_ALLOCATION', 'ALLOCATION_REVIEW_NOT_ALLOWED')
    require(review.get('parent_checkpoint') == checkpoint and review.get('parent_cursor') == cursor,
            'ALLOCATION_REVIEW_PARENT_MISMATCH')
    require(review.get('physics_and_criteria_changed') is False, 'REVIEW_CHANGES_PHYSICS_OR_CRITERIA')
    require(review.get('additional_physical_attempt_allowance') == allowance, 'REVIEW_ALLOWANCE_MISMATCH')
    diagnostic = review.get('diagnostic_runtime', {})
    require(type(diagnostic.get('native_map_allowance')) is int and type(diagnostic.get('native_map_calls')) is int and
            0 <= diagnostic['native_map_calls'] <= diagnostic['native_map_allowance'], 'DIAGNOSTIC_ALLOWANCE_NOT_CLOSED')
    require(diagnostic.get('main_controller_attempt_debit') == 0, 'DIAGNOSTIC_MAIN_CURSOR_CONFLATION')
    return copy.deepcopy(diagnostic)


def assert_preserved(parent_arrays, parent_metadata, arrays, metadata):
    require(set(parent_arrays) == set(arrays) and len(arrays) == 9, 'NINE_ARRAY_SET')
    for key, value in parent_arrays.items():
        require(value.dtype == arrays[key].dtype and value.shape == arrays[key].shape and
                value.tobytes() == arrays[key].tobytes(), 'ARRAY_CHANGED:' + key)
    require(set(metadata) == set(parent_metadata) | {TRANSITION_KEY}, 'METADATA_KEY_DRIFT')
    for key in set(parent_metadata) - {'restart_binding', 'restart_binding_sha256', TRANSITION_KEY}:
        require(parent_metadata[key] == metadata[key], 'PHYSICAL_METADATA_CHANGED:' + key)
    if TRANSITION_KEY in parent_metadata:
        require(metadata[TRANSITION_KEY][:-1] == parent_metadata[TRANSITION_KEY], 'ALLOCATION_HISTORY_REPLACED')
    before, after = parent_metadata['restart_binding'], metadata['restart_binding']
    for key in ('end_time_s', 'hard_events_s'):
        require(before[key] == after[key], 'SCHEDULE_CHANGED:' + key)
    for key, value in before['controls'].items():
        if key not in ('max_attempts', 'max_accepted_macros'):
            require(after['controls'][key] == value, 'NUMERICAL_CONTROL_CHANGED:' + key)
    require(all(after['dependency_closure'].get(k) == v for k, v in before['dependency_closure'].items()),
            'OLD_DEPENDENCY_REPLACED')
    return dict(all_nine_arrays_bitwise_equal=True, all_physical_metadata_equal=True,
                full_prefix_count=len(arrays['prefix_clock']), cursor_unchanged=True,
                source_identity_unchanged=True, absorption_identity_unchanged=True,
                kernel_history_unchanged=True, output_records_unchanged=True,
                native_calls=0, completed_scientific_checks_replayed=0)


def validate_runtime_bundle(bundle):
    require(bundle.get('schema') == 'rei.c13.runtime_allocation_transition_result.v1', 'RUNTIME_BUNDLE_SCHEMA')
    a, c, cursor = bundle['allocation'], bundle['controls'], bundle['cursor']
    validate_cursor(cursor)
    require(bundle['target_time_s'] == TARGET, 'FULL_TARGET_CHANGED')
    require(a['counters_reset'] is False and a['numerical_controller_parameters_changed'] is False and
            a['scientific_tolerances_changed'] is False and a['source_identity_changed'] is False and
            a['absorption_arithmetic_identity_changed'] is False, 'RUNTIME_ONLY_ALLOCATION_REQUIRED')
    require(c['max_attempts'] == a['child_completed_attempt_cap'] and
            c['max_attempts'] + a['external_failed_attempt_debit'] == a['all_physical_attempt_cap'] and
            a['all_physical_attempt_cap'] == a['parent_all_physical_attempt_cap'] + a['additional_physical_attempt_allowance'],
            'CUMULATIVE_ATTEMPT_CAP_IDENTITY')
    require(c['max_accepted_macros'] == a['child_accepted_macro_cap'] ==
            cursor['accepted_macros'] + a['additional_physical_attempt_allowance'], 'CUMULATIVE_MACRO_CAP_IDENTITY')
    require(a['parent_completed_attempts'] == cursor['attempts'] and
            a['remaining_completed_attempts'] == c['max_attempts'] - cursor['attempts'] and
            a['remaining_accepted_macros'] == c['max_accepted_macros'] - cursor['accepted_macros'] and
            a['next_child_attempt_number'] == cursor['attempts'] + 1 and
            a['next_physical_attempt_ordinal'] == cursor['attempts'] + a['external_failed_attempt_debit'] + 1,
            'CUMULATIVE_CURSOR_BUDGET_IDENTITY')
    require(len(a['failed_lanes']) == a['external_failed_attempt_debit'], 'PRIOR_FAILURE_DEBIT_COUNT')
    require(bundle['diagnostic_runtime']['main_controller_attempt_debit'] == 0, 'DIAGNOSTIC_MAIN_CURSOR_CONFLATION')


def prepare_runtime_allocation(repo, output_root, adoption_review_path, *, parent_root=PARENT_REL,
                               additional_physical_attempts=100, extra_dependency_paths=()):
    repo = Path(repo).resolve(strict=True)
    parent = inside(repo, parent_root)
    # Restore packages omit this zero-byte administrative lock. Opening in
    # append mode can recreate it but never rewrites any parent evidence. The
    # same lock excludes production chunks through selection and publication.
    with (parent / 'RUN/RUN.lock').open('a+b') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('PARENT_CHUNK_PROCESS_STILL_RUNNING') from None
        return _prepare_runtime_allocation_locked(repo, output_root, adoption_review_path,
                   parent_root=parent_root, additional_physical_attempts=additional_physical_attempts,
                   extra_dependency_paths=extra_dependency_paths)


def _prepare_runtime_allocation_locked(repo, output_root, adoption_review_path, *, parent_root,
                                      additional_physical_attempts, extra_dependency_paths):
    inspected = inspect_parent(repo, parent_root)
    repo, parent = inspected['repo'], inspected['parent']
    bundle, loaded = inspected['bundle'], inspected['loaded']
    metadata, gp = loaded['metadata'], inspected['generation_path']
    out = inside(repo, output_root, strict=False)
    require(not out.exists(), 'NEW_CHILD_DIRECTORY_REQUIRED')
    review_path = inside(repo, adoption_review_path)
    review = json.loads(review_path.read_text())
    diagnostic = validate_adoption_review(review, inspected['checkpoint'], inspected['cursor'], additional_physical_attempts)
    controls, allocation = allocation_controls(metadata['restart_binding']['controls'], inspected['cursor'],
                                               bundle['allocation'], additional_physical_attempts)
    # Resolve every requested provenance file before creating any child content.
    extra = [inside(repo, path) for path in extra_dependency_paths]
    arrays = {key: value.copy() for key, value in loaded['arrays'].items()}
    child = copy.deepcopy(metadata)
    out.mkdir(parents=True, exist_ok=False)
    durable_json(out / 'SCHEDULE.json', inspected['schedule'])
    durable_json(out / 'CONTROLS.json', controls)
    output_copy = copy_initial_output(parent / 'RUN', out / 'RUN', metadata['production_output_records'])
    durable_json(out / 'OUTPUT_COPY_RECEIPT.json', output_copy)
    deps = copy.deepcopy(metadata['restart_binding']['dependency_closure'])
    additions = [Path(__file__), HERE / 'run_full_history_chunk_v5.py', review_path,
                 parent / 'TRANSITION_RESULT.json', gp / 'manifest.json', gp / 'identity.json',
                 gp / 'metadata.json', gp / 'arrays.npz', parent / 'RUN/INITIAL_OUTPUT_DONE.json',
                 out / 'SCHEDULE.json', out / 'CONTROLS.json', out / 'OUTPUT_COPY_RECEIPT.json',
                 *inspected['journal_paths'], *inspected['failure_paths'], *extra]
    for path in additions:
        path = inside(repo, path)
        key, digest = 'dependency:' + str(path.relative_to(repo)), sha(path)
        require(key not in deps or deps[key] == digest, 'OLD_DEPENDENCY_REPLACEMENT')
        deps[key] = digest
    transition = dict(
        schema='rei.c13.runtime_allocation_identity_transition.v1',
        parent_run=str(parent.relative_to(repo)), parent_checkpoint=inspected['checkpoint'],
        parent_identity=bundle['identity'], parent_cursor=inspected['cursor'],
        parent_dependency_count=len(metadata['restart_binding']['dependency_closure']),
        allocation=allocation, diagnostic_runtime=diagnostic,
        adoption_review=dict(path=str(review_path.relative_to(repo)), sha256=sha(review_path)),
        source_module_path=str(SOURCE_REL), source_sha256=SOURCE_SHA,
        absorption_module_path=str(ABSORPTION_REL), absorption_sha256=ABSORPTION_SHA,
        full_target_s=TARGET, physical_prefix_copied_without_maps=True,
        physics_and_criteria_changed=False, initial_h0_replayed=False,
        completed_scientific_checks_replayed=0, native_calls=0, scientific_admission=False)
    tp = out / 'RUNTIME_ALLOCATION_TRANSITION.json'
    durable_json(tp, transition)
    deps['dependency:' + str(tp.relative_to(repo))] = sha(tp)
    binding = copy.deepcopy(metadata['restart_binding'])
    binding.update(controls=controls, dependency_closure=deps)
    child.update(restart_binding=binding, restart_binding_sha256=canonical_sha(binding))
    child.setdefault(TRANSITION_KEY, []).append(dict(path=str(tp.relative_to(repo)), sha256=sha(tp),
                                                  allocation=allocation, diagnostic_runtime=diagnostic))
    preservation = assert_preserved(loaded['arrays'], metadata, arrays, child)
    identity = copy.deepcopy(bundle['identity'])
    identity['control'] = canonical_sha(binding)
    from adaptive_checkpoint import write_adaptive_checkpoint
    generation = inspected['checkpoint']['generation']
    saved = write_adaptive_checkpoint(out / 'CHECKPOINTS', generation, arrays, child, identity)
    result = dict(schema='rei.c13.runtime_allocation_transition_result.v1',
                  checkpoint_directory=str(out / 'CHECKPOINTS'), generation=generation,
                  manifest_sha256=sha(saved / 'manifest.json'), generation_path=str(saved), identity=identity,
                  controls=controls, cursor=inspected['cursor'], target_time_s=TARGET, dependency_closure=deps,
                  parent_dependency_count=transition['parent_dependency_count'], schedule_path=str(out / 'SCHEDULE.json'),
                  source_module_path=str(SOURCE_REL), absorption_module_path=str(ABSORPTION_REL),
                  absorption_sha256=ABSORPTION_SHA, transition_path=str(tp), allocation=allocation,
                  diagnostic_runtime=diagnostic, preservation=preservation, output_copy=output_copy,
                  native_calls=0, scientific_admission=False)
    durable_json(out / 'TRANSITION_RESULT.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--adoption-review', type=Path, required=True)
    parser.add_argument('--parent-root', type=Path, default=PARENT_REL)
    parser.add_argument('--additional-physical-attempts', type=int, default=100)
    args = parser.parse_args()
    result = prepare_runtime_allocation(REPO, args.output_root, args.adoption_review,
                                        parent_root=args.parent_root,
                                        additional_physical_attempts=args.additional_physical_attempts)
    print(json.dumps(dict(generation=result['generation'], manifest_sha256=result['manifest_sha256'],
                         allocation=result['allocation'], native_calls=0), sort_keys=True))


if __name__ == '__main__':
    main()
