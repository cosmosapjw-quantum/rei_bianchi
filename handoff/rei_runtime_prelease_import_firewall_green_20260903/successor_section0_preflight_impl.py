#!/usr/bin/env python3
"""Fixed-authority successor Section-0 preflight without production import."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping
import urllib.error
import urllib.parse
import urllib.request

try:
    from . import common_v2 as _authority
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
    import common_v2 as _authority  # type: ignore
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


GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_HOST = "api.github.com"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
GITHUB_AUTHORITY: dict[str, str] = {
    "scheme": "https",
    "api_host": GITHUB_API_HOST,
    "repository": GITHUB_REPOSITORY,
    "api_version": GITHUB_API_VERSION,
}
PREFLIGHT_TTL_SECONDS = 1800
if (
    GITHUB_API_BASE != _authority.GITHUB_API_BASE
    or GITHUB_REPOSITORY != _authority.GITHUB_REPOSITORY
    or GITHUB_AUTHORITY != _authority.GITHUB_AUTHORITY
):
    raise RuntimeError("FIXED_GITHUB_AUTHORITY_CONSTANT_DRIFT")


def observe_global_ref_read_only(
    *,
    ref: str,
    expected_target: str,
    ordinal: int,
    token: str = "",
) -> dict[str, Any]:
    if not ref.startswith("refs/") or ordinal not in {1, 2}:
        raise FirewallError("GLOBAL_REF_OBSERVATION_INPUT_INVALID")
    relative = urllib.parse.quote(ref.removeprefix("refs/"), safe="/")
    endpoint = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_REPOSITORY}/git/ref/{relative}"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "rei-runtime-authority-binding-preflight/v2",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(endpoint, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {
                "status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED",
                "ordinal": ordinal,
                "method": "GET",
                "http_status": 404,
                "authority": GITHUB_AUTHORITY,
                "api_host": GITHUB_API_HOST,
                "repository": GITHUB_REPOSITORY,
                "ref": ref,
                "expected_target": expected_target,
                "authorization_effect": "NONE",
                "global_lease_acquired": False,
            }
        raise FirewallError(
            f"GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED:HTTP_{exc.code}"
        ) from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FirewallError("GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED") from exc
    if status != 200 or not isinstance(payload, dict):
        raise FirewallError("GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED")
    raise FirewallError(
        "STOP_ATTEMPT_ALREADY_RESERVED:"
        f"ref={payload.get('ref')!r}:"
        f"target={payload.get('object', {}).get('sha')!r}"
    )


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
    return {
        "schema": "rei-runtime-prelease-import-firewall-preflight-receipt/v2",
        "status": "PASS_READ_ONLY_STATIC_PREFLIGHT",
        "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (
            generated + timedelta(seconds=PREFLIGHT_TTL_SECONDS)
        ).isoformat(),
        "authority": {
            "scheme": "https",
            "api_host": GITHUB_API_HOST,
            "repository": GITHUB_REPOSITORY,
            "api_version": GITHUB_API_VERSION,
        },
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
        "global_ref_observations": [
            dict(first_ref_observation),
            dict(second_ref_observation),
        ],
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
