#!/usr/bin/env python3
"""Hostile hardening tests for the GREEN pre-lease import firewall."""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PREFIX = (
    "handoff.rei_runtime_prelease_import_firewall_green_20260903"
)
HEAD = "1" * 40
TREE = "2" * 40
SUCCESSOR_SHA = "3" * 64
PREFLIGHT_SHA = "4" * 64
FIXED_REF = (
    "refs/heads/attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)


def load_modules():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    common = importlib.import_module(f"{MODULE_PREFIX}.common")
    controller = importlib.import_module(
        f"{MODULE_PREFIX}.successor_runtime_controller"
    )
    return common, controller


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def base_preflight_receipt() -> dict:
    observation = {
        "status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED",
        "authorization_effect": "NONE",
        "global_lease_acquired": False,
    }
    return {
        "schema": "rei-runtime-prelease-import-firewall-preflight-receipt/v1",
        "status": "PASS_READ_ONLY_STATIC_PREFLIGHT",
        "firewall_release": {"commit": HEAD, "tree": TREE},
        "successor_section0_receipt_sha256": SUCCESSOR_SHA,
        "global_ref_observations": [observation, dict(observation)],
        "attempt_state": {
            "global_lease_acquired": False,
            "local_lease_created": False,
            "dispatch_intent_created": False,
            "remaining_attempts": 1,
            "absence_is_authorization": False,
        },
        "static_checks": {
            "production_module_loaded": False,
            "standalone_clone_verified": True,
            "pinned_source_bytes_verified": True,
            "closed_runtime_package_verified": True,
        },
        "native_runtime": "NOT_RUN",
    }


def write_attempt_receipts(
    common,
    state: Path,
    *,
    local_successor_sha: str = SUCCESSOR_SHA,
    global_ref: str = FIXED_REF,
) -> Path:
    global_path = state / "attempt-3.global-lease.json"
    local_path = state / "attempt-3.local-lease.json"
    dispatch_path = state / "attempt-3.dispatch-intent.json"
    write_json(
        global_path,
        {
            "status": "GLOBAL_ATTEMPT_RESERVED",
            "ref": global_ref,
            "target_commit": HEAD,
            "target_relation": "EXACT_FIREWALL_RELEASE_HEAD",
            "successor_section0_receipt_sha256": SUCCESSOR_SHA,
            "preflight_receipt_sha256": PREFLIGHT_SHA,
        },
    )
    write_json(
        local_path,
        {
            "status": "LOCAL_ATTEMPT_RESERVED",
            "firewall_release_head": HEAD,
            "firewall_release_tree": TREE,
            "global_lease_receipt_sha256": common.sha256_file(global_path),
            "successor_section0_receipt_sha256": local_successor_sha,
            "preflight_receipt_sha256": PREFLIGHT_SHA,
        },
    )
    write_json(
        dispatch_path,
        {
            "status": "DISPATCH_INTENT_WRITTEN",
            "firewall_release_head": HEAD,
            "firewall_release_tree": TREE,
            "global_lease_receipt_sha256": common.sha256_file(global_path),
            "local_lease_receipt_sha256": common.sha256_file(local_path),
            "successor_section0_receipt_sha256": SUCCESSOR_SHA,
            "preflight_receipt_sha256": PREFLIGHT_SHA,
            "retries_after_outcome": 0,
        },
    )
    return dispatch_path


def scoped_call_lines(path: Path, function_scope: str) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    target = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == function_scope
    )
    calls: list[tuple[int, str]] = []
    for node in ast.walk(target):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            continue
        calls.append((node.lineno, name))
    return sorted(calls)


class PreleaseImportFirewallHardeningTests(unittest.TestCase):
    def test_preflight_receipt_rejects_production_module_loaded(self) -> None:
        common, _ = load_modules()
        receipt = base_preflight_receipt()
        receipt["static_checks"]["production_module_loaded"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "preflight.json"
            write_json(path, receipt)
            with self.assertRaisesRegex(
                common.FirewallError,
                "READ_ONLY_PREFLIGHT_STATIC_CHECKS_INVALID",
            ):
                common.validate_preflight_receipt(
                    path,
                    expected_head=HEAD,
                    expected_tree=TREE,
                    successor_receipt_sha256=SUCCESSOR_SHA,
                )

    def test_preflight_receipt_rejects_dispatch_intent_created(self) -> None:
        common, _ = load_modules()
        receipt = base_preflight_receipt()
        receipt["attempt_state"]["dispatch_intent_created"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "preflight.json"
            write_json(path, receipt)
            with self.assertRaisesRegex(
                common.FirewallError,
                "READ_ONLY_PREFLIGHT_ATTEMPT_STATE_INVALID",
            ):
                common.validate_preflight_receipt(
                    path,
                    expected_head=HEAD,
                    expected_tree=TREE,
                    successor_receipt_sha256=SUCCESSOR_SHA,
                )

    def test_controller_authenticates_rustc_before_orchestration(self) -> None:
        _, controller = load_modules()
        calls = scoped_call_lines(Path(controller.__file__), "run_controller")
        names = [name for _, name in calls]
        self.assertIn("_validate_rustc", names, "PRELEASE_RUSTC_AUTHENTICATION_ABSENT")
        self.assertLess(
            next(line for line, name in calls if name == "_validate_rustc"),
            next(line for line, name in calls if name == "orchestrate_attempt"),
            "RUSTC_IDENTITY_MUST_BE_CHECKED_BEFORE_GLOBAL_RESERVATION",
        )

    def test_dispatch_alias_symlink_is_rejected(self) -> None:
        common, _ = load_modules()
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            dispatch = write_attempt_receipts(common, state)
            alias = state / "dispatch-alias.json"
            alias.symlink_to(dispatch.name)
            with self.assertRaisesRegex(
                common.FirewallError,
                "DISPATCH_INTENT_PATH_MISMATCH",
            ):
                common.validate_attempt_receipts(
                    state_root=state,
                    dispatch_intent=alias,
                    expected_head=HEAD,
                    expected_tree=TREE,
                )

    def test_cross_receipt_successor_hash_mismatch_is_rejected(self) -> None:
        common, _ = load_modules()
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            dispatch = write_attempt_receipts(
                common,
                state,
                local_successor_sha="5" * 64,
            )
            with self.assertRaisesRegex(
                common.FirewallError,
                "ATTEMPT_RECEIPT_CROSS_HASH_MISMATCH",
            ):
                common.validate_attempt_receipts(
                    state_root=state,
                    dispatch_intent=dispatch,
                    expected_head=HEAD,
                    expected_tree=TREE,
                )

    def test_global_receipt_requires_fixed_ref(self) -> None:
        common, _ = load_modules()
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary)
            dispatch = write_attempt_receipts(
                common,
                state,
                global_ref="refs/heads/unrelated",
            )
            with self.assertRaisesRegex(
                common.FirewallError,
                "GLOBAL_LEASE_RECEIPT_MISMATCH",
            ):
                common.validate_attempt_receipts(
                    state_root=state,
                    dispatch_intent=dispatch,
                    expected_head=HEAD,
                    expected_tree=TREE,
                )


if __name__ == "__main__":
    unittest.main()
