#!/usr/bin/env python3
"""C7: compare new binary64 APIs to the cached independent R7 oracle.

This file never imports or executes probe_nonlinear.py, solves a Fraction
system, runs a native solver, or reads physical histories. Fraction is used
only to decode the cached rational strings. Run only after C7 release.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest


sys.dont_write_bytecode = True
UNIT = Path(__file__).resolve().parents[1]
CACHE_PATH = UNIT / "probe/RESULT.json"
CACHE = json.loads(CACHE_PATH.read_text())
SPEC = json.loads((UNIT / "FIXTURE_SPEC.json").read_text())
CONTRACT = json.loads((UNIT / "CONTRACT.json").read_text())
TOLERANCES = CONTRACT["implementation_acceptance"]["float_fixture_tolerances"]
REL, ABS = TOLERANCES["relative"], TOLERANCES["absolute"]
module_spec = importlib.util.spec_from_file_location("nonlinear_budget_c7_subject", UNIT / "nonlinear_budget.py")
SUBJECT = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = SUBJECT
module_spec.loader.exec_module(SUBJECT)
EVIDENCE = {"scope": "SYNTHETIC_API_COMPARISON_TO_CACHED_R7_ONLY",
            "oracle_file": "probe/RESULT.json",
            "oracle_sha256": hashlib.sha256(CACHE_PATH.read_bytes()).hexdigest(),
            "oracle_reexecutions": 0, "new_fraction_solves": 0,
            "relative_tolerance": REL, "absolute_tolerance": ABS,
            "tolerance_scope": TOLERANCES["scope"],
            "core_fixtures": {}, "adapter_fixtures": {},
            "actual_stage_attribution": "NOT_RUN_MISSING_RESIDUAL_AND_JACOBIAN_PACKET",
            "native_builds": 0, "native_solver_runs": 0, "physical_history_reads": 0}


def numeric(value):
    if isinstance(value, list):
        return [numeric(x) for x in value]
    return float(Fraction(value))


def synthetic_packet(name, fixture):
    y = numeric(fixture["state"])
    context = "SYNTHETIC_C7_" + name
    return {"schema_version": 1, "input_kind": "SYNTHETIC_FIXTURE",
            "state_order": CONTRACT["state_order"], "energy_unit": "eV_per_H",
            "method": "BACKWARD_EULER_PREPARED_ABSORPTION",
            "old_state": numeric(fixture["old_state"]), "state": y,
            "residual": numeric(fixture["residual"]), "jacobian": numeric(fixture["jacobian"]),
            "residual_evaluation_state": list(y), "jacobian_evaluation_state": list(y),
            "context_id": context, "residual_context_id": context, "jacobian_context_id": context,
            "a": 1.0/21.0, "dt_s": 1.0, "f_He": numeric(SPEC["f_He"]),
            "k_B_eV_per_K": numeric(SPEC["k_B_eV_per_K"]), "jacobian_kind": "ANALYTIC"}


class CachedOracleScience(unittest.TestCase):
    def compare_numeric(self, actual, expected, path=""):
        """Return absolute residuals while enforcing the frozen fixture gate."""
        if isinstance(expected, list):
            self.assertIsInstance(actual, (list, tuple), path)
            self.assertEqual(len(actual), len(expected), path)
            errors = []
            for i, (a, e) in enumerate(zip(actual, expected)):
                errors.extend(self.compare_numeric(a, e, f"{path}[{i}]"))
            return errors
        target = numeric(expected)
        self.assertIsInstance(actual, (int, float), path)
        self.assertNotIsInstance(actual, bool, path)
        self.assertTrue(math.isfinite(actual), path)
        self.assertTrue(math.isclose(actual, target, rel_tol=REL, abs_tol=ABS),
                        f"{path}: actual={actual!r}; cached={expected}; target={target!r}")
        return [abs(actual-target)]

    def test_core_seven_cached_matrix_fixtures(self):
        fixture_names = [name for name in CACHE["fixtures"] if name != "BE_pair_cancellation"]
        self.assertEqual(len(fixture_names), 7)
        solved = {}
        field_map = {"A": "A", "b": "b", "residual_scales": "residual_scale",
                     "state_scales": "state_scale", "scaled_correction": "scaled_correction",
                     "delta": "delta", "native_scaled_residual_inf": "native_scaled_residual_inf",
                     "scaled_correction_inf": "scaled_correction_inf", "kappa_inf": "kappa_inf",
                     "linear_equation_residual": "linear_equation_residual",
                     "linear_backward_error": "linear_backward_error"}
        for name in fixture_names:
            with self.subTest(fixture=name):
                expected = CACHE["fixtures"][name]
                result = SUBJECT.solve_scaled(numeric(expected["residual"]), numeric(expected["jacobian"]),
                                              numeric(expected["residual_scale"]), numeric(expected["state_scale"]))
                if name == "singular":
                    self.assertEqual(result["status"], "HOLD")
                    self.assertEqual(result["reason"], "HOLD_SINGULAR_JACOBIAN")
                    self.assertIsNone(result["metrics"])
                    EVIDENCE["core_fixtures"][name] = {"result": "PASS_TYPED_HOLD", "metrics": None}
                    continue
                self.assertEqual(result["status"], "LINEAR_SYSTEM_DIAGNOSTIC")
                metrics = result["metrics"]
                errors = {}
                for field, cached in field_map.items():
                    errors[field] = max(self.compare_numeric(metrics[field], expected[cached], f"{name}.{field}"))
                solved[name] = metrics
                EVIDENCE["core_fixtures"][name] = {"result": "PASS_SCOPED", "absolute_residual_by_field": errors}
        # Reuse the two outcomes already calculated above for this comparison.
        for field in ("A", "b", "scaled_correction", "scaled_correction_inf", "kappa_inf"):
            self.compare_numeric(solved["energy_unit_change"][field],
                                 solved["coupled"][field], "unit_invariance."+field)
        EVIDENCE["energy_unit_invariance"] = "PASS_SCOPED_GENERIC_CORE_ONLY"

    def test_adapter_cached_thermal_and_synthetic_labels(self):
        for name in ("identity", "coupled", "floor_bridge", "large_inverse", "EOS_composition_cancellation"):
            with self.subTest(fixture=name):
                expected = CACHE["fixtures"][name]
                result = SUBJECT.analyze_stage(synthetic_packet(name, expected))
                self.assertEqual(result["status"], "SYNTHETIC_LINEARIZED_DIAGNOSTIC")
                self.assertEqual(result["input_kind"], "SYNTHETIC_FIXTURE")
                self.assertIsNone(result["nonlinear_error_certificate"])
                self.assertEqual(result["scientific_admission"], "NOT_ISSUED")
                self.assertEqual(result["correction_scope"], "CHEMICAL_STAGE_ONLY_NO_STATE_COMMIT")
                metrics = result["metrics"]
                errors = {}
                for field in ("delta", "scaled_correction_inf", "native_scaled_residual_inf", "kappa_inf"):
                    errors[field] = max(self.compare_numeric(metrics[field], expected[field], f"{name}.{field}"))
                ratio = numeric(expected["scaled_correction_inf"])/numeric(SPEC["target"])
                self.assertTrue(math.isclose(metrics["correction_to_local_target"], ratio,
                                             rel_tol=REL, abs_tol=ABS), name)
                self.assertEqual(metrics["passes_frozen_newton_inequality"],
                                 expected["passes_production_residual_inequality_synthetic_only"])
                actual_thermal, cached_thermal = metrics["thermal"], expected["thermal"]
                for field in ("temperature_before", "delta_temperature_linear", "corrected_state"):
                    errors["thermal."+field] = max(self.compare_numeric(actual_thermal[field], cached_thermal[field], name+"."+field))
                if name == "large_inverse":
                    self.assertEqual(actual_thermal["corrected_domain"], "INVALID")
                    self.assertIsNone(actual_thermal["temperature_corrected"])
                    self.assertIsNone(actual_thermal["delta_temperature_exact_map"])
                    self.assertTrue(actual_thermal["exact_map_hold_reason"])
                else:
                    self.assertEqual(actual_thermal["corrected_domain"], "VALID")
                    for field in ("temperature_corrected", "delta_temperature_exact_map"):
                        errors["thermal."+field] = max(self.compare_numeric(actual_thermal[field], cached_thermal[field], name+"."+field))
                EVIDENCE["adapter_fixtures"][name] = {"result": "PASS_SCOPED", "absolute_residual_by_field": errors,
                                                    "input_kind": result["input_kind"], "scientific_admission": result["scientific_admission"]}


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CachedOracleScience)
    outcome = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    # The scalar BE example has no new API operation. Its actual R7 result is
    # carried as cached evidence, without recalculating q/qh or exp(-z).
    be = CACHE["fixtures"]["BE_pair_cancellation"]
    EVIDENCE["BE_pair_cancellation"] = {"result": "REUSED_R7_NOT_REEXECUTED",
                                        "exact_BE_pair_difference": be["exact_BE_pair_difference"],
                                        "observed_pair_difference": be["observed_pair_difference"],
                                        "rF": be["rF"], "actual_production_stage": be["actual_production_stage"]}
    EVIDENCE["test_cases"] = outcome.testsRun
    EVIDENCE["failures"] = len(outcome.failures)
    EVIDENCE["errors"] = len(outcome.errors)
    EVIDENCE["result"] = "PASS_SCOPED" if outcome.wasSuccessful() else "FAIL"
    all_errors = [error for group in (EVIDENCE["core_fixtures"], EVIDENCE["adapter_fixtures"])
                  for entry in group.values() for error in entry.get("absolute_residual_by_field", {}).values()]
    EVIDENCE["maximum_observed_absolute_metric_residual"] = max(all_errors, default=None)
    EVIDENCE["residual_scope"] = "Observed fixture metrics in their respective scales/units; no universal error bound"
    print(json.dumps(EVIDENCE, indent=2, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
