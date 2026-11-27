"""Small resource/lease/recovery checks; these execute no scientific solver."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("he30_shared_runner", ROOT / "src" / "shared_runner.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def snapshot(n=64, total_gib=128, available_gib=128, quota=None):
    return {"affinity_cpu_ids": list(range(n)), "cpu_quota": quota,
            "cpu_busy": {c: 0. for c in range(n)}, "memory_limit_bytes": total_gib * r.GIB,
            "memory_available_bytes": available_gib * r.GIB}


class CapacityTests(unittest.TestCase):
    def test_ncp_profile_and_no_magic_cpu_exclusion(self):
        cap = r.capacity(snapshot(), 100)
        self.assertEqual(cap["new_workers"], 62)
        self.assertIn(55, cap["cpu_ids"])
        self.assertEqual(cap["memory_reserve_bytes"], 16 * r.GIB)

    def test_small_host_reserve_and_pending_cap(self):
        self.assertEqual(r.capacity(snapshot(n=1, total_gib=2, available_gib=2), 3)["new_workers"], 1)
        self.assertEqual(r.capacity(snapshot(), 1)["new_workers"], 1)
        self.assertEqual(r.capacity(snapshot(quota=3.9), 10)["new_workers"], 1)

    def test_active_memory_not_charged_twice(self):
        cap = r.capacity(snapshot(n=8, total_gib=8, available_gib=4), 20, active=2)
        self.assertEqual(cap["available_memory_new_slots"], 3)
        self.assertEqual(cap["new_workers"], 3)

    def test_other_load_reduces_capacity_without_global_hold(self):
        snap = snapshot(n=8, total_gib=16, available_gib=16)
        snap["cpu_busy"][0] = snap["cpu_busy"][1] = 1.
        self.assertEqual(r.capacity(snap, 20)["new_workers"], 4)
        snap["cpu_quota_headroom"] = 3.1
        self.assertEqual(r.capacity(snap, 20)["new_workers"], 1)


class LeaseAndRecoveryTests(unittest.TestCase):
    def test_cpu_and_identity_leases_are_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            held = r.acquire_cpu(directory, 0)
            cpu, free = r.select_cpu(directory, [0, 55])
            self.assertEqual(cpu, 55)
            first = r.acquire_job(directory, "input-A")
            self.assertIsNone(r.acquire_job(directory, "input-A"))
            second = r.acquire_job(directory, "input-B")
            self.assertIsNotNone(second)
            for handle in (held, free, first, second):
                handle.close()

    def test_atomic_immutable_receipt_preserves_previous_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            r.atomic_json(path, {"state": "failed"}, replace=False)
            old = path.read_bytes()
            with self.assertRaises(FileExistsError):
                r.atomic_json(path, {"state": "passed"}, replace=False)
            self.assertEqual(path.read_bytes(), old)

    def test_invalid_global_receipts_are_preserved(self):
        api = SimpleNamespace(case_identity=lambda c: "exact-case",
                              completed_result=lambda c, p: False)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            registry = base / ("rei_" + r.identity_token("exact-case") + ".receipt.json")
            for record in ([], {"identity": "different", "path": "x"},
                           {"identity": "exact-case", "path": None}):
                r.atomic_json(registry, record)
                old = registry.read_bytes()
                result = r.classify({"case_id": "a"}, base / "out", base, api)
                self.assertEqual(result["status"], "PRIOR_RECEIPT_INVALID")
                self.assertEqual(registry.read_bytes(), old)
            r.atomic_json(registry, {"identity": "exact-case", "path": "missing.json",
                                     "status": "COMPLETE"})
            result = r.classify({"case_id": "a"}, base / "out", base, api)
            self.assertEqual(result["status"], "PRIOR_ATTEMPT_PRESERVED")

    def test_actual_toy_workers_and_cross_root_exact_reuse(self):
        """Two file-only children complete; one fails; no science runs occur."""
        code = '''import hashlib,json
from pathlib import Path
def case_grid(): return [{"case_id": k} for k in ("a", "b", "bad")]
def case_identity(config): return hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
def completed_result(config,path):
    if not Path(path).is_file(): return False
    d=json.loads(Path(path).read_text())
    return d.get("identity")==case_identity(config) and d.get("complete") is True
def write_case(config,out):
    if config["case_id"]=="bad": raise RuntimeError("intentional I/O fixture failure")
    p=Path(out)/(config["case_id"]+".json")
    with p.open("x") as f: json.dump({"identity":case_identity(config),"complete":True},f)
'''
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            name = "he30_runner_file_fixture"
            (base / (name + ".py")).write_text(code)
            sys.path.insert(0, str(base))
            cpu = sorted(os.sched_getaffinity(0))[0]
            snap = snapshot(n=1, total_gib=8, available_gib=8)
            snap["affinity_cpu_ids"] = [cpu]
            snap["cpu_busy"] = {cpu: 0.}
            try:
                with patch.object(r, "observe", return_value=snap):
                    first = r.run(base / "out", 1, 10, lease_dir=base / "leases",
                                  reserve_cpus=0, reserve_gib=0, api_module=name)
                    self.assertEqual(first["worker_starts"], 3)
                    self.assertEqual(first["statuses"]["a"]["status"], "COMPLETE")
                    self.assertEqual(first["statuses"]["b"]["status"], "COMPLETE")
                    self.assertEqual(first["statuses"]["bad"]["status"], "FAILED")
                    old = (base / "out" / "a.json").read_bytes()
                    second = r.run(base / "out2", 1, 2, lease_dir=base / "leases",
                                   reserve_cpus=0, reserve_gib=0, api_module=name)
                    self.assertEqual(second["worker_starts"], 0)
                    self.assertEqual(second["statuses"]["a"]["status"], "REUSED_COMPLETE")
                    self.assertEqual(second["statuses"]["bad"]["status"], "PRIOR_ATTEMPT_PRESERVED")
                    self.assertEqual((base / "out" / "a.json").read_bytes(), old)
                    self.assertEqual(first["other_jobs_signalled"], 0)
            finally:
                sys.path.remove(str(base))
                sys.modules.pop(name, None)


if __name__ == "__main__":
    unittest.main()
