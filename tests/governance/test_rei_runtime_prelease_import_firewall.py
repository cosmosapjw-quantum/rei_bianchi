#!/usr/bin/env python3
"""GREEN contract for the pre-lease production-import firewall.

The historical PR #42/#43 paths remain immutable evidence.  The successor path
must perform a pure static/read-only preflight, acquire the global and persistent
local leases, write a dispatch intent, and only then enter a separate worker
that may reach the production bridge through ``run_native_once``.
"""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = (
    ROOT
    / "handoff"
    / "rei_runtime_prelease_import_firewall_green_20260903"
)
PREFLIGHT = PACKAGE / "successor_section0_preflight.py"
CONTROLLER = PACKAGE / "successor_runtime_controller.py"
WORKER = PACKAGE / "native_runtime_worker.py"
CONTRACT = PACKAGE / "CONTRACT.json"
PACKAGE_INDEX = PACKAGE / "PACKAGE_INDEX.json"
VERIFY_PACKAGE = PACKAGE / "verify_package.py"

MODULE_PREFIX = (
    "handoff.rei_runtime_prelease_import_firewall_green_20260903"
)


def parse_file(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def function_scoped_attribute_calls(path: Path, attribute: str) -> list[tuple[str, int]]:
    tree = parse_file(path)
    calls: list[tuple[str, int]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Attribute) and node.func.attr == attribute:
                calls.append((self.stack[-1] if self.stack else "<module>", node.lineno))
            self.generic_visit(node)

    Visitor().visit(tree)
    return calls


def function_scoped_named_calls(path: Path, function_name: str) -> list[tuple[str, int]]:
    tree = parse_file(path)
    calls: list[tuple[str, int]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == function_name:
                calls.append((self.stack[-1] if self.stack else "<module>", node.lineno))
            elif isinstance(node.func, ast.Attribute) and node.func.attr == function_name:
                calls.append((self.stack[-1] if self.stack else "<module>", node.lineno))
            self.generic_visit(node)

    Visitor().visit(tree)
    return calls


def named_call_sequence(path: Path, function_scope: str) -> list[str]:
    tree = parse_file(path)
    target = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == function_scope
    )
    result: list[tuple[int, str]] = []
    for node in ast.walk(target):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        else:
            continue
        result.append((node.lineno, name))
    return [name for _, name in sorted(result)]


def run_native_once_keyword_locations(path: Path, keyword: str) -> list[tuple[str, int]]:
    tree = parse_file(path)
    found: list[tuple[str, int]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            target = None
            if isinstance(node.func, ast.Name):
                target = node.func.id
            elif isinstance(node.func, ast.Attribute):
                target = node.func.attr
            if target == "run_native_once" and any(item.arg == keyword for item in node.keywords):
                found.append((self.stack[-1] if self.stack else "<module>", node.lineno))
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


class PreleaseProductionImportFirewallGreenTests(unittest.TestCase):
    def require_file(self, path: Path, message: str) -> None:
        self.assertTrue(path.is_file(), message)

    def load_controller(self):
        self.require_file(CONTROLLER, "EXPECTED_GREEN_CONTROLLER_ABSENT")
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        return importlib.import_module(f"{MODULE_PREFIX}.successor_runtime_controller")

    def test_green_package_files_exist(self) -> None:
        missing = [
            path.name
            for path in (
                PREFLIGHT,
                CONTROLLER,
                WORKER,
                CONTRACT,
                PACKAGE_INDEX,
                VERIFY_PACKAGE,
            )
            if not path.is_file()
        ]
        self.assertEqual(missing, [], "EXPECTED_GREEN_FIREWALL_PACKAGE_ABSENT")

    def test_read_only_preflight_never_loads_production_bridge(self) -> None:
        self.require_file(PREFLIGHT, "EXPECTED_GREEN_PREFLIGHT_ABSENT")
        self.assertEqual(
            function_scoped_attribute_calls(PREFLIGHT, "load_bridge"),
            [],
            "READ_ONLY_PREFLIGHT_EXECUTES_PRODUCTION_BRIDGE_BEFORE_ATTEMPT_LEASE",
        )
        source = PREFLIGHT.read_text(encoding="utf-8")
        self.assertIn('method="GET"', source)
        self.assertNotIn('method="POST"', source)

    def test_controller_never_loads_or_receives_production_bridge(self) -> None:
        self.require_file(CONTROLLER, "EXPECTED_GREEN_CONTROLLER_ABSENT")
        self.assertEqual(
            function_scoped_attribute_calls(CONTROLLER, "load_bridge"),
            [],
            "CONTROLLER_MUST_NOT_IMPORT_PRODUCTION_BRIDGE",
        )
        self.assertEqual(
            run_native_once_keyword_locations(CONTROLLER, "production_bridge"),
            [],
            "PRELOADED_PRODUCTION_BRIDGE_BYPASSES_ATTEMPT_BOUNDARY",
        )
        self.assertEqual(
            function_scoped_named_calls(CONTROLLER, "run_native_once"),
            [],
            "CONTROLLER_MUST_NOT_ENTER_NATIVE_RUNTIME_IN_PROCESS",
        )

    def test_worker_enters_native_runtime_only_after_receipt_validation(self) -> None:
        self.require_file(WORKER, "EXPECTED_GREEN_WORKER_ABSENT")
        sequence = named_call_sequence(WORKER, "main")
        validate_index = sequence.index("validate_attempt_receipts")
        runtime_index = sequence.index("run_native_once")
        self.assertLess(validate_index, runtime_index)
        self.assertEqual(
            len(function_scoped_named_calls(WORKER, "run_native_once")),
            1,
            "WORKER_MUST_REACH_NATIVE_RUNTIME_EXACTLY_ONCE",
        )
        self.assertEqual(
            run_native_once_keyword_locations(WORKER, "production_bridge"),
            [],
            "WORKER_MUST_NOT_ACCEPT_A_PRELOADED_PRODUCTION_BRIDGE",
        )

    def test_orchestration_order_is_global_local_dispatch_worker(self) -> None:
        controller = self.load_controller()
        events: list[str] = []

        def acquire_global():
            events.append("global")
            return {"status": "GLOBAL_ATTEMPT_RESERVED"}

        def create_local(global_record):
            self.assertEqual(global_record["status"], "GLOBAL_ATTEMPT_RESERVED")
            events.append("local")
            return {"status": "LOCAL_ATTEMPT_RESERVED"}

        def write_dispatch(global_record, local_record):
            self.assertEqual(global_record["status"], "GLOBAL_ATTEMPT_RESERVED")
            self.assertEqual(local_record["status"], "LOCAL_ATTEMPT_RESERVED")
            events.append("dispatch")
            return {"status": "DISPATCH_INTENT_WRITTEN"}

        def run_worker(dispatch_record):
            self.assertEqual(dispatch_record["status"], "DISPATCH_INTENT_WRITTEN")
            events.append("worker")
            return {"status": "WORKER_EXIT_0"}

        result = controller.orchestrate_attempt(
            acquire_global=acquire_global,
            create_local=create_local,
            write_dispatch=write_dispatch,
            run_worker=run_worker,
        )
        self.assertEqual(events, ["global", "local", "dispatch", "worker"])
        self.assertEqual(result["status"], "WORKER_EXIT_0")

    def test_global_failure_short_circuits_every_later_stage(self) -> None:
        controller = self.load_controller()
        events: list[str] = []

        def acquire_global():
            events.append("global")
            raise controller.ControllerError("GLOBAL_FAIL")

        with self.assertRaisesRegex(controller.ControllerError, "GLOBAL_FAIL"):
            controller.orchestrate_attempt(
                acquire_global=acquire_global,
                create_local=lambda record: events.append("local"),
                write_dispatch=lambda global_record, local_record: events.append("dispatch"),
                run_worker=lambda dispatch_record: events.append("worker"),
            )
        self.assertEqual(events, ["global"])

    def test_local_failure_prevents_dispatch_and_worker(self) -> None:
        controller = self.load_controller()
        events: list[str] = []

        def acquire_global():
            events.append("global")
            return {"status": "GLOBAL_ATTEMPT_RESERVED"}

        def create_local(record):
            events.append("local")
            raise controller.ControllerError("LOCAL_FAIL")

        with self.assertRaisesRegex(controller.ControllerError, "LOCAL_FAIL"):
            controller.orchestrate_attempt(
                acquire_global=acquire_global,
                create_local=create_local,
                write_dispatch=lambda global_record, local_record: events.append("dispatch"),
                run_worker=lambda dispatch_record: events.append("worker"),
            )
        self.assertEqual(events, ["global", "local"])

    def test_worker_failure_is_not_retried(self) -> None:
        controller = self.load_controller()
        calls: list[int] = []

        def run_worker(record):
            calls.append(1)
            raise controller.ControllerError("WORKER_FAIL")

        with self.assertRaisesRegex(controller.ControllerError, "WORKER_FAIL"):
            controller.orchestrate_attempt(
                acquire_global=lambda: {"status": "GLOBAL_ATTEMPT_RESERVED"},
                create_local=lambda record: {"status": "LOCAL_ATTEMPT_RESERVED"},
                write_dispatch=lambda global_record, local_record: {
                    "status": "DISPATCH_INTENT_WRITTEN"
                },
                run_worker=run_worker,
            )
        self.assertEqual(calls, [1])

    def test_contract_preserves_one_attempt_and_claim_ceiling(self) -> None:
        self.require_file(CONTRACT, "EXPECTED_GREEN_CONTRACT_ABSENT")
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["attempt_budget"]["ordinal"], 3)
        self.assertEqual(contract["attempt_budget"]["remaining_native_attempts"], 1)
        self.assertEqual(contract["attempt_budget"]["retries_after_outcome"], 0)
        self.assertEqual(
            contract["attempt_budget"]["global_lease_target_relation"],
            "EXACT_FIREWALL_RELEASE_HEAD",
        )
        self.assertEqual(
            contract["claim_ceiling"]["first_interval"],
            "NO_PASS_FIRST_CANONICAL_INTERVAL",
        )
        self.assertEqual(contract["claim_ceiling"]["provider_export"], "NOT_AUTHORIZED")
        self.assertEqual(contract["claim_ceiling"]["scientific_pass"], "NOT_CLAIMED")

    def test_package_index_has_no_self_hash_cycle(self) -> None:
        self.require_file(PACKAGE_INDEX, "EXPECTED_GREEN_PACKAGE_INDEX_ABSENT")
        index = json.loads(PACKAGE_INDEX.read_text(encoding="utf-8"))
        names = [row["path"] for row in index["entries"]]
        self.assertNotIn("PACKAGE_INDEX.json", names)
        self.assertEqual(len(names), len(set(names)))

    def test_executable_sources_do_not_open_first_interval_or_provider(self) -> None:
        for path in (PREFLIGHT, CONTROLLER, WORKER):
            self.require_file(path, f"EXPECTED_GREEN_SOURCE_ABSENT:{path.name}")
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("first_canonical_interval", source)
            self.assertNotIn("provider_export", source)


if __name__ == "__main__":
    unittest.main()
