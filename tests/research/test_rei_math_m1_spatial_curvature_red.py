#!/usr/bin/env python3
"""Intentional RED for the generic homogeneous spatial-curvature oracle."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = (
    ROOT
    / "research"
    / "rei_math_m1_generic_background"
    / "derive_spatial_curvature.py"
)


def load_module():
    if not MODULE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("rei_m1_curvature", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenericSpatialCurvatureExpectedRed(unittest.TestCase):
    def test_symbolic_oracle_module_exists(self) -> None:
        self.assertTrue(MODULE.is_file(), "M1_CURVATURE_ORACLE_ABSENT")

    def test_commutator_and_koszul_conventions_are_explicit(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        self.assertEqual(
            module.CONVENTIONS,
            {
                "metric_signature": "(-,+,+,+)",
                "spatial_orientation": "epsilon_123=+1",
                "commutator": "[e_a,e_b]=C^c_ab e_c",
                "structure": "C^c_ab=epsilon_abd n^(dc)+a_a delta^c_b-a_b delta^c_a",
                "curvature": "R(X,Y)Z=nabla_X nabla_Y Z-nabla_Y nabla_X Z-nabla_[X,Y] Z",
                "c": "explicit",
            },
        )

    def test_generic_ricci_tensor_reduces_modulo_jacobi(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        report = module.run_symbolic_audit()
        self.assertEqual(report["ricci_residuals_mod_jacobi"], [["0"] * 3 for _ in range(3)])

    def test_generic_ricci_scalar_reduces_modulo_jacobi(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        report = module.run_symbolic_audit()
        self.assertEqual(report["scalar_residual_mod_jacobi"], "0")

    def test_codazzi_divergence_identity_is_derived(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        report = module.run_symbolic_audit()
        self.assertEqual(report["codazzi_divergence_residuals"], ["0", "0", "0"])

    def test_bianchi_I_sentinel(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        self.assertEqual(
            module.sentinel_report()["I"],
            {"ricci": [["0"] * 3 for _ in range(3)], "scalar": "0"},
        )

    def test_bianchi_V_open_flrw_sentinel(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        self.assertEqual(
            module.sentinel_report()["V"],
            {
                "ricci": [["-2*A**2", "0", "0"], ["0", "-2*A**2", "0"], ["0", "0", "-2*A**2"]],
                "scalar": "-6*A**2",
            },
        )

    def test_bianchi_IX_closed_flrw_sentinel(self) -> None:
        module = load_module()
        self.assertIsNotNone(module, "M1_CURVATURE_ORACLE_ABSENT")
        self.assertEqual(
            module.sentinel_report()["IX"],
            {
                "ricci": [["N**2/2", "0", "0"], ["0", "N**2/2", "0"], ["0", "0", "N**2/2"]],
                "scalar": "3*N**2/2",
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
