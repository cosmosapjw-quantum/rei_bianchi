"""Focused no-science tests: synthetic byte-pinned files, fake solver and model.

No solve_ivp, owner integration, benchmark, or prior trajectory replay occurs.
The real archive is separately checked by the CLI --preflight read-only action.
"""
from copy import deepcopy
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import continue_saved as c


class FakeModel:
    def __init__(self):
        self.src = SimpleNamespace(aref=c.AREF, href=1., xmax=math.log(4.2))
        self.momentum = SimpleNamespace(cell_numbers=np.ones((2, 2)))
        self.amplitudes = []
        self.rhs_calls = 0
        self.diagnostic_shapes = []

    def set_amplitude(self, value):
        self.amplitudes.append(value)

    def initial(self, *args):
        raise AssertionError("historical initialization is prohibited")

    def solve(self, *args):
        raise AssertionError("historical integration is prohibited")

    def rhs(self, x, y):
        self.rhs_calls += 1
        return np.array([1., 0., 0., 0., 0., 0., 0., 0.])

    def diagnostics(self, x, state):
        self.diagnostic_shapes.append((x.shape, state.shape))
        n = len(x)
        pm = np.full(n, .02)
        pr = np.full(n, -.01)
        return {"x": x, "zbar": 1/(c.AREF*np.exp(x))-1,
                "H_per_s": np.full(n, 1e-17), "E0": state[3], "E2": state[4],
                "s_over_H": state[2], "Sigma": math.sqrt(3)*abs(state[2]),
                "sampled_min_angular_brightness": np.ones(n),
                "signed_Pi_m": pm, "signed_Pi_r": pr, "signed_Pi_total": pm+pr,
                "Pi_m": abs(pm), "Pi_r": abs(pr), "Pi_total": abs(pm+pr),
                "p_m_J_m3": pm, "p_r_J_m3": pr}


class FakeSolver:
    def __init__(self, corrupt_restart=False):
        self.calls = 0
        self.corrupt_restart = corrupt_restart
        self.arguments = None

    def __call__(self, rhs, interval, y0, *, t_eval, method, rtol, atol):
        self.calls += 1
        self.arguments = (interval, y0.copy(), method, rtol, atol, t_eval.copy())
        rhs(interval[0], y0)
        state = np.repeat(y0[:, None], len(t_eval), axis=1)
        state[0] += t_eval - t_eval[0]
        if self.corrupt_restart:
            state[0, 0] = np.nextafter(state[0, 0], np.inf)
        return SimpleNamespace(success=True, message="FAKE_SOLVER_NO_SCIENCE", t=t_eval.copy(), y=state, nfev=1)


class ZeroSlots:
    def __init__(self):
        self.calls = 0
        self.capacity = 128

    def acquire(self, task):
        self.calls += 1
        return None, {"slots": 0, "reason": "synthetic other work uses capacity"}

    def release(self, key):
        raise AssertionError("no lease was acquired")


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.owner = self.root / "owner"
        self.owner.mkdir()
        names = ["pilot.py", "SOURCE_ATTRIBUTION.json", "vendor/canonical_fv.py",
                 "vendor/lrs_boltzmann.py", "vendor/species_hierarchy.py",
                 "vendor/REI_BACKGROUND_FAMILY_LOCK.json", "matter_radiation_20261021/component_pilot.py"]
        files = {}
        manifest = []
        for name in names:
            path = self.owner / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("SYNTHETIC_NON_EXECUTABLE_OWNER_FIXTURE:" + name)
            files[name] = c.sha(path)
            manifest.append({"path": c.PREFIX+name, "sha256": files[name], "size_bytes": path.stat().st_size})
        self.files = files
        parent_files = {k: v for k, v in files.items() if k != "matter_radiation_20261021/component_pilot.py"}
        rows = []
        for i, (cid, group, lane, amplitude, rel) in enumerate([
            ("r00", "radiation625", "RADIATION_SLICE", 0., "results/pilot/cases/r00.npz"),
            ("m00", "matter600_mixed6", "MIXED_CANCELLATION", .4, "matter_radiation_20261021/results/new_sweep/cases/m00.npz"),
        ]):
            raw_path = self.owner / rel
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            x = np.linspace(0., math.log(4.2), 65)
            state = np.zeros((8, 65), dtype=np.float64)
            state[0] = np.linspace(0., 5., 65)
            state[2] = 1e-5
            state[3] = 1.
            z = np.linspace(20., 4., 65)
            h = np.full(65, 1e-17)
            np.savez(raw_path, state=state, x=x, zbar=z, H_per_s=h)
            initial = {"q": 1e-5} if i == 0 else {"q": 1e-5, "A_m": amplitude}
            identity = ({"model_files": parent_files, "configuration": {"massive_A": 0.}}
                        if i == 0 else {"parent_immutable_files": parent_files,
                                        "new_model_sha256": files["matter_radiation_20261021/component_pilot.py"]})
            receipt = {"status": "COMPLETED", "state_count": 8,
                       "case": {"id": cid, "lane": lane}, "identity": identity, "initial": initial}
            receipt_path = raw_path.with_suffix(".json")
            receipt_path.write_text(json.dumps(receipt))
            if i == 0:
                decomposition = self.owner / "matter_radiation_20261021/decomposition/cases" / (cid+".npz")
                decomposition.parent.mkdir(parents=True, exist_ok=True)
                np.savez(decomposition, x=x, zbar=z, H_per_s=h,
                         signed_Pi_m=np.full(65, .02), signed_Pi_r=np.full(65, -.01),
                         signed_Pi_total=np.full(65, .01))
                manifest.append({"path": c.PREFIX+decomposition.relative_to(self.owner).as_posix(),
                                 "sha256": c.sha(decomposition), "size_bytes": decomposition.stat().st_size})
            for path in (raw_path, receipt_path):
                relative = path.relative_to(self.owner).as_posix()
                manifest.append({"path": c.PREFIX+relative, "sha256": c.sha(path), "size_bytes": path.stat().st_size})
            rows.append({"case_id": cid, "group": group, "lane": lane, "npz_path": rel,
                         "npz_sha256": c.sha(raw_path), "receipt_sha256": c.sha(receipt_path),
                         "initial_matter_A": amplitude, "initial": initial,
                         "terminal": {"state": state[:, -1].tolist(), "x": float(x[-1]),
                                      "zbar": 4., "H_per_s": float(h[-1])}})
        self.lock_path = self.root / "OWNER_LOCK.json"
        self.lock_path.write_text(json.dumps({"upstream_archive_sha256": c.PINS["archive"], "files": files}))
        manifest_path = self.owner / "MATTER_RADIATION_PAYLOAD_MANIFEST.json"
        manifest_path.write_text(json.dumps({"files": manifest}))
        self.index_path = self.root / "terminal.json"
        self.index_path.write_text(json.dumps({"schema": "REI198_SAVED_TERMINAL_INDEX_V1",
            "archive_sha256": c.PINS["archive"], "state_order": c.STATE_ORDER, "rows": rows}))
        patches = {"owner_lock": c.sha(self.lock_path), "manifest": c.sha(manifest_path), "terminal_index": c.sha(self.index_path)}
        self.patcher = patch.dict(c.PINS, patches)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        count_patch = patch.object(c, "EXPECTED_CASES", 2)
        count_patch.start()
        self.addCleanup(count_patch.stop)
        self.output = self.root / "output"
        self.output.mkdir()
        (self.output / "cases").mkdir()

    def bundle(self):
        return c.preflight(self.owner, self.index_path, self.lock_path)

    def task(self, bundle, i=0):
        row = bundle["rows"][i]
        return {"bundle": bundle, "row": row, "case_dir": str(self.output / "cases" / row["case_id"]),
                "deadline_monotonic": time.monotonic()+20.,
                "cost_snapshot": {"committed_prior_run_wall_s": 0., "finished_case_cpu_s_at_dispatch": 0.}}

    def test_preflight_pins_both_scopes_without_loading_owner(self):
        with patch.object(c, "_load_owner", side_effect=AssertionError("preflight imported physics")):
            bundle = self.bundle()
        self.assertEqual(bundle["summary"]["status"], "PREFLIGHT_PASS_NO_ODE")
        self.assertEqual(bundle["summary"]["new_ODE_solves"], 0)
        self.assertEqual(bundle["rows"][1]["amplitude_from_receipt"], .4)
        self.assertEqual(bundle["identity"]["solver"], {"method": "DOP853", "rtol": 3e-11, "atol": 3e-13})

    def test_fake_solver_continuation_and_completed_resume(self):
        bundle = self.bundle()
        task = self.task(bundle, 1)
        model, solver = FakeModel(), FakeSolver()
        result = c.execute_case(task, model=model, solver=solver)
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(model.amplitudes, [.4])
        self.assertEqual(model.diagnostic_shapes, [((33,), (8, 33)), ((33,), (8, 33))])
        interval, y0, method, rtol, atol, grid = solver.arguments
        self.assertEqual(interval, (task["row"]["terminal"]["x"], c.TARGET_X))
        self.assertEqual((method, rtol, atol), ("DOP853", 3e-11, 3e-13))
        self.assertEqual(len(grid), 33)
        path = Path(task["case_dir"]) / "history.npz"
        original_bytes = path.read_bytes()
        with np.load(path, allow_pickle=False) as tail:
            self.assertEqual(c.f64_bytes(tail["state"][:, 0]), c.f64_bytes(y0))
            np.testing.assert_array_equal(tail["signed_Pi_total"], tail["signed_Pi_m"]+tail["signed_Pi_r"])
            np.testing.assert_array_equal(tail["Pi_total_frobenius"], math.sqrt(2)*abs(tail["signed_Pi_total"]))
            np.testing.assert_array_equal(tail["pi_total_33_J_m3"], tail["pi_m_33_J_m3"]+tail["pi_r_33_J_m3"])
            self.assertEqual(str(tail["scope"]), c.SCOPE)
        resumed = c.execute_case(task, model=model, solver=lambda *a, **k: self.fail("resume called solver"))
        self.assertEqual(resumed["dispatch_status"], "SKIPPED_COMPLETED_NO_ODE")
        self.assertEqual(path.read_bytes(), original_bytes)
        self.assertEqual(solver.calls, 1)

    def test_source_mismatch_fails_preflight(self):
        (self.owner / "pilot.py").write_text("changed source")
        with self.assertRaisesRegex(ValueError, "OWNER_SOURCE_SHA256_MISMATCH"):
            self.bundle()

    def test_saved_endpoint_mismatch_fails_before_solver(self):
        bundle = self.bundle()
        row = deepcopy(bundle["rows"][0])
        row["terminal"]["state"][0] = np.nextafter(row["terminal"]["state"][0], np.inf)
        with self.assertRaisesRegex(ValueError, "TERMINAL_STATE_BIT_IDENTITY_MISMATCH"):
            c.validate_case(self.owner, row, self.files, bundle["manifest"])

    def test_source_changes_after_preflight_fail_before_solver(self):
        task = self.task(self.bundle())
        (self.owner / "pilot.py").write_text("changed between dispatch and worker")
        solver = FakeSolver()
        result = c.execute_case(task, model=FakeModel(), solver=solver)
        self.assertEqual(result["status"], "FAILED_PRESERVED_NO_AUTOMATIC_RETRY")
        self.assertEqual(result["new_ODE_solves"], 0)
        self.assertEqual(solver.calls, 0)
        self.assertIn("OWNER_SOURCE_SHA256_MISMATCH", result["error"])

    def test_boundary_diagnostic_mismatch_fails_before_solver(self):
        task = self.task(self.bundle())
        model, solver = FakeModel(), FakeSolver()
        original = model.diagnostics
        def changed(x, state):
            data = original(x, state)
            data["H_per_s"] *= 2
            return data
        model.diagnostics = changed
        result = c.execute_case(task, model=model, solver=solver)
        self.assertEqual(result["status"], "FAILED_PRESERVED_NO_AUTOMATIC_RETRY")
        self.assertEqual(result["new_ODE_solves"], 0)
        self.assertEqual(solver.calls, 0)
        self.assertIn("RESTART_DIAGNOSTIC_NOT_BIT_IDENTICAL:H_per_s", result["error"])

    def test_returned_restart_mismatch_preserves_failure(self):
        task = self.task(self.bundle())
        result = c.execute_case(task, model=FakeModel(), solver=FakeSolver(corrupt_restart=True))
        self.assertEqual(result["status"], "FAILED_PRESERVED_NO_AUTOMATIC_RETRY")
        self.assertIn("RESTART_STATE_OR_CLOCK_NOT_BIT_IDENTICAL", result["error"])
        self.assertTrue((Path(task["case_dir"]) / "FAILED.json").is_file())
        with self.assertRaises(FileExistsError):
            c.execute_case(task, model=FakeModel(), solver=FakeSolver())

    def test_completed_history_tamper_prevents_resume(self):
        task = self.task(self.bundle())
        c.execute_case(task, model=FakeModel(), solver=FakeSolver())
        (Path(task["case_dir"]) / "history.npz").write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "COMPLETED_HISTORY_SHA256_MISMATCH"):
            c.execute_case(task, model=FakeModel(), solver=FakeSolver())

    def test_no_resource_slots_checkpoint_does_not_launch(self):
        pool = ZeroSlots()
        with patch.object(c, "execute_case", side_effect=AssertionError("no slot must not launch")):
            result = c.schedule(self.bundle(), self.output, max_new_cases=2, max_workers=2, pool=pool)
        self.assertEqual(result["status"], "PENDING_CHECKPOINT")
        self.assertEqual(result["new_cases_dispatched"], 0)
        self.assertEqual(pool.calls, 1)
        self.assertEqual(pool.capacity, 64)
        self.assertEqual(len(result["pending_selected_cases"]), 2)
        self.assertFalse(any((self.output / "cases").iterdir()))
        self.assertTrue(list((self.output / "invocations").glob("*/FINISHED.json")))

    def test_unfinished_invocation_charges_reserved_wall(self):
        invocation = self.output / "invocations" / "interrupted"
        invocation.mkdir(parents=True)
        c.dump_new(invocation / "STARTED.json", {"wall_reservation_s": c.CUMULATIVE_WALL_LIMIT_S})
        self.assertEqual(c._costs(self.output)["run_wall_s"], c.CUMULATIVE_WALL_LIMIT_S)
        result = c.schedule(self.bundle(), self.output, max_new_cases=2, pool=ZeroSlots())
        self.assertEqual(result["new_cases_dispatched"], 0)
        self.assertEqual(result["deferral"], "CUMULATIVE_WALL_BUDGET_EXHAUSTED")


if __name__ == "__main__":
    unittest.main()
