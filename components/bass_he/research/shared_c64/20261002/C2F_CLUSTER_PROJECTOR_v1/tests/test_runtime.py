"""Runtime contract/launcher tests. Synthetic callbacks; no physical solver."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

CODE = Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE))
from runtime_support import (ContractError, GIB, atomic_create, execution_environment,
    host_preflight, load_manifest, validate_manifest, validate_request, verify_thread_environment)
from run_manufactured import run_assigned
from launch_manufactured import process_snapshot


def fixture():
    return {"schema": "bass-he.c2f.manufactured.v1", "physical_launch_enabled": False,
            "cases": [{"case_id": f"test_{i}", "seed": i, "n_rows": 16, "rank": 5, "angle": 0.2} for i in range(5)],
            "limits": {"wall_seconds": 5, "memory_gib": 0.25, "max_ranks": 2, "max_threads_per_rank": 4}}


def fake_host():
    return {"effective_cpu_budget": 8, "physical_cores_in_affinity": {str(i): [i] for i in range(8)}, "memory_available_bytes": 8*GIB}


class ManifestTests(unittest.TestCase):
    def test_valid_bounded_manifest(self):
        self.assertEqual(validate_manifest(fixture()), fixture())

    def test_physics_extras_duplicate_and_unsafe_id_rejected(self):
        mutants = []
        for key, value in [("physical_launch_enabled", True), ("R_grid", [1, 2]), ("schema", "physical")]:
            x = fixture(); x[key] = value; mutants.append(x)
        for key, value in [("case_id", "../escape"), ("case_id", ".."), ("seed", True), ("rank", 7), ("n_rows", 10), ("n_rows", 65537), ("angle", float("nan")), ("angle", 1.21), ("angle", -0.1)]:
            x = fixture(); x["cases"][0][key] = value; mutants.append(x)
        x = fixture(); x["cases"][1]["case_id"] = x["cases"][0]["case_id"]; mutants.append(x)
        x = fixture(); x["limits"]["max_ranks"] = True; mutants.append(x)
        for mutant in mutants:
            with self.subTest(mutant=mutant), self.assertRaises(ContractError):
                validate_manifest(mutant)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"bad.json"
            path.write_text('{"schema": "first", "schema": "second"}')
            with self.assertRaisesRegex(ContractError, "duplicate"):
                load_manifest(path)

    def test_request_cpu_memory_backend_fail_closed(self):
        good = dict(manifest=fixture(), execution="mpi", backend="reference", native_library=None,
                    ranks=2, threads=4, binding="none", host=fake_host())
        validate_request(**good)
        changes = [{"execution": "serial"}, {"backend": "auto"}, {"backend": "native"},
                   {"native_library": "unexpected.so"}, {"threads": 5}, {"ranks": 3},
                   {"host": dict(fake_host(), effective_cpu_budget=7.5)},
                   {"host": dict(fake_host(), memory_available_bytes=100)},
                   {"binding": "core", "host": dict(fake_host(), physical_cores_in_affinity={})}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises((ContractError, FileNotFoundError)):
                validate_request(**dict(good, **change))

    def test_measured_host_budget_matches_visible_limits(self):
        host = host_preflight()
        self.assertLessEqual(host["effective_cpu_budget"], len(os.sched_getaffinity(0)))
        if host["cpu_quota_cores"] is not None:
            self.assertLessEqual(host["effective_cpu_budget"], host["cpu_quota_cores"])
        self.assertGreater(host["memory_total_bytes"], 0)

    def test_unbound_environment_and_mismatch_rejection(self):
        env = execution_environment(3, "none")
        self.assertEqual(env["OMP_PROC_BIND"], "FALSE")
        with patch.dict(os.environ, env, clear=True):
            verify_thread_environment(3, "none")
            os.environ["OPENBLAS_NUM_THREADS"] = "2"
            with self.assertRaises(ContractError):
                verify_thread_environment(3, "none")
        self.assertEqual(execution_environment(2, "core")["OMP_PROC_BIND"], "close")

    def test_atomic_create_preserves_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"result.json"
            atomic_create(p, {"first": 1})
            initial = p.read_bytes()
            with self.assertRaises(FileExistsError):
                atomic_create(p, {"second": 2})
            self.assertEqual(p.read_bytes(), initial)
            self.assertEqual(len(list(Path(tmp).iterdir())), 1)


class DispatchTests(unittest.TestCase):
    def test_exact_once_rank_strided_summary_dispatch(self):
        seen = []
        def callback(case, *, backend, native_library):
            seen.append(case["case_id"])
            return {"seed": case["seed"], "backend": backend}
        batches = [run_assigned(fixture()["cases"], r, 2, callback, "reference", None) for r in range(2)]
        rows = sorted(sum(batches, []), key=lambda row: row["case_index"])
        self.assertEqual([r["case_index"] for r in rows], list(range(5)))
        self.assertEqual([r["rank"] for r in rows], [0, 1, 0, 1, 0])
        self.assertEqual(len(set(seen)), 5)

    def test_callback_exception_nan_and_oversize_are_failures(self):
        def broken(case, **kwargs):
            raise RuntimeError("intentional callback failure")
        for callback in (broken, lambda *a, **k: float("nan"), lambda *a, **k: "x"*65537):
            rows = run_assigned(fixture()["cases"][:1], 0, 1, callback, "reference", None)
            self.assertEqual(rows[0]["status"], "FAIL")
            self.assertIn("error", rows[0])


class LauncherSeamTests(unittest.TestCase):
    def run_launcher(self, callback, changes=None, args_extra=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        code = root/"code"; code.mkdir()
        for filename in ("runtime_support.py", "run_manufactured.py", "launch_manufactured.py"):
            shutil.copyfile(CODE/filename, code/filename)
        (code/"manufactured_cases.py").write_text(callback)
        manifest = fixture()
        if changes:
            changes(manifest)
        (root/"manifest.json").write_text(json.dumps(manifest))
        output = root/"result.json"
        argv = [sys.executable, str(code/"launch_manufactured.py"), "--manifest", str(root/"manifest.json"),
                "--execution", "serial", "--backend", "reference", "--ranks", "1", "--threads", "1",
                "--binding", "none", "--output", str(output)] + (args_extra or [])
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        return root, output, argv, proc

    def test_serial_launch_and_create_only(self):
        root, output, argv, proc = self.run_launcher('def run_case(case, *, backend, native_library):\n    return {"value": case["seed"]}\n')
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        report = json.loads(output.read_text())
        self.assertEqual(report["status"], "PASS")
        before = output.read_bytes()
        second = subprocess.run(argv, capture_output=True, text=True, timeout=5)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(output.read_bytes(), before)
        worker = json.loads((root/"result.json.runtime"/"worker_result.json").read_text())
        self.assertEqual(len(worker["results"]), 5)
        self.assertFalse(worker["physical_launch_enabled"])

    def test_preflight_failure_is_preserved(self):
        root, output, argv, proc = self.run_launcher('def run_case(case, **kwargs):\n    raise AssertionError("must not run")\n',
                                                    args_extra=["--backend", "native"])
        self.assertEqual(proc.returncode, 1)
        report = json.loads(output.read_text())
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("explicit native library", report["error"]["message"])
        self.assertFalse((root/"result.json.runtime"/"worker_result.json").exists())

    def test_callback_failure_is_preserved(self):
        root, output, argv, proc = self.run_launcher('def run_case(case, **kwargs):\n    raise RuntimeError("mock failure")\n')
        self.assertEqual(proc.returncode, 1)
        report = json.loads(output.read_text())
        worker = json.loads((root/"result.json.runtime"/"worker_result.json").read_text())
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(worker["results"][0]["error"]["message"], "mock failure")

    def test_timeout_terminates_own_group_and_preserves_failure(self):
        root, output, argv, proc = self.run_launcher('import time\ndef run_case(case, **kwargs):\n    time.sleep(10)\n    return {}\n',
                    changes=lambda m: m["limits"].update(wall_seconds=0.2))
        self.assertEqual(proc.returncode, 1)
        report = json.loads(output.read_text())
        self.assertEqual(report["process"]["termination"], "WALL_TIMEOUT")
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue((root/"result.json.runtime"/"stderr.txt").exists())


    def test_detached_child_memory_timeout_cleanup_and_unrelated_survival(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(20)"])
        self.addCleanup(lambda: unrelated.poll() is None and unrelated.kill())
        child_code = "import os,time; from pathlib import Path; x=bytearray(32*1024**2); Path('detached.pid').write_text(str(os.getpid())); time.sleep(10)"
        callback = ("import subprocess,sys,time\n"
                    "def run_case(case, **kwargs):\n"
                    f"    subprocess.Popen([sys.executable, '-c', {child_code!r}], start_new_session=True)\n"
                    "    time.sleep(10)\n    return {}\n")
        root, output, argv, proc = self.run_launcher(callback, changes=lambda m: m["limits"].update(wall_seconds=0.8))
        self.assertEqual(proc.returncode, 1)
        report = json.loads(output.read_text())
        self.assertEqual(report["process"]["termination"], "WALL_TIMEOUT")
        self.assertGreater(report["process"]["sampled_owned_rss_peak_bytes"], 32*1024**2)
        child_pid = int((root/"code"/"detached.pid").read_text())
        observed = report["process"]["observed_processes"]
        child = next(p for p in observed if p["pid"] == child_pid)
        self.assertEqual(child["sid"], child_pid)
        self.assertEqual(report["process"]["cleanup"]["remaining"], [])
        self.assertFalse(any(p["pid"] == child_pid and p["state"] != "Z" for p in process_snapshot().values()))
        self.assertIsNone(unrelated.poll(), "unrelated process must survive owned cleanup")
        unrelated.terminate(); unrelated.wait(timeout=5)

    def test_detached_child_memory_budget_is_accounted(self):
        child_code = "import time; x=bytearray(64*1024**2); time.sleep(10)"
        callback = ("import subprocess,sys,time\n"
                    "def run_case(case, **kwargs):\n"
                    f"    subprocess.Popen([sys.executable, '-c', {child_code!r}], start_new_session=True)\n"
                    "    time.sleep(10)\n    return {}\n")
        root, output, argv, proc = self.run_launcher(callback, changes=lambda m: m["limits"].update(memory_gib=0.05))
        self.assertEqual(proc.returncode, 1)
        report = json.loads(output.read_text())
        self.assertEqual(report["process"]["termination"], "MEMORY_BUDGET_EXCEEDED")
        self.assertGreater(report["process"]["sampled_owned_rss_peak_bytes"], 0.05*GIB)
        self.assertEqual(report["process"]["cleanup"]["remaining"], [])


if __name__ == "__main__":
    unittest.main()
