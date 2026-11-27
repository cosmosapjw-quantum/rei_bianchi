"""Focused PHYS73 split/reuse/exact-assembly checks; no old solver execution."""
import copy
from concurrent.futures import Future
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("validated_l64", Path(__file__).with_name("validated_l64.py"))
v = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v)


def fixture(directory):
    """Manufactured exact-zero saved chain; never labelled a physical result."""
    directory.mkdir(parents=True)
    req = v.fixed_request(37)
    binding = {"request": req, "source_sha256": v.SOURCE_SHA, "engine": {"fixture": True}, "HH_R10": "OFF"}
    fp = v.digest(binding)
    v.write_new(directory / "REQUEST.json", {"schema": "PHYS69_BAND_REQUEST_V1", "binding": binding, "fingerprint": fp})
    zero = v.zero_record()
    one = {"display": "1", "midpoint": {"mantissa": "1", "exponent2": 0},
           "radius": {"mantissa": "0", "exponent2": 0}}
    state = {"20,37": zero, "21,37": zero}
    panels = []
    for i in range(152):
        c = F(65) - F(2*i+1, 8)
        payload = {"schema": "PHYS69_VALIDATED_BAND_VOLterra_PANEL_V1", "request": req,
                   "source_sha256": v.SOURCE_SHA, "center": str(c), "left": str(c-F(1, 8)),
                   "right": str(c+F(1, 8)), "half_width": "1/8", "full_intermediate_sum": [37],
                   "Coulomb_modes": [20, 21, 37], "HH_R10": "OFF",
                   "pairs": [{"pair": [a, 37], "q_right": zero, "q_left": zero} for a in (20, 21)],
                   "second_Born_terms": [{"j": 37, "integral": zero}],
                   "second_Born_increment": zero,
                   "Coulomb_zero_free_lower": {str(j): one for j in (20, 21, 37)}}
        ph = v.digest(payload)
        name = f"panel_{i:04d}.json"
        v.write_new(directory / name, {"fingerprint": fp, "index": i,
                                     "right_state_sha256": v.digest(state),
                                     "payload_sha256": ph, "payload": payload})
        panels.append({"index": i, "file": name, "payload_sha256": ph})
    cert = {"schema": "PHYS69_FINITE_T_BAND_CERTIFICATE_V1", "fingerprint": fp,
            "request": req, "source_sha256": v.SOURCE_SHA, "engine": binding["engine"],
            "scientific_execution": "COMPLETE", "full_intermediate_sum": [37],
            "Coulomb_modes": [20, 21, 37], "pairs": [[20, 37], [21, 37]], "m": 0,
            "panel_count_required": 152, "panels": panels, "HH_R10": "OFF",
            "radial_cutoff_error_included": False, "excluded_angular_error_included": False,
            "original_driven_xi_certified": False, "completed_PHYS68_intermediate_0_to_28_integrations": 0,
            "D1_q_B_cutoff": state, "D2_B_cutoff": zero,
            "D2_numerical_absolute_error_l1": v.rational(F(0)), "numerical_absolute_goal_met": True,
            "status": "CERTIFIED_BAND_NUMERICAL_GOAL_MET"}
    v.write_new(directory / "CERTIFICATE.json", cert)
    return binding


class SplitAndAssemblyTests(unittest.TestCase):
    def test_disjoint_modes_cover_missing_only(self):
        reqs = [v.fixed_request(j) for j in v.MODES]
        self.assertEqual([r["min_ell"] for r in reqs], list(range(37, 65)))
        self.assertTrue(all(r["min_ell"] == r["max_ell"] for r in reqs))
        self.assertEqual({r["precision_bits"] for r in reqs}, {768})
        self.assertEqual({r["coefficient_bits"] for r in reqs}, {2048})
        self.assertEqual(28*F("1e-64") + F("1e-65"), F("2.81e-63"))
        self.assertLess(F("2.81e-63"), v.D2_GOAL)

    def test_forbidden_old_modes_and_coercions(self):
        for j in (0, 28, 29, 36, 65, True, 37.0):
            with self.subTest(j=j), self.assertRaises(ValueError):
                v.fixed_request(j)

    def test_one_radial_error_and_exact_addition(self):
        boxes = [((F(1, 3), F(1, 100)), (F(-2, 7), F(1, 200))),
                 ((F(2, 3), F(1, 400)), (F(2, 7), F(1, 800)))]
        result = v.combine_boxes(boxes, F(1, 1000))
        self.assertEqual(v.read_rational(result["midpoint_exact"]["real"]), 1)
        self.assertEqual(v.read_rational(result["midpoint_exact"]["imag"]), 0)
        self.assertEqual(v.read_rational(result["numerical_error_l1"]), F(3, 160))
        self.assertEqual(v.read_rational(result["one_L64_radial_beta2"]), F(1, 1000))
        self.assertEqual(v.read_rational(result["absolute_error_about_display_midpoint"]), F(79, 4000))
        self.assertFalse(result["goal_met"])

    def test_display_rounding_charged(self):
        r = v.combine_boxes([((F(1, 3), F(0)), (F(0), F(0)))], F(0), 2)
        self.assertEqual(r["display_midpoint"]["real"], "0.33")
        self.assertEqual(v.read_rational(r["display_rounding_error_l1"]), F(1, 300))

    def test_boundary_goal_uses_exact_fraction(self):
        zero = ((F(0), F(0)), (F(0), F(0)))
        self.assertTrue(v.combine_boxes([zero], v.D2_GOAL)["goal_met"])
        self.assertFalse(v.combine_boxes([zero], v.D2_GOAL + F("1e-100"))["goal_met"])

    def test_malformed_exact_records_rejected(self):
        for bad in ({"mantissa": True, "exponent2": 0},
                    {"mantissa": "1", "exponent2": 1.0},
                    {"mantissa": "1.2", "exponent2": 0}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                v.dyadic(bad)
        bad = copy.deepcopy(v.zero_record())
        bad["real"]["radius"]["mantissa"] = "-1"
        with self.assertRaises(ValueError):
            v.box(bad)

    def test_plan_is_read_only_and_preserves_inherited(self):
        before = [v.sha(v.ROOT/p) for p in (v.OLD_PATH, v.BAND_PATH)]
        p = v.plan(modes=(37,), workers=28)
        self.assertEqual(p["workers"], 1)
        self.assertEqual(p["new_panels_if_complete"], 152)
        self.assertEqual(p["inherited_panel_payloads_reintegrated"], 0)
        self.assertEqual(before, [v.sha(v.ROOT/p) for p in (v.OLD_PATH, v.BAND_PATH)])

    def test_aggregate_uses_one_tail_and_all129_pairs(self):
        # Assembly fixture only: zero high modes are not claimed physical data.
        synthetic = {}
        for j in v.MODES:
            synthetic[j] = ({"request": v.fixed_request(j), "scientific_execution": "COMPLETE",
                             "full_intermediate_sum": [j], "D2_B_cutoff": v.zero_record(),
                             "D1_q_B_cutoff": {f"{a},{j}": v.zero_record() for a in (20, 21)}}, "fixture")
        result = v.assemble(v.ROOT, synthetic)
        self.assertEqual(len(result["D1_B_cutoff"]), 129)
        self.assertTrue(result["D1_goal_met"])
        old, band, _, _ = v.inherited()
        num = sum(r for c in (old, band) for _, r in v.box(c["D2_B_cutoff"]))
        self.assertEqual(v.read_rational(result["D2"]["numerical_error_l1"]), num)
        self.assertEqual(v.read_rational(result["D2"]["absolute_error_about_display_midpoint"]),
                         num + v.read_rational(result["D2"]["one_L64_radial_beta2"])
                         + v.read_rational(result["D2"]["display_rounding_error_l1"]))
        # D1 failure must prevent the shared success status even with a small D2.
        bad = copy.deepcopy(synthetic)
        bad[37][0]["D1_q_B_cutoff"]["20,37"]["real"]["radius"] = {"mantissa": "1", "exponent2": 0}
        failed = v.assemble(v.ROOT, bad)
        self.assertFalse(failed["D1_goal_met"])
        self.assertEqual(failed["status"], "VALID_ENCLOSURE_GOAL_NOT_MET")

    def test_complete_worker_reuses_without_kernel_call_or_certificate_write(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            directory = out / "bands/j37"
            binding = fixture(directory)
            before = {p.name: v.sha(p) for p in directory.iterdir()}
            class Request:
                def __init__(self, **kw):
                    pass
                def validate(self):
                    return self
            def forbidden(*args, **kwargs):
                raise AssertionError("completed mode must not enter numerical kernel")
            fake = types.SimpleNamespace(BandRequest=Request, request_binding=lambda *a: binding,
                                         run_band_profiles=forbidden)
            with patch.object(v, "numerical_modules", return_value=fake):
                result = v._worker((37, str(out), str(v.ROOT), None))
            self.assertEqual(result["status"], "REUSED_COMPLETE_VERIFIED")
            self.assertEqual(result["new_panels"], 0)
            self.assertEqual(before, {p.name: v.sha(p) for p in directory.iterdir()})

    def test_corrupt_complete_chain_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            directory = Path(t) / "job"
            binding = fixture(directory)
            path = directory / "panel_0041.json"
            bad = json.loads(path.read_text())
            bad["right_state_sha256"] = "0" * 64
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "predecessor"):
                v.verify_new_certificate(directory, binding)

    def test_atomic_writer_preserves_existing_target_on_collision(self):
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / "CERTIFICATE.json"
            v.write_new(target, {"fixture": "first immutable record"})
            before = target.read_bytes()
            with self.assertRaises(FileExistsError):
                v.write_new(target, {"fixture": "must not overwrite"})
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(sorted(p.name for p in Path(t).iterdir()), ["CERTIFICATE.json"])

    def test_interrupted_writer_never_publishes_partial_target(self):
        with tempfile.TemporaryDirectory() as t:
            target = Path(t) / "REQUEST.json"
            with patch.object(v.os, "fsync", side_effect=OSError("injected pre-link failure")):
                with self.assertRaisesRegex(OSError, "injected"):
                    v.write_new(target, {"fixture": True})
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(t).iterdir()), [])
            v.write_new(target, {"fixture": "retry succeeds"})
            self.assertEqual(json.loads(target.read_text()), {"fixture": "retry succeeds"})

    def test_prepublication_request_orphan_is_not_promoted(self):
        # Model SIGKILL before the atomic link; no numerical worker is called.
        class EmptyFixturePool:
            def __init__(self, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def submit(self, function, job):
                future = Future()
                future.set_result({"j": job[0], "status": "FIXTURE_NO_SCIENCE",
                                   "new_panels": 0, "reused_panels": 0})
                return future
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            orphan = out / (".REQUEST.json." + "a" * 32 + ".tmp")
            orphan.write_text("incomplete uncommitted fixture")
            fake = types.SimpleNamespace(engine_identity=lambda: {"fixture": True})
            with patch.object(v, "numerical_modules", return_value=fake), \
                    patch.object(v, "ProcessPoolExecutor", EmptyFixturePool), \
                    patch("builtins.print"):
                result = v.run(out, workers=1, modes=(37,), max_new_panels=0)
            self.assertEqual(result["status"], "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE")
            self.assertEqual(result["new_panels"], 0)
            self.assertEqual(orphan.read_text(), "incomplete uncommitted fixture")
            marker = json.loads((out / "REQUEST.json").read_text())
            self.assertEqual(marker["binding"]["source_sha256"], v.SOURCE_SHA)
            self.assertFalse((out / "CERTIFICATE.json").exists())

    def test_forged_mode_coverage_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            directory = Path(t) / "job"
            binding = fixture(directory)
            path = directory / "CERTIFICATE.json"
            bad = json.loads(path.read_text())
            bad["full_intermediate_sum"] = [36]
            path.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "full_intermediate_sum"):
                v.verify_new_certificate(directory, binding)


if __name__ == "__main__":
    unittest.main()
