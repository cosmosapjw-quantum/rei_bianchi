"""Changed execution-boundary tests; subprocess fixtures contain no physics."""
import concurrent.futures
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from host_probe import parse_cpu_list, probe_host
from launch_ncp import build_command, is_openmpi_launcher, validate_layout
from mpi_batch import atomic_create, backend_identity, code_identity, execute_task, json_bytes, read_manifest, sha256, validate_manifest, validate_worker_artifacts


def manifest():
    return {"schema": 1, "tasks": [{"task_id": "a", "parameters": {"R": 2.0}}],
            "limits": {"per_worker_memory_gib": 1.0, "task_wall_seconds": 5}}


def host():
    return {"core_binding_cpu_budget": 64, "memory_available_budget_bytes": 128 * 2**30,
            "cgroup_status": "V2_VISIBLE_ANCESTRY_INSPECTED"}


class RuntimeTests(unittest.TestCase):
    def test_openrte_historical_openmpi_launcher_version(self):
        self.assertTrue(is_openmpi_launcher("mpirun.openmpi (OpenRTE) 4.1.6"))
        self.assertTrue(is_openmpi_launcher("mpirun (Open MPI) 5.0.0"))
        self.assertFalse(is_openmpi_launcher("HYDRA build details: MPICH 4.2"))

    def test_manifest_rejects_invalid_limits_duplicate_or_unsafe_id(self):
        for key in ("per_worker_memory_gib", "task_wall_seconds"):
            for value in (-1, 0, float("inf"), True):
                doc = manifest()
                doc["limits"][key] = value
                with self.assertRaises(ValueError):
                    validate_manifest(doc)
        doc = manifest()
        doc["tasks"].append(doc["tasks"][0])
        with self.assertRaises(ValueError):
            validate_manifest(doc)
        for unsafe in ("../a", "a/b", "..", "", "a b"):
            doc = manifest()
            doc["tasks"][0]["task_id"] = unsafe
            with self.assertRaises(ValueError):
                validate_manifest(doc)

    def test_exact_float_and_raw_manifest_identity(self):
        a, b = manifest(), manifest()
        b["tasks"][0]["parameters"]["R"] = 2.0000000000000004
        self.assertNotEqual(sha256(json_bytes(a)), sha256(json_bytes(b)))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "manifest.json"
            path.write_bytes(json_bytes(a))
            parsed, first, raw = read_manifest(path)
            self.assertEqual(parsed, a)
            path.write_bytes(raw + b" ")
            self.assertNotEqual(first, read_manifest(path)[1])
            path.write_text('{"schema":1,"schema":1,"tasks":[],"limits":{}}')
            with self.assertRaises(ValueError):
                read_manifest(path)

    def test_layout_cpu_memory_and_headroom(self):
        result = validate_layout(host(), 16, 4, 4)
        self.assertEqual(result["workers"], 15)
        self.assertEqual(result["reserved_core_slots"], 64)
        for ranks, threads, memory in ((65, 1, 1), (32, 4, 1), (64, 1, 4), (0, 1, 1), (1, 0, 1)):
            with self.assertRaises(ValueError):
                validate_layout(host(), ranks, threads, memory)
        with self.assertRaises(ValueError):
            validate_layout(host(), 1, 1, 1, reserve_fraction=0.1)
        self.assertEqual(validate_layout(host(), 1, 1, 1)["workers"], 1)
        unknown = host()
        unknown["core_binding_cpu_budget"] = None
        with self.assertRaises(ValueError):
            validate_layout(unknown, 1, 1, 1)

    def test_launcher_binding_flags(self):
        self.assertEqual(backend_identity("numpy"), {"backend": "numpy"})
        command = build_command("mpirun", sys.executable, "tasks.json", "fresh", "native", 16, 4)
        self.assertIn("slot:PE=4", command)
        self.assertIn("--nooversubscribe", command)
        self.assertIn("--report-bindings", command)
        self.assertEqual(command[command.index("--host") + 1], "localhost:64")
        three = build_command("mpirun", sys.executable, "tasks.json", "fresh", "native", 3, 1)
        self.assertEqual(three[three.index("--host") + 1], "localhost:3")
        self.assertEqual(command[command.index("--bind-to") + 1], "core")

    def test_cpu_list_and_real_probe_snapshot(self):
        self.assertEqual(parse_cpu_list("0-2,5,8-9"), {0, 1, 2, 5, 8, 9})
        with self.assertRaises(ValueError):
            parse_cpu_list("4-2")
        report = probe_host()
        self.assertGreater(report["allowed_logical_cpu_count"], 0)
        self.assertGreater(report["logical_cpu_budget"], 0)
        self.assertEqual(report["memory_evidence"], "SNAPSHOT_NOT_RESERVATION")

    def test_atomic_create_only_concurrent_writers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "record.json"
            def attempt(value):
                try:
                    atomic_create(path, value)
                    return True
                except FileExistsError:
                    return False
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                winners = list(pool.map(attempt, [b"first", b"second"]))
            self.assertEqual(sum(winners), 1)
            self.assertIn(path.read_bytes(), (b"first", b"second"))
            self.assertEqual(list(Path(folder).glob(".pending-*")), [])

    def run_fixture(self, source, timeout=3):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        worker = base / "fake_worker.py"
        worker.write_text(source)
        limits = {"per_worker_memory_gib": 1, "task_wall_seconds": timeout}
        result = execute_task(manifest()["tasks"][0], base, "reference", sys.executable,
                              limits, code_identity(), 1, worker)
        self.assertEqual(json.loads((base / "a" / "TASK_EXECUTION.json").read_text()), result)
        return result, base, worker, limits

    def test_worker_success_requires_result_and_prevents_overwrite(self):
        source = 'import hashlib,json,pathlib,sys\nout=pathlib.Path(sys.argv[sys.argv.index("--output-dir")+1])\nraw=pathlib.Path(sys.argv[sys.argv.index("--task-json")+1]).read_bytes()\ntask=json.loads(raw)\n(out/"RESULT.json").write_text(json.dumps({"status":"PASS","task_id":task["task_id"],"parameters":task["parameters"],"backend":sys.argv[sys.argv.index("--backend")+1],"input_sha256":hashlib.sha256(raw).hexdigest()}))\n'
        source += f'root=pathlib.Path({str(Path(__file__).resolve().parents[1])!r})\n'
        source += 'result=json.loads((out/"RESULT.json").read_text())\n(out/"STATE.npz").write_bytes(b"fixture state")\nresult.update(code_sha256={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for sub in ("code","reference") for p in (root/sub).glob("*.py")},state_file="STATE.npz",state_bytes=13,state_sha256=hashlib.sha256(b"fixture state").hexdigest())\n(out/"RESULT.json").write_text(json.dumps(result))\n'
        result, base, worker, limits = self.run_fixture(source)
        self.assertEqual(result["status"], "WORKER_RESULT_PASS")
        before = (base / "a" / "TASK_EXECUTION.json").read_bytes()
        with self.assertRaises(FileExistsError):
            execute_task(manifest()["tasks"][0], base, "native", sys.executable,
                         limits, {"sha256": "different"}, 1, worker)
        self.assertEqual((base / "a" / "TASK_EXECUTION.json").read_bytes(), before)

    def test_nonzero_failure_preserved(self):
        result, base, _, _ = self.run_fixture('import sys\nprint("failure evidence",file=sys.stderr)\nsys.exit(7)\n')
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["returncode"], 7)
        self.assertEqual(result["failure_class"], "WORKER_NONZERO_EXIT")
        self.assertIn("failure evidence", (base / "a" / "STDERR.txt").read_text())

    def test_timeout_preserves_record(self):
        result, _, _, _ = self.run_fixture("import time\ntime.sleep(10)\n", timeout=0.1)
        self.assertEqual(result["failure_class"], "TASK_WALL_TIMEOUT")
        self.assertNotEqual(result["returncode"], 0)

    def test_exit_zero_without_result_is_failure(self):
        result, _, _, _ = self.run_fixture("pass\n")
        self.assertEqual(result["failure_class"], "MISSING_WORKER_RESULT")

    def test_exit_zero_wrong_task_result_is_failure(self):
        source = 'import json,pathlib,sys\nout=pathlib.Path(sys.argv[sys.argv.index("--output-dir")+1])\n(out/"RESULT.json").write_text(json.dumps({"status":"PASS","task_id":"wrong"}))\n'
        result, _, _, _ = self.run_fixture(source)
        self.assertEqual(result["failure_class"], "WORKER_RESULT_IDENTITY_MISMATCH")

    def test_tampered_state_source_and_native_result_rejected_without_solve(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / "STATE.npz"
            state.write_bytes(b"original")
            identity = {"files": {"code/a.py": "sourcehash"}}
            native = {"backend": "native", "library_sha256": "libhash", "build": {"flags": "strict"}}
            result = {"code_sha256": {"code/a.py": "sourcehash"}, "state_file": state.name,
                      "state_bytes": 8, "state_sha256": sha256(b"original"),
                      "metadata": {"native_library": {"library_sha256": "libhash", "build": {"flags": "strict"}}}}
            validate_worker_artifacts(result, folder, identity, native)
            result["metadata"]["native_library"]["library_sha256"] = "tampered"
            with self.assertRaisesRegex(RuntimeError, "WORKER_NATIVE"):
                validate_worker_artifacts(result, folder, identity, native)
            result["metadata"]["native_library"]["library_sha256"] = "libhash"
            result["code_sha256"]["code/a.py"] = "tampered"
            with self.assertRaisesRegex(RuntimeError, "WORKER_SOURCE"):
                validate_worker_artifacts(result, folder, identity, native)
            result["code_sha256"]["code/a.py"] = "sourcehash"
            state.write_bytes(b"modified")
            with self.assertRaisesRegex(RuntimeError, "STATE_ARTIFACT"):
                validate_worker_artifacts(result, folder, identity, native)

    def test_selected_library_byte_tamper_rejected_without_loading_library(self):
        with tempfile.TemporaryDirectory() as folder:
            library = Path(folder) / "fake.so"
            library.write_bytes(b"original")
            library.with_suffix(".build.json").write_text(json.dumps({"library_sha256": sha256(b"original")}))
            with patch.dict("os.environ", {"BASS_NATIVE_LIBRARY": str(library), "BASS_NATIVE_EXPECTED_SHA256": sha256(b"original")}):
                self.assertEqual(backend_identity("native")["library_sha256"], sha256(b"original"))
                library.write_bytes(b"modified")
                with self.assertRaisesRegex(RuntimeError, "EXPECTED_SHA256 mismatch"):
                    backend_identity("native")


if __name__ == "__main__":
    unittest.main(verbosity=2)
