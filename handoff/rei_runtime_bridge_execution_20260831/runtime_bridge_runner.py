#!/usr/bin/env python3
"""Fail-closed local executor for one bounded REI Rust bridge invocation.

This runner intentionally does not create a new trust root.  It binds a local
fresh-process execution to the exact Section 0 receipt, then calls the pinned
bridge factories.  Its only successful result preserves the documented
pre-start process-boundary residual.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping


PACKAGE = Path(__file__).resolve().parent
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
MANIFEST_PATH = PACKAGE / "MANIFEST.sha256"


class HandoffError(RuntimeError):
    """A typed, fail-closed handoff error."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HandoffError("RUNTIME_HANDOFF_CONTRACT_UNREADABLE") from exc
    if not isinstance(contract, dict):
        raise HandoffError("RUNTIME_HANDOFF_CONTRACT_SCHEMA_INVALID")
    expected = {
        "schema",
        "classification",
        "repository",
        "immutable_predecessor",
        "required_section_0_receipt",
        "runtime_bridge",
        "rust_backend",
        "required_operations",
        "forbidden_operations",
        "residual_blockers",
        "success_status",
        "failure_status",
        "claim_ceiling",
    }
    if set(contract) != expected:
        raise HandoffError("RUNTIME_HANDOFF_CONTRACT_SCHEMA_INVALID")
    if contract["schema"] != "rei-local-runtime-bridge-execution-contract/v1":
        raise HandoffError("RUNTIME_HANDOFF_CONTRACT_SCHEMA_INVALID")
    return contract


def verify_manifest(root: Path = PACKAGE, manifest: Path = MANIFEST_PATH) -> None:
    try:
        rows = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise HandoffError("RUNTIME_HANDOFF_MANIFEST_UNREADABLE") from exc
    expected: dict[Path, str] = {}
    for row in rows:
        digest, separator, name = row.partition("  ")
        candidate = Path(name)
        if (
            not separator
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or candidate.is_absolute()
            or ".." in candidate.parts
            or not name
            or candidate in expected
        ):
            raise HandoffError("RUNTIME_HANDOFF_MANIFEST_INVALID")
        expected[candidate] = digest
    actual = {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and path.name != manifest.name
    }
    if set(expected) != actual:
        raise HandoffError("RUNTIME_HANDOFF_MANIFEST_SCOPE_MISMATCH")
    for relative, digest in expected.items():
        target = root / relative
        if not target.is_file() or sha256_file(target) != digest:
            raise HandoffError(f"RUNTIME_HANDOFF_MANIFEST_HASH_MISMATCH: {relative}")


def load_section_0_receipt(path: Path, expected_sha256: str, expected_status: str) -> dict[str, Any]:
    if not path.is_file() or sha256_file(path) != expected_sha256:
        raise HandoffError("SECTION0_RECEIPT_IDENTITY_MISMATCH")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HandoffError("SECTION0_RECEIPT_UNREADABLE") from exc
    if not isinstance(receipt, dict) or receipt.get("status") != expected_status:
        raise HandoffError("SECTION0_RECEIPT_STATUS_MISMATCH")
    return receipt


def load_bridge(repo: Path, relative_path: str) -> Any:
    bridge_path = (repo / relative_path).resolve(strict=True)
    source_root = (repo / "src").resolve(strict=True)
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    spec = importlib.util.spec_from_file_location("rei_runtime_bridge_handoff", bridge_path)
    if spec is None or spec.loader is None:
        raise HandoffError("RUNTIME_BRIDGE_IMPORT_SPEC_MISSING")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git_checked(bridge: Any, repo: Path, *arguments: str) -> str:
    return bridge._run((str(bridge.GIT), "-C", str(repo), *arguments), cwd=repo)


def verify_predecessor(bridge: Any, repo: Path, contract: Mapping[str, Any]) -> tuple[str, str]:
    predecessor = contract["immutable_predecessor"]
    expected_commit = predecessor["commit"]
    merge_base = git_checked(bridge, repo, "merge-base", "HEAD", expected_commit).strip()
    if merge_base != expected_commit:
        raise HandoffError("IMMUTABLE_PREDECESSOR_NOT_ANCESTOR")
    predecessor_tree = git_checked(bridge, repo, "rev-parse", f"{expected_commit}^{{tree}}").strip()
    if predecessor_tree != predecessor["tree"]:
        raise HandoffError("IMMUTABLE_PREDECESSOR_TREE_MISMATCH")
    git_checked(bridge, repo, "fsck", "--full")
    git_checked(bridge, repo, "diff", "--check")
    if git_checked(bridge, repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise HandoffError("RUNTIME_HANDOFF_WORKTREE_NOT_CLEAN")
    return (
        git_checked(bridge, repo, "rev-parse", "HEAD").strip(),
        git_checked(bridge, repo, "rev-parse", "HEAD^{tree}").strip(),
    )


def create_evidence_root(raw: Path, bridge: Any, repo: Path) -> Path:
    root = raw.resolve(strict=False)
    for worktree in bridge._worktree_roots(repo):
        try:
            root.relative_to(worktree)
        except ValueError:
            continue
        raise HandoffError("RUNTIME_EVIDENCE_INSIDE_GIT_WORKTREE")
    if root.exists():
        raise HandoffError("RUNTIME_EVIDENCE_ROOT_PREEXISTS")
    root.mkdir(mode=0o700, parents=True)
    return root.resolve(strict=True)


def atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    encoded = canonical_bytes(value) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def run(
    *,
    repo: Path,
    section_0_receipt: Path,
    evidence_root: Path,
) -> tuple[dict[str, Any], Path]:
    verify_manifest()
    contract = load_contract()
    root = Path(repo).resolve(strict=True)
    bridge_path = root / contract["runtime_bridge"]["path"]
    if sha256_file(bridge_path) != contract["runtime_bridge"]["sha256"]:
        raise HandoffError("RUNTIME_BRIDGE_SOURCE_IDENTITY_MISMATCH")
    section_0 = load_section_0_receipt(
        section_0_receipt,
        contract["required_section_0_receipt"]["sha256"],
        contract["required_section_0_receipt"]["required_status"],
    )
    bridge = load_bridge(root, contract["runtime_bridge"]["path"])
    head, tree = verify_predecessor(bridge, root, contract)
    output_root = create_evidence_root(evidence_root, bridge, root)
    stage = root / contract["rust_backend"]["stage_path"]
    identity = bridge.authenticate_runtime(stage_dir=stage)
    if identity["source_sha256"] != contract["rust_backend"]["source_sha256"]:
        raise HandoffError("RUNTIME_SOURCE_IDENTITY_MISMATCH")
    if identity["abi_version"] != contract["rust_backend"]["abi_version"]:
        raise HandoffError("RUNTIME_ABI_IDENTITY_MISMATCH")
    if identity["precision_bits"] != contract["rust_backend"]["precision_bits"]:
        raise HandoffError("RUNTIME_PRECISION_IDENTITY_MISMATCH")
    if identity["rounding_policy"] != contract["rust_backend"]["rounding_policy"]:
        raise HandoffError("RUNTIME_ROUNDING_IDENTITY_MISMATCH")

    first = bridge.build_authenticated_backend(
        stage_dir=stage, output_dir=output_root / "build-a"
    )
    second = bridge.build_authenticated_backend(
        stage_dir=stage, output_dir=output_root / "build-b"
    )
    first_sha256 = sha256_file(first.artifact_path)
    second_sha256 = sha256_file(second.artifact_path)
    expected_artifact = contract["rust_backend"]["expected_artifact_sha256"]
    if first_sha256 != expected_artifact or second_sha256 != expected_artifact:
        raise HandoffError("RUNTIME_ARTIFACT_PIN_MISMATCH")
    if first.artifact_path.read_bytes() != second.artifact_path.read_bytes():
        raise HandoffError("RUNTIME_BUILD_NOT_BYTE_IDENTICAL")
    if first.receipt.canonical_bytes() != second.receipt.canonical_bytes():
        raise HandoffError("RUNTIME_RECEIPT_NOT_BYTE_IDENTICAL")

    quotient = bridge.interval_divide((1.0, 1.0), (2.0, 2.0), backend=first)
    if (
        len(quotient) != 2
        or not all(math.isfinite(value) for value in quotient)
        or quotient[0] > 0.5
        or quotient[1] < 0.5
    ):
        raise HandoffError("RUNTIME_NONZERO_DIVISION_ENCLOSURE_MISMATCH")
    try:
        bridge.interval_divide((1.0, 1.0), (-1.0, 1.0), backend=first)
    except bridge.RustBackendError as exc:
        if "ZERO_DIVISOR_INTERVAL" not in str(exc):
            raise HandoffError("RUNTIME_ZERO_DIVISION_WRONG_FAILURE") from exc
    else:
        raise HandoffError("RUNTIME_ZERO_DIVISION_ACCEPTED")

    residual = contract["residual_blockers"]
    if bridge.PROCESS_BOUNDARY_BLOCKER != residual["process_boundary"]:
        raise HandoffError("RUNTIME_PROCESS_BOUNDARY_CLASSIFICATION_MISMATCH")
    if bridge.PRESTART_RUNTIME_BLOCKER != residual["prestart_runtime"]:
        raise HandoffError("RUNTIME_PRESTART_CLASSIFICATION_MISMATCH")

    return ({
        "schema": "rei-local-runtime-bridge-execution-receipt/v1",
        "status": contract["success_status"],
        "immutable_predecessor": contract["immutable_predecessor"],
        "observed_head": head,
        "observed_tree": tree,
        "section_0_receipt_sha256": sha256_file(section_0_receipt),
        "section_0_status": section_0["status"],
        "runtime_identity": identity,
        "artifact_sha256": first_sha256,
        "backend_receipt": first.receipt.to_mapping(),
        "backend_receipt_sha256": first.receipt.identity_sha256(),
        "two_builds_byte_identical": True,
        "nonzero_division_enclosure": list(quotient),
        "zero_containing_divisor_rejection": "ZERO_DIVISOR_INTERVAL",
        "residual_blockers": residual,
        "claim_ceiling": contract["claim_ceiling"],
    }, output_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--section0-receipt", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    options = parser.parse_args(argv)
    try:
        result, output_root = run(
            repo=options.repo,
            section_0_receipt=options.section0_receipt,
            evidence_root=options.evidence_root,
        )
        receipt = output_root / "runtime_bridge_receipt.json"
        atomic_write_json(receipt, result)
    except HandoffError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            f"STOP_INVALID: UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 65
    print(json.dumps({"status": result["status"], "receipt": str(receipt)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
