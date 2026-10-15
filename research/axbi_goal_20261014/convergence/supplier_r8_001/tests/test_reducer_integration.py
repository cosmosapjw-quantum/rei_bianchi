"""Bounded manufactured integration checks against the installed owner reducer."""
import csv
import hashlib
import importlib.util
import io
import json
import math
import pathlib
import tempfile
import unittest
from contextlib import redirect_stdout
from fractions import Fraction as Q

from reconstruction_support import reconstruction_norm
from source_pair_guard import SourceRelationHold, require_source_relation

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEGMENT = ROOT / "supplier_r8_001"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M = load(ROOT / "compare_histories.py", "installed_reducer")
OLD = load(SEGMENT / "vendor/compare_histories.py", "frozen_reducer")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(root, name, positions, source="SYNTHETIC_SAME_SOURCE", bump=False, extra_config=""):
    path = root / name
    path.mkdir()
    spec = {"id": name, "clock_origin": M.CLOCK}
    h = 1 - .2454
    he = .2454 / 4
    f = he / h
    ah = ["run_id", "time_s", "species_id", "nproper", "Ybaryon", "A", "normalization_registry"]
    hh = list(dict.fromkeys(["case_id", "a", "time_s", "nH_proper_cm3", "ne_proper_cm3", *M.FIELDS.values()]))
    with (path / "history.csv").open("w", newline="") as hf, (path / "abundances.csv").open("w", newline="") as af:
        hw = csv.DictWriter(hf, fieldnames=hh)
        aw = csv.DictWriter(af, fieldnames=ah)
        hw.writeheader()
        aw.writeheader()
        for pos in positions:
            a = M.A0 if pos == 0 else M.A1 if pos == 1 else math.exp(M.L0 + pos * (M.L1 - M.L0))
            u = (math.log(a) - M.L0) / (M.L1 - M.L0)
            x = .1 + .8 * u + (.001 if bump and pos == .5003 else 0.)
            t = pos * 100
            nh = a ** -3
            nhe = f * nh
            nb = nh + 4 * nhe
            hw.writerow({"case_id": name, "a": a, "time_s": t, "nH_proper_cm3": nh,
                         "ne_proper_cm3": nh * x, "x_HI": 1 - x, "x_HII": x,
                         "x_HeI": 1., "x_HeII": 0., "x_HeIII": 0.,
                         "temperature_K": 10 + u, "J0_photon_u_eV_per_H": 0.,
                         "J2_photon_u_eV_per_H": 0.})
            for k, n, mass in [("H_I", nh * (1 - x), 1), ("H_II", nh * x, 1),
                               ("He_I", nhe, 4), ("He_II", 0., 4), ("He_III", 0., 4),
                               ("electron", nh * x, 0)]:
                aw.writerow({"run_id": name, "time_s": t, "species_id": k,
                             "nproper": n, "Ybaryon": n / nb, "A": mass,
                             "normalization_registry": "BASELINE_H_HE_CHARGE_AND_BARYON_V1"})
    for role, content in [("config", "end_zbar=4\nq_ref=0\nlocal_target=1e-5\n" + extra_config),
                          ("source_identity", source),
                          ("terminal", f"status=COMPLETE_REPRESENTED_INTERVAL\na=0.2\naccepted={len(positions)-1}\n")]:
        (path / (role + ".txt")).write_text(content)
    for role in ("history", "abundances", "config", "source_identity", "terminal"):
        file = path / (role + (".csv" if role in ("history", "abundances") else ".txt"))
        spec[role] = {"path": str(file), "sha256": sha(file)}
    return spec


def pair(root, unequal=False, mode=None, relation=None, kind="PAIRED", extra_candidate_config=""):
    ref = fixture(root, "R", [0, .5, 1])
    cand = fixture(root, "C", [0, .50025, .5003, .50035, 1],
                   source="SYNTHETIC_OTHER_SOURCE" if unequal else "SYNTHETIC_SAME_SOURCE",
                   bump=True, extra_config=extra_candidate_config)
    if kind == "REFINEMENT":
        path = pathlib.Path(cand["config"]["path"])
        path.write_text(path.read_text().replace("local_target=1e-5", "local_target=2.5e-6"))
        cand["config"]["sha256"] = sha(path)
    manifest = {"reference": ref, "candidate": cand, "comparison_kind": kind}
    if mode is not None:
        manifest["reconstruction_norm"] = mode
    if relation is not None:
        manifest["source_relation"] = relation
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    with redirect_stdout(io.StringIO()):
        result = M.run(manifest_path, root / "out")
    return result, manifest


class Integration(unittest.TestCase):
    def test_default_and_explicit_sampled_match_frozen(self):
        for mode in (None, "SAMPLED_ONLY"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = pathlib.Path(tmp)
                result, _ = pair(root, mode=mode)
                with redirect_stdout(io.StringIO()):
                    frozen = OLD.run(root / "manifest.json", root / "frozen")
                self.assertEqual(result["status"], frozen["status"])
                self.assertEqual(result["metrics"], frozen["metrics"])
                self.assertEqual(result["milestones"], frozen["milestones"])
                for name in ("sampled_comparisons.csv", "comparison_summary.csv", "milestones.csv"):
                    self.assertEqual((root / "out" / name).read_bytes(), (root / "frozen" / name).read_bytes())
                self.assertEqual(result["reconstruction_norm_mode"], "SAMPLED_ONLY")
                self.assertEqual(result["source_relation_status"], "BYTE_IDENTICAL_COMPILED_SOURCE")

    def test_exact_union_finds_narrow_feature_without_changing_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            result, _ = pair(root, mode="EXACT_UNION")
            row = next(x for x in result["metrics"] if x["observable"] == "x_HII")
            self.assertEqual(result["status"], "DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED")
            self.assertGreater(Q(row["reconstruction_sup_exact"]), Q("0.000999"))
            self.assertLess(row["sampled_sup_absolute_difference"], 1e-12)
            self.assertEqual(row["result_class"], "RESOLUTION_LIMITED")
            self.assertEqual(row["interpolation_uncertainty"], "UNKNOWN")
            self.assertEqual(row["evolution_refinement_uncertainty"], "UNKNOWN")
            self.assertIsNone(row["true_ivp_error"])
            self.assertEqual(result["scientific_admission"], "NOT_ISSUED")
            with redirect_stdout(io.StringIO()):
                frozen = OLD.run(root / "manifest.json", root / "frozen")
            self.assertEqual((root / "out/sampled_comparisons.csv").read_bytes(),
                             (root / "frozen/sampled_comparisons.csv").read_bytes())
            self.assertEqual((root / "out/milestones.csv").read_bytes(),
                             (root / "frozen/milestones.csv").read_bytes())

    def test_triangular_rational_oracle(self):
        witness = reconstruction_norm([(Q(0), Q(0)), (Q(1), Q(0))],
                                      [(Q(0), Q(0)), (Q(1, 3), Q(-2, 5)), (Q(1), Q(0))],
                                      "LN_A")
        self.assertEqual(witness["sup_absolute_difference"], Q(2, 5))
        self.assertEqual(witness["signed_difference_at_sup"], Q(-2, 5))
        self.assertEqual(witness["coordinate_at_sup"], Q(1, 3))
        self.assertEqual(witness["union_knots"], 3)
        self.assertIsNone(witness["true_ivp_error"])
        represented = reconstruction_norm([(0., 0.), (1., .1)], [(0., 0.), (1., .2)], "LN_A")
        self.assertEqual(represented["sup_absolute_difference"], Q.from_float(.2) - Q.from_float(.1))

    def test_unbound_and_missing_sources_hold_before_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            result, _ = pair(root, unequal=True)
            self.assertEqual(result["status"], "HOLD_SOURCE_RELATION_UNBOUND")
            self.assertFalse((root / "out/sampled_comparisons.csv").exists())
        with self.assertRaises(SourceRelationHold):
            require_source_relation({"source_identity": {}},
                                    {"source_identity": {"sha256": "1" * 64}}, {})

    def test_reviewed_ordered_relation_is_scoped(self):
        relation = json.loads((SEGMENT / "vendor/T1_SOURCE_RELATION.json").read_text())
        source = relation["source_relation"]
        self.assertFalse(relation["run_authorized_now"])
        self.assertEqual(require_source_relation({"source_identity": {"sha256": source["reference_sha256"]}},
                                                 {"source_identity": {"sha256": source["candidate_sha256"]}},
                                                 relation),
                         "DECLARED_REVIEWED_SEMANTIC_RELATION_NOT_PROVED_BY_REDUCER")
        with self.assertRaises(SourceRelationHold):
            require_source_relation({"source_identity": {"sha256": source["candidate_sha256"]}},
                                    {"source_identity": {"sha256": source["reference_sha256"]}}, relation)
        with self.assertRaises(SourceRelationHold):
            require_source_relation({"source_identity": {"sha256": "0" * 64}},
                                    {"source_identity": {"sha256": "1" * 64}}, {"source_relation": ["invalid"]})
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            ref = hashlib.sha256(b"SYNTHETIC_SAME_SOURCE").hexdigest()
            cand = hashlib.sha256(b"SYNTHETIC_OTHER_SOURCE").hexdigest()
            manufactured = {"reference_sha256": ref, "candidate_sha256": cand,
                            "relation": "REVIEWED_SAME_PHYSICAL_MODEL", "status": "ACCEPTED_SCOPED",
                            "evidence": "MANUFACTURED_TEST_RELATION_ONLY"}
            result, _ = pair(root, unequal=True, kind="REFINEMENT", relation=manufactured)
            self.assertEqual(result["status"], "DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED")
            self.assertEqual(result["scientific_admission"], "NOT_ISSUED")
            self.assertEqual(result["solver_runs"], 0)

    def test_config_change_still_restricted(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, _ = pair(pathlib.Path(tmp), extra_candidate_config="escape_fraction=.9\n")
            self.assertEqual(result["status"], "HOLD_PAIRED_OTHER_INPUTS_CHANGED")

    def test_invalid_norm_and_incomplete_history_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            result, _ = pair(root, mode="TRUE_IVP_FROM_SAMPLES")
            self.assertEqual(result["status"], "HOLD_RECONSTRUCTION_NORM_MODE")
            self.assertFalse((root / "out/comparison_summary.csv").exists())
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            _, manifest = pair(root)
            terminal = pathlib.Path(manifest["candidate"]["terminal"]["path"])
            terminal.write_text("status=STOPPED_CHECKPOINTED\n")
            manifest["candidate"]["terminal"]["sha256"] = sha(terminal)
            (root / "manifest.json").write_text(json.dumps(manifest))
            with redirect_stdout(io.StringIO()):
                result = M.run(root / "manifest.json", root / "incomplete")
            self.assertEqual(result["status"], "UNKNOWN_INCOMPLETE_HISTORY")
            self.assertIsNone(result["metrics"])

    def test_no_extrapolation_or_nonincreasing_knots(self):
        with self.assertRaises(ValueError):
            reconstruction_norm([(0, 0), (1, 1)], [(0, 0), (2, 1)], "LN_A")
        with self.assertRaises(ValueError):
            reconstruction_norm([(0, 0), (0, 1)], [(0, 0), (1, 1)], "LN_A")

    def test_preserved_reducer_self_test(self):
        with redirect_stdout(io.StringIO()) as stream:
            M.self_test()
        self.assertIn("SYNTHETIC_SELF_TEST_PASS", stream.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
