"""New controller boundaries using manufactured receipts; no scientific imports."""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SRC))
import batch_entry as batch
import build_parallel as build


class BuildAdapterTests(unittest.TestCase):
    def test_command_and_receipt_record_effective_jobs(self):
        calls, receipts = [], []
        target = types.SimpleNamespace(
            checked=lambda argv, out, label, wall: calls.append((argv, label, wall)),
            atomic_json=lambda p, v: receipts.append(dict(v)))
        sentinel = object()
        with patch.dict(os.environ):
            build.adapt_builder(target, 8, "a"*40, sentinel)
            target.checked(["cargo", "build", "--release", "--locked", "--lib"], Path("out"), "build", 1800)
            target.atomic_json(Path("BUILD_IDENTITY.json"), {"build_jobs": 2, "physical_runs": 0})
            self.assertEqual(os.environ["CARGO_BUILD_JOBS"], "8")
        self.assertIs(target.run_process, sentinel)
        self.assertEqual(calls[0][0][-2:], ["--jobs", "8"])
        self.assertEqual(calls[0][2], 1800)
        self.assertEqual(receipts[0]["build_jobs"], 8)
        self.assertFalse(receipts[0]["resource_adapter"]["numeric_flags_or_bridge_source_modified"])

    def test_unexpected_build_and_receipt_rejected(self):
        target = types.SimpleNamespace(checked=lambda *a: None, atomic_json=lambda *a: None)
        build.adapt_builder(target, 4, "a"*40, lambda *a: None)
        with self.assertRaises(ValueError):
            target.checked(["cargo", "test"], Path("x"), "build", 1800)
        with self.assertRaises(ValueError):
            target.atomic_json(Path("BUILD_IDENTITY.json"), {"build_jobs": 99, "physical_runs": 0})

    def test_nonbuild_command_not_rewritten(self):
        seen = []
        target = types.SimpleNamespace(checked=lambda *a: seen.append(a), atomic_json=lambda *a: None)
        build.adapt_builder(target, 8, "a"*40, lambda *a: None)
        target.checked(["git", "fetch", "origin", "pin"], Path("x"), "fetch", 300)
        self.assertEqual(seen[0][0], ["git", "fetch", "origin", "pin"])


class SavedIntakeTests(unittest.TestCase):
    def test_complete_and_empty_started_canary_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "one/canary").mkdir(parents=True)
            (root / "two").mkdir()
            (root / "two/RESULT.json").write_text(json.dumps({"schema": "he29.hpc64.canary.v1", "status": "CANARY_COMPLETED_SCOPED"}))
            result = batch.saved_intake([root])
            self.assertFalse(result["execution_allowed"])
            self.assertEqual(len(result["canary_evidence"]), 2)
            self.assertTrue(result["complete_in_declared_scope"])

    def test_malformed_raw_and_incomplete_scan_block(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "PACKED_RAW.json").write_text("not JSON")
            self.assertFalse(batch.saved_intake([root])["execution_allowed"])
            (root / "nested").mkdir()
            result = batch.saved_intake([root], max_directories=1)
            self.assertFalse(result["complete_in_declared_scope"])

    def test_verified_source_checkout_and_explicit_exclusions_not_runtime(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "checkout/.git").mkdir(parents=True)
            (root / "checkout/PACKED_RAW.json").write_text("not runtime")
            (root / "own").mkdir()
            (root / "own/PACKED_RAW.json").write_text("own new boundary")
            self.assertTrue(batch.saved_intake([root], [root / "own"])["execution_allowed"])


class BatchDispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ("newsource", "packed", "controller", "baseline", "data", "old", "bridge/target/release"):
            (self.root / name).mkdir(parents=True)
        (self.root / "bridge/target/release/libhe29_optimized_bridge.so").write_bytes(b"manufactured-library")
        (self.root / "bridge/BUILD_IDENTITY.json").write_text("{}")
        self.out = self.root / "out"
        self.argv = ["run", "--out", str(self.out), "--packed-root", str(self.root / "packed"),
            "--controller-root", str(self.root / "controller"), "--baseline-campaign", str(self.root / "baseline"),
            "--data-root", str(self.root / "data"), "--binary", str(self.root / "binary"),
            "--owner-receipt", str(self.root / "owner.json"), "--table-cache", str(self.root / "cache"),
            "--source-revision", "b"*40, "--observe-root", str(self.root / "old"),
            "--bridge-build", str(self.root / "bridge"), "--lease", str(self.root / "lease")]
        self.events = []
        self.process = {"execution_allowed": True, "hold_reasons": [], "matches": []}
        self.resource = {"execution_allowed": True, "hold_reasons": [], "cpu_ids": [0, 1], "table_workers": 2, "build_jobs": 2}
        self.runner = types.SimpleNamespace(
            verify_build=lambda *a: {"bass_publication_head": batch.PACKED_REVISION},
            baseline_contract=lambda *a: ({"table_sha256": batch.TABLE_SHA256}, {"pairs": 4}))
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in [("REPO", self.root / "newsource"), ("checked_checkout", lambda *a: {}),
            ("host_execution_lease", lambda *a: contextlib.nullcontext()), ("observe_host", lambda: {}),
            ("choose_resources", lambda *a, **k: self.resource), ("active_he29_processes", lambda *a: self.process),
            ("load_a5", lambda *a: self.runner), ("check_sources_external", lambda *a: ({"binary_sha256": "fake"}, {"data_files_sha_verified": 22})),
            ("watchdog_for", lambda *a: self.fake_watchdog)]:
            self.stack.enter_context(patch.object(batch, name, value))
        self.stack.enter_context(patch.dict(sys.modules, {"reference_runner": types.SimpleNamespace()}))
        self.stack.enter_context(patch.dict(os.environ))
        self.stack.enter_context(patch.object(os, "sched_getaffinity", return_value={0, 1, 2}))
        self.affinity = self.stack.enter_context(patch.object(os, "sched_setaffinity"))

    def fake_watchdog(self, argv, out, wall):
        self.events.append((argv, wall))
        case = Path(argv[argv.index("--out")+1]); case.mkdir()
        (case / "RESULT.json").write_text("{}")
        return {"returncode": 0, "timed_out": False, "wall_s": 1.0}

    def test_single_reused_bridge_dispatch_keeps_solver_contract(self):
        self.assertEqual(batch.main(self.argv), 0)
        self.assertEqual(len(self.events), 1)
        argv, wall = self.events[0]
        self.assertEqual(wall, 900)
        self.assertEqual(argv[argv.index("--table-workers")+1], "2")
        self.assertEqual(argv[argv.index("--sync-every")+1], "256")
        self.assertEqual(os.environ[batch.WORKER_FLAG], "1")
        self.assertTrue((self.out / "BASELINE_BEFORE_BUILD.json").is_file())
        summary = json.loads((self.out / "SUMMARY.json").read_text())
        self.assertEqual(summary["activity"]["baseline_pairs_started"], 0)
        self.assertEqual(summary["activity"]["new_builds_started"], 0)
        self.assertEqual(summary["solver_threads"], 1)
        self.affinity.assert_any_call(0, {0, 1, 2})

    def test_existing_return_blocks_dispatch_and_build(self):
        (self.root / "old/PACKED_RAW.json").write_text("{}")
        self.assertEqual(batch.main(self.argv), 2)
        self.assertEqual(self.events, [])
        self.assertFalse((self.out / "BRIDGE_INTAKE.json").exists())

    def test_resource_hold_plan_is_read_only(self):
        self.resource["execution_allowed"] = False
        self.argv[0] = "plan"
        with patch.object(batch, "load_a5", side_effect=AssertionError("must not import physics")):
            self.assertEqual(batch.main(self.argv), 2)
        self.assertEqual(self.events, [])

    def test_late_process_start_blocks_under_same_lease(self):
        with patch.object(batch, "active_he29_processes", side_effect=[self.process, {"execution_allowed": False}]):
            with self.assertRaisesRegex(RuntimeError, "PROCESS_CHANGED"):
                batch.main(self.argv)
        self.assertEqual(self.events, [])
        self.assertTrue((self.out / "FAILURE.json").exists())

    def test_failed_worker_is_not_admitted_or_retried(self):
        with patch.object(batch, "watchdog_for", return_value=lambda *a: {"returncode": 1, "timed_out": True}):
            self.assertEqual(batch.main(self.argv), 1)
        result = json.loads((self.out / "SUMMARY.json").read_text())
        self.assertEqual(result["status"], "HOLD_FIRST_FAILURE")
        self.assertEqual(result["activity"]["canary_workers_started"], 1)

    def test_existing_output_not_overwritten(self):
        self.out.mkdir()
        (self.out / "original").write_bytes(b"saved")
        with self.assertRaises(FileExistsError):
            batch.main(self.argv)
        self.assertEqual((self.out / "original").read_bytes(), b"saved")
        self.assertEqual(self.events, [])


if __name__ == "__main__":
    unittest.main()
