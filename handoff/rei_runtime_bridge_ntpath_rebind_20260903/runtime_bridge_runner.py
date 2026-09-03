#!/usr/bin/env python3
"""Exact-pinned rebind wrapper for one post-ntpath standalone native attempt.

The underlying PR #31 runner is reused byte-for-byte as a base module.  This
wrapper changes only handoff governance: it binds the PR #37 input lock,
installs a new create-only attempt claim, verifies the closed package by Git
blob identity, and records the material-delta lineage.  It never modifies or
monkeypatches the production REI bridge.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Mapping


PACKAGE = Path(__file__).resolve().parent
BASE_RUNNER_PATH = PACKAGE / "runtime_bridge_runner_base.py"
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
PACKAGE_INDEX_PATH = PACKAGE / "PACKAGE_INDEX.json"
ATTEMPT_CLAIM_PATH = Path(
    "/tmp/rei-runtime-bridge-ntpath-rebind-20260903.native-attempt.json"
)
PATCHED_PREDECESSOR_COMMIT = "5b6957237bbe8edfdfe3c980910cba690d23775c"
PATCHED_PREDECESSOR_TREE = "805e92779ba6e7d956d5ac936f0934f5879fd3a1"
PATCHED_INPUT_LOCK_SHA256 = (
    "20db870e76ff8a82f2b6f6d38d90eb915b73d5564d6dfbee60a524862ab2e989"
)
PRODUCTION_BRIDGE_SHA256 = (
    "91fe316f1e8b81d64e9929d7a4814b77808fdf486e2ca67cd2f615e8617fce85"
)


def _load_base_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "rei_runtime_bridge_ntpath_rebind_base", BASE_RUNNER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load base runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_base = _load_base_runner()
for _name in dir(_base):
    if not _name.startswith("__"):
        globals().setdefault(_name, getattr(_base, _name))

# The base file lives in this package, so its default package paths already
# resolve here.  These assignments make the governance override explicit.
_base.PACKAGE = PACKAGE
_base.CONTRACT_PATH = CONTRACT_PATH
_base.MANIFEST_PATH = PACKAGE_INDEX_PATH
_base.ATTEMPT_CLAIM_PATH = ATTEMPT_CLAIM_PATH

_ORIGINAL_LOAD_CONTRACT = _base.load_contract
_ORIGINAL_RUN = _base.run


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def verify_manifest(
    root: Path = PACKAGE,
    manifest: Path = PACKAGE_INDEX_PATH,
) -> None:
    """Verify a closed package by repository Git-blob identities.

    The index excludes itself to avoid a self-reference cycle.  Every other
    regular file in the package must appear exactly once and reproduce its
    SHA-1 Git blob object name.
    """

    try:
        index = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_INDEX_UNREADABLE") from exc
    if (
        not isinstance(index, dict)
        or set(index) != {"schema", "git_object_format", "entries"}
        or index["schema"] != "rei-runtime-handoff-package-index/v1"
        or index["git_object_format"] != "sha1"
        or not isinstance(index["entries"], list)
    ):
        raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_INDEX_INVALID")

    expected: dict[Path, str] = {}
    for row in index["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_INDEX_INVALID")
        raw_path = row["path"]
        blob_sha = row["blob_sha"]
        role = row["role"]
        pure = PurePosixPath(raw_path) if isinstance(raw_path, str) else None
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw_path
            or not isinstance(blob_sha, str)
            or len(blob_sha) != 40
            or any(character not in "0123456789abcdef" for character in blob_sha)
            or not isinstance(role, str)
            or not role
        ):
            raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_INDEX_INVALID")
        relative = Path(raw_path)
        if relative in expected:
            raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_INDEX_INVALID")
        expected[relative] = blob_sha

    package_root = Path(root).resolve(strict=True)
    index_path = Path(manifest).resolve(strict=True)
    actual: set[Path] = set()
    for candidate in package_root.rglob("*"):
        if candidate == index_path:
            continue
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_file()):
            raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_SCOPE_MISMATCH")
        if candidate.is_file():
            actual.add(candidate.relative_to(package_root))
    if set(expected) != actual:
        raise _base.HandoffError("RUNTIME_HANDOFF_PACKAGE_SCOPE_MISMATCH")
    for relative, blob_sha in expected.items():
        target = package_root / relative
        if not target.is_file() or target.is_symlink() or _git_blob_sha1(target) != blob_sha:
            raise _base.HandoffError(
                f"RUNTIME_HANDOFF_PACKAGE_BLOB_MISMATCH: {relative.as_posix()}"
            )


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = _ORIGINAL_LOAD_CONTRACT(path)
    predecessor = contract["immutable_predecessor"]
    if predecessor != {
        "pull_request": 37,
        "branch": "agent/implementation/rei-runtime-bridge-ntpath-closure-20260903-r1",
        "commit": PATCHED_PREDECESSOR_COMMIT,
        "tree": PATCHED_PREDECESSOR_TREE,
    }:
        raise _base.HandoffError("RUNTIME_HANDOFF_PATCHED_PREDECESSOR_MISMATCH")
    runtime_bridge = contract.get("runtime_bridge")
    input_lock = runtime_bridge.get("input_lock") if isinstance(runtime_bridge, dict) else None
    if (
        runtime_bridge.get("sha256") != PRODUCTION_BRIDGE_SHA256
        or not isinstance(input_lock, dict)
        or input_lock.get("sha256") != PATCHED_INPUT_LOCK_SHA256
        or input_lock.get("required_declared_import_root") != "ntpath"
        or input_lock.get("required_declared_path_count") != 17
        or input_lock.get("required_forbidden_import_roots") != ["jax", "jaxlib"]
    ):
        raise _base.HandoffError("RUNTIME_HANDOFF_PATCHED_INPUT_IDENTITY_MISMATCH")
    budget = contract["attempt_budget"]
    if (
        budget.get("prior_runtime_attempts") != 2
        or budget.get("material_delta_id")
        != "REI-RUNTIME-BRIDGE-01_DECLARED_IMPORT_NTPATH_CLOSURE"
        or budget.get("remaining_native_attempts") != 1
        or budget.get("retries_after_next_attempt") != 0
        or budget.get("create_only_claim_path") != str(ATTEMPT_CLAIM_PATH)
        or budget.get("superseded_consumed_claim_path")
        != "/tmp/rei-runtime-bridge-host-context-repair-20260901.native-attempt.json"
    ):
        raise _base.HandoffError("RUNTIME_HANDOFF_ATTEMPT_BUDGET_MISMATCH")
    if contract["claim_ceiling"].get("first_interval") != "NO_PASS_FIRST_CANONICAL_INTERVAL":
        raise _base.HandoffError("RUNTIME_HANDOFF_CLAIM_CEILING_MISMATCH")
    return contract


def _resolve_repo_file(repo: Path, relative: str, classification: str) -> Path:
    root = Path(repo).resolve(strict=True)
    candidate = root / relative
    if candidate.is_symlink():
        raise _base.HandoffError(classification)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise _base.HandoffError(classification) from exc
    if not resolved.is_file():
        raise _base.HandoffError(classification)
    return resolved


def verify_patched_runtime_inputs(
    repo: Path,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    effective = dict(contract) if contract is not None else load_contract()
    bridge_record = effective["runtime_bridge"]
    lock_record = bridge_record["input_lock"]
    lock_path = _resolve_repo_file(
        Path(repo), lock_record["path"], "PATCHED_INPUT_LOCK_UNAVAILABLE"
    )
    bridge_path = _resolve_repo_file(
        Path(repo), bridge_record["path"], "PRODUCTION_BRIDGE_UNAVAILABLE"
    )
    if _sha256(lock_path) != lock_record["sha256"]:
        raise _base.HandoffError("PATCHED_INPUT_LOCK_IDENTITY_MISMATCH")
    if _sha256(bridge_path) != bridge_record["sha256"]:
        raise _base.HandoffError("PRODUCTION_BRIDGE_IDENTITY_MISMATCH")
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _base.HandoffError("PATCHED_INPUT_LOCK_UNREADABLE") from exc
    closure = lock.get("runtime_closure") if isinstance(lock, dict) else None
    roots = closure.get("declared_import_roots") if isinstance(closure, dict) else None
    paths = closure.get("declared_paths") if isinstance(closure, dict) else None
    forbidden = closure.get("forbidden_import_roots") if isinstance(closure, dict) else None
    if (
        lock.get("schema") != lock_record["schema"]
        or not isinstance(roots, list)
        or roots != sorted(set(roots))
        or roots.count(lock_record["required_declared_import_root"]) != 1
        or "pathlib" not in roots
        or not isinstance(paths, list)
        or len(paths) != lock_record["required_declared_path_count"]
        or forbidden != lock_record["required_forbidden_import_roots"]
    ):
        raise _base.HandoffError("PATCHED_INPUT_LOCK_SEMANTIC_MISMATCH")
    return {
        "input_lock_path": lock_record["path"],
        "input_lock_sha256": lock_record["sha256"],
        "declared_import_root_count": len(roots),
        "declared_path_count": len(paths),
        "forbidden_import_roots": list(forbidden),
        "production_bridge_path": bridge_record["path"],
        "production_bridge_sha256": bridge_record["sha256"],
    }


def claim_runner_attempt(path: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise _base.HandoffError("RUNTIME_ATTEMPT_CLAIM_NOT_ABSOLUTE")
    try:
        parent = candidate.parent.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise _base.HandoffError("RUNTIME_ATTEMPT_CLAIM_PARENT_UNAVAILABLE") from exc
    target = parent / candidate.name
    try:
        _base.atomic_write_json(
            target,
            {
                "schema": "rei-runtime-host-context-attempt-claim/v1",
                "status": "NATIVE_ATTEMPT_CLAIMED",
                "immutable_predecessor_commit": PATCHED_PREDECESSOR_COMMIT,
                "immutable_predecessor_tree": PATCHED_PREDECESSOR_TREE,
                "patched_input_lock_sha256": PATCHED_INPUT_LOCK_SHA256,
                "material_delta_id": "REI-RUNTIME-BRIDGE-01_DECLARED_IMPORT_NTPATH_CLOSURE",
            },
        )
    except FileExistsError as exc:
        raise _base.HandoffError("RUNTIME_ATTEMPT_ALREADY_CLAIMED") from exc
    except OSError as exc:
        raise _base.HandoffError("RUNTIME_ATTEMPT_CLAIM_UNAVAILABLE") from exc
    return target.resolve(strict=True)


def run(
    *,
    repo: Path,
    section_0_receipt: Path,
    rustc: Path,
    evidence_root: Path,
) -> tuple[dict[str, Any], Path]:
    contract = load_contract()
    patched_inputs = verify_patched_runtime_inputs(repo, contract)
    result, output_root = _ORIGINAL_RUN(
        repo=repo,
        section_0_receipt=section_0_receipt,
        rustc=rustc,
        evidence_root=evidence_root,
    )
    augmented = dict(result)
    augmented["patched_runtime_inputs"] = patched_inputs
    augmented["attempt_lineage"] = {
        "prior_runtime_attempts": contract["attempt_budget"]["prior_runtime_attempts"],
        "material_delta_id": contract["attempt_budget"]["material_delta_id"],
        "new_attempt_claim_path": str(ATTEMPT_CLAIM_PATH),
        "retries_after_this_attempt": 0,
    }
    return augmented, output_root


# Patch only the reusable handoff base module.  The production bridge loaded
# later from the target repository remains byte-pinned and untouched.
_base.verify_manifest = verify_manifest
_base.load_contract = load_contract
_base.claim_runner_attempt = claim_runner_attempt
_base.run = run

HandoffError = _base.HandoffError
RuntimeClosureError = getattr(_base, "RuntimeClosureError", RuntimeError)


def main(
    argv: list[str] | None = None,
    *,
    attempt_claim_path: Path = ATTEMPT_CLAIM_PATH,
) -> int:
    return _base.main(argv, attempt_claim_path=attempt_claim_path)


if __name__ == "__main__":
    raise SystemExit(main())
