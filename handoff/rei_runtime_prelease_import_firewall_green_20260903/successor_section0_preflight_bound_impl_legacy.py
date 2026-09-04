#!/usr/bin/env python3
"""Fixed-authority successor preflight with explicitly bound receipt facts."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

try:
    from . import successor_section0_preflight_impl as _impl
    from .successor_section0_preflight_impl import (  # noqa: F401
        GITHUB_API_BASE,
        GITHUB_API_HOST,
        GITHUB_API_VERSION,
        GITHUB_REPOSITORY,
        GITHUB_AUTHORITY,
        PREFLIGHT_TTL_SECONDS,
        observe_global_ref_read_only,
    )
    from .common_v2 import (
        FirewallError,
        load_contract,
        sha256_file,
        validate_attempt_state_root,
        validate_new_output_root,
        validate_successor_receipt,
        verify_executing_package_binding,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
    from . import successor_section0_preflight_legacy as _legacy
except ImportError:
    import successor_section0_preflight_impl as _impl  # type: ignore
    from successor_section0_preflight_impl import (  # type: ignore # noqa: F401
        GITHUB_API_BASE,
        GITHUB_API_HOST,
        GITHUB_API_VERSION,
        GITHUB_REPOSITORY,
        GITHUB_AUTHORITY,
        PREFLIGHT_TTL_SECONDS,
        observe_global_ref_read_only,
    )
    from common_v2 import (  # type: ignore
        FirewallError,
        load_contract,
        sha256_file,
        validate_attempt_state_root,
        validate_new_output_root,
        validate_successor_receipt,
        verify_executing_package_binding,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
    import successor_section0_preflight_legacy as _legacy  # type: ignore


def _bound_observation(
    source: Mapping[str, Any],
    *,
    ordinal: int,
    release_head: str,
) -> dict[str, Any]:
    """Reconstruct a closed observation instead of copying arbitrary keys."""

    return {
        "status": source["status"],
        "ordinal": ordinal,
        "method": "GET",
        "http_status": 404,
        "authority": {
            "scheme": "https",
            "api_host": GITHUB_API_HOST,
            "repository": GITHUB_REPOSITORY,
            "api_version": GITHUB_API_VERSION,
        },
        "api_host": GITHUB_API_HOST,
        "repository": GITHUB_REPOSITORY,
        "ref": source["ref"],
        "expected_target": release_head,
        "authorization_effect": "NONE",
        "global_lease_acquired": False,
    }


def build_preflight_receipt(
    *,
    release_head: str,
    release_tree: str,
    successor_receipt_sha256: str,
    successor_receipt_path: Path,
    successor_receipt: Mapping[str, Any],
    first_ref_observation: Mapping[str, Any],
    second_ref_observation: Mapping[str, Any],
    state_root: Path,
    output_root: Path,
    emitter_stdout: str,
) -> dict[str, Any]:
    generated = datetime.now(timezone.utc)
    first = {
        "status": first_ref_observation["status"],
        "ordinal": 1,
        "method": "GET",
        "http_status": 404,
        "authority": GITHUB_AUTHORITY,
        "api_host": GITHUB_API_HOST,
        "repository": GITHUB_REPOSITORY,
        "ref": first_ref_observation["ref"],
        "expected_target": release_head,
        "authorization_effect": "NONE",
        "global_lease_acquired": False,
    }
    second = {
        "status": second_ref_observation["status"],
        "ordinal": 2,
        "method": "GET",
        "http_status": 404,
        "authority": GITHUB_AUTHORITY,
        "api_host": GITHUB_API_HOST,
        "repository": GITHUB_REPOSITORY,
        "ref": second_ref_observation["ref"],
        "expected_target": release_head,
        "authorization_effect": "NONE",
        "global_lease_acquired": False,
    }
    return {
        "schema": "rei-runtime-prelease-import-firewall-preflight-receipt/v2",
        "status": "PASS_READ_ONLY_STATIC_PREFLIGHT",
        "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (
            generated + timedelta(seconds=PREFLIGHT_TTL_SECONDS)
        ).isoformat(),
        "authority": GITHUB_AUTHORITY,
        "firewall_release": {"commit": release_head, "tree": release_tree},
        "successor_section0_receipt": str(
            Path(successor_receipt_path).resolve(strict=True)
        ),
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "successor_section0": {
            "schema": successor_receipt["schema"],
            "status": successor_receipt["status"],
            "semantic_toolchain_lock_sha256": successor_receipt[
                "semantic_toolchain_lock_sha256"
            ],
            "host_epoch_fingerprint": successor_receipt[
                "host_epoch_fingerprint"
            ],
            "emitter_stdout": emitter_stdout,
        },
        "global_ref_observations": [first, second],
        "attempt_state": {
            "global_lease_acquired": False,
            "local_lease_created": False,
            "dispatch_intent_created": False,
            "remaining_attempts": 1,
            "absence_is_authorization": False,
        },
        "static_checks": {
            "production_module_loaded": False,
            "standalone_clone_verified": True,
            "pinned_source_bytes_verified": True,
            "closed_runtime_package_verified": True,
            "executing_package_bound_to_head": True,
        },
        "attempt_state_root": str(Path(state_root).resolve(strict=True)),
        "output_root": str(Path(output_root).resolve(strict=True)),
        "native_runtime": "NOT_RUN",
        "next_node": "ATTEMPT_REF_PROTECTION_THEN_ATOMIC_LEASE",
    }


def run_read_only_preflight(
    *,
    repo: Path,
    expected_release_head: str,
    expected_release_tree: str,
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    attempt_state_root: Path,
    output_root: Path,
    token: str = "",
) -> tuple[dict[str, Any], Path, Path]:
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
    ref = contract["attempt_budget"]["global_lease_ref"]
    first = observe_global_ref_read_only(
        ref=ref,
        expected_target=expected_release_head,
        ordinal=1,
        token=token,
    )
    output = validate_new_output_root(
        output_root,
        repo=root,
        state_root=state,
    )
    successor_path = output / "successor-section0.json"
    emitter_stdout = _legacy.run_successor_emitter(
        repo=root,
        contract=contract,
        rustc=rustc,
        python=python,
        mpfr=mpfr,
        gmp=gmp,
        cc=cc,
        ld=ld,
        output=successor_path,
    )
    successor = validate_successor_receipt(successor_path, contract)
    second = observe_global_ref_read_only(
        ref=ref,
        expected_target=expected_release_head,
        ordinal=2,
        token=token,
    )
    if any(state.iterdir()):
        raise FirewallError("READ_ONLY_PREFLIGHT_MUTATED_ATTEMPT_STATE")
    receipt = build_preflight_receipt(
        release_head=expected_release_head,
        release_tree=expected_release_tree,
        successor_receipt_sha256=sha256_file(successor_path),
        successor_receipt_path=successor_path,
        successor_receipt=successor,
        first_ref_observation=first,
        second_ref_observation=second,
        state_root=state,
        output_root=output,
        emitter_stdout=emitter_stdout,
    )
    receipt_path = output / "read-only-static-preflight-receipt.json"
    write_o_excl(receipt_path, receipt)
    return receipt, successor_path, receipt_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--expected-release-head", required=True)
    parser.add_argument("--expected-release-tree", required=True)
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--mpfr", type=Path, required=True)
    parser.add_argument("--gmp", type=Path, required=True)
    parser.add_argument("--cc", type=Path, required=True)
    parser.add_argument("--ld", type=Path, required=True)
    parser.add_argument("--attempt-state-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    options = parser.parse_args(argv)
    try:
        receipt, successor_path, receipt_path = run_read_only_preflight(
            repo=options.repo,
            expected_release_head=options.expected_release_head,
            expected_release_tree=options.expected_release_tree,
            rustc=options.rustc,
            python=options.python,
            mpfr=options.mpfr,
            gmp=options.gmp,
            cc=options.cc,
            ld=options.ld,
            attempt_state_root=options.attempt_state_root,
            output_root=options.output_root,
            token=os.environ.get(options.token_env, ""),
        )
    except FirewallError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_STATIC_PREFLIGHT_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "successor_section0": str(successor_path),
                "receipt": str(receipt_path),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
