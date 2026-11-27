"""Persistence/resource checks with fake workers only: no scientific IVPs."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
import run_pilot as runner


class RunnerGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "source").mkdir()
        for name in ("atomic_network.py", "coupled_model.py", "kinetic.py", "plot_pilot.py", "run_pilot.py"):
            (self.root / "source" / name).write_text("# fake source, never imported\n")
        tables = self.root / "vendor" / "atomic"
        tables.mkdir(parents=True)
        for name in ("photo.dat", "rec_table1.dat"):
            (tables / name).write_text("fake table for persistence tests only\n")
        self.output = self.root / "results"
        self.manifest = runner.scientific_manifest(self.root)
        self.case = runner.default_cases("control")[0]
        self.options = runner.normalize_options()
        self.key, self.binding = runner.identity(self.case, self.options, self.manifest)
        self.payload = dict(output=str(self.output), root=str(self.root), case=self.case,
                            key=self.key, binding=self.binding)

    def tearDown(self):
        self.temp.cleanup()

    def fake_solver(self, case, **options):
        return {"x": np.array([0., 1.]), "species_names": np.array(["FAKE"])}, {
            "status": "COMPLETED_EXPLORATORY", "case": case, **options,
            "fixture_only": True}

    def test_science_identity_ignores_labels_and_operational_code(self):
        alias = {**self.case, "id": "another_thread_label", "notes": "metadata"}
        self.assertEqual(runner.identity(alias, None, self.manifest)[0], self.key)
        self.assertEqual(runner.identity({**alias, "T_initial_K": 300.}, None, self.manifest)[0], self.key)
        for name in ("plot_pilot.py", "run_pilot.py"):
            (self.root / "source" / name).write_text("# changed operational code\n")
        self.assertEqual(runner.scientific_manifest(self.root), self.manifest)
        (self.root / "source" / "kinetic.py").write_text("# changed scientific code\n")
        self.assertNotEqual(runner.scientific_manifest(self.root), self.manifest)
        self.assertNotEqual(runner.identity({**alias, "A_m": .8}, None, self.manifest)[0], self.key)

    def test_31_unique_pilot_cases_and_control_identity_is_shared(self):
        keys = [runner.identity(case, None, self.manifest)[0] for case in runner.default_cases()]
        self.assertEqual(len(keys), 31)
        self.assertEqual(len(set(keys)), 31)
        self.assertIn(self.key, keys)

    def test_completion_is_reused_and_corruption_never_replayed(self):
        with patch.object(runner, "_get_solver", return_value=self.fake_solver) as getter:
            first = runner._execute_case(self.payload)
            second = runner._execute_case(self.payload)
        self.assertEqual(first["status"], "COMPLETE")
        self.assertEqual(second["status"], "SKIPPED_COMPLETE")
        self.assertEqual(getter.call_count, 1)
        raw, _ = runner._case_paths(self.output, self.key)
        with raw.open("ab") as stream:
            stream.write(b"tamper")
        with patch.object(runner, "_get_solver", side_effect=AssertionError("MUST_NOT_EXECUTE")):
            result = runner._execute_case(self.payload)
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("CASE_DATA_INTEGRITY", result["error"])
        self.assertEqual(result["new_ode_calls"], 0)

    def test_failed_attempt_is_preserved_without_automatic_retry(self):
        def failing(*args, **kwargs):
            raise ArithmeticError("FAKE_FIRST_ATTEMPT_FAILURE")
        with patch.object(runner, "_get_solver", return_value=failing) as getter:
            first = runner._execute_case(self.payload)
            second = runner._execute_case(self.payload)
        self.assertEqual(first["status"], "FAILED")
        self.assertEqual(second["status"], "FAILED_PREVIOUS_ATTEMPT")
        self.assertEqual(getter.call_count, 1)
        self.assertEqual(len(list((self.output / "attempts").glob("*/*/FAILED.json"))), 1)

    def test_adoption_checks_execution_identity_and_does_not_solve(self):
        arrays, metadata = self.fake_solver(self.case, **self.options)
        existing = self.root / "completed_debug_case.npz"
        np.savez_compressed(existing, **arrays)
        changed = copy.deepcopy(self.manifest)
        changed["sha256"] = "different execution source"
        with self.assertRaisesRegex(ValueError, "ADOPTION_SOURCE_BINDING"):
            runner.adopt_completed(self.output, self.case, self.options, self.manifest,
                                   existing, metadata, changed, root=self.root)
        with patch.object(runner, "_get_solver", side_effect=AssertionError("NO_ODE_ALLOWED")):
            result = runner.adopt_completed(self.output, self.case, self.options, self.manifest,
                                            existing, metadata, self.manifest, root=self.root)
        self.assertEqual(result["status"], "COMPLETE")
        state, record = runner.existing_case(self.output, self.key, self.binding)
        self.assertEqual(state, "COMPLETE")
        self.assertEqual(record["provenance"]["new_ode_calls"], 0)
        self.assertEqual(record["npz"]["sha256"], runner.sha_file(existing))

    def test_resources_are_shared_and_foreign_lease_cannot_be_released(self):
        observation = {"cap_cpus": 8, "reserve_cpus": 1, "sampled_idle_cpus": 7.,
                       "available_gib": 6., "capacity_gib": 8., "reserve_gib": 1.5, "job_gib": .5}
        self.assertEqual(runner.resource_slots(observation, []), 6)
        self.assertEqual(runner.resource_slots(observation, [{"cpus": 6, "gib": 3.}]), 1)
        self.assertEqual(runner.resource_slots({**observation, "available_gib": 1.6}, []), 0)
        pool = runner.LeasePool(self.root / "leases")
        with patch.object(runner, "observe_resources", return_value=observation):
            token, _ = pool.acquire("FAKE_TEST_TASK")
        self.assertIsNotNone(token)
        with self.assertRaisesRegex(RuntimeError, "FOREIGN_LEASE_RELEASE_REFUSED"):
            runner.release_lease({**token, "owner": "someone_else"})
        runner.release_lease(token)
        self.assertFalse(list((self.root / "leases").glob("lease-*.json")))

    def test_preflight_never_imports_solver_or_starts_executor(self):
        observation = {"cap_cpus": 8, "reserve_cpus": 1}
        with patch.object(runner, "observe_resources", return_value=observation), \
             patch.object(runner, "_get_solver", side_effect=AssertionError("NO_ODE_ALLOWED")), \
             patch.object(runner.cf, "ProcessPoolExecutor", side_effect=AssertionError("NO_WORKER_ALLOWED")):
            result = runner.run_cases([self.case], self.output, preflight=True, root=self.root)
        self.assertEqual(result["status"], "PREFLIGHT")
        self.assertEqual(result["new_ode_calls"], 0)
        self.assertEqual(json.loads((self.output / "RUN.json").read_text())["pending_science_ids"], [self.key])


if __name__ == "__main__":
    unittest.main()
