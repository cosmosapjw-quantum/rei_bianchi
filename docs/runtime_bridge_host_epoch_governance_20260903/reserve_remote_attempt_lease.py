#!/usr/bin/env python3
"""Atomically reserve the one remaining native attempt through GitHub create-ref.

The script performs no GET-then-POST authorization and never updates or deletes
a ref.  HTTP 201 is the only successful acquisition outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_PROTOCOL = HERE / "GLOBAL_ATTEMPT_LEASE_PROTOCOL.json"
ATTEMPT_REF_PREFIX = "refs/heads/attempt-ledger/"
SEMANTIC_LOCK_SHA256 = "a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_o_excl(path: Path, value: dict[str, Any]) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(canonical_bytes(value) + b"\n")
        output.flush()
        os.fsync(output.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--successor-section0-receipt", type=Path, required=True)
    parser.add_argument("--api-base", default="https://api.github.com")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    receipt_path = args.successor_section0_receipt.resolve(strict=True)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASS_EQUIVALENT_SECTION_0_SUCCESSOR":
        raise SystemExit("SUCCESSOR_SECTION0_NOT_PASSED")
    if receipt.get("semantic_toolchain_lock_sha256") != SEMANTIC_LOCK_SHA256:
        raise SystemExit("SUCCESSOR_SECTION0_LOCK_MISMATCH")

    ref = protocol["lease_ref"]
    target = protocol["lease_target_commit"]
    if not ref.startswith(ATTEMPT_REF_PREFIX):
        raise SystemExit("GLOBAL_LEASE_REF_NAMESPACE_MISMATCH")
    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit("GLOBAL_LEASE_TOKEN_UNAVAILABLE")

    endpoint = args.api_base.rstrip("/") + protocol["acquisition"]["endpoint"]
    payload = canonical_bytes({"ref": ref, "sha": target})
    request = urllib.request.Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rei-runtime-global-attempt-lease/v1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            raise SystemExit("STOP_ATTEMPT_ALREADY_RESERVED") from exc
        raise SystemExit(f"STOP_GLOBAL_LEASE_HTTP_{exc.code}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit("STOP_GLOBAL_LEASE_TRANSPORT_OR_RESPONSE") from exc

    if status != 201 or body.get("ref") != ref or body.get("object", {}).get("sha") != target:
        raise SystemExit("STOP_REMOTE_LEASE_RESPONSE_MISMATCH")
    output = Path(args.output)
    if not output.is_absolute():
        raise SystemExit("GLOBAL_LEASE_RECEIPT_PATH_NOT_ABSOLUTE")
    output.parent.resolve(strict=True)
    record = {
        "schema": "rei-runtime-global-attempt-lease-receipt/v1",
        "status": "GLOBAL_ATTEMPT_RESERVED",
        "ref": ref,
        "target_commit": target,
        "successor_section0_receipt_sha256": sha256_file(receipt_path),
        "semantic_toolchain_lock_sha256": receipt["semantic_toolchain_lock_sha256"],
        "mutation_policy": "CREATE_ONLY_NO_UPDATE_NO_DELETE",
        "native_runtime": "NOT_RUN",
    }
    write_o_excl(output, record)
    print(json.dumps({"status": record["status"], "ref": ref, "receipt": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
