#!/usr/bin/env python3
"""RED contract for path binding on the active freshness/live controller lane."""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = (
    ROOT
    / "handoff"
    / "rei_runtime_attempt_ref_protection_freshness_20260904"
)
CONTROLLER = PACKAGE / "successor_runtime_controller.py"
LEASE = PACKAGE / "lease_bound.py"
WORKER = PACKAGE / "native_runtime_worker.py"


def function(path: Path, name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"FUNCTION_NOT_FOUND:{path}:{name}")


def call_lines(path: Path, name: str) -> dict[str, int]:
    found: dict[str, int] = {}
    for node in ast.walk(function(path, name)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called = node.func.attr
        else:
            continue
        found.setdefault(called, node.lineno)
    return found


class ActiveFreshnessPathBindingExpectedRed(unittest.TestCase):
    def setUp(self) -> None:
        for path in (CONTROLLER, LEASE, WORKER):
            self.assertTrue(path.is_file(), f"REQUIRED_SOURCE_ABSENT:{path}")

    def test_active_controller_attests_paths_before_prelease_revalidation(self) -> None:
        calls = call_lines(CONTROLLER, "run_controller")
        self.assertIn(
            "validate_runtime_toolchain_witness_paths",
            calls,
            "P0_ACTIVE_CONTROLLER_PATH_ATTESTATION_ABSENT",
        )
        self.assertIn("revalidate_successor_toolchain", calls)
        self.assertLess(
            calls["validate_runtime_toolchain_witness_paths"],
            calls["revalidate_successor_toolchain"],
            "P0_ACTIVE_PATH_ATTESTATION_ORDER_INVALID",
        )

    def test_active_controller_binds_preflight_and_every_attempt_record(self) -> None:
        source = CONTROLLER.read_text(encoding="utf-8")
        for token in (
            "expected_runtime_toolchain_snapshot=runtime_snapshot",
            "runtime_toolchain_snapshot_sha256=runtime_snapshot_sha",
            '"runtime_toolchain_snapshot_sha256": runtime_snapshot_sha',
        ):
            self.assertIn(
                token,
                source,
                f"P0_ACTIVE_CONTROLLER_SNAPSHOT_BINDING_ABSENT:{token}",
            )

    def test_live_protection_global_lease_carries_runtime_snapshot(self) -> None:
        source = LEASE.read_text(encoding="utf-8")
        function_source = ast.get_source_segment(
            source, function(LEASE, "acquire_global_lease")
        )
        self.assertIsNotNone(function_source)
        self.assertIn(
            "runtime_toolchain_snapshot_sha256",
            function_source,
            "P0_LIVE_GLOBAL_LEASE_SNAPSHOT_ABSENT",
        )

    def test_active_worker_rechecks_paths_before_native_entry(self) -> None:
        calls = call_lines(WORKER, "main")
        self.assertIn(
            "validate_runtime_toolchain_witness_paths",
            calls,
            "P0_ACTIVE_WORKER_PATH_RECHECK_ABSENT",
        )
        self.assertIn("run_native_once", calls)
        self.assertLess(
            calls["validate_runtime_toolchain_witness_paths"],
            calls["run_native_once"],
            "P0_ACTIVE_WORKER_RECHECK_AFTER_NATIVE_ENTRY",
        )
        source = WORKER.read_text(encoding="utf-8")
        self.assertIn(
            "runtime_toolchain_snapshot_sha256",
            source,
            "P0_ACTIVE_WORKER_SNAPSHOT_HASH_GUARD_ABSENT",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
