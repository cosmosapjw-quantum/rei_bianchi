"""Independent batch identity/resource/process tests. No HH campaign is run."""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
batch = importlib.import_module("ncp_batch")
source = importlib.import_module("original_source")


def running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    stat = Path(f"/proc/{pid}/stat")
    if stat.exists() and stat.read_text().rsplit(")", 1)[-1].split()[0] == "Z":
        return False
    return True


class BatchChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="phys73_batch_test_")
        self.root = Path(self.temp.name)
        self.counter = self.root / "counter"
        self.product = self.root / "product.bin"
        self.command = [sys.executable, "-c",
                        "import pathlib,sys; c=pathlib.Path(sys.argv[1]); "
                        "c.write_text(str(int(c.read_text())+1) if c.exists() else '1'); "
                        "pathlib.Path(sys.argv[2]).write_bytes(b'fixture-result')",
                        str(self.counter), str(self.product)]
        self.identity = {"purpose": "manufactured-process-test", "source": "fixture_v1"}

    def tearDown(self):
        self.temp.cleanup()

    def job(self, outputs=None, **kwargs):
        return batch.run_job(self.root, "fixture", self.command,
                             [self.product] if outputs is None else outputs,
                             self.identity, 5, **kwargs)

    def test_resume_runs_zero_children_and_preserves_evidence(self):
        first = self.job()
        self.assertEqual(first["status"], "COMPLETE")
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        second = self.job()
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(second["this_invocation"], "REUSED_VERIFIED_NO_CHILD")
        self.assertEqual(self.counter.read_text(), "1")
        self.assertEqual(before, after)

    def test_changed_output_rejects_without_child(self):
        self.job()
        self.product.write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.job()
        self.assertEqual(self.counter.read_text(), "1")

    def test_expected_output_contract_is_bound(self):
        self.job()
        with self.assertRaises(ValueError):
            self.job(outputs=[self.root / "different.bin"])
        self.assertEqual(self.counter.read_text(), "1")

    def test_explicit_child_environment_is_bound(self):
        self.job(environment={"PHYS73_FIXTURE_CONTEXT": "first"})
        with self.assertRaises(ValueError):
            self.job(environment={"PHYS73_FIXTURE_CONTEXT": "changed"})
        self.assertEqual(self.counter.read_text(), "1")

    def test_success_receipt_cannot_drop_payload_membership(self):
        self.job()
        path = self.root / "jobs/fixture/SUCCESS.json"
        receipt = json.loads(path.read_text())
        receipt["outputs_sha256"] = {}
        path.write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):
            self.job()
        self.assertEqual(self.counter.read_text(), "1")

    def test_success_receipt_must_record_zero_exit(self):
        self.job()
        path = self.root / "jobs/fixture/SUCCESS.json"
        receipt = json.loads(path.read_text())
        receipt["exit_code"] = 2
        path.write_text(json.dumps(receipt))
        with self.assertRaises(ValueError):
            self.job()
        self.assertEqual(self.counter.read_text(), "1")

    def test_directory_membership_change_is_detected(self):
        directory = self.root / "payload"
        directory.mkdir()
        self.product = directory / "product.bin"
        self.command[-1] = str(self.product)
        self.job(outputs=[directory])
        (directory / "new-unbound-payload").write_bytes(b"extra")
        with self.assertRaises(ValueError):
            self.job(outputs=[directory])
        self.assertEqual(self.counter.read_text(), "1")

    def test_directory_symlink_is_not_silently_omitted(self):
        directory = self.root / "payload"
        directory.mkdir()
        self.product = directory / "product.bin"
        self.command[-1] = str(self.product)
        target = self.root / "external.bin"
        target.write_bytes(b"external")
        (directory / "alias.bin").symlink_to(target)
        result = self.job(outputs=[directory])
        self.assertEqual(result["status"], "FAILED")
        self.assertIn("OUTPUT_VALIDATION", result["failure"])
        self.assertFalse((self.root / "jobs/fixture/SUCCESS.json").exists())

    def test_top_level_output_symlink_is_rejected(self):
        target = self.root / "external.bin"
        target.write_bytes(b"external")
        self.product.symlink_to(target)
        try:
            result = self.job()
        except ValueError:
            pass
        else:
            self.assertEqual(result["status"], "FAILED")
            self.assertIn("OUTPUT_VALIDATION", result["failure"])
        self.assertFalse((self.root / "jobs/fixture/SUCCESS.json").exists())

    @unittest.skipUnless(hasattr(os, "killpg"), "POSIX process groups required")
    def test_timeout_stops_own_descendants_and_preserves_unrelated_process(self):
        ready = self.root / "grandchild.pid"
        child_code = ("import os,pathlib,signal,sys,time; "
                      "signal.signal(signal.SIGTERM,signal.SIG_IGN); "
                      "pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(30)")
        leader_code = ("import subprocess,sys,time; "
                       "subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]]); time.sleep(30)")
        unrelated = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(30)"],
                                     start_new_session=True)
        record = None
        try:
            record = batch.run_job(self.root, "timeout", [sys.executable, "-c", leader_code,
                                    child_code, str(ready)], [], self.identity, 0.5)
            self.assertEqual(record["status"], "FAILED")
            self.assertEqual(record["failure"], "WALL_TIMEOUT")
            self.assertTrue(ready.exists(), "grandchild must start before timeout")
            descendant = int(ready.read_text())
            # SIGKILL delivery is asynchronous; allow bounded kernel scheduling/reaping time.
            until = time.monotonic() + 2.0
            while running(descendant) and time.monotonic() < until:
                time.sleep(0.01)
            self.assertFalse(running(descendant), "own SIGTERM-resistant descendant leaked")
            self.assertIsNone(unrelated.poll(), "unrelated process was stopped")
        finally:
            if record and record.get("child_pid"):
                try:
                    os.killpg(record["child_pid"], signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if ready.exists():
                try:
                    os.kill(int(ready.read_text()), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            unrelated.terminate()
            try:
                unrelated.wait(timeout=2)
            except subprocess.TimeoutExpired:
                unrelated.kill()
                unrelated.wait()

    def test_resource_plan_accounts_64_cpu_128_gib_and_small_hosts(self):
        for cpus, memory in [(64, 128), (8, 8), (1, 5), (4, 16)]:
            observed = {"effective_cpus": cpus, "effective_memory_bytes": memory * 2**30}
            plan = batch.resource_plan(64, 128, observed)
            self.assertLessEqual(plan["legacy_reserved_cpus"], cpus)
            self.assertLessEqual(plan["legacy_reserved_gib"], memory - plan["reserve_gib"])
            self.assertLessEqual(plan["source_preparation_workers"], cpus)
            self.assertLessEqual(plan["source_preparation_workers"] * plan["source_worker_memory_gib"],
                                 memory - plan["reserve_gib"])
            if cpus == 64:
                self.assertEqual(plan["source_preparation_workers"], 64)

    def test_too_small_memory_has_an_input_error(self):
        with self.assertRaises(ValueError):
            batch.resource_plan(8, 4, {"effective_cpus": 8, "effective_memory_bytes": 4 * 2**30})


class PreparationChecks(unittest.TestCase):
    def test_api_rejects_mislabeled_physics_before_evaluation(self):
        request = source.validated_request(0, 3, 8, 28, 40)
        request["eta_C"] = "0"
        with tempfile.TemporaryDirectory(prefix="phys73_prepare_guard_") as root:
            with patch.object(source, "angular_forcing", side_effect=AssertionError("must not evaluate")):
                with self.assertRaises(ValueError):
                    source.prepare(Path(root) / "bad", request)

    def test_resume_requires_expected_payload_membership(self):
        request = source.validated_request(0, 3, 8, 28, 40)

        def fake_coulomb_task(spec):
            # Manufactured packet: the test exercises receipt identity, not special functions.
            ell, radii, _, weighted = spec[:4]
            return dict(ell=ell, d=[complex(i) for i in range(len(radii))],
                        t=[0j] + [1 + 0j] * (len(radii) - 1), x=[complex(x) for x in weighted],
                        seconds=0.0, new_Coulomb_nodes=0, cache_hits=0, cache_path=None)

        with tempfile.TemporaryDirectory(prefix="phys73_prepare_resume_") as root:
            with patch.object(source, "coulomb_task", side_effect=fake_coulomb_task):
                source.prepare(root, request)
            receipt_path = Path(root) / "PREPARED.json"
            receipt = json.loads(receipt_path.read_text())
            receipt["files_sha256"] = {}
            receipt_path.write_text(json.dumps(receipt))
            with patch.object(source, "coulomb_task", side_effect=AssertionError("must not evaluate")):
                with self.assertRaises(ValueError):
                    source.prepare(root, request)


if __name__ == "__main__":
    unittest.main(verbosity=2)
