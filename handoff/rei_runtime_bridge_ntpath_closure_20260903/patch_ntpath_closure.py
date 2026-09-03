#!/usr/bin/env python3
"""Apply and verify the one-root CPython ``pathlib -> ntpath`` closure delta.

This script changes only ``runtime_closure.declared_import_roots`` in the
source-bound REI input lock.  It neither changes the production bridge nor
invokes the native runtime.  The generated receipt is evidence for a later,
separately budgeted standalone-host rerun.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "stages" / "REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
INPUT_LOCK = STAGE / "INPUT_LOCK.json"
BRIDGE = STAGE / "analysis" / "rust_source_bound_thermal.py"
RECEIPT = Path(__file__).resolve().parent / "NT_PATH_CLOSURE_RECEIPT_R1.json"

EXPECTED_BRIDGE_SHA256 = (
    "91fe316f1e8b81d64e9929d7a4814b77808fdf486e2ca67cd2f615e8617fce85"
)
EXPECTED_DECLARED_PATH_COUNT = 17
EXPECTED_FORBIDDEN_ROOTS = ["jax", "jaxlib"]
EXPECTED_PREPATCH_ROOTS = [
    "base64",
    "binascii",
    "builtins",
    "contextvars",
    "ctypes",
    "dataclasses",
    "enum",
    "hashlib",
    "hmac",
    "json",
    "math",
    "os",
    "pathlib",
    "re",
    "rei_bianchi",
    "secrets",
    "shutil",
    "stat",
    "struct",
    "subprocess",
    "sys",
    "typing",
]
EXPECTED_POSTPATCH_ROOTS = sorted([*EXPECTED_PREPATCH_ROOTS, "ntpath"])


class ClosurePatchError(RuntimeError):
    """A typed fail-closed patch or verification failure."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_lock() -> dict[str, Any]:
    try:
        value = json.loads(INPUT_LOCK.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ClosurePatchError("INPUT_LOCK_UNREADABLE") from exc
    if not isinstance(value, dict) or not isinstance(value.get("runtime_closure"), dict):
        raise ClosurePatchError("RUNTIME_CLOSURE_MISSING")
    return value


def _pathlib_provenance() -> dict[str, Any]:
    import pathlib

    source_path = Path(inspect.getsourcefile(pathlib) or "")
    if not source_path.is_file():
        raise ClosurePatchError("PATHLIB_SOURCE_UNAVAILABLE")
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level_imports = sorted(
        {
            alias.name.split(".", 1)[0]
            for node in tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
    )
    if "ntpath" not in top_level_imports:
        raise ClosurePatchError("PATHLIB_NTPATH_DEPENDENCY_NOT_OBSERVED")
    return {
        "python_version": sys.version.split()[0],
        "pathlib_source": str(source_path),
        "pathlib_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "pathlib_top_level_imports": top_level_imports,
        "dependency_relation": "CPYTHON_STDLIB_TRANSITIVE_IMPORT",
    }


def _assert_common_guards(lock: dict[str, Any]) -> dict[str, Any]:
    closure = lock["runtime_closure"]
    roots = closure.get("declared_import_roots")
    if not isinstance(roots, list) or roots != sorted(set(roots)):
        raise ClosurePatchError("DECLARED_IMPORT_ROOTS_NOT_SORTED_UNIQUE")
    if closure.get("forbidden_import_roots") != EXPECTED_FORBIDDEN_ROOTS:
        raise ClosurePatchError("FORBIDDEN_IMPORT_ROOTS_CHANGED")
    paths = closure.get("declared_paths")
    if not isinstance(paths, list) or len(paths) != EXPECTED_DECLARED_PATH_COUNT:
        raise ClosurePatchError("DECLARED_PATH_CLOSURE_CHANGED")
    if _sha256(BRIDGE) != EXPECTED_BRIDGE_SHA256:
        raise ClosurePatchError("PRODUCTION_BRIDGE_BYTES_CHANGED")
    return closure


def assert_red() -> dict[str, Any]:
    lock = _load_lock()
    closure = _assert_common_guards(lock)
    roots = closure["declared_import_roots"]
    if roots != EXPECTED_PREPATCH_ROOTS:
        raise ClosurePatchError("PREPATCH_IMPORT_ROOTS_MISMATCH")
    if "pathlib" not in roots or "ntpath" in roots:
        raise ClosurePatchError("EXPECTED_NTPATH_RED_NOT_PRESENT")
    return {
        "status": "EXPECTED_RED",
        "missing_root": "ntpath",
        "declared_import_root_count": len(roots),
        "pathlib_provenance": _pathlib_provenance(),
    }


def apply_patch() -> dict[str, Any]:
    lock = _load_lock()
    closure = _assert_common_guards(lock)
    roots = closure["declared_import_roots"]
    if roots == EXPECTED_POSTPATCH_ROOTS:
        return verify_green()
    if roots != EXPECTED_PREPATCH_ROOTS:
        raise ClosurePatchError("PREPATCH_IMPORT_ROOTS_MISMATCH")

    before = copy.deepcopy(lock)
    old_sha256 = _sha256(INPUT_LOCK)
    closure["declared_import_roots"] = EXPECTED_POSTPATCH_ROOTS

    comparison = copy.deepcopy(lock)
    comparison["runtime_closure"]["declared_import_roots"] = (
        before["runtime_closure"]["declared_import_roots"]
    )
    if comparison != before:
        raise ClosurePatchError("PATCH_CHANGED_MORE_THAN_DECLARED_IMPORT_ROOTS")

    INPUT_LOCK.write_text(
        json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    new_sha256 = _sha256(INPUT_LOCK)
    if new_sha256 == old_sha256:
        raise ClosurePatchError("INPUT_LOCK_IDENTITY_DID_NOT_CHANGE")

    receipt = {
        "schema": "rei-runtime-ntpath-closure-receipt/v1",
        "status": "PASS_DECLARED_IMPORT_NTPATH_CLOSURE_PATCH",
        "repository": "cosmosapjw-quantum/rei_bianchi",
        "workflow_input_commit": os.environ.get("GITHUB_SHA", "LOCAL_OR_UNRECORDED"),
        "source_scientific_parent": (
            "f4eb2c893ce6449f8899ab6f02c83421fc7c7019"
        ),
        "changed_semantic_field": "runtime_closure.declared_import_roots",
        "exact_import_root_delta": ["ntpath"],
        "declared_import_root_count_before": len(EXPECTED_PREPATCH_ROOTS),
        "declared_import_root_count_after": len(EXPECTED_POSTPATCH_ROOTS),
        "declared_path_count": EXPECTED_DECLARED_PATH_COUNT,
        "forbidden_import_roots": EXPECTED_FORBIDDEN_ROOTS,
        "input_lock_sha256_before": old_sha256,
        "input_lock_sha256_after": new_sha256,
        "production_bridge_sha256": EXPECTED_BRIDGE_SHA256,
        "production_bridge_changed": False,
        "pathlib_provenance": _pathlib_provenance(),
        "native_runtime_invoked": False,
        "attempt_budget_consumed": False,
        "required_next_gate": (
            "FRESH_STANDALONE_RUNTIME_HANDOFF_REBOUND_TO_PATCHED_INPUT_LOCK"
        ),
        "claim_ceiling": {
            "runtime_bridge": "STOP_INVALID_UNTIL_FRESH_RERUN",
            "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
            "provider_export": "NOT_AUTHORIZED",
            "scientific_pass": "NOT_CLAIMED",
        },
    }
    if RECEIPT.exists():
        raise ClosurePatchError("PATCH_RECEIPT_PREEXISTS")
    RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def _load_bridge():
    source_root = ROOT / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    spec = importlib.util.spec_from_file_location("rei_ntpath_closure_bridge", BRIDGE)
    if spec is None or spec.loader is None:
        raise ClosurePatchError("RUNTIME_BRIDGE_IMPORT_SPEC_MISSING")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _portable_observer_check(lock: dict[str, Any]) -> dict[str, Any]:
    bridge = _load_bridge()
    closure = lock["runtime_closure"]
    authority = bridge._RuntimeAuthority(
        schema=closure["schema"],
        enforcement_scope=closure["enforcement_scope"],
        input_lock_sha256=_sha256(INPUT_LOCK),
        declared_path_count=EXPECTED_DECLARED_PATH_COUNT,
        allowed_paths=frozenset(),
        allowed_import_roots=frozenset(closure["declared_import_roots"]),
        forbidden_import_roots=frozenset(closure["forbidden_import_roots"]),
        git_record_count=0,
    )
    _, capability = bridge._observe_runtime_invocation(
        authority,
        lambda _capability: __import__("ntpath"),
    )
    if "ntpath" not in capability._observed_imports:
        raise ClosurePatchError("NTPATH_IMPORT_NOT_OBSERVED")

    rejected: dict[str, str] = {}
    for module_name, expected in (("random", "UNDECLARED_IMPORT"), ("jax", "FORBIDDEN_IMPORT")):
        try:
            bridge._observe_runtime_invocation(
                authority,
                lambda _capability, name=module_name: __import__(name),
            )
        except bridge.RuntimeClosureError as exc:
            if exc.classification != expected:
                raise ClosurePatchError(
                    f"WRONG_IMPORT_REJECTION:{module_name}:{exc.classification}"
                ) from exc
            rejected[module_name] = exc.classification
        else:
            raise ClosurePatchError(f"UNRELATED_IMPORT_ACCEPTED:{module_name}")
    return {
        "ntpath_observed_and_admitted": True,
        "negative_controls": rejected,
    }


def verify_green() -> dict[str, Any]:
    lock = _load_lock()
    closure = _assert_common_guards(lock)
    roots = closure["declared_import_roots"]
    if roots != EXPECTED_POSTPATCH_ROOTS:
        raise ClosurePatchError("POSTPATCH_IMPORT_ROOTS_MISMATCH")
    for unrelated in ("random", "site", "jax", "jaxlib"):
        if unrelated in roots:
            raise ClosurePatchError(f"UNRELATED_IMPORT_ROOT_ADMITTED:{unrelated}")
    result = {
        "status": "PASS",
        "declared_import_root_count": len(roots),
        "exact_delta_from_parent": ["ntpath"],
        "pathlib_provenance": _pathlib_provenance(),
        "observer_check": _portable_observer_check(lock),
        "production_bridge_sha256": _sha256(BRIDGE),
        "forbidden_import_roots": closure["forbidden_import_roots"],
        "native_runtime_invoked": False,
        "claim_boundary": (
            "IMPORT_CLOSURE_ONLY_NOT_RUNTIME_BRIDGE_OR_SCIENCE_PASS"
        ),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--assert-red", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--verify-green", action="store_true")
    args = parser.parse_args()
    if args.assert_red:
        result = assert_red()
    elif args.apply:
        result = apply_patch()
    else:
        result = verify_green()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
