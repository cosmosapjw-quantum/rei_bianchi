#!/usr/bin/env python3
"""Intentional RED for 03A4 runtime-toolchain witness path binding.

This test-only suite proves that an exact-hash compiler or native-library copy
at an arbitrary caller-selected path must not stand in for the hard-coded paths
that the post-lease production bridge will actually use.  It is static and
must not contact GitHub, create attempt state, import the production bridge,
start a worker, or run native code.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_prelease_import_firewall_green_20260903"
CONTRACT = PACKAGE / "CONTRACT.json"
PREFLIGHT = PACKAGE / "successor_section0_preflight_bound_impl.py"
COMMON = PACKAGE / "common_v3_impl.py"
CONTROLLER = PACKAGE / "successor_runtime_controller.py"
WORKER = PACKAGE / "native_runtime_worker.py"
BRIDGE = (
    ROOT
    / "stages"
    / "REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
    / "analysis"
    / "rust_source_bound_thermal.py"
)

EXPECTED_RUNTIME_PATHS = {
    "cc": "/usr/bin/x86_64-linux-gnu-gcc",
    "ld": "/usr/bin/ld",
    "mpfr": "/usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1",
    "gmp": "/usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _function(path: Path, name: str) -> ast.FunctionDef:
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"FUNCTION_NOT_FOUND:{path}:{name}")


def _function_text(path: Path, name: str) -> str:
    source = path.read_text(encoding="utf-8")
    node = _function(path, name)
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise AssertionError(f"FUNCTION_SOURCE_UNAVAILABLE:{path}:{name}")
    return segment


def _call_lines(path: Path, name: str) -> dict[str, int]:
    calls: dict[str, int] = {}
    for node in ast.walk(_function(path, name)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            called = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called = node.func.attr
        else:
            continue
        calls.setdefault(called, node.lineno)
    return calls


class ToolchainWitnessPathBindingExpectedRed(unittest.TestCase):
    def setUp(self) -> None:
        for path in (CONTRACT, PREFLIGHT, COMMON, CONTROLLER, WORKER, BRIDGE):
            self.assertTrue(path.is_file(), f"REQUIRED_SOURCE_ABSENT:{path}")

    def test_contract_declares_exact_postlease_runtime_paths(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        binding = contract.get("runtime_toolchain_path_binding")
        self.assertIsInstance(
            binding,
            dict,
            "P0_RUNTIME_TOOLCHAIN_PATH_BINDING_ABSENT",
        )
        self.assertEqual(
            binding.get("paths"),
            EXPECTED_RUNTIME_PATHS,
            "P0_RUNTIME_TOOLCHAIN_PATH_MAP_MISMATCH",
        )
        self.assertEqual(binding.get("authority"), "POSTLEASE_PRODUCTION_PATHS")

    def test_preflight_validates_witness_paths_before_section0_emission(self) -> None:
        calls = _call_lines(PREFLIGHT, "run_read_only_preflight")
        self.assertIn(
            "validate_runtime_toolchain_witness_paths",
            calls,
            "P0_PREFLIGHT_ACCEPTS_CALLER_SELECTED_TOOLCHAIN_WITNESS_PATHS",
        )
        self.assertIn("run_successor_emitter", calls)
        self.assertLess(
            calls["validate_runtime_toolchain_witness_paths"],
            calls["run_successor_emitter"],
            "P0_RUNTIME_PATH_VALIDATION_MUST_PRECEDE_SECTION0_EMISSION",
        )

    def test_prelease_revalidation_uses_the_same_runtime_path_validator(self) -> None:
        calls = _call_lines(COMMON, "revalidate_successor_toolchain")
        self.assertIn(
            "validate_runtime_toolchain_witness_paths",
            calls,
            "P0_PRELEASE_REVALIDATION_ACCEPTS_ALTERNATE_HASH_COPY",
        )
        self.assertIn("subprocess", COMMON.read_text(encoding="utf-8"))

    def test_preflight_receipt_binds_runtime_path_snapshot(self) -> None:
        source = _function_text(PREFLIGHT, "build_preflight_receipt")
        for token in (
            '"runtime_toolchain_paths"',
            '"runtime_toolchain_snapshot_sha256"',
        ):
            self.assertIn(
                token,
                source,
                f"P0_PREFLIGHT_RUNTIME_PATH_RECEIPT_FIELD_ABSENT:{token}",
            )
        validator = _function_text(COMMON, "validate_preflight_receipt")
        self.assertIn(
            "runtime_toolchain_snapshot_sha256",
            validator,
            "P0_CONTROLLER_DOES_NOT_VALIDATE_PREFLIGHT_RUNTIME_PATH_SNAPSHOT",
        )

    def test_dispatch_and_worker_bind_the_same_runtime_path_snapshot(self) -> None:
        common_source = COMMON.read_text(encoding="utf-8")
        controller_source = CONTROLLER.read_text(encoding="utf-8")
        worker_source = WORKER.read_text(encoding="utf-8")
        for source, role in (
            (common_source, "common"),
            (controller_source, "controller"),
            (worker_source, "worker"),
        ):
            self.assertIn(
                "runtime_toolchain_snapshot_sha256",
                source,
                f"P0_RUNTIME_PATH_SNAPSHOT_NOT_PROPAGATED:{role}",
            )
        worker_calls = _call_lines(WORKER, "main")
        self.assertIn(
            "validate_runtime_toolchain_witness_paths",
            worker_calls,
            "P0_WORKER_DOES_NOT_RECHECK_ACTUAL_RUNTIME_PATHS",
        )
        self.assertLess(
            worker_calls["validate_runtime_toolchain_witness_paths"],
            worker_calls["run_native_once"],
            "P0_WORKER_PATH_RECHECK_MUST_PRECEDE_RUNTIME_ENTRY",
        )

    def test_alternate_exact_hash_copy_has_a_typed_rejection(self) -> None:
        combined = CONTRACT.read_text(encoding="utf-8") + COMMON.read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH",
            combined,
            "P0_ALTERNATE_EXACT_HASH_COPY_REJECTION_ABSENT",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
