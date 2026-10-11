"""New manufactured controller/journal/portable-binding tests; no native work."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from prepare_hpc_run import (allocation_controls, resolve_historical, verify_closure,
                             validate_runtime_config, check_resources, sha)
from run_hpc_chunk import CooperativeStop, execute_chunk, assert_saved_cursor, check_closed_chunks
from production_journal import AttemptJournal, JournalError, durable_json
from adaptive_controller import run_bounded


def cursor():
    # Deliberately nonzero manufactured history; unrelated to saved production.
    return dict(schema='rei.q1b.c11.adaptive_cursor.v1', attempts=9, accepted_macros=7,
                rejected_macros=2, accepted_boundaries=14, accepted_clock_s=3., next_step_s=.25)


def controls():
    return dict(schema='rei.q1b.c11.adaptive_controls.v1', method_order=1,
                physical_state_floor=False, scientific_normalization_changed=False,
                local_defect_target=.01, safety=.8, min_shrink=.2, max_growth=2.,
                min_step_s=1e-8, max_step_s=2., initial_step_s=.25,
                max_attempts=11, max_accepted_macros=9,
                observable_scales={'value': 1.}, distribution_scales={})


class RuntimeTests(unittest.TestCase):
    def test_resource_guard_preserves_config_and_rejects_memory_or_cpu_shortage(self):
        config = dict(schema='rei.hpc.runtime_config.v1', cell_workers=8, worker_timeout_s=120.,
                      native_thread_count=1, map_execution='SERIAL_ORIGINAL_THREE_MAP_CONTROLLER',
                      closure_verification='STARTUP_AND_EXIT_SINGLE_OWNER_IMMUTABLE_INPUTS',
                      checkpoint_format='IMMUTABLE_SEED_PLUS_ACCEPTED_PAIRS',
                      resource_estimates=dict(coordinator_gib=8., worker_gib=1., reserve_gib=8.,
                                              reserve_cores=2, memory_estimates_measured=False))
        frozen = copy.deepcopy(config)
        accepted = check_resources(config, affinity_cpus=64, available_bytes=128*1024**3)
        self.assertEqual(accepted['workers'], 8)
        self.assertFalse(accepted['memory_estimates_measured'])
        self.assertEqual(accepted['memory_reserve_gib'], 8.)
        for cpus, gib in ((8,128), (64,20)):
            with self.subTest(cpus=cpus, gib=gib), self.assertRaisesRegex(ValueError, 'EXCEEDS_RESOURCE_PLAN'):
                check_resources(config, affinity_cpus=cpus, available_bytes=gib*1024**3)
            self.assertEqual(config, frozen)
        with self.assertRaisesRegex(ValueError, 'INSUFFICIENT_MEMORY_HEADROOM'):
            check_resources(config, affinity_cpus=64, available_bytes=7*1024**3)
        local = copy.deepcopy(config)
        local['cell_workers'] = 2
        local['resource_estimates'].update(coordinator_gib=2., worker_gib=.25, reserve_gib=1.)
        self.assertEqual(check_resources(local, affinity_cpus=4, available_bytes=7*1024**3)['workers'], 2)

    def test_portable_private_closure_and_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            file = root / 'research/example/value.bin'
            file.parent.mkdir(parents=True)
            file.write_bytes(b'frozen')
            self.assertEqual(resolve_historical('/old/machine/repo/research/example/value.bin', root), file)
            closure = {'dependency:research/example/value.bin': sha(file)}
            verify_closure(closure, root)
            file.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'FROZEN_DEPENDENCY_DRIFT'):
                verify_closure(closure, root)
            with self.assertRaisesRegex(ValueError, 'TRAVERSAL'):
                resolve_historical('../outside', root)

    def test_allocation_keeps_failure_debit_and_numerics(self):
        old = controls()
        old['max_attempts'] = 9
        allocation = dict(external_failed_attempt_debit=2, all_physical_attempt_cap=11,
                          failed_lanes=[dict(run='A', attempt=4), dict(run='B', attempt=7)])
        new, receipt = allocation_controls(old, cursor(), allocation, 30)
        self.assertEqual(new['max_attempts'], 39)
        self.assertEqual(new['max_accepted_macros'], 37)
        self.assertEqual(receipt['external_failed_attempt_debit'], 2)
        self.assertEqual(receipt['next_physical_attempt_ordinal'], 12)
        self.assertFalse(receipt['counters_reset'])
        self.assertEqual({k:v for k,v in new.items() if not k.startswith('max_')},
                         {k:v for k,v in old.items() if not k.startswith('max_')})

    def test_manufactured_controller_commits_three_maps_and_signal_stops_next_trial(self):
        with tempfile.TemporaryDirectory() as td:
            seed = cursor()
            journal = AttemptJournal(Path(td)/'journal', seed, dict(generation=7, manifest_sha256='a'*64))
            current = dict(t_s=3., value=2.)
            maps = []
            accepted_pairs = []
            stop = CooperativeStop()
            def attempt(saved, number):
                nonlocal current
                one = controls()
                one['max_attempts'] = one['max_accepted_macros'] = 1
                accepted = None
                def step(state, t1):
                    maps.append((state['t_s'], t1))
                    if len(maps) == 1:
                        stop.request(15)
                    return dict(t_s=t1, value=state['value'] + (t1-state['t_s']))
                def commit(pair, trial, after):
                    nonlocal accepted, current
                    accepted_pairs.append(copy.deepcopy(pair))
                    file = Path(td) / f'gen-{after["accepted_macros"]}.json'
                    durable_json(file, dict(pair=pair, cursor=after, trial=trial))
                    current = pair[-1]
                    accepted = dict(cursor=after, trial=trial,
                                    checkpoint=dict(generation=after['accepted_macros'], manifest_sha256=sha(file)))
                result = run_bounded(current, 6., step, lambda s: {'value':s['value']},
                                     lambda s: None, one, cursor=saved, on_accept=commit)
                self.assertEqual(result['cursor'], accepted['cursor'])
                return accepted
            result = execute_chunk(journal, attempt, controls=controls(), target=6., new_attempt_cap=8,
                                   wall_s=100., stop=stop)
            self.assertEqual(result['status'], 'CHUNK_SIGNAL_BOUNDARY')
            self.assertEqual(maps, [(3.,3.25),(3.,3.125),(3.125,3.25)])
            self.assertEqual(len(accepted_pairs[0]), 2)
            self.assertEqual(result['cursor']['attempts'], 10)
            self.assertEqual(result['cursor']['accepted_macros'], 8)
            self.assertEqual(result['cursor']['rejected_macros'], 2)
            resumed = AttemptJournal(Path(td)/'journal', seed, dict(generation=7, manifest_sha256='a'*64))
            self.assertEqual(resumed.head['cursor'], result['cursor'])
            self.assertIsNone(resumed.inflight)

    def test_failure_and_inflight_are_never_retried(self):
        for committed_failure in (False, True):
            with self.subTest(committed_failure=committed_failure), tempfile.TemporaryDirectory() as td:
                ref = dict(generation=7, manifest_sha256='a'*64)
                journal = AttemptJournal(td, cursor(), ref)
                calls = []
                def fail(c, number):
                    calls.append(number)
                    raise ArithmeticError('manufactured worker failure')
                if committed_failure:
                    result = execute_chunk(journal, fail, controls=controls(), target=6.,
                                           new_attempt_cap=3, wall_s=10., stop=CooperativeStop())
                    self.assertEqual(result['status'], 'FAILED_ATTEMPT')
                else:
                    journal.begin({'manufactured':True})
                reopened = AttemptJournal(td, cursor(), ref)
                with self.assertRaises(JournalError):
                    execute_chunk(reopened, fail, controls=controls(), target=6., new_attempt_cap=3,
                                  wall_s=10., stop=CooperativeStop())
                self.assertEqual(len(calls), int(committed_failure))
                self.assertEqual(reopened.head['cursor'], cursor())

    def test_terminal_cap_and_preexisting_signal_open_no_attempt(self):
        for signal_stop in (False, True):
            with tempfile.TemporaryDirectory() as td:
                journal = AttemptJournal(td, cursor(), dict(generation=7, manifest_sha256='a'*64))
                c = controls()
                stop = CooperativeStop()
                if signal_stop:
                    stop.request(15)
                else:
                    c['max_attempts'] = 9
                result = execute_chunk(journal, lambda *args: self.fail('attempt began'), controls=c, target=6.,
                                       new_attempt_cap=2, wall_s=10., stop=stop)
                self.assertEqual(result['status'], 'CHUNK_SIGNAL_BOUNDARY' if signal_stop else 'ALLOCATION_EXHAUSTED')
                self.assertEqual(list(Path(td).glob('attempt-*.begin.json')), [])

    def test_rejection_tail_and_unclosed_chunk_fail_closed(self):
        saved = cursor()
        live = dict(saved, attempts=10, rejected_macros=3)
        assert_saved_cursor(saved, live)
        with self.assertRaisesRegex(ValueError, 'PREFIX_MISMATCH'):
            assert_saved_cursor(saved, dict(live, accepted_clock_s=4.))
        with tempfile.TemporaryDirectory() as td:
            run = Path(td)
            durable_json(run/'CHUNKS/chunk-00000001/LAUNCH.json', {'new':True})
            with self.assertRaisesRegex(ValueError, 'UNRESOLVED_PRIOR_CHUNK'):
                check_closed_chunks(run)


if __name__ == '__main__':
    unittest.main()
