"""Delta-only tests; actual source evaluation uses the one selected 20000 K point."""
from decimal import Decimal, localcontext
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest


UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "src"))
import source_diagnostic as diagnostic


PI60 = Decimal("3.14159265358979323846264338327950288419716939937510582097494")


def decimal_original_cpp_value_and_derivative(temperature, coefficients):
    """60-digit original e/(e+1/e) quotient, differentiated before reduction."""
    with localcontext() as ctx:
        ctx.prec = 60
        a = [Decimal(str(x)) for x in coefficients]
        x = Decimal(str(temperature)).ln()
        e1 = ((x - a[2]) / a[3]).exp()
        e2 = ((x - a[5]) / a[6]).exp()
        d1, d2 = e1 + 1 / e1, e2 + 1 / e2
        de1, de2 = e1 / a[3], e2 / a[6]
        dd1 = de1 - de1 / (e1 * e1)
        dd2 = de2 - de2 / (e2 * e2)
        f = (a[0] + x * a[1]) * e1 / d1 + a[4] * e2 / d2
        df = (a[1] * e1 / d1 + (a[0] + x * a[1])
              * (de1 * d1 - e1 * dd1) / (d1 * d1)
              + a[4] * (de2 * d2 - e2 * dd2) / (d2 * d2))
        factor = PI60 * Decimal("1e-20")
        return +f * factor, +df * factor


class SourceDiagnosticTests(unittest.TestCase):
    def assert_relative(self, actual, expected, tolerance=5e-14):
        self.assertTrue(math.isclose(actual, float(expected), rel_tol=tolerance, abs_tol=0.0),
                        (actual, str(expected), tolerance))

    def test_frozen_source_at_one_selected_temperature(self):
        result = diagnostic.diagnose_h_he_source(20000.0)
        # Decimal coefficients come directly from the frozen source, rather
        # than from the implementation's binary64 coefficient conversion.
        source = json.loads(diagnostic.default_evidence_paths()["selected_source"].read_bytes())
        q11, derivative = decimal_original_cpp_value_and_derivative(
            20000, source["fit_rows"]["Q11"]["coefficients_decimal"])
        q12, _ = decimal_original_cpp_value_and_derivative(
            20000, source["fit_rows"]["Q12"]["coefficients_decimal"])
        self.assert_relative(result["Q11_saved_m2"], q11)
        self.assert_relative(result["Q12_m2"], q12)
        self.assert_relative(result["dQ11_dlnT_m2"], derivative)
        with localcontext() as ctx:
            ctx.prec = 60
            expected = derivative / q11 - 3 * (q12 / q11 - 1)
        self.assertAlmostEqual(result["same_law_residual"], float(expected), delta=5e-14)
        self.assertLessEqual(result["Q11_binding_relative_difference"],
                             result["Q11_binding_relative_tolerance"])
        self.assertEqual(result["source_temperature_count"], 1)
        self.assertFalse(result["temperature_scan_performed"])
        self.assertFalse(result["physical_provider_admitted"])
        self.assertFalse(result["residual_is_uncertainty"])
        self.assertIsNone(result["source_calibrated_uncertainty"])
        # The authorized runner can preserve this output without evaluating
        # the source a second time solely to produce a diagnostic artifact.
        print(json.dumps({"selected_source_diagnostic": result}, allow_nan=False, sort_keys=True))

    def test_manufactured_fit_against_decimal_original_at_domain_endpoints(self):
        coefficients = (12.0, 0.125, 7.0, -3.0, 4.0, 5.0, 2.0)
        for temperature in (50.0, 300.0, 50000.0):
            with self.subTest(temperature=temperature):
                expected, slope = decimal_original_cpp_value_and_derivative(temperature, coefficients)
                self.assert_relative(diagnostic.bruno_fit_area(temperature, coefficients), expected)
                self.assert_relative(diagnostic.bruno_fit_darea_dlogT(temperature, coefficients), slope)

    def test_manufactured_saturated_logistic_retains_small_derivative(self):
        # Both sigmoid values round to one in ordinary binary64. Using
        # sigmoid(z)*(1-sigmoid(z)) would incorrectly return zero slope.
        coefficients = (2.0, 0.0, -20.0, 1.0, 3.0, -22.0, 1.0)
        expected, derivative = decimal_original_cpp_value_and_derivative(50, coefficients)
        self.assert_relative(diagnostic.bruno_fit_area(50, coefficients), expected)
        actual = diagnostic.bruno_fit_darea_dlogT(50, coefficients)
        self.assertGreater(actual, 0.0)
        self.assert_relative(actual, derivative, tolerance=2e-13)

    def test_domain_and_scalar_rejections_before_source_evaluation(self):
        for value in (True, False, None, "20000", complex(20000, 0),
                      math.nan, math.inf, -math.inf, 0.0, -1.0,
                      math.nextafter(50.0, 0.0), math.nextafter(50000.0, math.inf), 10**400):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    diagnostic.diagnose_h_he_source(value)
        # These source-domain points are valid for generic manufactured
        # tests but excluded from this one-point actual-source allocation.
        for value in (50.0, 50000.0, math.nextafter(20000.0, math.inf)):
            with self.assertRaises(ValueError):
                diagnostic.diagnose_h_he_source(value)

    def test_invalid_coefficient_and_moment_inputs(self):
        valid = [12.0, 0.125, 7.0, -3.0, 4.0, 5.0, 2.0]
        for index, bad in ((0, True), (1, math.nan), (2, math.inf), (3, 0.0),
                           (6, 0.0), (4, complex(1, 0))):
            coefficients = list(valid)
            coefficients[index] = bad
            for function in (diagnostic.bruno_fit_area, diagnostic.bruno_fit_darea_dlogT):
                with self.assertRaises(ValueError):
                    function(300, coefficients)
        with self.assertRaises(ValueError):
            diagnostic.bruno_fit_area(300, valid[:-1])
        for inputs in ((True, 1.0, 0.0), (0.0, 1.0, 0.0), (1.0, -1.0, 0.0),
                       (1.0, 1.0, math.nan), (1e-300, 1e300, 0.0)):
            with self.assertRaises(ValueError):
                diagnostic.same_law_residual(*inputs)

    def test_exact_manufactured_identity_and_sign(self):
        # sigma_1 proportional to g**p gives Q12/Q11=(p+6)/6 and slope p/2.
        for power in (-2.0, 0.0, 2.0, 4.0):
            slope, ratio, residual = diagnostic.same_law_residual(
                2.0, 2.0 * (power + 6.0) / 6.0, power)
            self.assertEqual(slope, power / 2.0)
            self.assertAlmostEqual(residual, 0.0, delta=1e-15)
            self.assertEqual(ratio, (power + 6.0) / 6.0)
        self.assertGreater(diagnostic.same_law_residual(1.0, 1.0, 0.25)[2], 0.0)

    def test_changed_or_missing_evidence_is_rejected(self):
        paths = diagnostic.default_evidence_paths()
        with tempfile.TemporaryDirectory(prefix="he_source_identity_") as directory:
            altered = Path(directory) / "changed.json"
            altered.write_bytes(paths["selected_source"].read_bytes() + b"\n")
            changed = dict(paths)
            changed["selected_source"] = altered
            with self.assertRaisesRegex(ValueError, "Changed evidence identity: selected_source"):
                diagnostic.load_pinned_inputs(changed)
            changed = dict(paths)
            changed["saved_result"] = altered
            with self.assertRaisesRegex(ValueError, "Changed evidence identity: saved_result"):
                diagnostic.load_pinned_inputs(changed)
        missing = dict(paths)
        del missing["upstream_cpp"]
        with self.assertRaisesRegex(ValueError, "complete frozen evidence"):
            diagnostic.load_pinned_inputs(missing)


if __name__ == "__main__":
    unittest.main()
