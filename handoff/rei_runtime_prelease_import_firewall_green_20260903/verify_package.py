#!/usr/bin/env python3
"""Independent static verifier for the closed firewall package."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

try:
    from .common import (
        FirewallError,
        PACKAGE,
        load_contract,
        verify_package_index,
    )
except ImportError:
    from common import (  # type: ignore
        FirewallError,
        PACKAGE,
        load_contract,
        verify_package_index,
    )


def _scoped_calls(path: Path, target: str) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: list[tuple[str, int]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node: ast.Call) -> None:
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name == target:
                result.append((self.stack[-1] if self.stack else "<module>", node.lineno))
            self.generic_visit(node)

    Visitor().visit(tree)
    return result


def verify_source_boundary() -> dict[str, object]:
    preflight = PACKAGE / "successor_section0_preflight.py"
    controller = PACKAGE / "successor_runtime_controller.py"
    worker = PACKAGE / "native_runtime_worker.py"
    for path in (preflight, controller, worker):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    preflight_text = preflight.read_text(encoding="utf-8")
    controller_text = controller.read_text(encoding="utf-8")
    if "load_bridge" in preflight_text or 'method="POST"' in preflight_text:
        raise FirewallError("PREFLIGHT_PRODUCTION_OR_MUTATION_BOUNDARY_VIOLATION")
    if "load_bridge" in controller_text or _scoped_calls(controller, "run_native_once"):
        raise FirewallError("CONTROLLER_PRODUCTION_BOUNDARY_VIOLATION")

    worker_runtime_calls = _scoped_calls(worker, "run_native_once")
    worker_receipt_calls = _scoped_calls(worker, "validate_attempt_receipts")
    if worker_runtime_calls != [("main", worker_runtime_calls[0][1])] if worker_runtime_calls else True:
        raise FirewallError("WORKER_RUNTIME_ENTRY_COUNT_INVALID")
    if len(worker_receipt_calls) != 1 or worker_receipt_calls[0][0] != "main":
        raise FirewallError("WORKER_RECEIPT_VALIDATION_COUNT_INVALID")
    if worker_receipt_calls[0][1] >= worker_runtime_calls[0][1]:
        raise FirewallError("WORKER_RUNTIME_ENTRY_PRECEDES_RECEIPT_VALIDATION")
    return {
        "preflight_production_imports": 0,
        "controller_production_imports": 0,
        "worker_runtime_entries": 1,
        "worker_receipt_validation_precedes_runtime": True,
    }


def main() -> int:
    try:
        verify_package_index()
        contract = load_contract()
        boundary = verify_source_boundary()
    except FirewallError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_PACKAGE_VERIFIER_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(
        json.dumps(
            {
                "status": contract["success_status"],
                "package": str(PACKAGE),
                "source_boundary": boundary,
                "native_runtime": "NOT_RUN",
                "authority_effect": "NONE",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
