#!/usr/bin/env python3
"""Post-lease worker for exactly one entry into the locked REI runtime."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

try:
    from .common import (
        FirewallError,
        git_blob_sha1,
        load_contract,
        load_json_file,
        sha256_file,
        validate_attempt_receipts as validate_receipt_files,
        validate_preflight_receipt,
        validate_successor_receipt,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
except ImportError:
    from common import (  # type: ignore
        FirewallError,
        git_blob_sha1,
        load_contract,
        load_json_file,
        sha256_file,
        validate_attempt_receipts as validate_receipt_files,
        validate_preflight_receipt,
        validate_successor_receipt,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )


def validate_attempt_receipts(
    *,
    state_root: Path,
    dispatch_intent: Path,
    expected_head: str,
    expected_tree: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return validate_receipt_files(
        state_root=state_root,
        dispatch_intent=dispatch_intent,
        expected_head=expected_head,
        expected_tree=expected_tree,
    )


def _load_locked_successor_runner(
    repo: Path,
    contract: Mapping[str, Any],
) -> Any:
    record = contract["source_lineage"]["runtime_package"]
    path = Path(repo).resolve(strict=True) / record["runner_path"]
    if path.is_symlink() or not path.is_file():
        raise FirewallError("LOCKED_SUCCESSOR_RUNNER_UNAVAILABLE")
    if git_blob_sha1(path) != record["runner_blob_sha1"]:
        raise FirewallError("LOCKED_SUCCESSOR_RUNNER_BLOB_MISMATCH")
    spec = importlib.util.spec_from_file_location(
        "rei_firewall_postlease_successor_runner",
        path,
    )
    if spec is None or spec.loader is None:
        raise FirewallError("LOCKED_SUCCESSOR_RUNNER_IMPORT_SPEC_MISSING")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_native_once(
    *,
    repo: Path,
    rustc: Path,
    evidence_root: Path,
    firewall_contract: Mapping[str, Any],
    successor_receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], Path]:
    module = _load_locked_successor_runner(repo, firewall_contract)
    runtime_contract_path = (
        Path(repo).resolve(strict=True)
        / firewall_contract["source_lineage"]["runtime_package"]["contract_path"]
    )
    runtime_contract = module.load_contract(runtime_contract_path)
    entry = getattr(module, "run_" + "native_once")
    return entry(
        repo=Path(repo).resolve(strict=True),
        rustc=Path(rustc),
        evidence_root=Path(evidence_root),
        contract=runtime_contract,
        successor_receipt=successor_receipt,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--expected-release-head", required=True)
    parser.add_argument("--expected-release-tree", required=True)
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--attempt-state-root", type=Path, required=True)
    parser.add_argument("--dispatch-intent", type=Path, required=True)
    options = parser.parse_args(argv)
    try:
        if os.environ.get("REI_NATIVE_DISPATCH_FORBIDDEN") == "1":
            raise FirewallError("HOSTED_CI_NATIVE_DISPATCH_FORBIDDEN")
        _, _, dispatch = validate_attempt_receipts(
            state_root=options.attempt_state_root,
            dispatch_intent=options.dispatch_intent,
            expected_head=options.expected_release_head,
            expected_tree=options.expected_release_tree,
        )
        verify_package_index()
        contract = load_contract()
        root = options.repo.resolve(strict=True)
        verify_static_release(
            root,
            contract,
            expected_head=options.expected_release_head,
            expected_tree=options.expected_release_tree,
        )
        successor_path = Path(dispatch["successor_section0_receipt"])
        preflight_path = Path(dispatch["preflight_receipt"])
        if (
            sha256_file(successor_path)
            != dispatch["successor_section0_receipt_sha256"]
        ):
            raise FirewallError("DISPATCH_SUCCESSOR_RECEIPT_HASH_MISMATCH")
        if sha256_file(preflight_path) != dispatch["preflight_receipt_sha256"]:
            raise FirewallError("DISPATCH_PREFLIGHT_RECEIPT_HASH_MISMATCH")
        if Path(dispatch["evidence_root"]).resolve(strict=False) != Path(
            options.evidence_root
        ).resolve(strict=False):
            raise FirewallError("DISPATCH_EVIDENCE_ROOT_MISMATCH")
        successor = validate_successor_receipt(successor_path, contract)
        validate_preflight_receipt(
            preflight_path,
            expected_head=options.expected_release_head,
            expected_tree=options.expected_release_tree,
            successor_receipt_sha256=sha256_file(successor_path),
        )
        result, output_root = run_native_once(
            repo=root,
            rustc=options.rustc,
            evidence_root=options.evidence_root,
            firewall_contract=contract,
            successor_receipt=successor,
        )
        state = options.attempt_state_root.resolve(strict=True)
        result["firewall_lineage"] = {
            "firewall_release_head": options.expected_release_head,
            "firewall_release_tree": options.expected_release_tree,
            "global_lease_receipt_sha256": sha256_file(
                state / "attempt-3.global-lease.json"
            ),
            "local_lease_receipt_sha256": sha256_file(
                state / "attempt-3.local-lease.json"
            ),
            "dispatch_intent_sha256": sha256_file(options.dispatch_intent),
            "attempt_ordinal": 3,
            "retries_after_outcome": 0,
            "production_entry_process": "SEPARATE_POST_LEASE_WORKER",
        }
        runtime_receipt = output_root / "runtime_bridge_receipt.json"
        write_o_excl(runtime_receipt, result)
    except FirewallError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_POSTLEASE_WORKER_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(
        json.dumps(
            {
                "status": "WORKER_EXIT_0",
                "runtime_status": result["status"],
                "runtime_receipt": str(runtime_receipt),
                "runtime_receipt_sha256": sha256_file(runtime_receipt),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
