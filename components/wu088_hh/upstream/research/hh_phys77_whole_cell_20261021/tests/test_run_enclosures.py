"""Contract tests use a fake JSON worker only: zero real enclosure/ODE calls."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_enclosures", ROOT / "source/run_enclosures.py")
runner = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "source"))
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)
RESOURCE_CANDIDATES = [runner.DEFAULT_RESOURCES,
    ROOT.parent / "WU088_HH_PHYS77/research/hh_phys74_rei_pilot_20261021/resources.py"]
RESOURCES = next((p for p in RESOURCE_CANDIDATES if p.exists()), None)

FAKE_ENGINE = '''"""Fake engine: no physics, integration, or interval evaluation."""
import hashlib, json
def certify_request(request):
    mode = request.get("fake_mode", "pass")
    if mode == "raise":
        raise RuntimeError("injected fake failure")
    count = request["config"]["max_cells"]
    case_id = request["table"]["provenance"]["case_identity"]["case_id"]
    digest = hashlib.sha256(json.dumps(request, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return {"status": "NOT_CERTIFIED_REQUESTED_PREFIX" if mode == "noncert" else "PASS_REQUESTED_PREFIX",
        "case_id": "wrong" if mode == "bad_id" else case_id,
        "request_sha256": "0" * 64 if mode == "bad_hash" else digest,
        "requested_cells": count, "enclosed_cells": 0 if mode == "noncert" else count,
        "fake_worker_no_physics": True, "NCP_jobs": 0}
'''


def fake_result(request):
    namespace = {}
    exec(FAKE_ENGINE, namespace)
    return namespace["certify_request"](request)


class FakeAdmission:
    """A deterministic admission stub used only with the fake engine."""
    def __init__(self, available=True):
        self.available, self.live, self.serial, self.peak = available, set(), 0, 0

    def acquire(self, task):
        if not self.available:
            return None, {"fake_available_slots": 0}
        self.serial += 1
        key = str(self.serial)
        self.live.add(key)
        self.peak = max(self.peak, len(self.live))
        return key, {"fake_available_slots": 2}

    def handoff(self, key, pid):
        assert key in self.live and pid > 0

    def release(self, key):
        self.live.remove(key)
        return None


class RunnerContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "run_enclosures.py").write_bytes(Path(runner.__file__).read_bytes())
        (self.source / "cell_enclosure.py").write_text(FAKE_ENGINE)
        self.requests = self.root / "requests"
        self.requests.mkdir()
        self.output = self.root / "output"
        self.lock = self.source / "RUNNER_SOURCE_LOCK.json"
        self.freeze()

    def freeze(self, **extra):
        document = {"schema": runner.LOCK_SCHEMA, "entry_file": "cell_enclosure.py",
                    "entry_function": "certify_request", "files": {
                        name: runner.sha_bytes((self.source / name).read_bytes())
                        for name in ("run_enclosures.py", "cell_enclosure.py")}, **extra}
        self.lock.write_bytes(runner.canonical(document))

    def request(self, case="case0", mode="pass"):
        value = {"schema": "PHYS77_ENCLOSURE_REQUEST_V1",
                 "table": {"provenance": {"case_identity": {"case_id": case}}},
                 "predictor": {"x": ["0", "0.1", "0.2"]},
                 "config": {"max_cells": 1}, "fake_mode": mode, "label": "가"}
        (self.requests / (case + ".json")).write_bytes(runner.canonical(value))
        return value

    def preflight(self, **kwargs):
        return runner.preflight(self.requests, self.output, self.lock, RESOURCES, **kwargs)

    def execute(self, bundle, worker=fake_result, retry=False, index=0):
        return runner.execute_case({"row": bundle["rows"][index], "guard": bundle["guard"],
            "output": str(self.output), "retry_failed": retry}, worker=worker)

    def test_preflight_is_read_only_and_does_not_import_engine(self):
        (self.source / "cell_enclosure.py").write_text("raise RuntimeError('must not import')\n")
        self.freeze()
        self.request()
        bundle = self.preflight()
        self.assertEqual(bundle["eligible_cases"], 1)
        self.assertFalse(self.output.exists())
        self.assertNotIn("cell_enclosure", __import__("sys").modules)

    def test_nested_case_and_exact_exporter_canonical_hash(self):
        request = self.request("bound_case")
        row = self.preflight()["rows"][0]
        self.assertEqual(row["case_id"], "bound_case")
        expected = runner.sha_bytes(json.dumps(request, sort_keys=True,
            separators=(",", ":"), allow_nan=False).encode())
        self.assertEqual(row["identity"]["request_canonical_sha256"], expected)
        self.assertNotEqual(row["identity"]["request_sha256"], expected)
        request["case_id"] = "conflicting"
        (self.requests / "bound_case.json").write_bytes(runner.canonical(request))
        with self.assertRaisesRegex(ValueError, "CONFLICTING_CASE_ID"):
            self.preflight()

    def test_source_mismatch_rejected_preflight_and_before_worker(self):
        self.request()
        bundle = self.preflight()
        with (self.source / "cell_enclosure.py").open("a") as f:
            f.write("\n# changed\n")
        with self.assertRaisesRegex(ValueError, "SHA256_MISMATCH"):
            self.preflight()
        worker = mock.Mock(side_effect=AssertionError("must not call"))
        result = self.execute(bundle, worker)
        self.assertEqual(result["status"], "FAILED_PRESERVED")
        self.assertEqual(result["new_enclosure_calls"], 0)
        worker.assert_not_called()

    def test_resource_helper_and_external_dependency_guards(self):
        bad_helper = self.root / "resources.py"
        bad_helper.write_text("# unpinned helper\n")
        with self.assertRaisesRegex(ValueError, "SHA256_MISMATCH"):
            runner.load_source_lock(self.lock, bad_helper)
        document = json.loads(self.lock.read_text())
        (self.source / "owner_interval.py").write_text("# fake owner\n")
        document["files"]["owner_interval.py"] = runner.sha_bytes((self.source / "owner_interval.py").read_bytes())
        self.lock.write_bytes(runner.canonical(document))
        with self.assertRaisesRegex(ValueError, "EXACT_EXTERNAL_TRANSPORT_LOCK"):
            runner.load_source_lock(self.lock, RESOURCES)

    def test_input_mutation_after_preflight_never_calls_worker(self):
        self.request()
        bundle = self.preflight()
        with (self.requests / "case0.json").open("a") as f:
            f.write(" ")
        worker = mock.Mock(side_effect=AssertionError("must not call"))
        result = self.execute(bundle, worker)
        self.assertEqual(result["status"], "FAILED_PRESERVED")
        self.assertEqual(result["new_enclosure_calls"], 0)
        worker.assert_not_called()

    def test_postcall_input_change_preserves_first_result_without_acceptance(self):
        request = self.request()
        bundle = self.preflight()
        expected = fake_result(request)
        def mutate_input(value):
            with (self.requests / "case0.json").open("a") as f:
                f.write(" ")
            return fake_result(value)
        first = self.execute(bundle, mutate_input)
        attempt = runner.case_directory(self.output, bundle["rows"][0]) / first["attempt"]
        self.assertEqual(first["status"], "FAILED_PRESERVED")
        self.assertEqual(first["new_enclosure_calls"], 1)
        self.assertEqual(json.loads((attempt / "RESULT_UNVERIFIED.json").read_text()), expected)
        self.assertTrue((attempt / "FAILED.json").exists())
        self.assertFalse((attempt / "COMPLETED.json").exists())
        self.assertFalse((attempt / "result.json").exists())
        failure = json.loads((attempt / "FAILED.json").read_text())
        self.assertEqual(failure["unverified_result_sha256"],
                         runner.sha_bytes((attempt / "RESULT_UNVERIFIED.json").read_bytes()))
        worker = mock.Mock(side_effect=AssertionError("must not replay"))
        self.assertEqual(self.execute(bundle, worker)["status"], "PRIOR_ATTEMPT_PRESERVED")
        worker.assert_not_called()

    def test_completed_resume_is_hash_verified_and_never_replayed(self):
        self.request()
        bundle = self.preflight()
        worker = mock.Mock(side_effect=fake_result)
        first = self.execute(bundle, worker)
        directory = runner.case_directory(self.output, bundle["rows"][0])
        artifacts = {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
        second = self.execute(bundle, worker, retry=True)
        self.assertEqual(first["status"], "COMPLETED")
        self.assertEqual(second["status"], "SKIPPED_COMPLETED")
        self.assertEqual(worker.call_count, 1)
        self.assertEqual(artifacts, {str(p.relative_to(directory)): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()})
        self.assertEqual(self.preflight()["completed_skipped"], 1)

    def test_corrupt_completion_blocks_even_explicit_retry(self):
        self.request()
        bundle = self.preflight()
        self.execute(bundle)
        directory = runner.case_directory(self.output, bundle["rows"][0])
        result_path = next(directory.glob("attempt-*/result.json"))
        with result_path.open("a") as f:
            f.write(" ")
        worker = mock.Mock(side_effect=AssertionError("must not call"))
        result = self.execute(bundle, worker, retry=True)
        self.assertEqual(result["status"], "BLOCKED_CORRUPT_OR_UNSAFE_OUTPUT")
        self.assertEqual(self.preflight(retry_failed=True)["eligible_cases"], 0)
        worker.assert_not_called()

    def test_noncertificate_is_not_completed_and_retry_preserves_prior_attempt(self):
        self.request(mode="noncert")
        bundle = self.preflight()
        first = self.execute(bundle)
        directory = runner.case_directory(self.output, bundle["rows"][0])
        first_attempt = directory / first["attempt"]
        old = {p.name: p.read_bytes() for p in first_attempt.iterdir()}
        self.assertEqual(first["status"], "NOT_CERTIFIED_PRESERVED")
        self.assertFalse((first_attempt / "COMPLETED.json").exists())
        self.assertTrue((first_attempt / "NOT_CERTIFIED.json").exists())
        worker = mock.Mock(side_effect=fake_result)
        self.assertEqual(self.execute(bundle, worker)["status"], "PRIOR_ATTEMPT_PRESERVED")
        worker.assert_not_called()
        self.assertEqual(self.preflight()["eligible_cases"], 0)
        self.assertEqual(self.preflight(retry_failed=True)["eligible_cases"], 1)
        retry = self.execute(bundle, worker, retry=True)
        self.assertNotEqual(first["attempt"], retry["attempt"])
        self.assertEqual(old, {p.name: p.read_bytes() for p in first_attempt.iterdir()})

    def test_exception_preserved_and_requires_explicit_distinct_retry(self):
        self.request(mode="raise")
        bundle = self.preflight()
        first = self.execute(bundle)
        self.assertEqual(first["status"], "FAILED_PRESERVED")
        self.assertEqual(self.execute(bundle)["status"], "PRIOR_ATTEMPT_PRESERVED")
        retry = self.execute(bundle, retry=True)
        self.assertEqual(retry["status"], "FAILED_PRESERVED")
        self.assertNotEqual(first["attempt"], retry["attempt"])

    def test_result_identity_mismatch_is_not_accepted(self):
        for case, mode in (("bad0", "bad_id"), ("bad1", "bad_hash")):
            self.request(case, mode)
        bundle = self.preflight()
        for index in range(2):
            result = self.execute(bundle, index=index)
            self.assertEqual(result["status"], "FAILED_PRESERVED")
            self.assertIn("RESULT_REQUEST_IDENTITY_MISMATCH", result["error"])

    def test_case_lock_conflict_is_pending_and_makes_no_attempt(self):
        self.request()
        bundle = self.preflight()
        directory = runner.case_directory(self.output, bundle["rows"][0])
        worker = mock.Mock(side_effect=AssertionError("must not call"))
        with runner.case_lock(directory):
            result = self.execute(bundle, worker)
        self.assertEqual(result["status"], "PENDING_CASE_LOCK")
        self.assertFalse(list(directory.glob("attempt-*")))
        worker.assert_not_called()

    def test_resource_caps_and_remaining_shared_capacity(self):
        values = dict(affinity_cpus=256, quota_cpus=None, busy_cores=0, load1=0,
            host_cpus=256, available_gib=1024, capacity_gib=1024, reserve_gib=16, job_gib=1)
        self.assertEqual(runner.resource_slots(**values), 64)
        self.assertEqual(runner.resource_slots(**{**values, "job_gib": 8}), 14)
        self.assertEqual(runner.resource_slots(**{**values, "quota_cpus": 0.9}), 0)
        self.assertEqual(runner.resource_slots(**{**values, "quota_cpus": 2}), 2)
        shared = {**values, "affinity_cpus": 64, "host_cpus": 64, "busy_cores": 40,
            "load1": 40, "available_gib": 96, "capacity_gib": 128, "leased_cpus": 40,
            "leased_gib": 40}
        self.assertEqual(runner.resource_slots(**shared), 24)
        self.assertEqual(runner.resource_slots(**{**shared, "available_gib": 15}), 0)

    def test_no_available_lease_and_zero_budget_are_pending_without_dispatch(self):
        self.request()
        bundle = self.preflight()
        admission = FakeAdmission(available=False)
        result = runner.run_batch(bundle, self.output, workers=64, max_new_cases=1,
                                  admission=admission)
        self.assertEqual(result["status"], "PENDING_CHECKPOINT")
        self.assertEqual(result["launched_jobs"], 0)
        self.assertEqual(result["new_enclosure_calls"], 0)
        self.assertFalse((self.output / "cases").exists())
        with mock.patch.object(runner, "SharedAdmission", side_effect=AssertionError("no leases needed")):
            result = runner.run_batch(bundle, self.output, workers=64, max_new_cases=0)
        self.assertEqual(result["launched_jobs"], 0)

    def test_shared_lease_lock_is_nonblocking_and_preserves_peer_lease(self):
        module = runner._resource_module(RESOURCES)
        with mock.patch.object(module, "_start", return_value="synthetic-start"), \
             mock.patch.object(runner, "_resource_module", return_value=module):
            admission = runner.SharedAdmission(RESOURCES, self.root / "leases", 16, 1)
        # Only synthetic capacity observations are mocked; actual flock and
        # pinned HH74 lease read/write ownership checks are exercised here.
        admission.pool.capacity = admission.pool.cap = 64
        peer = admission.pool.path / "lease-peer.json"
        record = dict(owner="another-session", pid=os.getpid(), start=admission.pool.start,
            boot=admission.pool.boot, cpus=63, gib=63, task="synthetic-live-peer")
        peer.write_bytes(runner.canonical(record))
        peer_bytes = peer.read_bytes()
        with mock.patch.object(runner, "sample_resources", return_value={"admissible_slots": 1}), \
             mock.patch.object(admission.module, "_start", return_value="synthetic-start"), \
             mock.patch.object(admission.module, "busy_cores", return_value=0), \
             mock.patch.object(admission.module, "memory_available", return_value=(128 * runner.GIB, 128 * runner.GIB)):
            with admission.pool.locked():
                key, observation = admission.acquire("fake-only")
                self.assertIsNone(key)
                self.assertEqual(observation["status"], "PENDING_SHARED_LEASE_OR_RESOURCE_OBSERVATION")
            key, _ = admission.acquire("fake-only")
            self.assertIsNotNone(key)
            admission.handoff(key, os.getpid())
            second, _ = admission.acquire("no-capacity-left")
            self.assertIsNone(second)
            self.assertIsNone(admission.release(key))
        self.assertEqual(peer.read_bytes(), peer_bytes)

    def test_unobservable_pid_namespace_defers_without_touching_lease_directory(self):
        module = runner._resource_module(RESOURCES)
        leases = self.root / "must-remain-absent"
        with mock.patch.object(module, "_start", return_value="DEAD"), \
             mock.patch.object(runner, "_resource_module", return_value=module):
            with self.assertRaisesRegex(RuntimeError, "PID_NAMESPACE_LIVENESS_UNOBSERVABLE"):
                runner.SharedAdmission(RESOURCES, leases, 16, 1)
        self.assertFalse(leases.exists())

    def test_spawned_fake_workers_are_bounded_and_resume_only_pending(self):
        for case in ("a", "b", "c"):
            self.request(case)
        admission = FakeAdmission()
        result = runner.run_batch(self.preflight(), self.output, workers=2, max_new_cases=2,
                                  admission=admission, max_dispatch_seconds=30)
        self.assertEqual(result["new_enclosure_calls"], 2)
        self.assertEqual(result["accepted_completions"], 2)
        self.assertEqual(result["undispatched_cases"], ["c"])
        self.assertLessEqual(result["max_active_observed"], 2)
        self.assertEqual(admission.live, set())
        bundle = self.preflight()
        self.assertEqual(bundle["completed_skipped"], 2)
        result2 = runner.run_batch(bundle, self.output, workers=2, max_new_cases=3,
                                   admission=FakeAdmission(), max_dispatch_seconds=30)
        self.assertEqual(result2["new_enclosure_calls"], 1)
        self.assertEqual(result2["accepted_completions"], 1)
        self.assertEqual(result2["status"], "COMPLETE_SELECTED_REQUESTS")


if __name__ == "__main__":
    unittest.main()
