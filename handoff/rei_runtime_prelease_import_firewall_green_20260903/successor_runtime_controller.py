#!/usr/bin/env python3
"""Fixed-authority lease controller with canonical runtime-path binding."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

try:
    from . import common_v2 as _authority
    from .common_v2 import (
        FirewallError,
        GITHUB_AUTHORITY,
        GLOBAL_ATTEMPT_REF,
        acquire_global_lease,
        create_dispatch_intent,
        create_local_lease,
        load_contract,
        remaining_attempts_after_stop,
        revalidate_successor_toolchain,
        sha256_file,
        validate_attempt_ref_protection,
        validate_attempt_state_root,
        validate_preflight_receipt,
        validate_runtime_toolchain_witness_paths,
        validate_successor_receipt,
        verify_executing_package_binding,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
    from . import successor_runtime_controller_legacy as _legacy
except ImportError:
    import common_v2 as _authority  # type: ignore
    from common_v2 import (  # type: ignore
        FirewallError,
        GITHUB_AUTHORITY,
        GLOBAL_ATTEMPT_REF,
        acquire_global_lease,
        create_dispatch_intent,
        create_local_lease,
        load_contract,
        remaining_attempts_after_stop,
        revalidate_successor_toolchain,
        sha256_file,
        validate_attempt_ref_protection,
        validate_attempt_state_root,
        validate_preflight_receipt,
        validate_runtime_toolchain_witness_paths,
        validate_successor_receipt,
        verify_executing_package_binding,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
    import successor_runtime_controller_legacy as _legacy  # type: ignore


GITHUB_API_BASE = "https://api.github.com"
GITHUB_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
if (
    GITHUB_API_BASE != _authority.GITHUB_API_BASE
    or GITHUB_REPOSITORY != _authority.GITHUB_REPOSITORY
):
    raise RuntimeError("FIXED_GITHUB_AUTHORITY_CONSTANT_DRIFT")

ControllerError = _legacy.ControllerError
orchestrate_attempt = _legacy.orchestrate_attempt
_validate_evidence_root = _legacy._validate_evidence_root
_validate_python = _legacy._validate_python
_validate_rustc = _legacy._validate_rustc
run_worker_process = _legacy.run_worker_process


def run_controller(
    *,
    repo: Path,
    expected_release_head: str,
    expected_release_tree: str,
    successor_section0_receipt: Path,
    static_preflight_receipt: Path,
    attempt_ref_protection_receipt: Path,
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    evidence_root: Path,
    attempt_state_root: Path,
    token: str,
) -> tuple[Mapping[str, Any], Path]:
    if os.environ.get("REI_NATIVE_DISPATCH_FORBIDDEN") == "1":
        raise ControllerError("HOSTED_CI_NATIVE_DISPATCH_FORBIDDEN")
    verify_package_index()
    contract = load_contract()
    root = Path(repo).resolve(strict=True)
    state = validate_attempt_state_root(attempt_state_root, repo=root)
    verify_static_release(
        root,
        contract,
        expected_head=expected_release_head,
        expected_tree=expected_release_tree,
    )
    verify_executing_package_binding(root, contract)

    runtime_snapshot = validate_runtime_toolchain_witness_paths(
        contract,
        cc=cc,
        ld=ld,
        mpfr=mpfr,
        gmp=gmp,
    )
    runtime_snapshot_sha = runtime_snapshot["sha256"]

    validate_successor_receipt(successor_section0_receipt, contract)
    successor_path = Path(successor_section0_receipt).resolve(strict=True)
    successor_sha = sha256_file(successor_path)
    preflight_path = Path(static_preflight_receipt).resolve(strict=True)
    preflight_output_root = preflight_path.parent
    validate_preflight_receipt(
        preflight_path,
        expected_head=expected_release_head,
        expected_tree=expected_release_tree,
        successor_receipt_sha256=successor_sha,
        expected_attempt_state_root=state,
        expected_output_root=preflight_output_root,
        expected_successor_receipt_path=successor_path,
        expected_authority=GITHUB_AUTHORITY,
        expected_global_ref=GLOBAL_ATTEMPT_REF,
        expected_runtime_toolchain_snapshot=runtime_snapshot,
    )
    preflight_sha = sha256_file(preflight_path)

    protection_path = Path(attempt_ref_protection_receipt).resolve(strict=True)
    validate_attempt_ref_protection(
        protection_path,
        contract=contract,
        expected_global_ref=GLOBAL_ATTEMPT_REF,
    )
    protection_sha = sha256_file(protection_path)
    if not token:
        raise ControllerError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")

    toolchain = contract["successor_section0"]["semantic_toolchain_lock"]
    python_path = _validate_python(python, toolchain["python_sha256"])
    rustc_path = _validate_rustc(rustc, toolchain["rustc_sha256"])
    evidence = _validate_evidence_root(
        evidence_root,
        repo=root,
        state_root=state,
    )
    revalidation_output = (
        preflight_output_root / "prelease-toolchain-revalidation.json"
    )
    revalidation = revalidate_successor_toolchain(
        repo=root,
        contract=contract,
        rustc=rustc_path,
        python=python_path,
        mpfr=mpfr,
        gmp=gmp,
        cc=cc,
        ld=ld,
        original_successor_receipt=successor_path,
        output=revalidation_output,
    )
    revalidation_sha = revalidation["receipt_sha256"]
    if (
        revalidation.get("runtime_toolchain_snapshot_sha256")
        != runtime_snapshot_sha
        or revalidation.get("runtime_toolchain_paths")
        != runtime_snapshot["paths"]
    ):
        raise ControllerError("PRELEASE_RUNTIME_TOOLCHAIN_SNAPSHOT_DRIFT")

    global_path = state / "attempt-3.global-lease.json"
    local_path = state / "attempt-3.local-lease.json"
    dispatch_path = state / "attempt-3.dispatch-intent.json"
    outcome_path = state / "attempt-3.outcome.json"
    reservation_may_have_occurred = False
    dispatch_started = False

    def reserve_global() -> Mapping[str, Any]:
        nonlocal reservation_may_have_occurred
        reservation_may_have_occurred = True
        return acquire_global_lease(
            contract=contract,
            release_head=expected_release_head,
            successor_receipt_sha256=successor_sha,
            preflight_receipt_sha256=preflight_sha,
            attempt_ref_protection_receipt_sha256=protection_sha,
            prelease_toolchain_revalidation_sha256=revalidation_sha,
            runtime_toolchain_snapshot_sha256=runtime_snapshot_sha,
            token=token,
            output=global_path,
        )

    def reserve_local(global_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return create_local_lease(
            output=local_path,
            repo=root,
            state_root=state,
            release_head=expected_release_head,
            release_tree=expected_release_tree,
            global_record=global_record,
            successor_receipt_sha256=successor_sha,
            preflight_receipt_sha256=preflight_sha,
            runtime_toolchain_snapshot_sha256=runtime_snapshot_sha,
        )

    def record_dispatch(
        global_record: Mapping[str, Any],
        local_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return create_dispatch_intent(
            output=dispatch_path,
            state_root=state,
            release_head=expected_release_head,
            release_tree=expected_release_tree,
            global_record=global_record,
            local_record=local_record,
            successor_receipt=successor_path,
            preflight_receipt=preflight_path,
            evidence_root=evidence,
            runtime_toolchain_snapshot_sha256=runtime_snapshot_sha,
        )

    def execute_worker(dispatch_record: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal dispatch_started
        if dispatch_record.get("status") != "DISPATCH_INTENT_WRITTEN":
            raise ControllerError("DISPATCH_INTENT_NOT_WRITTEN")
        if (
            dispatch_record.get("runtime_toolchain_snapshot_sha256")
            != runtime_snapshot_sha
        ):
            raise ControllerError("DISPATCH_RUNTIME_TOOLCHAIN_SNAPSHOT_DRIFT")
        dispatch_started = True
        return run_worker_process(
            python=python_path,
            repo=root,
            expected_release_head=expected_release_head,
            expected_release_tree=expected_release_tree,
            rustc=rustc_path,
            evidence_root=evidence,
            attempt_state_root=state,
            dispatch_intent=dispatch_path,
        )

    try:
        worker_result = orchestrate_attempt(
            acquire_global=reserve_global,
            create_local=reserve_local,
            write_dispatch=record_dispatch,
            run_worker=execute_worker,
        )
        outcome = {
            "schema": "rei-runtime-firewall-attempt-outcome/v2",
            "status": "WORKER_COMPLETED",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "dispatch_started": True,
            "worker_status": worker_result["status"],
            "runtime_receipt": worker_result["runtime_receipt"],
            "runtime_receipt_sha256": worker_result["runtime_receipt_sha256"],
            "attempt_ref_protection_receipt_sha256": protection_sha,
            "prelease_toolchain_revalidation_sha256": revalidation_sha,
            "runtime_toolchain_snapshot_sha256": runtime_snapshot_sha,
            "retries_remaining": 0,
            "next_gate": "RUNTIME_RESULT_AUDIT",
        }
        write_o_excl(outcome_path, outcome)
        return worker_result, outcome_path
    except Exception as exc:
        if not outcome_path.exists():
            try:
                write_o_excl(
                    outcome_path,
                    {
                        "schema": "rei-runtime-firewall-attempt-outcome/v2",
                        "status": "STOP_INVALID",
                        "created_at_utc": datetime.now(timezone.utc).isoformat(),
                        "dispatch_started": dispatch_started,
                        "first_blocker": f"{type(exc).__name__}:{exc}",
                        "global_reservation_or_indeterminate": (
                            reservation_may_have_occurred
                        ),
                        "attempt_ref_protection_receipt_sha256": protection_sha,
                        "prelease_toolchain_revalidation_sha256": revalidation_sha,
                        "runtime_toolchain_snapshot_sha256": runtime_snapshot_sha,
                        "retries_remaining": remaining_attempts_after_stop(
                            global_acquired=reservation_may_have_occurred
                        ),
                    },
                )
            except Exception:
                pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--expected-release-head", required=True)
    parser.add_argument("--expected-release-tree", required=True)
    parser.add_argument("--successor-section0-receipt", type=Path, required=True)
    parser.add_argument("--static-preflight-receipt", type=Path, required=True)
    parser.add_argument(
        "--attempt-ref-protection-receipt", type=Path, required=True
    )
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--mpfr", type=Path, required=True)
    parser.add_argument("--gmp", type=Path, required=True)
    parser.add_argument("--cc", type=Path, required=True)
    parser.add_argument("--ld", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--attempt-state-root", type=Path, required=True)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    options = parser.parse_args(argv)
    try:
        result, outcome = run_controller(
            repo=options.repo,
            expected_release_head=options.expected_release_head,
            expected_release_tree=options.expected_release_tree,
            successor_section0_receipt=options.successor_section0_receipt,
            static_preflight_receipt=options.static_preflight_receipt,
            attempt_ref_protection_receipt=(
                options.attempt_ref_protection_receipt
            ),
            rustc=options.rustc,
            python=options.python,
            mpfr=options.mpfr,
            gmp=options.gmp,
            cc=options.cc,
            ld=options.ld,
            evidence_root=options.evidence_root,
            attempt_state_root=options.attempt_state_root,
            token=os.environ.get(options.token_env, ""),
        )
    except FirewallError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_CONTROLLER_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(
        json.dumps(
            {
                "status": result["status"],
                "runtime_receipt": result["runtime_receipt"],
                "outcome": str(outcome),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
