#!/usr/bin/env python3
"""Lease controller with live protection and canonical runtime paths.

The controller never imports the REI production bridge.  It binds the same
post-lease runtime-path snapshot in preflight, immediate pre-reservation
reattestation, the protected global lease, local lease, dispatch intent and the
separate worker.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

try:
    from .compat import old_common as _old, load_old_controller
    from .lease_bound import acquire_global_lease
    from .protection_live import (
        GLOBAL_ATTEMPT_REF,
        load_contract as load_live_contract,
        revalidate_attempt_ref_protection_live,
        validate_fresh_attempt_ref_protection,
        verify_executing_package_binding,
    )
except ImportError:
    from compat import old_common as _old, load_old_controller  # type: ignore
    from lease_bound import acquire_global_lease  # type: ignore
    from protection_live import (  # type: ignore
        GLOBAL_ATTEMPT_REF,
        load_contract as load_live_contract,
        revalidate_attempt_ref_protection_live,
        validate_fresh_attempt_ref_protection,
        verify_executing_package_binding,
    )


PACKAGE = Path(__file__).resolve().parent
WORKER = PACKAGE / "native_runtime_worker.py"
_OLD_CONTROLLER = load_old_controller()
ControllerError = _OLD_CONTROLLER.ControllerError
orchestrate_attempt = _OLD_CONTROLLER.orchestrate_attempt
_validate_evidence_root = _OLD_CONTROLLER._validate_evidence_root
_validate_python = _OLD_CONTROLLER._validate_python
_validate_rustc = _OLD_CONTROLLER._validate_rustc
revalidate_successor_toolchain = _old.revalidate_successor_toolchain
validate_runtime_toolchain_witness_paths = (
    _old.validate_runtime_toolchain_witness_paths
)


def run_worker_process(
    *,
    python: Path,
    repo: Path,
    expected_release_head: str,
    expected_release_tree: str,
    rustc: Path,
    evidence_root: Path,
    attempt_state_root: Path,
    dispatch_intent: Path,
) -> dict[str, Any]:
    command = [
        str(python),
        "-I",
        "-S",
        "-B",
        str(WORKER),
        "--repo",
        str(repo),
        "--expected-release-head",
        expected_release_head,
        "--expected-release-tree",
        expected_release_tree,
        "--rustc",
        str(rustc),
        "--evidence-root",
        str(evidence_root),
        "--attempt-state-root",
        str(attempt_state_root),
        "--dispatch-intent",
        str(dispatch_intent),
    ]
    completed = subprocess.run(
        command,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={
            "PATH": "/usr/bin:/bin",
            "LC_ALL": "C",
            "LANG": "C",
            "REI_NATIVE_DISPATCH_FORBIDDEN": "0",
        },
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ControllerError(
            f"WORKER_EXIT_NONZERO:{completed.returncode}:{detail}"
        )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise ControllerError("WORKER_SUCCESS_RECEIPT_MISSING")
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        raise ControllerError("WORKER_SUCCESS_RECEIPT_INVALID") from exc
    if not isinstance(payload, dict) or payload.get("status") != "WORKER_EXIT_0":
        raise ControllerError("WORKER_SUCCESS_RECEIPT_INVALID")
    return payload


def run_controller(
    *,
    repo: Path,
    expected_release_head: str,
    expected_release_tree: str,
    successor_section0_receipt: Path,
    static_preflight_receipt: Path,
    source_protection_receipt: Path,
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
    load_live_contract()
    authority_contract = _old.load_contract()
    root = Path(repo).resolve(strict=True)
    state = _old.validate_attempt_state_root(attempt_state_root, repo=root)
    _old.verify_static_release(
        root,
        authority_contract,
        expected_head=expected_release_head,
        expected_tree=expected_release_tree,
    )
    _old.verify_executing_package_binding(root, authority_contract)
    verify_executing_package_binding(root)

    runtime_snapshot = validate_runtime_toolchain_witness_paths(
        authority_contract,
        cc=cc,
        ld=ld,
        mpfr=mpfr,
        gmp=gmp,
    )
    runtime_snapshot_sha = runtime_snapshot["sha256"]

    _old.validate_successor_receipt(
        successor_section0_receipt, authority_contract
    )
    successor_path = Path(successor_section0_receipt).resolve(strict=True)
    successor_sha = _old.sha256_file(successor_path)
    preflight_path = Path(static_preflight_receipt).resolve(strict=True)
    preflight_output_root = preflight_path.parent
    _old.validate_preflight_receipt(
        preflight_path,
        expected_head=expected_release_head,
        expected_tree=expected_release_tree,
        successor_receipt_sha256=successor_sha,
        expected_attempt_state_root=state,
        expected_output_root=preflight_output_root,
        expected_successor_receipt_path=successor_path,
        expected_authority=_old.GITHUB_AUTHORITY,
        expected_global_ref=GLOBAL_ATTEMPT_REF,
        expected_runtime_toolchain_snapshot=runtime_snapshot,
    )
    preflight_sha = _old.sha256_file(preflight_path)
    source_protection_path = Path(source_protection_receipt).resolve(strict=True)
    validate_fresh_attempt_ref_protection(
        source_protection_path,
        contract=authority_contract,
        expected_global_ref=GLOBAL_ATTEMPT_REF,
    )
    source_protection_receipt_sha256 = _old.sha256_file(
        source_protection_path
    )
    if not token:
        raise ControllerError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")

    toolchain = authority_contract["successor_section0"][
        "semantic_toolchain_lock"
    ]
    python_path = _validate_python(python, toolchain["python_sha256"])
    rustc_path = _validate_rustc(rustc, toolchain["rustc_sha256"])
    evidence = _validate_evidence_root(
        evidence_root,
        repo=root,
        state_root=state,
    )
    revalidation_output = (
        preflight_output_root / "prelease-toolchain-revalidation-live.json"
    )
    revalidation = revalidate_successor_toolchain(
        repo=root,
        contract=authority_contract,
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
    live_protection_path = (
        preflight_output_root / "attempt-3.live-protection-readback.json"
    )
    reservation_may_have_occurred = False
    dispatch_started = False
    live_protection_sha = ""

    def reserve_global() -> Mapping[str, Any]:
        nonlocal reservation_may_have_occurred, live_protection_sha
        live_record = revalidate_attempt_ref_protection_live(
            source_protection_receipt=source_protection_path,
            contract=authority_contract,
            expected_global_ref=GLOBAL_ATTEMPT_REF,
            expected_release_head=expected_release_head,
            token=token,
            output=live_protection_path,
        )
        live_protection_sha = live_record["receipt_sha256"]
        reservation_may_have_occurred = True
        return acquire_global_lease(
            contract=authority_contract,
            release_head=expected_release_head,
            successor_receipt_sha256=successor_sha,
            preflight_receipt_sha256=preflight_sha,
            attempt_ref_protection_receipt_sha256=live_protection_sha,
            source_protection_receipt_sha256=(
                source_protection_receipt_sha256
            ),
            source_protection_receipt=source_protection_path,
            live_protection_receipt=live_protection_path,
            prelease_toolchain_revalidation_sha256=revalidation_sha,
            runtime_toolchain_snapshot_sha256=runtime_snapshot_sha,
            token=token,
            output=global_path,
        )

    def reserve_local(global_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return _old.create_local_lease(
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
        return _old.create_dispatch_intent(
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
            "schema": "rei-runtime-firewall-attempt-outcome/v3",
            "status": "WORKER_COMPLETED",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "dispatch_started": True,
            "worker_status": worker_result["status"],
            "runtime_receipt": worker_result["runtime_receipt"],
            "runtime_receipt_sha256": worker_result["runtime_receipt_sha256"],
            "source_protection_receipt_sha256": (
                source_protection_receipt_sha256
            ),
            "live_attempt_ref_protection_readback_sha256": (
                live_protection_sha
            ),
            "prelease_toolchain_revalidation_sha256": revalidation_sha,
            "runtime_toolchain_snapshot_sha256": runtime_snapshot_sha,
            "retries_remaining": 0,
            "next_gate": "RUNTIME_RESULT_AUDIT",
        }
        _old.write_o_excl(outcome_path, outcome)
        return worker_result, outcome_path
    except Exception as exc:
        if not outcome_path.exists():
            try:
                _old.write_o_excl(
                    outcome_path,
                    {
                        "schema": "rei-runtime-firewall-attempt-outcome/v3",
                        "status": "STOP_INVALID",
                        "created_at_utc": datetime.now(timezone.utc).isoformat(),
                        "dispatch_started": dispatch_started,
                        "first_blocker": f"{type(exc).__name__}:{exc}",
                        "global_reservation_or_indeterminate": (
                            reservation_may_have_occurred
                        ),
                        "source_protection_receipt_sha256": (
                            source_protection_receipt_sha256
                        ),
                        "live_attempt_ref_protection_readback_sha256": (
                            live_protection_sha or None
                        ),
                        "prelease_toolchain_revalidation_sha256": (
                            revalidation_sha
                        ),
                        "runtime_toolchain_snapshot_sha256": (
                            runtime_snapshot_sha
                        ),
                        "retries_remaining": _old.remaining_attempts_after_stop(
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
    parser.add_argument("--source-protection-receipt", type=Path, required=True)
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
            source_protection_receipt=options.source_protection_receipt,
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
    except _old.FirewallError as exc:
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
