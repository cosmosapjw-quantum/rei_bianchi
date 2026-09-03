#!/usr/bin/env python3
"""Post-lease worker that revalidates the live protection evidence first."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

try:
    from .compat import old_common as _old, load_old_worker
    from .lease_bound import validate_attempt_receipts_live
    from .protection_live import (
        GLOBAL_ATTEMPT_REF,
        verify_executing_package_binding,
    )
except ImportError:
    from compat import old_common as _old, load_old_worker  # type: ignore
    from lease_bound import validate_attempt_receipts_live  # type: ignore
    from protection_live import (  # type: ignore
        GLOBAL_ATTEMPT_REF,
        verify_executing_package_binding,
    )


_OLD_WORKER = load_old_worker()
run_native_once = _OLD_WORKER.run_native_once


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
            raise _old.FirewallError("HOSTED_CI_NATIVE_DISPATCH_FORBIDDEN")
        authority_contract = _old.load_contract()
        global_record, _, dispatch = validate_attempt_receipts_live(
            state_root=options.attempt_state_root,
            dispatch_intent=options.dispatch_intent,
            expected_head=options.expected_release_head,
            expected_tree=options.expected_release_tree,
            contract=authority_contract,
        )
        root = options.repo.resolve(strict=True)
        _old.verify_static_release(
            root,
            authority_contract,
            expected_head=options.expected_release_head,
            expected_tree=options.expected_release_tree,
        )
        _old.verify_executing_package_binding(root, authority_contract)
        verify_executing_package_binding(root)
        successor_path = Path(dispatch["successor_section0_receipt"])
        preflight_path = Path(dispatch["preflight_receipt"])
        if (
            _old.sha256_file(successor_path)
            != dispatch["successor_section0_receipt_sha256"]
        ):
            raise _old.FirewallError(
                "DISPATCH_SUCCESSOR_RECEIPT_HASH_MISMATCH"
            )
        if (
            _old.sha256_file(preflight_path)
            != dispatch["preflight_receipt_sha256"]
        ):
            raise _old.FirewallError(
                "DISPATCH_PREFLIGHT_RECEIPT_HASH_MISMATCH"
            )
        if Path(dispatch["evidence_root"]).resolve(strict=False) != Path(
            options.evidence_root
        ).resolve(strict=False):
            raise _old.FirewallError("DISPATCH_EVIDENCE_ROOT_MISMATCH")
        successor = _old.validate_successor_receipt(
            successor_path, authority_contract
        )
        _old.validate_preflight_receipt(
            preflight_path,
            expected_head=options.expected_release_head,
            expected_tree=options.expected_release_tree,
            successor_receipt_sha256=_old.sha256_file(successor_path),
            expected_attempt_state_root=options.attempt_state_root,
            expected_output_root=preflight_path.resolve(strict=True).parent,
            expected_successor_receipt_path=successor_path,
            expected_authority=_old.GITHUB_AUTHORITY,
            expected_global_ref=GLOBAL_ATTEMPT_REF,
        )
        result, output_root = run_native_once(
            repo=root,
            rustc=options.rustc,
            evidence_root=options.evidence_root,
            firewall_contract=authority_contract,
            successor_receipt=successor,
        )
        state = options.attempt_state_root.resolve(strict=True)
        result["firewall_lineage"] = {
            "firewall_release_head": options.expected_release_head,
            "firewall_release_tree": options.expected_release_tree,
            "global_lease_receipt_sha256": _old.sha256_file(
                state / "attempt-3.global-lease.json"
            ),
            "local_lease_receipt_sha256": _old.sha256_file(
                state / "attempt-3.local-lease.json"
            ),
            "dispatch_intent_sha256": _old.sha256_file(
                options.dispatch_intent
            ),
            "source_protection_receipt_sha256": global_record[
                "source_protection_receipt_sha256"
            ],
            "live_attempt_ref_protection_readback_sha256": global_record[
                "live_attempt_ref_protection_readback_sha256"
            ],
            "attempt_ordinal": 3,
            "retries_after_outcome": 0,
            "production_entry_process": "SEPARATE_POST_LEASE_WORKER",
            "fixed_remote_authority": _old.GITHUB_AUTHORITY,
            "executing_package_bound_to_head": True,
        }
        runtime_receipt = output_root / "runtime_bridge_receipt.json"
        _old.write_o_excl(runtime_receipt, result)
    except _old.FirewallError as exc:
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
                "runtime_receipt_sha256": _old.sha256_file(runtime_receipt),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
