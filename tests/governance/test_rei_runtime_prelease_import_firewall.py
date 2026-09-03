#!/usr/bin/env python3
"""TDD RED contract for the pre-lease production-import firewall.

The previous runtime blocker arose at the production bridge's import/observed
invocation boundary. A read-only preflight must therefore not execute that
module, and the one-attempt controller may load it only after both the global
and persistent local leases have been acquired.
"""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = (
    ROOT
    / "handoff"
    / "rei_runtime_successor_section0_preflight_20260903"
    / "successor_section0_preflight.py"
)
SUCCESSOR = (
    ROOT
    / "handoff"
    / "rei_runtime_bridge_successor_host_20260903"
    / "successor_runtime_runner.py"
)


def function_scoped_calls(path: Path, attribute: str) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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


def run_native_once_keyword_locations(path: Path, keyword: str) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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
            target = node.func.id if isinstance(node.func, ast.Name) else None
            if target == "run_native_once" and any(item.arg == keyword for item in node.keywords):
                found.append((self.stack[-1] if self.stack else "<module>", node.lineno))
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


class PreleaseProductionImportFirewallTests(unittest.TestCase):
    def test_read_only_preflight_never_loads_production_bridge(self) -> None:
        self.assertEqual(
            function_scoped_calls(PREFLIGHT, "load_bridge"),
            [],
            "READ_ONLY_PREFLIGHT_EXECUTES_PRODUCTION_BRIDGE_BEFORE_ATTEMPT_LEASE",
        )

    def test_successor_controller_loads_bridge_only_inside_native_worker(self) -> None:
        calls = function_scoped_calls(SUCCESSOR, "load_bridge")
        self.assertEqual(
            [scope for scope, _ in calls],
            ["run_native_once"],
            "PRODUCTION_BRIDGE_IMPORT_MUST_OCCUR_ONLY_AFTER_GLOBAL_AND_LOCAL_LEASES",
        )

    def test_prelease_controller_does_not_pass_preloaded_bridge_to_worker(self) -> None:
        self.assertEqual(
            run_native_once_keyword_locations(SUCCESSOR, "production_bridge"),
            [],
            "PRELOADED_PRODUCTION_BRIDGE_BYPASSES_ATTEMPT_BOUNDARY",
        )


if __name__ == "__main__":
    unittest.main()
