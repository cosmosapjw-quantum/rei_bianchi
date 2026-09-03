#!/usr/bin/env python3
"""Intentional RED contract for final-attempt authority binding.

This test-only suite must fail on Draft PR #45.  It performs static source and
contract checks only.  It must not contact GitHub, create attempt state, import
the production bridge, start a native worker, run the first interval, or admit a
provider.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_prelease_import_firewall_green_20260903"
PREFLIGHT = PACKAGE / "successor_section0_preflight.py"
CONTROLLER = PACKAGE / "successor_runtime_controller.py"
COMMON_V2 = PACKAGE / "common_v2.py"
CONTRACT = PACKAGE / "CONTRACT.json"

EXPECTED_API = "https://api.github.com"
EXPECTED_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
EXPECTED_REF = (
    "refs/heads/attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _function(path: Path, name: str) -> ast.FunctionDef:
    for node in ast.walk(_tree(path)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"FUNCTION_NOT_FOUND:{path}:{name}")


def _function_parameters(path: Path, name: str) -> set[str]:
    node = _function(path, name)
    return {
        item.arg
        for item in (
            list(node.args.posonlyargs)
            + list(node.args.args)
            + list(node.args.kwonlyargs)
        )
    }


def _parser_options(path: Path) -> set[str]:
    options: set[str] = set()
    for node in ast.walk(_tree(path)):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                options.add(arg.value)
    return options


def _call_lines(path: Path, function_name: str) -> dict[str, int]:
    calls: dict[str, int] = {}
    for node in ast.walk(_function(path, function_name)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            continue
        calls.setdefault(name, node.lineno)
    return calls


def _function_text(path: Path, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    node = _function(path, function_name)
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise AssertionError(f"FUNCTION_SOURCE_UNAVAILABLE:{path}:{function_name}")
    return segment


class AuthorityBindingExpectedRed(unittest.TestCase):
    def setUp(self) -> None:
        for path in (PREFLIGHT, CONTROLLER, COMMON_V2, CONTRACT):
            self.assertTrue(path.is_file(), f"PR45_REQUIRED_SOURCE_ABSENT:{path}")

    def test_preflight_cli_has_no_api_base_override(self) -> None:
        self.assertNotIn(
            "--api-base",
            _parser_options(PREFLIGHT),
            "P0_CONFIGURABLE_GITHUB_AUTHORITY:preflight",
        )

    def test_controller_cli_has_no_api_base_override(self) -> None:
        self.assertNotIn(
            "--api-base",
            _parser_options(CONTROLLER),
            "P0_CONFIGURABLE_GITHUB_AUTHORITY:controller",
        )

    def test_production_functions_have_no_api_base_parameter(self) -> None:
        self.assertNotIn(
            "api_base",
            _function_parameters(PREFLIGHT, "run_read_only_preflight"),
            "P0_CONFIGURABLE_GITHUB_AUTHORITY:run_read_only_preflight",
        )
        self.assertNotIn(
            "api_base",
            _function_parameters(CONTROLLER, "run_controller"),
            "P0_CONFIGURABLE_GITHUB_AUTHORITY:run_controller",
        )

    def test_fixed_github_authority_is_typed(self) -> None:
        combined = PREFLIGHT.read_text(encoding="utf-8") + CONTROLLER.read_text(
            encoding="utf-8"
        )
        self.assertIn("GITHUB_API_BASE", combined, "FIXED_GITHUB_API_BASE_ABSENT")
        self.assertIn("GITHUB_REPOSITORY", combined, "FIXED_GITHUB_REPOSITORY_ABSENT")
        self.assertIn(EXPECTED_API, combined)
        self.assertIn(EXPECTED_REPOSITORY, combined)

    def test_preflight_receipt_binds_authority_and_observation_facts(self) -> None:
        source = _function_text(PREFLIGHT, "build_preflight_receipt")
        for field in (
            '"authority"',
            '"api_host"',
            '"repository"',
            '"method"',
            '"ordinal"',
            '"http_status"',
        ):
            self.assertIn(
                field,
                source,
                f"PREFLIGHT_AUTHORITY_BINDING_FIELD_ABSENT:{field}",
            )

    def test_preflight_validator_binds_controller_paths_and_authority(self) -> None:
        parameters = _function_parameters(COMMON_V2, "validate_preflight_receipt")
        required = {
            "expected_attempt_state_root",
            "expected_output_root",
            "expected_successor_receipt_path",
            "expected_authority",
            "expected_global_ref",
        }
        missing = sorted(required - parameters)
        self.assertFalse(
            missing,
            "PREFLIGHT_PATH_OR_AUTHORITY_EXPECTATIONS_ABSENT:" + ",".join(missing),
        )

    def test_executing_package_is_bound_to_verified_checkout(self) -> None:
        self.assertIn(
            "verify_executing_package_binding",
            _call_lines(PREFLIGHT, "run_read_only_preflight"),
            "P0_EXECUTING_PACKAGE_NOT_BOUND_TO_VERIFIED_HEAD:preflight",
        )
        self.assertIn(
            "verify_executing_package_binding",
            _call_lines(CONTROLLER, "run_controller"),
            "P0_EXECUTING_PACKAGE_NOT_BOUND_TO_VERIFIED_HEAD:controller",
        )

    def test_exact_head_git_blobs_bind_executable_package_files(self) -> None:
        source = COMMON_V2.read_text(encoding="utf-8")
        for token in (
            "EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE",
            "EXECUTING_PACKAGE_BLOB_MISMATCH",
            "HEAD:",
        ):
            self.assertIn(token, source, f"EXECUTION_PACKAGE_GIT_BINDING_ABSENT:{token}")

    def test_full_toolchain_recheck_precedes_global_reservation(self) -> None:
        calls = _call_lines(CONTROLLER, "run_controller")
        self.assertIn(
            "revalidate_successor_toolchain",
            calls,
            "FULL_13_FIELD_TOOLCHAIN_RECHECK_ABSENT",
        )
        self.assertIn("orchestrate_attempt", calls)
        self.assertLess(
            calls["revalidate_successor_toolchain"],
            calls["orchestrate_attempt"],
            "TOOLCHAIN_RECHECK_MUST_PRECEDE_GLOBAL_RESERVATION",
        )

    def test_attempt_ref_server_protection_is_required(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertIn(
            "attempt_ref_protection",
            contract,
            "ATTEMPT_REF_SERVER_PROTECTION_CONTRACT_ABSENT",
        )
        self.assertEqual(
            contract["attempt_budget"]["global_lease_ref"],
            EXPECTED_REF,
        )
        self.assertIn(
            "validate_attempt_ref_protection",
            CONTROLLER.read_text(encoding="utf-8"),
            "ATTEMPT_REF_SERVER_PROTECTION_VALIDATOR_ABSENT",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
