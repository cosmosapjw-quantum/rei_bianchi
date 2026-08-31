#!/usr/bin/env python3
"""Fail-closed executor for one standalone-clone REI Rust bridge run.

This runner changes only the handoff execution context.  It neither modifies
nor monkeypatches the locked production bridge.  A successful result therefore
preserves the bridge's documented pre-start/process-boundary residuals and the
existing scientific claim ceiling.
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
ATTEMPT_CLAIM_PATH = Path(
    "/tmp/rei-runtime-bridge-host-context-repair-20260901.native-attempt.json"
)


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
        "research_decision",
        "execution_context",
        "attempt_budget",
        "required_operations",
        "forbidden_operations",
        "residual_blockers",
        "success_status",
        "failure_status",
        "claim_ceiling",
    }
    if set(contract) != expected:
        raise HandoffError("RUNTIME_HANDOFF_CONTRACT_SCHEMA_INVALID")
    if contract["schema"] != "rei-runtime-host-context-repair/v1":
        raise HandoffError("RUNTIME_HANDOFF_CONTRACT_SCHEMA_INVALID")
    context = contract.get("execution_context")
    budget = contract.get("attempt_budget")
    if (
        not isinstance(context, dict)
        or context.get("repository_mode") != "FRESH_STANDALONE_CLONE"
        or not isinstance(budget, dict)
        or budget.get("remaining_native_attempts") != 1
        or budget.get("create_only_claim_path") != str(ATTEMPT_CLAIM_PATH)
        or budget.get("create_only_claim_schema")
        != "rei-runtime-host-context-attempt-claim/v1"
    ):
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


def load_section_0_receipt(
    path: Path, expected_sha256: str, expected_status: str
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or sha256_file(path) != expected_sha256:
        raise HandoffError("SECTION0_RECEIPT_IDENTITY_MISMATCH")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HandoffError("SECTION0_RECEIPT_UNREADABLE") from exc
    if not isinstance(receipt, dict) or receipt.get("status") != expected_status:
        raise HandoffError("SECTION0_RECEIPT_STATUS_MISMATCH")
    return receipt


def configure_rustc_locator(raw: Path) -> Path:
    """Bind an explicit locator; the locked bridge remains identity authority."""

    candidate = Path(raw)
    if not candidate.is_absolute():
        raise HandoffError("RUSTC_LOCATOR_NOT_ABSOLUTE")
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise HandoffError("RUSTC_LOCATOR_UNAVAILABLE") from exc
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise HandoffError("RUSTC_LOCATOR_UNAVAILABLE")
    os.environ["REI_RUSTC_1_94_1"] = str(resolved)
    return resolved


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


def _resolve_git_report_path(repo: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = repo / candidate
    try:
        return candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED") from exc


def verify_standalone_repository_context(bridge: Any, repo: Path) -> tuple[Path, ...]:
    """Require a single-root clone with a private common Git directory."""

    dot_git = repo / ".git"
    if dot_git.is_symlink() or not dot_git.is_dir():
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")
    expected_git_dir = dot_git.resolve(strict=True)
    git_dir = _resolve_git_report_path(
        repo, git_checked(bridge, repo, "rev-parse", "--absolute-git-dir").strip()
    )
    common_dir = _resolve_git_report_path(
        repo, git_checked(bridge, repo, "rev-parse", "--git-common-dir").strip()
    )
    if git_dir != expected_git_dir or common_dir != expected_git_dir:
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")

    alternates = expected_git_dir / "objects/info/alternates"
    if alternates.is_symlink() or alternates.exists():
        raise HandoffError("RUNTIME_REPOSITORY_ALTERNATES_FORBIDDEN")
    shallow = git_checked(
        bridge, repo, "rev-parse", "--is-shallow-repository"
    ).strip()
    if shallow != "false":
        raise HandoffError("RUNTIME_SHALLOW_REPOSITORY_FORBIDDEN")

    report = git_checked(bridge, repo, "worktree", "list", "--porcelain")
    records = [record.splitlines() for record in report.strip().split("\n\n") if record]
    if len(records) != 1:
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")
    record = records[0]
    if any(line == "bare" or line.startswith("prunable") for line in record):
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")
    roots = [line.removeprefix("worktree ") for line in record if line.startswith("worktree ")]
    if len(roots) != 1:
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")
    observed_root = _resolve_git_report_path(repo, roots[0])
    if observed_root != repo:
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")
    return (observed_root,)


def verify_predecessor(
    bridge: Any, repo: Path, contract: Mapping[str, Any]
) -> tuple[str, str]:
    predecessor = contract["immutable_predecessor"]
    expected_commit = predecessor["commit"]
    merge_base = git_checked(bridge, repo, "merge-base", "HEAD", expected_commit).strip()
    if merge_base != expected_commit:
        raise HandoffError("IMMUTABLE_PREDECESSOR_NOT_ANCESTOR")
    predecessor_tree = git_checked(
        bridge, repo, "rev-parse", f"{expected_commit}^{{tree}}"
    ).strip()
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
    try:
        worktrees = bridge._worktree_roots(repo)
    except FileNotFoundError as exc:
        raise HandoffError("RUNTIME_WORKTREE_INVENTORY_CHANGED_AFTER_PREFLIGHT") from exc
    for worktree in worktrees:
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


def claim_runner_attempt(path: Path) -> Path:
    """Acquire the create-only lease before any handoff dispatch can occur."""

    candidate = Path(path)
    if not candidate.is_absolute():
        raise HandoffError("RUNTIME_ATTEMPT_CLAIM_NOT_ABSOLUTE")
    try:
        parent = candidate.parent.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise HandoffError("RUNTIME_ATTEMPT_CLAIM_PARENT_UNAVAILABLE") from exc
    target = parent / candidate.name
    try:
        atomic_write_json(
            target,
            {
                "schema": "rei-runtime-host-context-attempt-claim/v1",
                "status": "NATIVE_ATTEMPT_CLAIMED",
                "immutable_predecessor_commit": (
                    "723882d80d57ee8a919bc52ab74633b743447d0c"
                ),
            },
        )
    except FileExistsError as exc:
        raise HandoffError("RUNTIME_ATTEMPT_ALREADY_CLAIMED") from exc
    except OSError as exc:
        raise HandoffError("RUNTIME_ATTEMPT_CLAIM_UNAVAILABLE") from exc
    return target.resolve(strict=True)


def run(
    *,
    repo: Path,
    section_0_receipt: Path,
    rustc: Path,
    evidence_root: Path,
) -> tuple[dict[str, Any], Path]:
    verify_manifest()
    contract = load_contract()
    raw_repo = Path(repo)
    if raw_repo.is_symlink():
        raise HandoffError("RUNTIME_STANDALONE_CLONE_REQUIRED")
    root = raw_repo.resolve(strict=True)
    bridge_path = root / contract["runtime_bridge"]["path"]
    if sha256_file(bridge_path) != contract["runtime_bridge"]["sha256"]:
        raise HandoffError("RUNTIME_BRIDGE_SOURCE_IDENTITY_MISMATCH")
    section_0 = load_section_0_receipt(
        section_0_receipt,
        contract["required_section_0_receipt"]["sha256"],
        contract["required_section_0_receipt"]["required_status"],
    )
    rustc_path = configure_rustc_locator(rustc)
    bridge = load_bridge(root, contract["runtime_bridge"]["path"])
    standalone_roots = verify_standalone_repository_context(bridge, root)
    head, tree = verify_predecessor(bridge, root, contract)
    output_root = create_evidence_root(evidence_root, bridge, root)
    stage = root / contract["rust_backend"]["stage_path"]
    identity = bridge.authenticate_runtime(stage_dir=stage)
    if identity["source_sha256"] != contract["rust_backend"]["source_sha256"]:
        raise HandoffError("RUNTIME_SOURCE_IDENTITY_MISMATCH")
    if identity["rustc_sha256"] != sha256_file(rustc_path):
        raise HandoffError("RUSTC_LOCATOR_IDENTITY_BINDING_MISMATCH")
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
        "schema": "rei-runtime-host-context-repair-receipt/v1",
        "status": contract["success_status"],
        "immutable_predecessor": contract["immutable_predecessor"],
        "observed_head": head,
        "observed_tree": tree,
        "section_0_receipt_sha256": sha256_file(section_0_receipt),
        "section_0_status": section_0["status"],
        "execution_context": {
            "repository_mode": "FRESH_STANDALONE_CLONE",
            "worktree_roots": [str(path) for path in standalone_roots],
            "rustc_locator": str(rustc_path),
            "rustc_locator_sha256": sha256_file(rustc_path),
        },
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


def main(
    argv: list[str] | None = None,
    *,
    attempt_claim_path: Path = ATTEMPT_CLAIM_PATH,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--section0-receipt", type=Path, required=True)
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    options = parser.parse_args(argv)
    try:
        claim_runner_attempt(attempt_claim_path)
        result, output_root = run(
            repo=options.repo,
            section_0_receipt=options.section0_receipt,
            rustc=options.rustc,
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
