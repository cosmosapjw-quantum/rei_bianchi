#!/usr/bin/env python3
"""Run new bounded trials with an ordered cell pool and one durable coordinator.

Frozen dependency bytes are verified at startup and exit, not between maps.
This explicitly requires an immutable input tree and single owner of this run.
SIGTERM is cooperative: finish/reconcile the active trial, then start no next
trial. Wall time is likewise a boundary budget, not a per-map kill deadline.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
Q1B = HERE.parent
REPO = Q1B.parents[2]
for directory in (Q1B / 'c10', Q1B, Q1B.parent / 'n1', Q1B / 'c11/precision',
                  Q1B / 'c11/controller', Q1B / 'c11/restart', Q1B / 'c11/endpoint',
                  Q1B / 'c11/integration', Q1B / 'c11/integration/production', HERE):
    sys.path.insert(0, str(directory))
from production_journal import (AttemptJournal, JournalError, durable_json, ensure_json, fsync_dir,
                                run_chunk, reconcile_output_records)
from prepare_hpc_run import (REL, canonical_sha, check_resources, require, resolve_historical, sha,
                             verify_runtime_bundle, verify_runtime_inputs)

OK_STATUSES = {'CHUNK_ATTEMPT_BOUNDARY', 'CHUNK_WALL_BOUNDARY', 'CHUNK_SIGNAL_BOUNDARY',
               'ALLOCATION_EXHAUSTED', 'REACHED_FULL_TARGET', 'CHUNK_RECOVERED_COMMIT_BOUNDARY'}


class CooperativeStop:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.requested = False
        self.signal_number = None
        self._first_clock = True
        self._previous = {}

    def request(self, signum=None, frame=None):
        self.requested = True
        self.signal_number = signum

    def budget_clock(self):
        # run_chunk takes its origin on the first call. Always give it a finite
        # origin, even if SIGTERM arrived just before entry; later checks stop.
        if self._first_clock:
            self._first_clock = False
            return self.clock()
        return math.inf if self.requested else self.clock()

    def __enter__(self):
        for signum in (signal.SIGTERM, signal.SIGINT):
            self._previous[signum] = signal.signal(signum, self.request)
        return self

    def __exit__(self, *args):
        for signum, handler in self._previous.items():
            signal.signal(signum, handler)


def execute_chunk(journal, attempt, *, controls, target, new_attempt_cap, wall_s, stop,
                  request=None, reconcile=None):
    """Original transaction loop; only its wall clock gains cooperative signals."""
    result = run_chunk(journal, attempt, target=target, total_attempts=controls['max_attempts'],
                       total_macros=controls['max_accepted_macros'], new_attempt_cap=new_attempt_cap,
                       wall_s=wall_s, clock=stop.budget_clock, request=request, reconcile=reconcile)
    if result['status'] == 'CHUNK_WALL_BOUNDARY' and stop.requested:
        result['status'] = 'CHUNK_SIGNAL_BOUNDARY'
    result['stop_signal'] = stop.signal_number
    return result


def save_state(path, state):
    import numpy as np
    from native_step_v3 import COUNTER_NAMES
    with Path(path).open('xb') as handle:
        np.savez_compressed(handle, t_s=state['t_s'], gas=state['gas'], N=state['N'], U_eV=state['U_eV'],
                            R=state['R'], support=state['support'],
                            counters=np.array([state['counters'][key] for key in COUNTER_NAMES]),
                            nH_ref=state['nH_ref'], nHe_ref=state['nHe_ref'])
        handle.flush()
        os.fsync(handle.fileno())
    fsync_dir(Path(path).parent)


def import_source(relative):
    path = resolve_historical(relative, REPO)
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('hpc_pinned_source_precision', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def runtime_inputs(bundle):
    """Use saved original moments and explicit private provider-data location."""
    import numpy as np
    import provider as provider_module
    from grid_cells import load_grid
    from source_cells import CellSource
    from native_step_v3 import initial_state
    parent_repo = Path(bundle['parent_repo'])
    provider_module.PHYSICAL = parent_repo / 'research/physical_provider_20261010'
    provider = provider_module.HistoryProvider(r=0.)
    source = CellSource(provider, load_grid(Q1B / 'GRID_C2.json'))
    with np.load(parent_repo / REL / 'evidence/SOURCE_C2.npz', allow_pickle=False) as saved:
        initial = initial_state(source, saved_initial=saved)
    return provider, source, initial


def assert_saved_cursor(saved, live):
    for key in ('accepted_clock_s', 'accepted_macros', 'accepted_boundaries'):
        require(saved[key] == live[key], 'JOURNAL_CHECKPOINT_PREFIX_MISMATCH')
    require(saved['attempts'] <= live['attempts'] and
            live['attempts'] - saved['attempts'] == live['rejected_macros'] - saved['rejected_macros'],
            'JOURNAL_CHECKPOINT_REJECTION_TAIL')


def check_closed_chunks(run):
    for path in (run / 'CHUNKS').glob('chunk-*'):
        require((path / 'LAUNCH.json').exists() and (path / 'RESULT.json').exists(),
                'UNRESOLVED_PRIOR_CHUNK_NO_IMPLICIT_RETRY:' + path.name)
        old = json.loads((path / 'RESULT.json').read_text())
        require(old['status'] in OK_STATUSES, 'FAILED_PRIOR_CHUNK_REQUIRES_EXPLICIT_REVIEW:' + path.name)


def _run_locked(args, bundle, out, stop):
    started = time.monotonic()
    verify_runtime_inputs(bundle)
    resource_observation = check_resources(bundle['runtime_config'])
    import numpy as np
    from adaptive_controller import run_bounded, native_observables, next_boundary
    from run_adaptive_native_v2 import strict_validate, NativeCell, ledger, convert
    from cell_history_fields import build_record, physical_state_sha256, geometry_diagnostics, FIELDS24
    from segmented_checkpoint import SegmentedStore
    from ordered_cell_pool import Pool
    from native_step_hpc import positive_native_step

    controls, schedule, target = bundle['controls'], bundle['schedule'], bundle['target_time_s']
    store = SegmentedStore(bundle['checkpoint_directory'])
    journal = AttemptJournal(out / 'JOURNAL', bundle['cursor'], bundle['seed_checkpoint'])
    def publish(rows):
        reconcile_output_records(out / 'OUTPUT24', rows)
    def reconcile(begin):
        receipt = store.reconcile(begin, sha(journal._path(begin['attempt'], 'begin')))
        if receipt is not None:
            loaded = store.load(receipt['checkpoint'])
            publish(loaded['metadata']['production_transaction']['output_records'])
        return receipt
    journal.resume(reconcile)
    loaded = store.load(journal.head['checkpoint'])
    require(loaded['metadata']['hpc_runtime_binding'] == bundle['runtime_binding'], 'HPC_CHECKPOINT_BINDING')
    assert_saved_cursor(loaded['cursor'], journal.head['cursor'])
    # A process loss is reviewed explicitly; an accepted atomic transaction can
    # be reconciled above without computing anything, but never silently rerun.
    check_closed_chunks(out)
    provider, source, initial = runtime_inputs(bundle)
    source_api = import_source(bundle['source_module_path'])
    require(sha(resolve_historical(bundle['source_module_path'], REPO)) == bundle['parent_identity']['source'],
            'SOURCE_IDENTITY_CHANGED')
    absorption = resolve_historical(bundle['absorption_module_path'], REPO)
    require(sha(absorption) == bundle['absorption_sha256'], 'ABSORPTION_IDENTITY_CHANGED')
    require(physical_state_sha256(initial) == physical_state_sha256(loaded['initial_state']), 'ORIGINAL_IC_CHANGED')
    current = loaded['state']
    output_history = list(loaded['output_records'])
    publish(output_history)
    initial_receipt = json.loads((out / 'INITIAL_OUTPUT_DONE.json').read_text())
    require(initial_receipt['record']['state_sha256'] == physical_state_sha256(initial) and
            initial_receipt['row_sha256'] == sha(out / 'OUTPUT24/epoch-000.json'), 'INITIAL_OUTPUT_IDENTITY')
    def validate(state):
        strict_validate(state, initial, provider)
        require(geometry_diagnostics(source, state['t_s'])['max_error'] <= 1e-11, 'ORIGINAL_GEOMETRY_GATE')
    chunks = out / 'CHUNKS'
    chunks.mkdir(exist_ok=True)
    sequence = 1 + max([int(p.name.split('-')[1]) for p in chunks.glob('chunk-*')] or [0])
    chunk = chunks / f'chunk-{sequence:08d}'
    chunk.mkdir(exist_ok=False)
    durable_json(chunk / 'LAUNCH.json', dict(schema='rei.hpc.chunk_launch.v1',
        transition_bundle_sha256=sha(args.transition_bundle), runtime_binding_sha256=bundle['runtime_binding_sha256'],
        checkpoint=journal.head['checkpoint'], cursor=journal.head['cursor'],
        new_attempt_cap=args.new_attempt_cap, cooperative_wall_s=args.wall_s,
        total_controls=controls, runtime_config=bundle['runtime_config'], pid=os.getpid(),
        startup_resource_plan=resource_observation,
        python=sys.version, numpy=np.__version__, scientific_admission=False, speedup_claim=None,
        completed_scientific_checks_replayed=0))
    # Preserve executed source bytes once; dependency closure lives in HPCMETA.
    for relative, digest in bundle['execution_pins'].items():
        if Path(relative).suffix != '.py':
            continue
        path = out / 'ASRUN' / relative
        if path.exists():
            require(sha(path) == digest, 'ASRUN_SOURCE_DRIFT')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                handle.write((REPO / relative).read_bytes()); handle.flush(); os.fsync(handle.fileno())
            fsync_dir(path.parent)
    config = bundle['runtime_config']
    native = pool = None
    calls = 0
    new_checkpoints = []
    map_metrics = []
    result = None
    try:
        # Check terminal budgets before even opening native processes.
        if (journal.head['cursor']['attempts'] >= controls['max_attempts'] or
            journal.head['cursor']['accepted_macros'] >= controls['max_accepted_macros'] or
            journal.head['cursor']['accepted_clock_s'] == target or stop.requested):
            def no_attempt(*unused):
                raise AssertionError('TERMINAL_ALLOCATION_STARTED_MAP')
            result = execute_chunk(journal, no_attempt, controls=controls, target=target,
                new_attempt_cap=args.new_attempt_cap, wall_s=max(args.wall_s, 1e-9), stop=stop)
        else:
            parent_repo = Path(bundle['parent_repo'])
            with Pool(workers=config['cell_workers'], timeout_s=config['worker_timeout_s'],
                      opacity_binary=parent_repo / 'research/accel02_20261011/n1/native/target/release/rei_n1_native',
                      absorption_path=absorption) as pool, NativeCell(
                      parent_repo / REL / 'native/target/release/rei_q1b_cell_native_v1') as native:
                require(pool.metrics['opacity_binding'] == 'PINNED_NATIVE_OPACITY', 'TEST_OPACITY_NOT_ALLOWED_IN_RUNTIME')
                def request(cursor):
                    t1, kind = next_boundary(cursor['accepted_clock_s'], cursor['next_step_s'], target,
                                             schedule['hard_events_s'])
                    debit = bundle['allocation']['external_failed_attempt_debit']
                    return dict(t0_s=cursor['accepted_clock_s'], t1_s=t1, boundary_kind=kind,
                        target_time_s=target, input_state_sha256=physical_state_sha256(current),
                        external_failed_attempt_debit=debit,
                        new_physical_attempt_ordinal=cursor['attempts'] + debit + 1,
                        runtime_binding_sha256=bundle['runtime_binding_sha256'])
                def attempt(cursor, number):
                    nonlocal current, calls
                    accepted_receipt = None
                    step_count = 0
                    adir = out / 'ATTEMPTS' / f'attempt-{number:08d}'
                    adir.mkdir(parents=True, exist_ok=False)
                    one = copy.deepcopy(controls)
                    one['max_attempts'] = one['max_accepted_macros'] = 1
                    durable_json(adir / 'CONTROL_LINEAGE.json', dict(total_controls=controls,
                        total_controls_canonical_sha256=canonical_sha(controls), actual_effective_controls=one,
                        saved_cursor=cursor, counters_reset=False, numerical_controls_changed=False))
                    def step(state, t1):
                        nonlocal calls, step_count
                        calls += 1
                        step_count += 1
                        stem = adir / f'MAP_{step_count:02d}'
                        file = lambda suffix: stem.with_name(stem.name + suffix)
                        save_state(file('_INPUT.npz'), state)
                        durable_json(file('_REQUEST.json'), dict(t0_s=state['t_s'], t1_s=t1,
                            input_file_sha256=sha(file('_INPUT.npz')),
                            input_state_sha256=physical_state_sha256(state),
                            runtime_binding_sha256=bundle['runtime_binding_sha256']))
                        require(not pool.pop_refinement_records(), 'STALE_ABSORPTION_REFINEMENT_RECORDS')
                        try:
                            value = positive_native_step(state, t1, source, pool, native, source_api=source_api)
                        finally:
                            refinements = pool.pop_refinement_records()
                            durable_json(file('_ABSORPTION_REFINEMENTS.json'), convert(dict(records=refinements)))
                        value['diagnostics']['absorption_refinements'] = refinements
                        save_state(file('_OUTPUT.npz'), value)
                        durable_json(file('_DIAGNOSTICS.json'), convert(value['diagnostics']))
                        metrics = convert(value['hpc_metrics'])
                        durable_json(file('_PERFORMANCE.json'), metrics)
                        map_metrics.append(metrics)
                        return value
                    def accepted(pair, trial, new_cursor):
                        nonlocal current, accepted_receipt
                        records = []
                        for half, state in enumerate(pair, 1):
                            validate(state)
                            save_state(adir / f'ACCEPTED_HALF_{half}.npz', state)
                            if state['t_s'] in schedule['output_epochs_s']:
                                index = schedule['output_epochs_s'].index(state['t_s'])
                                records.append(build_record(state, source, source_api=source_api,
                                    epoch_index=index, generation=new_cursor['accepted_macros'],
                                    state_sha256=physical_state_sha256(state), ledger=ledger(state, initial)))
                        transaction = dict(attempt=number, begin_sha256=sha(journal._path(number, 'begin')),
                                           trial=trial, output_records=records)
                        checkpoint = store.commit(pair, new_cursor, trial, transaction, records)
                        current = pair[-1]
                        output_history.extend(records)
                        publish(records)
                        new_checkpoints.append(checkpoint)
                        accepted_receipt = dict(cursor=new_cursor, trial=trial, checkpoint=checkpoint)
                        print(json.dumps(convert(dict(event='ACCEPTED_CHECKPOINT', checkpoint=checkpoint,
                            cursor=new_cursor, elapsed_s=time.monotonic() - started))), flush=True)
                    outcome = run_bounded(current, target, step, lambda state: native_observables(state, provider),
                                          validate, one, hard_events=schedule['hard_events_s'],
                                          cursor=cursor, on_accept=accepted)
                    require(len(outcome['attempts']) == 1, 'EXACTLY_ONE_NEW_TRIAL_REQUIRED')
                    trial = outcome['attempts'][0]
                    receipt = accepted_receipt if trial['accepted'] else dict(cursor=outcome['cursor'], trial=trial,
                                                    checkpoint=copy.deepcopy(journal.head['checkpoint']))
                    require(receipt['cursor'] == outcome['cursor'], 'TRANSACTION_CURSOR_MISMATCH')
                    durable_json(adir / 'RESULT.json', convert(receipt))
                    return convert(receipt)
                result = execute_chunk(journal, attempt, controls=controls, target=target,
                    new_attempt_cap=args.new_attempt_cap, wall_s=max(1e-9, args.wall_s - (time.monotonic() - started)),
                    stop=stop, request=request, reconcile=reconcile)
                if result['status'] == 'REACHED_FULL_TARGET':
                    require(len(output_history) == len(schedule['output_epochs_s']), 'FULL_OUTPUT_COUNT')
                    require(all(row['time_s'] == schedule['output_epochs_s'][i] and set(row['fields']) == set(FIELDS24)
                                for i, row in enumerate(output_history)), 'FULL_OUTPUT_BINDING')
                    ensure_json(out / 'FULL_HISTORY_REACHED.json', dict(cursor=result['cursor'],
                        checkpoint=result['checkpoint'], scientific_admission=False, convergence='NOT_EVALUATED'))
    except Exception as exc:
        result = dict(schema='rei.hpc.chunk_result.v1', status='FAILED_CHUNK_SETUP_OR_PUBLICATION',
            failure=dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc()),
            cursor=journal.head['cursor'], checkpoint=journal.head['checkpoint'], scientific_admission=False)
    finally:
        try:
            verify_runtime_inputs(bundle)
        except Exception as exc:
            result = dict(status='FAILED_EXIT_IDENTITY_CHECK', failure=dict(type=type(exc).__name__, message=str(exc)),
                          prior_result=result, cursor=journal.head['cursor'], checkpoint=journal.head['checkpoint'])
        if result is None:
            result = dict(status='UNEXPECTED_NO_RESULT', cursor=journal.head['cursor'], checkpoint=journal.head['checkpoint'])
        result.update(schema='rei.hpc.chunk_result.v1', native_calls=0 if native is None else native.calls,
            opacity_calls=0 if pool is None else pool.native_calls,
            sigma_energy_evaluations=0 if pool is None else pool.energy_evaluations,
            trial_map_calls=calls, elapsed_s=time.monotonic() - started, new_checkpoints=new_checkpoints,
            output_epoch_count=len(list((out / 'OUTPUT24').glob('epoch-*.json'))), target_time_s=target,
            old_completed_replays=0, completed_scientific_checks_replayed=0, scientific_admission=False,
            performance=dict(map_metrics=map_metrics, speedup_claim=None), stop_signal=stop.signal_number)
        if pool is not None:
            result['worker_pool'] = convert(pool.metrics)
            result['worker_failure_receipt'] = convert(getattr(pool, 'failure_receipt', None))
            result['worker_cleanup_receipt'] = convert(getattr(pool, 'cleanup_receipt', None))
        durable_json(chunk / 'RESULT.json', convert(result))
    print(json.dumps(convert(result)), flush=True)
    return 0 if result['status'] in OK_STATUSES else 1


def _run(args):
    bundle = json.loads(args.transition_bundle.read_text())
    verify_runtime_bundle(bundle)
    out = Path(bundle['work_root']) / 'RUN'
    require(Path(bundle['checkpoint_directory']).resolve() == out.parent / 'CHECKPOINTS', 'HPC_WORK_ROOT_BINDING')
    require(args.transition_bundle.resolve() == out.parent / 'HPCMETA/TRANSITION_RESULT.json', 'HPC_BUNDLE_LOCATION')
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        require(os.environ.get(name) == '1', 'SET_SINGLE_THREAD_ENV_BEFORE_PYTHON:' + name)
    if hasattr(os, 'sched_getaffinity'):
        require(bundle['runtime_config']['cell_workers'] <= len(os.sched_getaffinity(0)), 'WORKERS_EXCEED_CPU_AFFINITY')
    with (out / 'RUN.lock').open('a+b') as lock, CooperativeStop() as stop:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise JournalError('ANOTHER_CHUNK_PROCESS_OWNS_RUN') from None
        return _run_locked(args, bundle, out, stop)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transition-bundle', type=Path, required=True)
    parser.add_argument('--new-attempt-cap', type=int, default=10000)
    parser.add_argument('--wall-s', type=float, default=43200.)
    args = parser.parse_args()
    if args.new_attempt_cap <= 0 or not math.isfinite(args.wall_s) or args.wall_s <= 0:
        parser.error('positive attempt and finite wall budgets required')
    return _run(args)


if __name__ == '__main__':
    raise SystemExit(main())
