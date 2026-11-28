"""Manufactured return-file cases only; no native, solver or old suite runs."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
import partial_returns as reader


def h(text):
    return hashlib.sha256(text.encode()).hexdigest()


class PartialReturnChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "campaign"
        self.binary = self.base / "manufactured_owner_bytes"
        self.binary.write_bytes(b"manufactured identity bytes; never executable\n")
        self.trust = {
            "source_files": dict(reader.SCIENCE_SOURCES),
            "parent_sources": {reader.SERVER_SOURCE: h("manufactured server")},
            "input_sources": {"inputs/SAVED_NATIVE_POINTS.json": h("manufactured saved points")},
            "original_binary_sha256": reader.digest(self.binary),
            "table_sha256": {f"m8_r{r}_table512": h(f"manufactured table {r},512") for r in (2, 4, 8)},
            "baseline_code_revision": reader.BASELINE_CODE,
            "parent_manifest_sha256": h("manufactured parent manifest"),
            "input_manifest_sha256": h("manufactured input manifest")}
        loader = patch.object(reader, "load_trusted_identity", return_value=self.trust)
        self.load_trust = loader.start()
        self.addCleanup(loader.stop)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")

    def change(self, path, mutate):
        data = json.loads(path.read_text())
        mutate(data)
        self.write(path, data)

    @staticmethod
    def result(method, temperature):
        return {"gas_final": [.1, .2, .1, 1.], "species_defect": [0., 0., 0.],
                "number_defect": 0., "energy_defect_ev": 0., "min_photon": 0.,
                "temperature_K": temperature, "gas_positive": True,
                "metadata": {"method": method, "rtol": 1e-10, "atol_scaled": 1e-12,
                             "nfev": 7, "njev": 2, "nlu": 3, "segment_count": 2, "t_end_s": 10.}}

    def complete(self, r=2, nodes=512, *, runtime="python fixture A"):
        folder = self.root / f"m8_r{r}_table{nodes}"
        identity = {k: copy.deepcopy(self.trust[k]) for k in
                    ("source_files", "parent_sources", "input_sources")}
        sha = self.trust["original_binary_sha256"]
        identity.update(m=8, angles=4, q=0., r=r, table_nodes=nodes,
            owner_source=reader.OWNER, binary_sha256=sha,
            build_receipt={"owner_source": reader.OWNER, "binary_sha256": sha,
                           "server_source_sha256": self.trust["parent_sources"][reader.SERVER_SOURCE]},
            numerical_thread_environment=dict(reader.THREADS),
            runtime={"python": runtime, "numpy": "numpy fixture", "scipy": "scipy fixture",
                     "platform": "manufactured platform"})
        table_hash = h(f"manufactured table {r},{nodes}")
        qualification = {"scope": "six_saved_native_points_only", "points": 6,
                         "max_relative_nonzero_error": 0., "binary_byte_identity": True,
                         "original_binary_sha256": sha, "upstream_grackle_equivalence": "HOLD"}
        methods = {"Radau": self.result("Radau", 12.),
                   "DOP853": self.result("DOP853", 12. + 1e-12)}
        for name, value in (("IDENTITY.json", identity),
                ("TABLE.json", {"source_table_sha256": table_hash,
                                "diagnostics": {"build_wall_s": 1.5, "estimated_bytes": 160}}),
                ("SAVED_POINT_PARITY.json", qualification)):
            self.write(folder / name, value)
        for method, seconds, calls in (("Radau", 5., 5), ("DOP853", 7., 7)):
            self.write(folder / (method + ".json"),
                       {"result": methods[method], "wall_s": seconds, "native_calls": calls})
        self.write(folder / "RESULT.json", {"status": "REFERENCE_COMPLETED_SCOPED",
            "results": methods, "comparison": reader.admit_pair(methods["Radau"], methods["DOP853"]),
            "comparisons": [], "point_qualification": qualification, "table_sha256": table_hash,
            "method_calls": {"Radau": 5, "DOP853": 7}, "native_calls": 20, "wall_s": 25.,
            "continuum_convergence": "HOLD", "transport_replays": 0})
        return folder

    def process(self, folder, *, code, timeout):
        process = folder.with_name(folder.name + "_process")
        process.mkdir(parents=True, exist_ok=True)
        (process / "stdout.log").write_bytes(b"manufactured stdout\n")
        (process / "stderr.log").write_bytes(b"")
        self.write(process / "COMMAND.json", {"argv": ["manufactured; never invoked"], "timeout_s": 26.})
        self.write(process / "RECEIPT.json", {"returncode": code, "timed_out": timeout, "wall_s": 26.,
            "stdout_sha256": reader.digest(process / "stdout.log"),
            "stderr_sha256": reader.digest(process / "stderr.log")})

    @staticmethod
    def by_key(report, r=2, nodes=512):
        return next(case for case in report["cases"] if case["key"] == f"m8_r{r}_table{nodes}")

    def test_absent_campaign_does_not_load_dependencies_or_create_paths(self):
        report = reader.classify_campaign(self.root)
        self.assertEqual([case["status"] for case in report["cases"]], ["ABSENT"] * 4)
        self.assertEqual(report["admitted_pairs"], 0)
        self.assertEqual(report["solver_calls"], 0)
        self.assertFalse(self.root.exists())
        self.load_trust.assert_not_called()

    def test_identity_table_single_and_two_method_partial_phases(self):
        desired = ({"IDENTITY.json"}, {"TABLE.json"},
                   {"IDENTITY.json", "TABLE.json", "SAVED_POINT_PARITY.json", "Radau.json"},
                   set(reader.CASE_JSON) - {"RESULT.json", "FAILURE.json"})
        for (r, nodes), keep in zip(reader.JOBS, desired):
            folder = self.complete(r, nodes)
            for path in folder.iterdir():
                if path.name not in keep:
                    path.unlink()
        report = reader.classify_campaign(self.root)
        self.assertEqual([case["status"] for case in report["cases"]],
            ["IDENTITY_ONLY", "TABLE_ONLY", "METHOD_ONLY", "BOTH_METHODS_NO_RESULT"])
        self.assertEqual(report["admitted_pairs"], 0)
        one = self.by_key(report, 8)
        self.assertEqual(one["results"]["Radau"]["temperature_K"], 12.)
        self.assertEqual(one["physical_admission"]["methods"]["Radau"]["status"], "PASS")
        self.assertEqual(one["performance"]["methods"]["Radau"]["wall_s"], 5.)
        self.assertIsNone(one["performance"]["case_wall_s"])
        two = self.by_key(report, 4, 1024)
        self.assertEqual(two["physical_admission"]["pair"]["status"], "PASS")
        self.assertFalse(two["admitted"])

    def test_complete_all_four_preserves_inputs_and_separates_timing_scopes(self):
        for r, nodes in reader.JOBS:
            self.complete(r, nodes)
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report = reader.classify_campaign(self.root, binary=self.binary)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertTrue(report["complete"])
        self.assertEqual(report["admitted_pairs"], 4)
        self.assertEqual(report["admitted_cohort_count"], 1)
        for case in report["cases"]:
            self.assertEqual(case["status"], "COMPLETE_VALID")
            self.assertEqual(case["binary_bytes_readback"], "MATCH")
            self.assertEqual(case["performance"]["case_wall_s"], 25.)
            self.assertEqual(case["performance"]["table_build_wall_s"], 1.5)
            self.assertEqual(case["performance"]["methods"]["Radau"]["wall_s"], 5.)

    def test_invalid_case_is_retained_beside_two_valid_distinct_cohorts(self):
        self.complete(2)
        bad = self.complete(4)
        self.change(bad / "Radau.json", lambda record: record["result"].update(temperature_K=12. + 2e-12))
        self.complete(8, runtime="python fixture B")
        report = reader.classify_campaign(self.root)
        self.assertEqual(report["admitted_pairs"], 2)
        self.assertEqual(report["admitted_cohort_count"], 2)
        self.assertEqual(report["cross_cohort_contrasts"], "HOLD")
        case = self.by_key(report, 4)
        self.assertEqual(case["status"], "INVALID")
        self.assertEqual(case["physical_admission"]["pair"]["status"], "PASS")
        self.assertEqual(case["return_consistency"]["status"], "FAIL")
        self.assertIn("METHOD_RESULT_MISMATCH", " ".join(error["message"] for error in case["errors"]))
        self.assertTrue(self.by_key(report, 2)["admitted"])
        self.assertTrue(self.by_key(report, 8)["admitted"])

    def test_timeout_failure_and_completed_science_are_separate_observations(self):
        timed = self.complete(2)
        (timed / "RESULT.json").unlink()
        (timed / "DOP853.json").unlink()
        self.process(timed, code=-15, timeout=True)
        failed = self.complete(4)
        (failed / "RESULT.json").unlink()
        self.write(failed / "FAILURE.json", {"status": "HOLD_FIRST_FAILURE", "error": "manufactured failure"})
        self.process(failed, code=1, timeout=False)
        complete = self.complete(8)
        self.process(complete, code=-15, timeout=True)
        report = reader.classify_campaign(self.root)
        self.assertEqual(self.by_key(report, 2)["status"], "TIMED_OUT")
        self.assertEqual(self.by_key(report, 2)["phase"], "METHOD_ONLY")
        self.assertEqual(self.by_key(report, 4)["status"], "FAILED")
        case = self.by_key(report, 8)
        self.assertTrue(case["admitted"])
        self.assertEqual(case["status"], "COMPLETE_VALID")
        self.assertTrue(case["process"]["timed_out"])
        self.assertEqual(case["performance"]["process_wall_s"], 26.)

    def test_nonfinite_duplicate_and_overflow_json_reject_only_their_cases(self):
        a, b, c, d = [self.complete(r, n) for r, n in reader.JOBS]
        (a / "RESULT.json").write_text('{"status":"x","status":"REFERENCE_COMPLETED_SCOPED"}')
        (b / "Radau.json").write_text('{"result":{"temperature_K":NaN}}')
        (c / "TABLE.json").write_text('{"source_table_sha256":"x","unused":1e999}')
        report = reader.classify_campaign(self.root)
        self.assertEqual([case["status"] for case in report["cases"]],
                         ["INVALID", "INVALID", "INVALID", "COMPLETE_VALID"])
        self.assertEqual(report["admitted_pairs"], 1)
        self.assertTrue(any("DUPLICATE_JSON_KEY" in error["message"] for error in report["cases"][0]["errors"]))
        self.assertTrue(any("NONFINITE_JSON" in error["message"] for error in report["cases"][1]["errors"]))
        self.assertTrue(any("NONFINITE_JSON" in error["message"] for error in report["cases"][2]["errors"]))

    def test_identity_source_binary_point_thread_and_table_mismatches(self):
        mutations = [
            ("IDENTITY.json", lambda d: d["source_files"].update({"src/reference_runner.py": h("changed")})),
            ("IDENTITY.json", lambda d: d["parent_sources"].update({reader.SERVER_SOURCE: h("changed")})),
            ("IDENTITY.json", lambda d: d["input_sources"].update({"inputs/SAVED_NATIVE_POINTS.json": h("changed")})),
            ("IDENTITY.json", lambda d: d["build_receipt"].update(binary_sha256=h("other binary"))),
            ("IDENTITY.json", lambda d: d["build_receipt"].update(owner_source="wrong owner")),
            ("IDENTITY.json", lambda d: d["build_receipt"].update(server_source_sha256=h("other server"))),
            ("IDENTITY.json", lambda d: d["numerical_thread_environment"].update(OMP_NUM_THREADS="2")),
            ("IDENTITY.json", lambda d: d["runtime"].pop("scipy")),
            ("SAVED_POINT_PARITY.json", lambda d: d.update(points=5)),
            ("SAVED_POINT_PARITY.json", lambda d: d.update(max_relative_nonzero_error=6e-13)),
            ("SAVED_POINT_PARITY.json", lambda d: d.update(original_binary_sha256=h("other saved binary"))),
            ("TABLE.json", lambda d: d.update(source_table_sha256=h("different table"))),
        ]
        for index, (name, mutate) in enumerate(mutations):
            with self.subTest(index=index, file=name):
                self.root = self.base / f"identity_fixture_{index}"
                folder = self.complete()
                self.change(folder / name, mutate)
                case = self.by_key(reader.classify_campaign(self.root))
                self.assertFalse(case["admitted"])
                self.assertEqual(case["identity_validation"]["status"], "FAIL")
                self.assertEqual(case["physical_admission"]["pair"]["status"], "PASS")

    def test_original_physical_gate_and_new_method_identity_are_distinct(self):
        physics = self.complete(2)
        changed = self.result("Radau", 12.)
        changed["min_photon"] = -1e-20
        self.change(physics / "Radau.json", lambda d: d.update(result=changed))
        self.change(physics / "RESULT.json", lambda d: d["results"].update(Radau=changed))
        metadata = self.complete(4)
        self.change(metadata / "Radau.json", lambda d: d["result"]["metadata"].update(rtol=2e-10))
        self.change(metadata / "RESULT.json", lambda d: d["results"]["Radau"]["metadata"].update(rtol=2e-10))
        report = reader.classify_campaign(self.root)
        a, b = self.by_key(report, 2), self.by_key(report, 4)
        self.assertEqual(a["physical_admission"]["pair"]["status"], "FAIL")
        self.assertEqual(a["return_consistency"]["status"], "PASS")
        self.assertEqual(b["physical_admission"]["pair"]["status"], "PASS")
        self.assertEqual(b["return_consistency"]["status"], "FAIL")
        self.assertFalse(a["admitted"] or b["admitted"])

    def test_optional_binary_hash_readback_and_missing_binary_are_explicit(self):
        self.complete()
        recorded = self.by_key(reader.classify_campaign(self.root))
        self.assertTrue(recorded["admitted"])
        self.assertEqual(recorded["binary_bytes_readback"], "NOT_PROVIDED")
        self.binary.write_bytes(b"different manufactured binary bytes\n")
        mismatch = self.by_key(reader.classify_campaign(self.root, binary=self.binary))
        self.assertFalse(mismatch["admitted"])
        self.assertEqual(mismatch["binary_bytes_readback"], "MISMATCH")
        missing = self.by_key(reader.classify_campaign(self.root, binary=self.base / "absent_binary"))
        self.assertFalse(missing["admitted"])
        self.assertEqual(missing["binary_bytes_readback"], "FAILED")

    def test_trust_dependency_error_does_not_discard_method_diagnostics(self):
        self.complete()
        self.load_trust.side_effect = FileNotFoundError("manufactured missing saved DATA")
        report = reader.classify_campaign(self.root)
        case = self.by_key(report)
        self.assertEqual(report["global_errors"][0]["layer"], "trust_dependency")
        self.assertFalse(case["admitted"])
        self.assertEqual(case["physical_admission"]["pair"]["status"], "PASS")
        self.assertEqual(case["results"]["Radau"]["temperature_K"], 12.)

    def test_process_stream_hash_failure_is_preserved_without_rewriting_science(self):
        folder = self.complete()
        self.process(folder, code=0, timeout=False)
        (folder.with_name(folder.name + "_process") / "stdout.log").write_bytes(b"changed log")
        case = self.by_key(reader.classify_campaign(self.root))
        self.assertTrue(case["admitted"])
        self.assertTrue(any(error["layer"] == "process" and not error["affects_admission"]
                            and "STREAM_HASH_MISMATCH" in error["message"] for error in case["errors"]))

    def test_pinned_json_and_create_only_cli_contract_use_manufactured_files(self):
        fixture = self.base / "pinned.json"
        self.write(fixture, {"scope": "manufactured"})
        original = reader.digest(fixture)
        self.assertEqual(reader._pinned_json(fixture, original)["scope"], "manufactured")
        self.write(fixture, {"scope": "changed"})
        with self.assertRaisesRegex(ValueError, "TRUSTED_INPUT_HASH"):
            reader._pinned_json(fixture, original)
        destination = self.base / "analysis.json"
        self.assertEqual(reader.main([str(self.root), "--out", str(destination)]), 1)
        before = destination.read_bytes()
        with self.assertRaises(FileExistsError):
            reader.main([str(self.root), "--out", str(destination)])
        self.assertEqual(before, destination.read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
