#!/usr/bin/env python3
"""Static successor Section-0 preflight with no production-module import."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Mapping
import urllib.error
import urllib.parse
import urllib.request

try:
    from .common import (
        FirewallError,
        load_contract,
        sha256_file,
        validate_attempt_state_root,
        validate_new_output_root,
        validate_successor_receipt,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )
except ImportError:
    from common import (  # type: ignore
        FirewallError,
        load_contract,
        sha256_file,
        validate_attempt_state_root,
        validate_new_output_root,
        validate_successor_receipt,
        verify_package_index,
        verify_static_release,
        write_o_excl,
    )


def observe_global_ref_read_only(
    *,
    ref: str,
    expected_target: str,
    token: str = "",
    api_base: str = "https://api.github.com",
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    if not ref.startswith("refs/"):
        raise FirewallError("GLOBAL_REF_INVALID")
    relative = urllib.parse.quote(ref.removeprefix("refs/"), safe="/")
    endpoint = (
        api_base.rstrip("/")
        + "/repos/cosmosapjw-quantum/rei_bianchi/git/ref/"
        + relative
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "rei-runtime-prelease-import-firewall-preflight/v1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(endpoint, method="GET", headers=headers)
    try:
        with opener(request, timeout=30) as response:
            status = response.status
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {
                "status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED",
                "http_status": 404,
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


def _require_absolute_executable(path: Path, classification: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise FirewallError(classification)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FirewallError(classification) from exc
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise FirewallError(classification)
    return resolved


def _require_absolute_file(path: Path, classification: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise FirewallError(classification)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FirewallError(classification) from exc
    if not resolved.is_file():
        raise FirewallError(classification)
    return resolved


def run_successor_emitter(
    *,
    repo: Path,
    contract: Mapping[str, Any],
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    output: Path,
) -> str:
    rule = contract["successor_section0"]
    python_path = _require_absolute_executable(
        python, "SUCCESSOR_PYTHON_UNAVAILABLE"
    )
    rustc_path = _require_absolute_executable(
        rustc, "SUCCESSOR_RUSTC_UNAVAILABLE"
    )
    cc_path = _require_absolute_executable(cc, "SUCCESSOR_CC_UNAVAILABLE")
    ld_path = _require_absolute_executable(ld, "SUCCESSOR_LD_UNAVAILABLE")
    mpfr_path = _require_absolute_file(mpfr, "SUCCESSOR_MPFR_UNAVAILABLE")
    gmp_path = _require_absolute_file(gmp, "SUCCESSOR_GMP_UNAVAILABLE")
    emitter = (Path(repo) / rule["emitter_path"]).resolve(strict=True)
    policy = (Path(repo) / rule["policy_path"]).resolve(strict=True)
    command = [
        str(python_path),
        "-I",
        "-S",
        "-B",
        str(emitter),
        "--policy",
        str(policy),
        "--rustc",
        str(rustc_path),
        "--python",
        str(python_path),
        "--mpfr",
        str(mpfr_path),
        "--gmp",
        str(gmp_path),
        "--cc",
        str(cc_path),
        "--ld",
        str(ld_path),
        "--output",
        str(output),
    ]
    completed = subprocess.run(
        command,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise FirewallError("SUCCESSOR_SECTION0_REATTESTATION_FAILED:" + detail)
    return completed.stdout.strip()


def build_preflight_receipt(
    *,
    release_head: str,
    release_tree: str,
    successor_receipt_sha256: str,
    successor_receipt: Mapping[str, Any],
    first_ref_observation: Mapping[str, Any],
    second_ref_observation: Mapping[str, Any],
    state_root: Path,
    output_root: Path,
    emitter_stdout: str,
) -> dict[str, Any]:
    return {
        "schema": "rei-runtime-prelease-import-firewall-preflight-receipt/v1",
        "status": "PASS_READ_ONLY_STATIC_PREFLIGHT",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "firewall_release": {"commit": release_head, "tree": release_tree},
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
        },
        "attempt_state_root": str(state_root),
        "output_root": str(output_root),
        "native_runtime": "NOT_RUN",
        "next_node": "ATOMIC_GLOBAL_LOCAL_LEASE_AND_SEPARATE_WORKER",
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
    api_base: str = "https://api.github.com",
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
    ref = contract["attempt_budget"]["global_lease_ref"]
    first = observe_global_ref_read_only(
        ref=ref,
        expected_target=expected_release_head,
        token=token,
        api_base=api_base,
    )
    output = validate_new_output_root(
        output_root,
        repo=root,
        state_root=state,
    )
    successor_path = output / "successor-section0.json"
    emitter_stdout = run_successor_emitter(
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
        token=token,
        api_base=api_base,
    )
    if any(state.iterdir()):
        raise FirewallError("READ_ONLY_PREFLIGHT_MUTATED_ATTEMPT_STATE")
    receipt = build_preflight_receipt(
        release_head=expected_release_head,
        release_tree=expected_release_tree,
        successor_receipt_sha256=sha256_file(successor_path),
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
    parser.add_argument("--api-base", default="https://api.github.com")
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
            api_base=options.api_base,
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
