from __future__ import annotations

import dataclasses
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[3]
STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load_bridge():
    path = STAGE / "analysis/rust_source_bound_thermal.py"
    spec = importlib.util.spec_from_file_location("rei_joint_backend_tests", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CertificateSemanticAliasTests(unittest.TestCase):
    def test_historical_residual_slots_expose_implicit_rhs_semantics(self) -> None:
        from rei_bianchi.joint_implicit_remainder import TangentCertificate

        certificate = TangentCertificate(
            request_sha256="1" * 64,
            precision_bits=256,
            rounding_policy="MPFR_RNDD_RNDU",
            backend_schema="rei-source-bound-mpfr256/v2",
            solution_lower=(-2.0, -1.0),
            solution_upper=(0.0, 1.0),
            krawczyk_lower=(-1.5, -0.5),
            krawczyk_upper=(-0.5, 0.5),
            center=(-1.0, 0.0),
            residual_lower=(-7.0, 3.0),
            residual_upper=(-7.0, 3.0),
            preconditioner=(1.0, 0.0, 0.0, 1.0),
            rho_upper=0.0,
            lower_margins=(0.5, 0.5),
            upper_margins=(0.5, 0.5),
            iterations=1,
            strict_self_inclusion=True,
            backend_identity_sha256="2" * 64,
        )
        self.assertEqual(certificate.implicit_rhs_lower, (-7.0, 3.0))
        self.assertEqual(certificate.implicit_rhs_upper, (-7.0, 3.0))


class JointImplicitRemainderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from rei_bianchi import joint_implicit_remainder

        cls.joint = joint_implicit_remainder
        cls.bridge = _load_bridge()
        cls.build_root = tempfile.TemporaryDirectory(prefix="rei-joint-rebuild-")
        cls.backend = cls.bridge.build_authenticated_backend(
            stage_dir=STAGE, output_dir=Path(cls.build_root.name)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build_root.cleanup()

    @staticmethod
    def corner_request():
        from rei_bianchi.joint_implicit_remainder import TangentRequest

        # A midpoint-only solve misses the valid negative endpoint corners.
        return TangentRequest(
            dimension=2,
            a_lower=(1.0, 0.0, 0.0, 1.0),
            a_upper=(4.0, 0.0, 0.0, 4.0),
            z_lower=(4.0, 7.0),
            z_upper=(4.0, 7.0),
            delta_a_lower=(0.375, 0.0, 0.0, 0.10714285714285714),
            delta_a_upper=(0.375, 0.0, 0.0, 0.10714285714285714),
            delta_b_lower=(0.0, 0.0),
            delta_b_upper=(0.0, 0.0),
            authority_sha256="1" * 64,
            owner_sha256="2" * 64,
            context_sha256="3" * 64,
        )

    def test_full_interval_a_contains_independent_corner_counterexample(self) -> None:
        request = self.corner_request()
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        self.joint.validate_tangent_certificate(request, certificate)
        for index, exact_corners in enumerate(((-1.5, -0.375), (-0.75, -0.1875))):
            for corner in exact_corners:
                self.assertLessEqual(certificate.solution_lower[index], corner)
                self.assertGreaterEqual(certificate.solution_upper[index], corner)
        self.assertTrue(certificate.strict_self_inclusion)

    def test_three_by_three_full_interval_system_is_supported(self) -> None:
        request = self.joint.TangentRequest(
            dimension=3,
            a_lower=(2.0, 0.0, 0.0, 0.0, 4.0, 0.0, 0.0, 0.0, 6.0),
            a_upper=(3.0, 0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 7.0),
            z_lower=(1.0, 2.0, 3.0),
            z_upper=(1.0, 2.0, 3.0),
            delta_a_lower=(0.5, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 1.0 / 6.0),
            delta_a_upper=(0.5, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 1.0 / 6.0),
            delta_b_lower=(0.0, 0.0, 0.0),
            delta_b_upper=(0.0, 0.0, 0.0),
            authority_sha256="4" * 64,
            owner_sha256="5" * 64,
            context_sha256="6" * 64,
        )
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        exact_ranges = ((-0.25, -1.0 / 6.0), (-0.125, -0.1), (-1.0 / 12.0, -1.0 / 14.0))
        for lower, upper, (exact_lower, exact_upper) in zip(
            certificate.solution_lower, certificate.solution_upper, exact_ranges
        ):
            self.assertLessEqual(lower, exact_lower)
            self.assertGreaterEqual(upper, exact_upper)

    def test_tangent_replays_locked_krawczyk_fixture(self) -> None:
        request = self.joint.TangentRequest(
            dimension=2,
            a_lower=(1.5, -1.0, -1.0, 2.0),
            a_upper=(2.5, -1.0, -1.0, 2.0),
            z_lower=(0.75, 0.875),
            z_upper=(1.5, 1.25),
            delta_a_lower=(1.0, 0.0, 0.0, 0.0),
            delta_a_upper=(1.0, 0.0, 0.0, 0.0),
            delta_b_lower=(0.0, 0.0),
            delta_b_upper=(0.0, 0.0),
            candidate_lower=(-2.25, -1.125),
            candidate_upper=(0.75, 0.375),
            authority_sha256="1" * 64,
            owner_sha256="2" * 64,
            context_sha256="3" * 64,
        )
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        self.bridge.admit_tangent_certificate(request, certificate, backend=self.backend)
        self.assertEqual(certificate.solution_lower, request.candidate_lower)
        self.assertEqual(certificate.solution_upper, request.candidate_upper)
        self.assertEqual(certificate.residual_lower, (-1.5, -0.0))
        self.assertEqual(certificate.residual_upper, (-0.75, 0.0))
        self.assertEqual(certificate.center, (-0.75, -0.375))
        expected_c = (2.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0, 2.0 / 3.0)
        for observed, expected in zip(certificate.preconditioner, expected_c):
            self.assertAlmostEqual(observed, expected, places=15)
        for observed, exact in zip(certificate.krawczyk_lower, (-1.75, -0.875)):
            self.assertLessEqual(observed, exact)
        for observed, exact in zip(certificate.krawczyk_upper, (0.25, 0.125)):
            self.assertGreaterEqual(observed, exact)
        self.assertLess(certificate.rho_upper, 0.334)
        self.assertTrue(all(value > 0.0 for value in certificate.lower_margins))
        self.assertTrue(all(value > 0.0 for value in certificate.upper_margins))

    def test_three_by_three_locked_research_fixture(self) -> None:
        request = self.joint.TangentRequest(
            dimension=3,
            a_lower=(1.75, -1.0, 0.0, -1.0, 3.0, -1.0, 0.0, -1.0, 2.0),
            a_upper=(2.25, -1.0, 0.0, -1.0, 3.0, -1.0, 0.0, -1.0, 2.0),
            z_lower=(0.75, 0.875, 0.875),
            z_upper=(1.25, 1.125, 1.125),
            delta_a_lower=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            delta_a_upper=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            delta_b_lower=(0.0, 0.0, 0.0),
            delta_b_upper=(0.0, 0.0, 0.0),
            candidate_lower=(-1.125, -0.5, -0.25),
            candidate_upper=(-0.125, 0.0, 0.0),
            authority_sha256="4" * 64,
            owner_sha256="5" * 64,
            context_sha256="6" * 64,
        )
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        self.bridge.admit_tangent_certificate(request, certificate, backend=self.backend)
        self.assertEqual(certificate.residual_lower, (-1.25, 0.0, 0.0))
        self.assertEqual(certificate.residual_upper, (-0.75, 0.0, 0.0))
        self.assertEqual(certificate.center, (-0.625, -0.25, -0.125))
        self.assertLessEqual(certificate.rho_upper, 5.0 / 32.0)
        for observed, exact in zip(
            certificate.krawczyk_lower, (-245.0 / 256.0, -49.0 / 128.0, -49.0 / 256.0)
        ):
            self.assertLessEqual(observed, exact)
        for observed, exact in zip(
            certificate.krawczyk_upper, (-75.0 / 256.0, -15.0 / 128.0, -15.0 / 256.0)
        ):
            self.assertGreaterEqual(observed, exact)

    def test_linear_primitive_is_separate_from_tangent(self) -> None:
        request = self.joint.LinearRequest(
            dimension=2,
            a_lower=(2.0, -1.0, -5.0, 3.0),
            a_upper=(2.0, -1.0, -5.0, 3.0),
            b_lower=(1.0, 1.0),
            b_upper=(1.0, 1.0),
            candidate_lower=(3.5, 6.5),
            candidate_upper=(4.5, 7.5),
            authority_sha256="c" * 64,
            owner_sha256="d" * 64,
            context_sha256="e" * 64,
        )
        certificate = self.bridge.certify_linear(request, backend=self.backend)
        self.assertEqual(certificate.center, (4.0, 7.0))
        self.assertLess(certificate.rho_upper, 1.0)

    def mixed_request(self):
        return self.joint.MixedVfRequest(
            dimension=2,
            a_lower=(2.0, -1.0, -1.0, 1.0),
            a_upper=(2.0, -1.0, -1.0, 1.0),
            b_vf_lower=(13.0, 17.0),
            b_vf_upper=(13.0, 17.0),
            a_vf_lower=(1.0, 0.0, 0.0, 1.0),
            a_vf_upper=(1.0, 0.0, 0.0, 1.0),
            z_lower=(1.0, 2.0),
            z_upper=(1.0, 2.0),
            a_v_lower=(0.0, 1.0, 1.0, 0.0),
            a_v_upper=(0.0, 1.0, 1.0, 0.0),
            z_f_lower=(7.0, 11.0),
            z_f_upper=(7.0, 11.0),
            a_f_lower=(1.0, 1.0, 0.0, 1.0),
            a_f_upper=(1.0, 1.0, 0.0, 1.0),
            z_v_lower=(3.0, 5.0),
            z_v_upper=(3.0, 5.0),
            candidate_lower=(-4.5, -1.5),
            candidate_upper=(-3.5, -0.5),
            authority_sha256="7" * 64,
            owner_sha256="8" * 64,
            context_sha256="9" * 64,
        )

    def test_mixed_rhs_includes_all_three_matrix_products(self) -> None:
        request = self.mixed_request()
        lower, upper = self.bridge.diagnostic_mixed_rhs(request, backend=self.backend)
        self.assertEqual(lower, (-7.0, 3.0))
        self.assertEqual(upper, (-7.0, 3.0))

    def test_atomic_mixed_certificate_binds_every_term(self) -> None:
        request = self.mixed_request()
        certificate = self.bridge.certify_mixed_vf(request, backend=self.backend)
        self.assertEqual(certificate.request_sha256, request.sha256())
        self.assertEqual(certificate.residual_lower, (-7.0, 3.0))
        self.assertEqual(certificate.center, (-4.0, -1.0))
        self.bridge.admit_mixed_vf_certificate(request, certificate, backend=self.backend)
        for name, omitted_rhs, wrong_solution in (
            ("a_vf", (-6.0, 5.0), (-1.0, 4.0)),
            ("a_v", (4.0, 10.0), (14.0, 24.0)),
            ("a_f", (1.0, 8.0), (9.0, 17.0)),
        ):
            mutated = dataclasses.replace(
                request,
                **{
                    f"{name}_lower": (0.0, 0.0, 0.0, 0.0),
                    f"{name}_upper": (0.0, 0.0, 0.0, 0.0),
                    "candidate_lower": tuple(value - 0.5 for value in wrong_solution),
                    "candidate_upper": tuple(value + 0.5 for value in wrong_solution),
                },
            )
            self.assertEqual(
                self.bridge.diagnostic_mixed_rhs(mutated, backend=self.backend),
                (omitted_rhs, omitted_rhs),
            )
            with self.assertRaisesRegex(
                self.joint.CertificateValidationError, "REQUEST_DIGEST_MISMATCH"
            ):
                self.joint.validate_mixed_vf_certificate(mutated, certificate)

    def test_missing_delta_a_and_mixed_terms_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            self.joint.CertificateValidationError, "MISSING_DELTA_A"
        ):
            self.joint.TangentRequest(
                dimension=2,
                a_lower=(1.0, 0.0, 0.0, 1.0),
                a_upper=(1.0, 0.0, 0.0, 1.0),
                z_lower=(1.0, 1.0),
                z_upper=(1.0, 1.0),
                delta_a_lower=None,
                delta_a_upper=None,
                delta_b_lower=(0.0, 0.0),
                delta_b_upper=(0.0, 0.0),
                authority_sha256="7" * 64,
                owner_sha256="8" * 64,
                context_sha256="9" * 64,
            )
        values = dataclasses.asdict(self.mixed_request())
        values["a_f_lower"] = None
        values["a_f_upper"] = None
        with self.assertRaisesRegex(
            self.joint.CertificateValidationError, "MISSING_MIXED_TERM"
        ):
            self.joint.MixedVfRequest(**values)

    def test_structural_validation_is_not_backend_admission(self) -> None:
        request = self.corner_request()
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        forged = dataclasses.replace(certificate, backend_identity_sha256="f" * 64)
        self.joint.validate_tangent_certificate(request, forged)
        with self.assertRaisesRegex(self.bridge.RustBackendError, "BACKEND_IDENTITY_MISMATCH"):
            self.bridge.admit_tangent_certificate(request, forged, backend=self.backend)

    def test_non_strict_mutation_is_rejected(self) -> None:
        request = self.corner_request()
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        mutated = dataclasses.replace(
            certificate,
            krawczyk_lower=(certificate.solution_lower[0], certificate.krawczyk_lower[1]),
        )
        with self.assertRaisesRegex(
            self.joint.CertificateValidationError, "KRAWCZYK_NOT_STRICT_INTERIOR"
        ):
            self.joint.validate_tangent_certificate(request, mutated)

    def test_request_and_certificate_records_are_closed_and_canonical(self) -> None:
        request = self.corner_request()
        certificate = self.bridge.certify_tangent(request, backend=self.backend)
        self.assertEqual(certificate.request_sha256, request.sha256())
        self.assertNotIn(b"NaN", request.canonical_bytes())
        self.assertNotIn(b"Infinity", certificate.canonical_bytes())
        mapping = certificate.to_mapping()
        mapping["unexpected"] = 1
        with self.assertRaisesRegex(self.joint.CertificateValidationError, "UNKNOWN_FIELD"):
            self.joint.TangentCertificate.from_mapping(mapping)


if __name__ == "__main__":
    unittest.main()
