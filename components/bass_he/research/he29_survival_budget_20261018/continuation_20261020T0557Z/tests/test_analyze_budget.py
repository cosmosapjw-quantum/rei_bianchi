"""New affine/return integration fixtures; no old audit, suite or solver replay."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LANE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LANE / "src"))
import analyze_budget as budget
import partial_returns as returns


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


class BudgetIntegrationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.data_root = self.base / "baseline_data"
        self.study = self.data_root / "inputs/study"
        self.manifest = {}
        self.sources = {returns.SERVER_SOURCE: sha("manufactured server"),
                        "research/fixture/physics.py": sha("manufactured physics")}
        self.audit = {"status": "REUSED_BYTES_VERIFIED", "sha256": sha("manufactured opaque audit"),
            "bytes": 0, "raw_json_utf8": "manufactured audit fixture; never evaluated",
            "data": {"spectral_mixed_differences": "OPAQUE_OLD_MIXED_RESULT",
                     "time_T_n64_minus_n32_K": "OPAQUE_OLD_TIME_RESULT"}}
        primary = {2: 10., 4: 10. + 2.**-20, 8: 10. + 2.**-19}
        for r in (2, 4, 8):
            for n in (32, 64):
                key = budget.transport_key(r, n)
                identity = {"n": n, "source_table_nodes": 512,
                    "spec": {"m": 8, "angles": 4, "q": 0., "strips": r},
                    "owner_source": budget.OWNER, "numerical_thread_environment": dict(budget.THREADS),
                    "binary_sha256": sha("manufactured binary"), "parent_sources": self.sources}
                temperature = primary[r] + 2.**(-24 - (r // 2)) * (32 / n)
                result = {"status": "SCOPED_NATIVE_COMPLETED", "source_table_sha256": sha(f"table{r},512"),
                          "results": {"transport": {"temperature_K": temperature, "metadata": {"n": n}}}}
                table = {"source_table_sha256": result["source_table_sha256"]}
                for name, value in (("IDENTITY.json", identity), ("RESULT.json", result), ("TABLE.json", table)):
                    path = self.study / key / name
                    self.write(path, value)
                    self.manifest[f"inputs/study/{key}/{name}"] = returns.digest(path)
        self.classified = {"cases": [], "global_errors": [], "complete": True,
                           "admitted_pairs": 4, "solver_calls": 0, "native_calls": 0}
        for r, nodes in budget.JOBS:
            key = budget.case_key(r, nodes)
            temperature = primary[r] + (2.**-30 if nodes == 1024 else 0.)
            identity = {"m": 8, "angles": 4, "q": 0., "r": r, "table_nodes": nodes,
                        "owner_source": budget.OWNER, "numerical_thread_environment": dict(budget.THREADS),
                        "binary_sha256": sha("manufactured binary"), "parent_sources": self.sources}
            self.classified["cases"].append({"key": key, "r": r, "table_nodes": nodes,
                "admitted": True, "status": "COMPLETE_VALID", "cohort_id": sha("cohort A"),
                "identity": identity, "table": {"source_table_sha256": sha(f"table{r},{nodes}")},
                "results": {"Radau": {"temperature_K": temperature},
                            "DOP853": {"temperature_K": temperature + 2.**-40}},
                "performance": {"methods": {"Radau": {"wall_s": 5., "scope": "method only"}},
                                "case_wall_s": 25., "process_wall_s": 26.}})

    @staticmethod
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")

    def load(self):
        with patch.object(budget, "_input_manifest", return_value=self.manifest):
            return budget.load_transport(self.study)

    def test_complete_conditional_decomposition_merges_shared_references(self):
        transport = self.load()
        before = copy.deepcopy((self.classified, transport, self.audit))
        result = budget.build_budget(self.classified, transport, self.audit)
        self.assertEqual((self.classified, transport, self.audit), before)
        self.assertEqual(transport["files_matched"], 18)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(len(result["signed_residuals"]), 6)
        self.assertEqual(len(result["contrasts"]), 3)
        self.assertEqual(result["reused_audit"], self.audit)
        self.assertEqual(result["old_audit_recomputations"], 0)
        self.assertEqual(result["reference_choice_rule"]["primary_method"], "Radau")
        strip = result["contrasts"][0]
        self.assertEqual(strip["projection"]["coherent_hull"]["exact_width"], "0")
        self.assertNotEqual(strip["projection"]["product_hull"]["exact_width"], "0")
        for contrast in result["contrasts"]:
            for row in contrast["decompositions"]:
                self.assertTrue(row["closure_exact_zero"])
                self.assertEqual(row["closure"]["linear_form"]["coefficients"], {})
                self.assertEqual(row["closure"]["product_hull"]["exact_lower"], "0")
                self.assertEqual(row["closure"]["product_hull"]["exact_upper"], "0")
                self.assertEqual(row["assembled_difference"]["linear_form"]["coefficients"], {})
                self.assertEqual(row["assembled_difference"]["product_hull"]["exact_width"], "0")
                self.assertEqual(row["assembled_difference"]["product_hull"]["exact_lower"],
                                 row["observed_transport_delta"]["product_hull"]["exact_lower"])

    def test_no_pair_and_method_only_keep_rows_on_hold_and_timing_opaque(self):
        for row in self.classified["cases"]:
            row.update(admitted=False, status="ABSENT")
        self.classified["cases"][0]["status"] = "METHOD_ONLY"
        result = budget.build_budget(self.classified, self.load(), self.audit)
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(result["missing_cases"], [budget.case_key(*job) for job in budget.JOBS])
        self.assertEqual(result["reference_candidates"], {})
        self.assertEqual(result["signed_residuals"], [])
        self.assertEqual(result["contrasts"], [])
        self.assertEqual(result["reference_dependent_rows"], 0)
        self.assertEqual(result["performance"][0]["recorded_metrics"], self.classified["cases"][0]["performance"])
        self.assertEqual(result["reused_audit"]["data"], self.audit["data"])

    def test_cross_cohort_hold_and_one_invalid_return_preserve_other_contrasts(self):
        self.classified["cases"][0]["cohort_id"] = sha("cohort B")
        result = budget.build_budget(self.classified, self.load(), self.audit)
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(len(result["contrasts"]), 2)
        self.assertEqual(result["held_contrasts"][0]["status"], "HOLD_COHORT_MISMATCH")
        self.classified["cases"][0].update(admitted=False, status="INVALID")
        invalid = budget.build_budget(self.classified, self.load(), self.audit)
        self.assertEqual(invalid["exit_code"], 2)
        self.assertEqual(len(invalid["contrasts"]), 2)
        self.assertEqual(len(invalid["signed_residuals"]), 4)
        self.assertEqual(invalid["missing_cases"], ["m8_r2_table512"])

    def test_input_byte_and_model_table_mismatch_hold_only_affected_residuals(self):
        path = self.study / "m8_r2_n32/RESULT.json"
        path.write_bytes(path.read_bytes() + b" ")  # Same JSON values, changed protected bytes.
        transport = self.load()
        result = budget.build_budget(self.classified, transport, self.audit)
        self.assertEqual(result["exit_code"], 2)
        self.assertEqual(len(result["signed_residuals"]), 5)
        self.assertEqual(len(result["contrasts"]), 3)
        self.assertEqual(result["contrasts"][0]["decomposition_holds"],
                         [{"n": 32, "status": "HOLD_MATCHING_TRANSPORT_REQUIRED"}])
        self.assertEqual(len(result["contrasts"][1]["decompositions"]), 2)
        clean = self.load()
        row = next(row for row in clean["cases"] if row["key"] == "m8_r4_n64")
        row["table_sha256"] = sha("different table")
        mismatch = budget.build_budget(self.classified, clean, self.audit)
        self.assertTrue(any(item["case"] == "m8_r4_table512" and item["n"] == 64
                            for item in mismatch["held_residuals"]))

    def test_cli_external_data_default_and_create_only_output(self):
        absent = copy.deepcopy(self.classified)
        for row in absent["cases"]:
            row.update(admitted=False, status="ABSENT")
        destination = self.base / "budget.json"
        with patch.object(returns, "classify_campaign", return_value=absent) as classify, \
             patch.object(budget, "_input_manifest", return_value=self.manifest), \
             patch.object(budget, "load_audit", return_value=self.audit):
            args = ["--root", str(self.base / "absent_campaign"), "--out", str(destination),
                    "--data-root", str(self.data_root), "--binary", str(self.base / "recorded_binary")]
            self.assertEqual(budget.main(args), 1)
            classify.assert_called_once_with(str(self.base / "absent_campaign"),
                binary=str(self.base / "recorded_binary"), data_root=str(self.data_root))
            result = json.loads(destination.read_text())
            self.assertEqual(result["transport_input"]["files_matched"], 18)
            original = destination.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failure:
                budget.main(args)
            self.assertEqual(failure.exception.code, 2)
            self.assertEqual(destination.read_bytes(), original)
            classify.assert_called_once()

    def test_external_data_route_uses_git_manifests_and_rejects_changed_data(self):
        # New path-routing fixture: copy four already frozen DATA records only.
        # No physical result calculation or archived code execution occurs.
        external = self.base / "existing_baseline_checkout"
        names = ["inputs/SAVED_NATIVE_POINTS.json"] + [
            f"inputs/study/m8_r{r}_n64/RESULT.json" for r in (2, 4, 8)]
        for name in names:
            target = external / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((returns.HE29 / name).read_bytes())
        self.write(external / "provenance/INPUT_SHA256.json", {"untrusted_archive_manifest": "ignored"})
        source = external / "src/reference_contract.py"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("raise RuntimeError('DATA checkout code must never execute')\n")
        identity = returns.load_trusted_identity(data_root=external)
        self.assertEqual(identity["source_files"], returns.SCIENCE_SOURCES)
        self.assertEqual(identity["input_manifest_sha256"], returns.INPUT_MANIFEST_SHA)
        self.assertEqual(set(identity["table_sha256"]), {"m8_r2_table512", "m8_r4_table512", "m8_r8_table512"})
        target = external / "inputs/SAVED_NATIVE_POINTS.json"
        target.write_bytes(target.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "TRUSTED_INPUT_HASH"):
            returns.load_trusted_identity(data_root=external)


if __name__ == "__main__":
    unittest.main(verbosity=2)
