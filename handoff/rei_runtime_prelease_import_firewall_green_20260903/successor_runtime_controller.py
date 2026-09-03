#!/usr/bin/env python3
"""Lease-owning controller that never imports the production bridge."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Mapping

try:
    from .common import (
        FirewallError,
        acquire_global_lease,
        create_dispatch_intent,
        create_local_lease,
        load_contract,
        remaining_attempts_after_stop,
        sha256_file,
        validate_attempt_state_root,
        validate_preflight_receipt,
        validate_successor_receipt,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
except ImportError:
    from common import (  # type: ignore
        FirewallError,
        acquire_global_lease,
        create_dispatch_intent,
        create_local_lease,
        load_contract,
        remaining_attempts_after_stop,
        sha256_file,
        validate_attempt_state_root,
        validate_preflight_receipt,
        validate_successor_receipt,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )


PACKAGE = Path(__file__).resolve().parent
WORKER = PACKAGE / "native_runtime_worker.py"


class ControllerError(FirewallError):
    """Typed controller error."""


def orchestrate_attempt(
    *,
    acquire_global: Callable[[], Mapping[str, Any]],
    create_local: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    write_dispatch: Callable[
        [Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]
    ],
    run_worker: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> Mapping[str, Any]:
    """Execute exactly one global -> local -> intent -> worker chain."""

    global_record = acquire_global()
    if global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED":
        raise ControllerError("GLOBAL_LEASE_NOT_RESERVED")
    local_record = create_local(global_record)
    if local_record.get("status") != "LOCAL_ATTEMPT_RESERVED":
        raise ControllerError("LOCAL_LEASE_NOT_RESERVED")
    dispatch_record = write_dispatch(global_record, local_record)
    if dispatch_record.get("status") != "DISPATCH_INTENT_WRITTEN":
        raise ControllerError("DISPATCH_INTENT_NOT_WRITTEN")
    return run_worker(dispatch_record)


def _validate_evidence_root(
    path: Path,
    *,
    repo: Path,
    state_root: Path,
) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise ControllerError("EVIDENCE_ROOT_INVALID")
    resolved = candidate.resolve(strict=False)
    repository = Path(repo).resolve(strict=True)
    state = Path(state_root).resolve(strict=True)
    tmp = Path("/tmp").resolve(strict=True)
    for root in (repository, state, tmp):
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        raise ControllerError("EVIDENCE_ROOT_FORBIDDEN")
    if resolved.exists() or resolved.is_symlink():
        raise ControllerError("EVIDENCE_ROOT_PREEXISTS")
    if not resolved.parent.is_dir():
        raise ControllerError("EVIDENCE_ROOT_PARENT_UNAVAILABLE")
    return resolved


def _validate_python(path: Path, expected_sha256: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise ControllerError("WORKER_PYTHON_NOT_ABSOLUTE")
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ControllerError("WORKER_PYTHON_UNAVAILABLE") from exc
    if (
        not resolved.is_file()
        or not os.access(resolved, os.X_OK)
        or sha256_file(resolved) != expected_sha256
    ):
        raise ControllerError("WORKER_PYTHON_IDENTITY_MISMATCH")
    return resolved


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
    rustc: Path,
    python: Path,
    evidence_root: Path,
    attempt_state_root: Path,
    token: str,
    api_base: str = "https://api.github.com",
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
    successor = validate_successor_receipt(successor_section0_receipt, contract)
    successor_sha = sha256_file(successor_section0_receipt)
    preflight = validate_preflight_receipt(
        static_preflight_receipt,
        expected_head=expected_release_head,
        expected_tree=expected_release_tree,
        successor_receipt_sha256=successor_sha,
    )
    preflight_sha = sha256_file(static_preflight_receipt)
    python_path = _validate_python(
        python, contract["successor_section0"]["semantic_toolchain_lock"]["python_sha256"]
    )
    evidence = _validate_evidence_root(
        evidence_root,
        repo=root,
        state_root=state,
    )
    if not token:
        raise ControllerError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")

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
            token=token,
            output=global_path,
            api_base=api_base,
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
            successor_receipt=successor_section0_receipt,
            preflight_receipt=static_preflight_receipt,
            evidence_root=evidence,
        )

    def execute_worker(dispatch_record: Mapping[str, Any]) -> Mapping[str, Any]:
        nonlocal dispatch_started
        if dispatch_record.get("status") != "DISPATCH_INTENT_WRITTEN":
            raise ControllerError("DISPATCH_INTENT_NOT_WRITTEN")
        dispatch_started = True
        return run_worker_process(
            python=python_path,
            repo=root,
            expected_release_head=expected_release_head,
            expected_release_tree=expected_release_tree,
            rustc=rustc,
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
            "schema": "rei-runtime-firewall-attempt-outcome/v1",
            "status": "WORKER_COMPLETED",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "dispatch_started": True,
            "worker_status": worker_result["status"],
            "runtime_receipt": worker_result["runtime_receipt"],
            "runtime_receipt_sha256": worker_result["runtime_receipt_sha256"],
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
                        "schema": "rei-runtime-firewall-attempt-outcome/v1",
                        "status": "STOP_INVALID",
                        "created_at_utc": datetime.now(timezone.utc).isoformat(),
                        "dispatch_started": dispatch_started,
                        "first_blocker": f"{type(exc).__name__}:{exc}",
                        "global_reservation_or_indeterminate": (
                            reservation_may_have_occurred
                        ),
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
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--attempt-state-root", type=Path, required=True)
    parser.add_argument("--api-base", default="https://api.github.com")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    options = parser.parse_args(argv)
    try:
        result, outcome = run_controller(
            repo=options.repo,
            expected_release_head=options.expected_release_head,
            expected_release_tree=options.expected_release_tree,
            successor_section0_receipt=options.successor_section0_receipt,
            static_preflight_receipt=options.static_preflight_receipt,
            rustc=options.rustc,
            python=options.python,
            evidence_root=options.evidence_root,
            attempt_state_root=options.attempt_state_root,
            token=os.environ.get(options.token_env, ""),
            api_base=options.api_base,
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
