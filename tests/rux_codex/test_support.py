"""Regression cases for dependency/evidence and endpoint semantic failures."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / "rux_codex" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


workflow = module("workflow")
report = module("retained_report")


def node(nid, dependencies=(), status="PENDING", **overrides):
    result = {"id": nid, "depends_on": list(dependencies), "status": status,
              "owner_repo": "rei_bianchi", "write_paths": ["out/"], "read_first": [],
              "commands": [["python", "read_only.py"]], "outputs": [f"{nid}.txt"],
              "acceptance": ["Preserve frozen scientific gates exactly."], "model_role": "lower-tier", "activation": True}
    result.update(overrides)
    return result


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.path = self.repo / "dag.json"

    def load(self, nodes, state=None):
        self.path.write_text(json.dumps({"schema": "test.v1", "nodes": nodes}))
        state_path = None
        if state is not None:
            state_path = self.repo / "state.json"
            state_path.write_text(json.dumps(state))
        return workflow.load_contract(self.path, self.repo, state_path)

    def test_independent_retained_lane_has_no_wave_barrier(self):
        (self.repo / "retained.txt").write_text("recorded artifact")
        _, nodes, statuses = self.load([
            node("retained", status="COMPLETED_REUSED"), node("physical", status="ON_HOLD", external_requirements=["exact source intake unavailable"]),
            node("plot", ["retained"]), node("physical_run", ["physical"]),
            node("optional", activation=False), node("waiting", external_requirements=["owner scenario selection"])])
        self.assertEqual([entry["id"] for entry in workflow.ready_nodes(nodes, statuses)], ["plot"])

    def test_status_text_cannot_complete_missing_artifact(self):
        with self.assertRaisesRegex(workflow.ContractError, "missing evidence"):
            self.load([node("a", status="COMPLETED_REUSED")])
        (self.repo / "a.txt").write_text("artifact")
        with self.assertRaisesRegex(workflow.ContractError, "evidence"):
            self.load([node("a")], {"nodes": {"a": {"status": "COMPLETED"}}})
        with self.assertRaisesRegex(workflow.ContractError, "missing evidence"):
            self.load([node("a")], {"nodes": {"a": {"status": "COMPLETED", "evidence": ["missing.json"]}}})

    def test_existing_completion_unlocks_only_direct_consumers(self):
        (self.repo / "a.txt").write_text("artifact")
        (self.repo / "proof.json").write_text("{}");
        _, nodes, statuses = self.load([node("a"), node("b", ["a"]), node("c", ["b"])],
                                      {"nodes": {"a": {"status": "COMPLETED", "evidence": ["proof.json"]}}})
        self.assertEqual([entry["id"] for entry in workflow.ready_nodes(nodes, statuses)], ["b"])

    def test_graph_errors_and_shell_strings_fail(self):
        cases = [([node("a"), node("a")], "duplicate node"),
                 ([node("a", ["missing"])], "unknown dependency"),
                 ([node("a", ["b"]), node("b", ["a"])], "cyclic"),
                 ([node("a", commands=["cargo run --release"])], "commands"),
                 ([node("a", outputs=[])], "outputs"),
                 ([node("a", acceptance=[])], "acceptance")]
        for nodes, error in cases:
            with self.subTest(error=error), self.assertRaisesRegex(workflow.ContractError, error):
                self.load(nodes)

    def test_resolved_external_requirement_needs_artifact(self):
        with self.assertRaisesRegex(workflow.ContractError, "missing evidence"):
            self.load([node("a", external_requirements=[{"resolved": True, "evidence": ["absent.json"]}])])

    def test_packet_keeps_exact_gate_and_one_node(self):
        gate = ["No QV=xHII relabeling; no cosmological extrapolation beyond provider/source domain"]
        _, nodes, statuses = self.load([node("a", acceptance=gate), node("b")])
        packet = workflow.packet("a", nodes, statuses, self.repo)
        self.assertEqual(packet["return_contract"]["acceptance_verbatim"], gate)
        self.assertEqual(packet["node"]["id"], "a")
        self.assertNotIn("nodes", packet)
        self.assertIn("no agents spawned", packet["execution"])


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "endpoints.csv"
        self.rows = [{"run": f"{resolution}_{geometry}", "time_s": 1e13,
                      "x_HII": 0.6 if geometry == "BI" else 0.5,
                      "temperature_K": 100 if geometry == "BI" else 120,
                      "gamma_HI_per_s": 3e-14 if geometry == "BI" else 2e-14,
                      "photon_u_ev_per_h": 0.2 if geometry == "BI" else 0.4}
                     for resolution in report.RESOLUTIONS for geometry in ("FLRW", "BI")]

    def save(self):
        with self.path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(self.rows[0]))
            writer.writeheader(); writer.writerows(self.rows)

    def test_paired_sign_and_units_use_saved_endpoints(self):
        self.save()
        rows = report.differences(report.read_endpoints(self.path))
        self.assertEqual(len(rows), 7)
        self.assertAlmostEqual(rows[0]["x_HII_BI_minus_FLRW"], 0.1)
        self.assertEqual(rows[0]["temperature_K_BI_minus_FLRW"], -20)
        self.assertAlmostEqual(rows[0]["gamma_HI_per_s_BI_minus_FLRW"], 1e-14)
        self.assertEqual(rows[0]["photon_u_ev_per_h_BI_minus_FLRW"], -0.2)
        self.assertEqual(rows[0]["time_s"], 1e13)

    def test_missing_duplicate_nonfinite_and_mismatched_time_fail(self):
        original = [dict(row) for row in self.rows]
        mutations = [(lambda: self.rows.pop(), "missing paired"),
                     (lambda: self.rows.append(dict(self.rows[0])), "duplicate"),
                     (lambda: self.rows[0].update(temperature_K="nan"), "nonfinite"),
                     (lambda: self.rows[0].update(time_s=1e13 - 1), "times")]
        for mutate, error in mutations:
            self.rows = [dict(row) for row in original]
            mutate(); self.save()
            with self.subTest(error=error), self.assertRaisesRegex(report.DataError, error):
                report.read_endpoints(self.path)

    def test_ledger_max_is_distinct_from_final_not_an_errorbar(self):
        entry = {"candidate": "T0_BI", "reference": "T0_FLRW", "matched_endpoint_count": 10,
                 "final_difference_by_observable": dict.fromkeys(report.OBSERVABLES, -2),
                 "max_abs_by_observable": dict.fromkeys(report.OBSERVABLES, 7)}
        result = report.recorded_comparisons({"geometry_difference": entry, "weak_shear_half": entry})
        self.assertEqual(result["geometry_difference"]["recorded_final_difference"]["temperature_K"], -2)
        self.assertEqual(result["geometry_difference"]["recorded_max_abs_difference"]["temperature_K"], 7)

    def test_private_receipts_are_not_copied_as_metadata(self):
        metadata = report.inherited_metadata({"status": "RECORDED", "failed_candidate_repairs": [{"original_raw_local_path": "/private/raw"}], "raw_availability": "/private/raw"}, {"scientific_admission": "HOLD"})
        self.assertNotIn("/private/raw", json.dumps(metadata))
        self.assertEqual(metadata["campaign_summary"]["status"], "RECORDED")


if __name__ == "__main__":
    unittest.main()
