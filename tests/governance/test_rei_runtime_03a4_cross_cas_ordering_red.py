#!/usr/bin/env python3
"""Intentional RED contract for the 03A4 cross-CAS no-bypass sidecar."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "docs"
    / "rei_runtime_bridge_03a4_cross_cas"
    / "cross_cas_contract.py"
)
EXPECTED_NODES = (
    "IndependentAudit",
    "TargetHostStaticPreflight",
    "FreshProtectionReadback",
    "GlobalLease",
    "LocalLease",
    "DispatchIntent",
    "NativeWorker",
    "RuntimeResultAudit",
    "FirstIntervalEligibility",
    "ProviderReview",
)
EXPECTED_EDGES = tuple(zip(EXPECTED_NODES[:-1], EXPECTED_NODES[1:]))


def load_future():
    spec = importlib.util.spec_from_file_location("rei_03a4_cross_cas", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CrossCasOrderingExpectedRed(unittest.TestCase):
    def test_exact_canonical_node_order(self) -> None:
        module = load_future()
        self.assertEqual(module.NODES, EXPECTED_NODES)
        self.assertEqual(module.EDGES, EXPECTED_EDGES)

    def test_sympy_exact_chain_and_boolean_implications(self) -> None:
        module = load_future()
        result = module.verify_sympy_exact()
        self.assertTrue(all(result.values()))

    def test_mpmath_high_precision_matrix_witness(self) -> None:
        module = load_future()
        result = module.verify_mpmath_numeric()
        self.assertEqual(result["precision_decimal_digits"], 100)
        self.assertEqual(result["a_power_n_norm"], "0.0")
        self.assertEqual(result["a_power_n_minus_1_nonzero"], 1)

    def test_forbidden_shortcut_is_rejected(self) -> None:
        module = load_future()
        mutation = module.EDGES + (("IndependentAudit", "NativeWorker"),)
        self.assertFalse(module.is_exact_adjacent_chain(mutation))
        self.assertTrue(module.has_prelease_native_bypass(mutation))

    def test_receipt_is_methodology_only(self) -> None:
        module = load_future()
        receipt = module.build_receipt(
            sympy_result=module.verify_sympy_exact(),
            mpmath_result=module.verify_mpmath_numeric(),
            external_axes={
                "octave": "NOT_RUN_IN_PYTHON_TEST",
                "sage": "NOT_RUN_IN_PYTHON_TEST",
                "singular": "NOT_RUN_IN_PYTHON_TEST",
                "lean_mathlib": "NOT_RUN_IN_PYTHON_TEST",
            },
        )
        self.assertEqual(receipt["authority_effect"], "NONE")
        self.assertEqual(receipt["native_runtime"], "NOT_RUN")
        self.assertEqual(receipt["global_attempt_ref"], "ABSENT_REQUIRED")
        self.assertEqual(receipt["next_canonical_node"], "TARGET_HOST_STATIC_PREFLIGHT")

    def test_all_external_fixtures_are_declared(self) -> None:
        module = load_future()
        self.assertEqual(
            set(module.EXTERNAL_FIXTURES),
            {"octave", "sage", "singular", "lean_mathlib"},
        )

    def test_no_repository_or_native_mutation_surface(self) -> None:
        load_future()
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            'method="POST"',
            'method="PATCH"',
            'method="DELETE"',
            "create_global_lease",
            "create_local_lease",
            "create_dispatch_intent",
            "native_runtime_worker",
            "run_native_once",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
