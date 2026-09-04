#!/usr/bin/env python3
"""Post-lease worker bound to exact receipts and canonical runtime paths."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

try:
    from .common_v2 import (
        FirewallError,
        GITHUB_AUTHORITY,
        GLOBAL_ATTEMPT_REF,
        load_contract,
        sha256_file,
        validate_attempt_receipts,
        validate_preflight_receipt,
        validate_runtime_toolchain_witness_paths,
        validate_successor_receipt,
        verify_executing_package_binding,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
    from . import native_runtime_worker_legacy as _legacy
except ImportError:
    from common_v2 import (  # type: ignore
        FirewallError,
        GITHUB_AUTHORITY,
        GLOBAL_ATTEMPT_REF,
        load_contract,
        sha256_file,
        validate_attempt_receipts,
        validate_preflight_receipt,
        validate_runtime_toolchain_witness_paths,
        validate_successor_receipt,
        verify_executing_package_binding,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
    import native_runtime_worker_legacy as _legacy  # type: ignore


run_native_once = _legacy.run_native_once


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
        global_record, local_record, dispatch = validate_attempt_receipts(
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
        verify_executing_package_binding(root, contract)

        declared = contract["runtime_toolchain_path_binding"]["paths"]
        resolved = {
            role: Path(declared[role]).resolve(strict=True)
            for role in ("cc", "ld", "mpfr", "gmp")
        }
        runtime_snapshot = validate_runtime_toolchain_witness_paths(
            contract,
            cc=resolved["cc"],
            ld=resolved["ld"],
            mpfr=resolved["mpfr"],
            gmp=resolved["gmp"],
        )
        runtime_snapshot_sha = runtime_snapshot["sha256"]
        for record, classification in (
            (global_record, "GLOBAL_LEASE_RUNTIME_TOOLCHAIN_MISMATCH"),
            (local_record, "LOCAL_LEASE_RUNTIME_TOOLCHAIN_MISMATCH"),
            (dispatch, "DISPATCH_RUNTIME_TOOLCHAIN_MISMATCH"),
        ):
            if (
                record.get("runtime_toolchain_snapshot_sha256")
                != runtime_snapshot_sha
            ):
                raise FirewallError(classification)

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
            expected_attempt_state_root=options.attempt_state_root,
            expected_output_root=preflight_path.resolve(strict=True).parent,
            expected_successor_receipt_path=successor_path,
            expected_authority=GITHUB_AUTHORITY,
            expected_global_ref=GLOBAL_ATTEMPT_REF,
            expected_runtime_toolchain_snapshot=runtime_snapshot,
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
            "runtime_toolchain_snapshot_sha256": runtime_snapshot_sha,
            "attempt_ordinal": 3,
            "retries_after_outcome": 0,
            "production_entry_process": "SEPARATE_POST_LEASE_WORKER",
            "fixed_remote_authority": GITHUB_AUTHORITY,
            "executing_package_bound_to_head": True,
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
