"""No eigensolves: contract, launch rejection, durable ownership/provider failures."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

CODE = Path(__file__).resolve().parents[1] / "code"
sys.path.insert(0, str(CODE))

import launch_reference
import physical_contract as contract
from run_reference import physical_callback, run_assigned
from runtime_support import ContractError, file_identity


def manifest():
    return {"schema": contract.SCHEMA, "node": contract.NODE,
            "physical_launch_enabled": True, "evidence_scope": contract.SCOPE,
            "preregistration": {"path": "prereg.json", "sha256": "0" * 64},
            "tasks": [{"task_id": "R4_coarse_m0", "R": 4., "ZA": 1., "ZB": 2.,
                       "m": 0, "lmax": 12, "rmax": 20., "elements": 24,
                       "boundaries": [0., 4./3, 8./3, 10., 20.], "degree": 4,
                       "quadrature": 14, "tol": 1e-11, "maxiter": 2000,
                       "center": "O", "nroots": 6, "level": "coarse"}],
            "limits": {"wall_seconds": 300, "memory_gib": 4,
                       "max_ranks": 2, "max_threads_per_rank": 4,
                       "max_tasks": 12, "max_eigenstates": 54}}


def inputs(directory):
    value = manifest()
    prereg = directory / "prereg.json"
    prereg.write_text('{"status":"test_fixture_no_physical_execution"}\n')
    value["preregistration"]["sha256"] = file_identity(prereg)["sha256"]
    path = directory / "manifest.json"
    path.write_text(json.dumps(value))
    review = {"schema": contract.REVIEW_SCHEMA, "status": "PASS",
              "approved_manifest_sha256": file_identity(path)["sha256"],
              "approved_preregistration_sha256": file_identity(prereg)["sha256"],
              "reviewer": "unit-test-only", "evidence_scope": contract.SCOPE}
    review_path = directory / "review.json"
    review_path.write_text(json.dumps(review))
    return path, review_path


class ContractTests(unittest.TestCase):
    def test_layout_bound_to_preregistration(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "prereg.json"
            layouts = [{"id": "np", "execution": "serial", "backend": "numpy", "ranks": 1,
                        "threads": 1, "binding": "none"},
                       {"id": "native", "execution": "mpi", "backend": "native", "ranks": 2,
                        "threads": 1, "binding": "none"}]
            path.write_text(json.dumps({"campaign": {"layouts": layouts}}))
            self.assertEqual(contract.validate_registered_layout(path, "serial", "numpy", 1, 1, "none"), "np")
            with self.assertRaisesRegex(ContractError, "absent"):
                contract.validate_registered_layout(path, "serial", "numpy", 1, 2, "none")
            layouts[0]["threads"] = 2
            path.write_text(json.dumps({"campaign": {"layouts": layouts}}))
            with self.assertRaisesRegex(ContractError, "absent"):
                contract.validate_registered_layout(path, "serial", "numpy", 1, 1, "none")

    def test_native_flags_and_source_are_checked_without_loading_library(self):
        root = CODE.parent
        original = root / "native/build/libbass_element.so"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "libbass_element.so"
            path.write_bytes(original.read_bytes())
            metadata = original.with_suffix(".build.json")
            build = json.loads(metadata.read_text())
            target_metadata = path.with_suffix(".build.json")
            target_metadata.write_text(json.dumps(build))
            observed = contract.native_identity(path)
            self.assertEqual(observed["abi"], 3)
            self.assertIn("-ffp-contract=off", observed["strict_flags"])
            build["flags"].append("-ffast-math")
            target_metadata.write_text(json.dumps(build))
            with self.assertRaisesRegex(ContractError, "strict ABI3"):
                contract.native_identity(path)
            build = json.loads(metadata.read_text())
            build["source_sha256"] = "0" * 64
            target_metadata.write_text(json.dumps(build))
            with self.assertRaisesRegex(ContractError, "source SHA256"):
                contract.native_identity(path)
            build = json.loads(metadata.read_text())
            target_metadata.write_text(json.dumps(build))
            path.write_bytes(b"tampered binary")
            with self.assertRaisesRegex(ContractError, "library bytes"):
                contract.native_identity(path)

    def test_valid_frozen_boundaries(self):
        value = manifest()
        self.assertIs(contract.validate_manifest(value), value)
        self.assertEqual(value["tasks"][0]["boundaries"], [0., 4./3, 8./3, 10., 20.])

    def test_closed_schema_and_no_launch(self):
        for update in ({"physical_launch_enabled": False}, {"physical_launch_enabled": 1},
                       {"extra": "ignored?"}, {"schema": "bass-he.c2f.manufactured.v1"}):
            with self.subTest(update=update), self.assertRaises(ContractError):
                contract.validate_manifest({**manifest(), **update})

    def test_bad_boundary_sequences_and_missing_nuclear_radius(self):
        for boundaries in ([0., 4./3, 4./3, 8./3, 20.], [0., 4./3, 20.],
                           [1., 4./3, 8./3, 20.], [0., 4./3, 8./3, float("nan"), 20.]):
            value = manifest()
            value["tasks"][0]["boundaries"] = boundaries
            with self.subTest(boundaries=boundaries), self.assertRaises(ContractError):
                contract.validate_manifest(value)

    def test_bad_tasks_and_budget(self):
        for update in ({"m": -1}, {"lmax": 29}, {"tol": 0.}, {"nroots": 7},
                       {"center": "B"}, {"task_id": "../../escape"}, {"degree": True}):
            value = manifest()
            value["tasks"][0].update(update)
            with self.subTest(update=update), self.assertRaises(ContractError):
                contract.validate_manifest(value)
        for key, bad in (("wall_seconds", 301), ("memory_gib", 4.01),
                         ("max_eigenstates", 5), ("max_ranks", 3)):
            value = manifest()
            value["limits"][key] = bad
            with self.subTest(key=key), self.assertRaises(ContractError):
                contract.validate_manifest(value)

    def test_duplicate_solve_even_with_new_task_id(self):
        value = manifest()
        duplicate = deepcopy(value["tasks"][0])
        duplicate["task_id"] = "duplicate_alias"
        value["tasks"].append(duplicate)
        with self.assertRaisesRegex(ContractError, "duplicate physical"):
            contract.validate_manifest(value)

    def test_json_duplicate_keys_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            for text in ('{"x":1,"x":2}', '{"x":NaN}'):
                path.write_text(text)
                with self.subTest(text=text), self.assertRaises(ContractError):
                    contract.load_json(path)

    def test_exact_reviewed_input_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            path, review = inputs(Path(temp))
            loaded, identities, approved = contract.approved_inputs(path, review)
            self.assertEqual(len(loaded["tasks"]), 1)
            self.assertEqual(approved["status"], "PASS")
            self.assertEqual(set(identities), {"manifest", "preregistration", "review"})
            path.write_text(path.read_text() + "\n")
            with self.assertRaisesRegex(ContractError, "exact manifest"):
                contract.approved_inputs(path, review)

    def test_preregistration_tamper_and_review_status(self):
        with tempfile.TemporaryDirectory() as temp:
            path, review = inputs(Path(temp))
            document = json.loads(review.read_text())
            document["status"] = "HOLD"
            review.write_text(json.dumps(document))
            with self.assertRaisesRegex(ContractError, "PASS review"):
                contract.approved_inputs(path, review)
            (Path(temp) / "prereg.json").write_text('{}')
            with self.assertRaisesRegex(ContractError, "preregistration SHA256"):
                contract.approved_inputs(path, review)

    def test_preregistration_escape(self):
        for path in ("../prereg.json", "/tmp/prereg.json", "a\\b.json"):
            value = manifest()
            value["preregistration"]["path"] = path
            with self.subTest(path=path), self.assertRaises(ContractError):
                contract.validate_manifest(value)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inner = root / "inner"
            inner.mkdir()
            path, review = inputs(inner)
            (inner / "prereg.json").rename(root / "outside.json")
            (inner / "prereg.json").symlink_to(root / "outside.json")
            with self.assertRaisesRegex(ContractError, "symlink escapes"):
                contract.approved_inputs(path, review)

    def test_only_exact_registered_layouts_and_host_caps(self):
        host = {"effective_cpu_budget": 8., "physical_cores_in_affinity": {str(i): [i] for i in range(8)},
                "memory_available_bytes": 8 * 1024**3}
        contract.validate_request(manifest(), "serial", "numpy", None, 1, 1, "none", host)
        with patch.object(contract, "native_identity", return_value={}):
            contract.validate_request(manifest(), "mpi", "native", "/explicit.so", 2, 1, "none", host)
        for execution, backend, ranks, threads, binding in (
                ("serial", "numpy", 2, 1, "none"), ("serial", "native", 1, 1, "none"),
                ("mpi", "native", 2, 4, "none"), ("mpi", "numpy", 2, 1, "none"),
                ("serial", "numpy", 1, 1, "core")):
            with self.subTest(layout=(execution, backend, ranks, threads, binding)), self.assertRaises(ContractError):
                contract.validate_request(manifest(), execution, backend, None, ranks, threads, binding, host)
        for badhost in ({**host, "effective_cpu_budget": .5}, {**host, "memory_available_bytes": 2 * 1024**3}):
            with self.assertRaises(ContractError):
                contract.validate_request(manifest(), "serial", "numpy", None, 1, 1, "none", badhost)
        with self.assertRaisesRegex(ContractError, "must not receive"):
            contract.validate_request(manifest(), "serial", "numpy", "/surprise.so", 1, 1, "none", host)


class OwnershipTests(unittest.TestCase):
    @staticmethod
    def callback(task, *, backend, archive_path):
        # Arbitrary opaque bytes deliberately avoid any numerical eigensolve.
        archive_path.write_bytes((task["task_id"] + backend).encode())
        identity = file_identity(archive_path)
        return {"state_count": task["nroots"], "archive": {
            "source_id": task["task_id"], "source_sha256": identity["sha256"],
            "source_bytes": identity["bytes"], "source_path": identity["path"],
            "state_ids": [str(i) for i in range(task["nroots"])]}}

    def test_rank_striding_and_immediate_receipts(self):
        tasks = [{**manifest()["tasks"][0], "task_id": f"task_{i}"} for i in range(5)]
        with tempfile.TemporaryDirectory() as temp:
            batches = [run_assigned(tasks, rank, 2, self.callback, "numpy", temp, {"test": "fixture"})
                       for rank in range(2)]
            rows = sorted((row for batch in batches for row in batch), key=lambda x: x["task_index"])
            self.assertEqual([row["task_index"] for row in rows], list(range(5)))
            self.assertTrue(all(row["rank"] == row["task_index"] % 2 for row in rows))
            self.assertTrue(all(row["status"] == "PASS" for row in rows))
            for row in rows:
                receipt = json.loads(Path(row["receipt"]["path"]).read_text())
                self.assertEqual(receipt["status"], "PASS")
                self.assertEqual(row["result"]["archive"]["source_sha256"],
                                 file_identity(Path(temp) / (row["task_id"] + ".npz"))["sha256"])

    def test_failure_preserved_and_following_tasks_continue(self):
        tasks = [{**manifest()["tasks"][0], "task_id": f"task_{i}"} for i in range(2)]
        def callback(task, **kwargs):
            if task["task_id"] == "task_0":
                raise RuntimeError("sentinel provider failure")
            return self.callback(task, **kwargs)
        with tempfile.TemporaryDirectory() as temp:
            rows = run_assigned(tasks, 0, 1, callback, "numpy", temp, {})
            self.assertEqual([row["status"] for row in rows], ["FAIL", "PASS"])
            failure = json.loads((Path(temp) / "task_0.json").read_text())
            self.assertIn("sentinel provider", failure["error"]["message"])

    def test_existing_receipt_and_archive_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            task = manifest()["tasks"][0]
            path = Path(temp) / (task["task_id"] + ".json")
            path.write_text("keep existing evidence")
            callback = unittest.mock.Mock()
            rows = run_assigned([task], 0, 1, callback, "numpy", temp, {})
            self.assertEqual(rows[0]["status"], "FAIL")
            self.assertIn("receipt_error", rows[0])
            callback.assert_not_called()
            self.assertEqual(path.read_text(), "keep existing evidence")

    def test_import_path_failure_is_durable_not_fallback(self):
        with tempfile.TemporaryDirectory() as temp, patch("run_reference.importlib.import_module", side_effect=ModuleNotFoundError("missing provider")):
            rows = run_assigned(manifest()["tasks"], 0, 1, physical_callback, "numpy", temp, {})
            self.assertEqual(rows[0]["error"]["type"], "ModuleNotFoundError")
            self.assertTrue((Path(temp) / "R4_coarse_m0.json").is_file())
            self.assertFalse((Path(temp) / "R4_coarse_m0.npz").exists())

    def test_launcher_no_launch_rejection_never_spawns(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            path, review = inputs(directory)
            value = json.loads(path.read_text())
            value["physical_launch_enabled"] = False
            path.write_text(json.dumps(value))
            output = directory / "result.json"
            with patch("launch_reference.subprocess.Popen") as spawn:
                status = launch_reference.main([
                    "--manifest", str(path), "--review", str(review), "--execution", "serial",
                    "--backend", "numpy", "--ranks", "1", "--threads", "1", "--binding", "none",
                    "--output", str(output)])
                spawn.assert_not_called()
            self.assertEqual(status, 1)
            self.assertEqual(json.loads(output.read_text())["stage"], "LAUNCH_OR_PREFLIGHT")
            original = output.read_bytes()
            self.assertEqual(launch_reference.main([
                "--manifest", str(path), "--review", str(review), "--execution", "serial",
                "--backend", "numpy", "--ranks", "1", "--threads", "1", "--binding", "none",
                "--output", str(output)]), 2)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
