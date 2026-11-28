"""One bounded verification batch for the new generic kernel; never integrates ODEs."""
from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import time
import unittest

import bell_kernel as kernel

HERE = Path(__file__).resolve().parent
GRID: list[dict] = []
COUNTS = {"completed_order_profiles": 0, "scalar_quadrature_sums": 0,
          "E1_oracle_evaluations": 0, "new_ODE": 0, "old_test_reruns": 0}


class BellKernelVerification(unittest.TestCase):
    def setUp(self) -> None:
        # Abstract pure-A model, intentionally not a species registration.
        self.p = kernel.BellParameters(10.0, 4.0e-14, (), "abstract pure-A analytic witness")

    def test_01_pure_a_rate_and_incident_moment_against_e1(self) -> None:
        for u in (2.0, 5.39, 13.6, 24.6, 100.0, 255.0, 600.0, 700.0, 1119.5):
            temperature = self.p.threshold_eV / (kernel.KB_EV_K * u)
            model = kernel.evaluate_maxwellian(self.p, temperature)
            COUNTS["completed_order_profiles"] += 2
            COUNTS["scalar_quadrature_sums"] += 4
            oracle = kernel.pure_a_oracle(self.p, temperature)
            COUNTS["E1_oracle_evaluations"] += 1
            comparisons = []
            for profile in (model.order32, model.order64):
                rate_error = abs(math.expm1(profile.log_rate_cm3_s - oracle.log_rate_cm3_s))
                moment_error = abs(profile.mean_excess_energy_eV / oracle.mean_excess_energy_eV - 1.0)
                comparisons.append({"order": profile.order, "relative_rate_error": rate_error,
                                    "relative_mean_excess_error": moment_error})
                with self.subTest(u=u, order=profile.order):
                    limit = 2e-8 if profile.order == 32 else 2e-11
                    self.assertLess(rate_error, limit)
                    self.assertLess(moment_error, limit)
                    self.assertGreater(profile.mean_incident_energy_eV, self.p.threshold_eV)
                    self.assertEqual(profile.positive_node_count, profile.order)
            GRID.append({"u": u, "temperature_K": temperature,
                         "assessment": asdict(model), "oracle": asdict(oracle),
                         "comparisons": comparisons})

    def test_threshold_and_absolute_cross_section(self) -> None:
        self.assertEqual(kernel.cross_section_cm2(self.p, 0.0), 0.0)
        self.assertEqual(kernel.cross_section_cm2(self.p, 9.999), 0.0)
        self.assertEqual(kernel.cross_section_cm2(self.p, 10.0), 0.0)
        # Algebraic exact value at E=2I for the independently specified pure-A model.
        expected = 4.0e-14 * math.log(2.0) / 200.0
        self.assertAlmostEqual(kernel.cross_section_cm2(self.p, 20.0) / expected, 1.0, places=13)

    def test_parameters_are_explicit_and_immutable(self) -> None:
        with self.assertRaises(TypeError):
            kernel.BellParameters()  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            kernel.BellParameters(10.0, 4e-14, [], "mutable B rejected")  # type: ignore[arg-type]
        with self.assertRaises(FrozenInstanceError):
            self.p.threshold_eV = 5.0  # type: ignore[misc]
        self.assertEqual(kernel.PHYSICAL_ADMISSION, "NOT_ISSUED")

    def test_invalid_inputs_are_rejected(self) -> None:
        for temperature in (0.0, -1.0, math.nan, math.inf):
            with self.subTest(temperature=temperature), self.assertRaises(ValueError):
                kernel.maxwellian_at_order(self.p, temperature, 32)
        for order in (0, 8, 64.0, True):
            with self.subTest(order=order), self.assertRaises(ValueError):
                kernel.maxwellian_at_order(self.p, 300.0, order)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            kernel.maxwellian_at_order(self.p, True, 32)
        with self.assertRaises(ValueError):
            kernel.cross_section_cm2(self.p, -1.0)

    def test_negative_cross_section_is_rejected_without_clipping(self) -> None:
        p = kernel.BellParameters(10.0, 1e-14, (-1e-12,), "deliberately unphysical witness")
        with self.assertRaises(kernel.CrossSectionPositivityError):
            kernel.cross_section_cm2(p, 10.1)
        with self.assertRaises(kernel.CrossSectionPositivityError):
            kernel.maxwellian_at_order(p, 300.0, 32)

    def test_logarithmic_underflow_has_no_physical_zero_claim(self) -> None:
        # Reuse the computed new-batch witness, rather than rerun its quadrature.
        row = next((row for row in GRID if row["u"] == 1119.5), None)
        if row is None:
            # Only needed if the independent grid witness itself failed earlier.
            temperature = self.p.threshold_eV / (kernel.KB_EV_K * 1119.5)
            profile = kernel.maxwellian_at_order(self.p, temperature, 64)
            COUNTS["completed_order_profiles"] += 1
            COUNTS["scalar_quadrature_sums"] += 2
        else:
            profile = kernel.RateEstimate(**row["assessment"]["order64"])
        self.assertTrue(profile.rate_underflow)
        self.assertEqual(profile.rate_cm3_s, 0.0)
        self.assertTrue(math.isfinite(profile.log_rate_cm3_s))
        self.assertGreater(profile.mean_excess_energy_eV, 0.0)
        with self.assertRaises(FrozenInstanceError):
            profile.rate_cm3_s = 1.0  # type: ignore[misc]


def main() -> int:
    start_wall = time.monotonic()
    start_cpu = time.process_time()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BellKernelVerification)
    # Preserve exact names before unittest consumes its suite iterator.
    names = [test.id() for test in suite]
    stream = io.StringIO()
    outcome = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    previous = sorted(HERE.glob("BELL_KERNEL_VERIFY_ATTEMPT_*.json"))
    attempt = len(previous) + 1
    receipt = {
        "schema": "phys80.bell-kernel.finite-verification.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "attempt": attempt, "status": "PASS" if outcome.wasSuccessful() else "FAIL",
        "unique_test_count": len(names), "unique_test_names": names,
        "tests_run": outcome.testsRun, "failures": len(outcome.failures),
        "errors": len(outcome.errors), "skipped": len(outcome.skipped),
        "operation_counts": COUNTS,
        "quadrature_comparison_count": len(GRID) * 2,
        "quadrature_observable_comparison_count": len(GRID) * 2 * 2,
        "cpu_seconds": time.process_time() - start_cpu,
        "wall_seconds": time.monotonic() - start_wall,
        "physical_admission": kernel.PHYSICAL_ADMISSION,
        "scope": "New abstract pure-A kernel witnesses only; no species admission or ODE.",
        "source_hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                          for name in ("bell_kernel.py", "verify_bell_kernel.py")},
        "grid": GRID, "stdout": stream.getvalue(),
    }
    payload = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    (HERE / f"BELL_KERNEL_VERIFY_ATTEMPT_{attempt:03d}.json").write_text(payload)
    (HERE / "BELL_KERNEL_VERIFY_RECEIPT.json").write_text(payload)
    print(stream.getvalue(), end="")
    print(json.dumps({key: receipt[key] for key in ("status", "unique_test_count", "operation_counts", "cpu_seconds")}, sort_keys=True))
    return 0 if outcome.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
