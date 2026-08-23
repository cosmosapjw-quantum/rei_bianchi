from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import math
from pathlib import Path
import sys
import unittest


STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE / "analysis"))
sys.path.insert(0, str(STAGE / "validation"))

import certificate_adapter as ca
import independent_exact_oracle as oracle
import verified_backend as vb


class PointLinearCertificateTests(unittest.TestCase):
    def _certify(self, matrix, rhs):
        return ca.certify_point_interval_system(matrix, matrix, rhs, rhs)

    def test_integer_witness_is_exact_and_independently_replayable(self) -> None:
        matrix = [[2.0, -1.0], [-5.0, 3.0]]
        rhs = [1.0, 1.0]
        certificate = self._certify(matrix, rhs)
        self.assertEqual(certificate.status, ca.LinearCertificateStatus.CERTIFIED_UNIQUE_POINT)
        self.assertEqual(certificate.solution_exact, ((4, 1), (7, 1)))
        self.assertEqual(
            [(item.lo, item.hi) for item in certificate.solution_binary64],
            [(4.0, 4.0), (7.0, 7.0)],
        )
        verdict = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, certificate)
        self.assertTrue(verdict.passed, verdict.failures)

    def test_m_matrix_witness_uses_adjacent_outward_bounds(self) -> None:
        matrix = [[11.0, -10000.0], [-10.0, 10001.0]]
        rhs = [1.0, 2.0]
        certificate = self._certify(matrix, rhs)
        self.assertEqual(certificate.status, ca.LinearCertificateStatus.CERTIFIED_UNIQUE_POINT)
        self.assertEqual(
            certificate.solution_exact,
            ((30001, 10011), (32, 10011)),
        )
        bounds = [(item.lo, item.hi) for item in certificate.solution_binary64]
        self.assertEqual(
            bounds,
            [
                (2.996803516132254, 2.9968035161322546),
                (0.0031964838677454796, 0.00319648386774548),
            ],
        )
        verdict = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, certificate)
        self.assertTrue(verdict.passed, verdict.failures)

    def test_independent_replay_rejects_corrupted_solution(self) -> None:
        matrix = [[2.0, -1.0], [-5.0, 3.0]]
        rhs = [1.0, 1.0]
        certificate = self._certify(matrix, rhs)
        corrupted = replace(certificate, solution_exact=((5, 1), (7, 1)))
        verdict = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, corrupted)
        self.assertFalse(verdict.passed)
        self.assertIn("exact residual is nonzero", verdict.failures)

    def test_independent_replay_rejects_each_det_digest_and_bound_mutation(self) -> None:
        matrix = [[2.0, -1.0], [-5.0, 3.0]]
        rhs = [1.0, 1.0]
        certificate = self._certify(matrix, rhs)

        determinant = replace(certificate, determinant=(2, 1))
        det_verdict = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, determinant)
        self.assertFalse(det_verdict.passed)
        self.assertIn("determinant witness mismatch", det_verdict.failures)

        digest = replace(certificate, canonical_input_digest="0" * 64)
        digest_verdict = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, digest)
        self.assertFalse(digest_verdict.passed)
        self.assertIn("canonical input digest mismatch", digest_verdict.failures)

        below_four = math.nextafter(4.0, -math.inf)
        bounds = replace(
            certificate,
            solution_binary64=(
                vb.Binary64Interval(below_four, below_four),
                certificate.solution_binary64[1],
            ),
        )
        bound_verdict = oracle.verify_point_certificate(matrix, matrix, rhs, rhs, bounds)
        self.assertFalse(bound_verdict.passed)
        self.assertIn("binary64 enclosure excludes exact solution", bound_verdict.failures)

    def test_nonpoint_and_singular_systems_never_certify(self) -> None:
        nonpoint = ca.certify_point_interval_system(
            [[1.0]], [[2.0]], [1.0], [1.0]
        )
        self.assertEqual(
            nonpoint.status,
            ca.LinearCertificateStatus.NONPOINT_INTERVAL_UNSUPPORTED,
        )
        singular = self._certify([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])
        self.assertEqual(singular.status, ca.LinearCertificateStatus.SINGULAR)
        self.assertIsNone(singular.solution_exact)

    def test_nonfinite_input_is_typed_and_never_certified(self) -> None:
        result = self._certify([[float("nan")]], [1.0])
        self.assertEqual(result.status, ca.LinearCertificateStatus.NONFINITE_INPUT)
        self.assertIsNone(result.solution_exact)

    def test_output_overflow_is_typed_not_certified(self) -> None:
        tiny = float.fromhex("0x0.0000000000001p-1022")
        certificate = self._certify([[tiny]], [sys.float_info.max])
        self.assertEqual(
            certificate.status,
            ca.LinearCertificateStatus.ENCLOSURE_OVERFLOW,
        )
        self.assertIsNone(certificate.solution_binary64)

    def test_row_permutation_preserves_exact_solution(self) -> None:
        first = self._certify([[3.0, 1.0], [1.0, 2.0]], [7.0, 5.0])
        permuted = self._certify([[1.0, 2.0], [3.0, 1.0]], [5.0, 7.0])
        self.assertEqual(first.status, ca.LinearCertificateStatus.CERTIFIED_UNIQUE_POINT)
        self.assertEqual(first.solution_exact, ((Fraction(9, 5).numerator, 5), (8, 5)))
        self.assertEqual(first.solution_exact, permuted.solution_exact)


if __name__ == "__main__":
    unittest.main()
