"""Real subprocess integration tests; fixed synthetic tasks only."""
import hashlib
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

import core
from core import collect, load_manifest, run_task, ContractError
from run_local import run_local

HERE = Path(__file__).resolve().parent
BACKEND = HERE / "synthetic_backend.py"


def identity(path):
    p = Path(path).resolve()
    b = p.read_bytes()
    return {"path": str(p), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}


EXE = identity(sys.executable)
SCRIPT = identity(BACKEND)


def expected(num, den, literal=""):
    return f"EXACT_RATIONAL_V1\n{num}/{den}\nimag=0/1\nliteral={literal}\n".encode()


def make_plan(folder, name="run", modes=None, sleeps=None, literal=""):
    vals = [(-17, 9), (13, 7), (-31, 16), (5, 3)]
    modes = modes or ["ok"] * len(vals)
    sleeps = sleeps or [120, 10, 70, 30]
    tasks = []
    for i, ((n, d), mode, delay) in enumerate(zip(vals, modes, sleeps)):
        tasks.append({
            "task_id": f"rational_{i:02d}", "executable": EXE, "inputs": [SCRIPT],
            "argv": [EXE["path"], "-B", SCRIPT["path"], "--output", "OUTPUT_PATH",
                     "--numerator", str(n), "--denominator", str(d), "--sleep-ms", str(delay),
                     "--mode", mode, "--literal", literal],
            "env": {}, "cost_hint": delay,
            "semantic_identity": {"precision": "EXACT_FRACTION", "full_parameter_box": {"real": [f"{n}/{d}", f"{n}/{d}"], "imag": ["0", "0"]}},
            "limits": {"wall_seconds": 3, "address_space_bytes": 256 << 20,
                       "rss_bytes": 128 << 20, "poll_ms": 20, "max_output_bytes": 1 << 20},
            "expected_output_sha256": hashlib.sha256(expected(n, d, literal)).hexdigest(),
        })
    doc = {"schema": "WU088_NCP64_TASK_MANIFEST_V1", "scope": "SYNTHETIC_ONLY",
           "output_root": str(Path(folder) / name), "tasks": tasks}
    path = Path(folder) / (name + ".json")
    path.write_text(json.dumps(doc, indent=2) + "\n")
    return path, doc


class ExecutorTests(unittest.TestCase):
    def test_serial_parallel_canonical_exact_payloads(self):
        with tempfile.TemporaryDirectory() as d:
            results = []
            for workers in (1, 2, 3):
                p, doc = make_plan(d, "w" + str(workers))
                r = run_local(str(p), workers)
                self.assertEqual(r["status"], "COLLECTED", r)
                self.assertEqual([x["task_id"] for x in r["tasks"]], sorted(x["task_id"] for x in doc["tasks"]))
                self.assertEqual(load_manifest(p)["dispatch_order"], [0, 2, 3, 1])
                for i, t in enumerate(r["tasks"]):
                    n, den = [(-17, 9), (13, 7), (-31, 16), (5, 3)][i]
                    self.assertEqual(Path(t["payload_path"]).read_bytes(), expected(n, den))
                results.append(r["canonical_payload_digest"])
            self.assertEqual(len(set(results)), 1)

    def test_resume_does_not_rerun_completed_backend(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d)
            self.assertEqual(run_task(p, 0)["status"], "COMPLETE")
            ck = Path(doc["output_root"]) / "tasks/rational_00/checkpoint.json"
            before = ck.read_bytes(), ck.stat().st_mtime_ns
            self.assertEqual(run_task(p, 0)["status"], "REUSED")
            self.assertEqual((ck.read_bytes(), ck.stat().st_mtime_ns), before)
            self.assertEqual((ck.parent / "work/invocations.txt").read_text(), "1")

    def test_missing_and_tampered_payload_cannot_collect(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d)
            run_task(p, 0)
            self.assertEqual(collect(p)["status"], "INCONCLUSIVE")
            r = run_local(str(p), 2)
            self.assertEqual(r["status"], "COLLECTED")
            Path(r["tasks"][0]["payload_path"]).write_bytes(b"CORRUPT")
            self.assertEqual(run_task(p, 0)["status"], "INCONCLUSIVE")
            self.assertEqual(collect(p)["status"], "INCONCLUSIVE")

    def test_manifest_precision_or_inputs_change_refuses_resume(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d)
            self.assertEqual(run_task(p, 0)["status"], "COMPLETE")
            doc["tasks"][0]["semantic_identity"]["precision"] = "DIFFERENT"
            p.write_text(json.dumps(doc))
            self.assertEqual(run_task(p, 0)["status"], "INCONCLUSIVE")

    def test_duplicate_task_and_dispatch_and_traversal_refused(self):
        with tempfile.TemporaryDirectory() as d:
            for kind in ("id", "dispatch", "traversal"):
                p, doc = make_plan(d, kind)
                if kind == "id": doc["tasks"][1]["task_id"] = doc["tasks"][0]["task_id"]
                elif kind == "dispatch": doc["dispatch_order"] = [0, 0, 2, 3]
                else: doc["tasks"][0]["task_id"] = "../escape"
                p.write_text(json.dumps(doc))
                with self.assertRaises(ContractError):
                    load_manifest(p)

    def test_partial_and_failed_jobs_are_never_completed(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d, modes=["partial", "fail", "ok", "ok"])
            for i in (0, 1):
                r = run_task(p, i)
                self.assertEqual(r["status"], "INCONCLUSIVE")
                self.assertEqual(run_task(p, i)["status"], "INCONCLUSIVE")
            self.assertEqual(collect(p)["status"], "INCONCLUSIVE")

    def test_wrong_executable_hash_and_partial_checkpoint_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d)
            doc["tasks"][0]["executable"] = dict(EXE, sha256="0"*64)
            p.write_text(json.dumps(doc))
            self.assertEqual(run_task(p, 0)["status"], "INCONCLUSIVE")
            q, qdoc = make_plan(d, "partial")
            self.assertEqual(run_task(q, 0)["status"], "COMPLETE")
            ck = Path(qdoc["output_root"]) / "tasks/rational_00/checkpoint.json"
            ck.write_text('{"state":"RUNNING"}')
            self.assertEqual(run_task(q, 0)["status"], "INCONCLUSIVE")

    def test_timeout_descendant_and_sampled_rss_are_inconclusive(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d, modes=["timeout", "child", "memory", "ok"])
            doc["tasks"][0]["limits"]["wall_seconds"] = 1
            doc["tasks"][2]["limits"]["rss_bytes"] = 32 << 20
            p.write_text(json.dumps(doc))
            reasons = {0: "WALL_TIMEOUT", 1: "DESCENDANTS_SURVIVE_LEADER", 2: "RSS_LIMIT"}
            for i in (0, 1, 2):
                r = run_task(p, i)
                self.assertEqual(r["status"], "INCONCLUSIVE")
                self.assertEqual(r["guard"]["reason"], reasons[i], r)

    def test_exact_argv_no_shell_expansion(self):
        with tempfile.TemporaryDirectory() as d:
            literal = "$(touch SHOULD_NOT_EXIST); echo bad"
            p, doc = make_plan(d, literal=literal)
            r = run_task(p, 0)
            self.assertEqual(r["status"], "COMPLETE", r)
            self.assertEqual(Path(r["payload_path"]).read_bytes(), expected(-17, 9, literal))
            self.assertFalse((Path(doc["output_root"]) / "tasks/rational_00/work/SHOULD_NOT_EXIST").exists())

    def test_worker_sigterm_cleans_active_child_group(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d, modes=["timeout", "ok", "ok", "ok"])
            argv = [sys.executable, "-B", str(HERE/"worker.py"), "--manifest", str(p), "--task-index", "0"]
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            started = Path(doc["output_root"]) / "tasks/rational_00/work/started.pid"
            deadline = time.monotonic() + 5
            while not started.exists() and time.monotonic() < deadline:
                time.sleep(.01)
            self.assertTrue(started.exists())
            child = int(started.read_text())
            proc.send_signal(signal.SIGTERM)
            out, err = proc.communicate(timeout=5)
            self.assertEqual(proc.returncode, 2, (out, err))
            self.assertEqual(json.loads(out)["guard"]["reason"], "CANCELLED")
            with self.assertRaises(ProcessLookupError):
                os.kill(child, 0)

    def test_scientific_scope_is_not_enabled(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d)
            doc["scope"] = "ACTUAL_HH"
            p.write_text(json.dumps(doc))
            with self.assertRaises(ContractError):
                load_manifest(p)

    def test_successful_replace_without_complete_readback_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p, doc = make_plan(d)
            original = core.atomic_json
            def lost_complete(path, data):
                if data.get("state") == "COMPLETE":
                    return  # Simulate successful API return with old RUNNING bytes visible.
                return original(path, data)
            with patch("core.atomic_json", side_effect=lost_complete):
                r = run_task(p, 0)
            self.assertEqual(r["status"], "INCONCLUSIVE")
            self.assertIn("CHECKPOINT_FINAL_READBACK_MISMATCH", r["reason"])
            ck = Path(doc["output_root"]) / "tasks/rational_00/checkpoint.json"
            self.assertEqual(json.loads(ck.read_text())["state"], "RUNNING")
            self.assertEqual(run_task(p, 0)["status"], "INCONCLUSIVE")
            self.assertEqual((ck.parent / "work/invocations.txt").read_text(), "1")


if __name__ == "__main__":
    unittest.main()
