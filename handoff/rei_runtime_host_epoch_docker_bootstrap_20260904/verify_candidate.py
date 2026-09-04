#!/usr/bin/env python3
"""Offline verifier for an imported REI 03A4 H1/H2 candidate root.

This program is executed by the candidate root's own /usr/bin/python3 with
Docker networking disabled, the root filesystem read-only, every Linux
capability dropped, and no-new-privileges enabled.  It does not import the REI
production bridge and has no GitHub mutation surface.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping


SCHEMA = "rei-runtime-host-epoch-docker-bootstrap/v1"
PASS_STATUS = "PASS_03A4_HOST_EPOCH_H1_H2_DOCKER_CANDIDATE"
NONAUTHORITY_MARKERS = (
    "GLOBAL_ATTEMPT_REF_FORBIDDEN",
    "LOCAL_LEASE_FORBIDDEN",
    "NATIVE_RUNTIME_FORBIDDEN",
    "H3_RUST_CLOSURE_NOT_RUN",
    "SECTION0_NOT_RUN",
    "SCIENTIFIC_PASS_NOT_CLAIMED",
)


class CandidateError(RuntimeError):
    """Typed fail-closed H1/H2 candidate rejection."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CandidateError("CONTRACT_UNREADABLE") from exc
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise CandidateError("CONTRACT_SCHEMA_INVALID")
    return value


def parse_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def parse_dpkg_status(path: Path = Path("/var/lib/dpkg/status")) -> dict[str, dict[str, str]]:
    packages: dict[str, dict[str, str]] = {}
    fields: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines() + [""]:
        if not raw:
            name = fields.get("Package")
            if name and fields.get("Status") == "install ok installed":
                packages[name] = dict(fields)
            fields = {}
            continue
        if raw[0].isspace() or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        fields[key] = value.strip()
    return packages


def require_read_only_root() -> str:
    probe = "/rei-03a4-h2-write-probe"
    try:
        descriptor = os.open(
            probe,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except OSError as exc:
        if exc.errno != errno.EROFS:
            raise CandidateError(
                f"ROOT_FILESYSTEM_READ_ONLY_PROBE_AMBIGUOUS:{exc.errno}"
            ) from exc
        return "EROFS"
    else:
        os.close(descriptor)
        try:
            os.unlink(probe)
        except OSError:
            pass
        raise CandidateError("ROOT_FILESYSTEM_NOT_READ_ONLY")


def require_network_none() -> list[str]:
    interfaces = sorted(entry.name for entry in Path("/sys/class/net").iterdir())
    non_loopback = [name for name in interfaces if name != "lo"]
    if non_loopback:
        raise CandidateError(
            "NON_LOOPBACK_NETWORK_INTERFACE_PRESENT:" + ",".join(non_loopback)
        )
    return interfaces


def require_packages(
    contract: Mapping[str, Any],
) -> dict[str, dict[str, str]]:
    packages = parse_dpkg_status()
    policy = contract.get("packages")
    if not isinstance(policy, Mapping):
        raise CandidateError("PACKAGE_POLICY_INVALID")
    required = policy.get("required")
    exact = policy.get("exact_versions")
    if not isinstance(required, list) or not isinstance(exact, Mapping):
        raise CandidateError("PACKAGE_POLICY_INVALID")
    missing = sorted(name for name in required if name not in packages)
    if missing:
        raise CandidateError("REQUIRED_PACKAGE_MISSING:" + ",".join(missing))
    for name, expected in exact.items():
        actual = packages.get(str(name), {}).get("Version")
        if actual != expected:
            raise CandidateError(
                f"PACKAGE_VERSION_MISMATCH:{name}:{actual}:{expected}"
            )
    return {
        str(name): {
            "version": packages[str(name)].get("Version", ""),
            "architecture": packages[str(name)].get("Architecture", ""),
        }
        for name in required
    }


def require_runtime_paths(contract: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    declared = contract.get("runtime_paths")
    resolved_expected = contract.get("expected_resolved_paths")
    h2_lock = contract.get("h2_lock")
    supporting = contract.get("supporting_lock")
    if not all(
        isinstance(value, Mapping)
        for value in (declared, resolved_expected, h2_lock, supporting)
    ):
        raise CandidateError("RUNTIME_PATH_CONTRACT_INVALID")

    expected_hashes = {
        "cc": h2_lock.get("cc_sha256"),
        "ld": h2_lock.get("ld_sha256"),
        "python": h2_lock.get("python_sha256"),
        "mpfr": h2_lock.get("mpfr_sha256"),
        "gmp": h2_lock.get("gmp_sha256"),
        "git": supporting.get("git_sha256"),
    }
    rows: dict[str, dict[str, Any]] = {}
    for role in ("cc", "ld", "python", "git", "mpfr", "gmp"):
        raw = declared.get(role)
        if not isinstance(raw, str) or not raw.startswith("/"):
            raise CandidateError(f"RUNTIME_TOOLCHAIN_PATH_INVALID:{role}")
        path = Path(raw)
        try:
            resolved = Path.resolve(path, strict=True)
        except (OSError, RuntimeError) as exc:
            raise CandidateError(
                f"RUNTIME_TOOLCHAIN_PATH_UNAVAILABLE:{role}"
            ) from exc
        if not resolved.is_file():
            raise CandidateError(f"RUNTIME_TOOLCHAIN_PATH_NOT_FILE:{role}")
        expected_resolved = resolved_expected.get(role)
        if str(resolved) != expected_resolved:
            raise CandidateError(
                f"RUNTIME_TOOLCHAIN_PATH_MISMATCH:{role}:{resolved}:{expected_resolved}"
            )
        if role in {"cc", "ld", "python", "git"} and not os.access(resolved, os.X_OK):
            raise CandidateError(f"RUNTIME_TOOLCHAIN_PATH_NOT_EXECUTABLE:{role}")
        actual_hash = sha256_file(resolved)
        expected_hash = expected_hashes[role]
        if actual_hash != expected_hash:
            raise CandidateError(
                f"RUNTIME_TOOLCHAIN_HASH_MISMATCH:{role}:{actual_hash}:{expected_hash}"
            )
        stat_result = resolved.stat()
        rows[role] = {
            "declared_path": raw,
            "resolved_path": str(resolved),
            "sha256": actual_hash,
            "size_bytes": stat_result.st_size,
        }
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--rootfs-sha256", required=True)
    parser.add_argument("--builder-image-id", required=True)
    parser.add_argument("--builder-image-digests", required=True)
    parser.add_argument("--archive-label", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        contract = load_json(args.contract)
        marker = Path("/var/lib/rei-03a4-host-epoch/snapshot-id")
        if marker.read_text(encoding="utf-8").strip() != contract["ubuntu_snapshot"]["id"]:
            raise CandidateError("SNAPSHOT_MARKER_MISMATCH")
        os_release = parse_os_release()
        if os_release.get("VERSION_CODENAME") != "noble":
            raise CandidateError("OS_RELEASE_NOT_NOBLE")
        interfaces = require_network_none()
        write_probe = require_read_only_root()
        packages = require_packages(contract)
        runtime_paths = require_runtime_paths(contract)
        receipt = {
            "schema": "rei-runtime-host-epoch-h1-h2-candidate-receipt/v1",
            "status": PASS_STATUS,
            "release": contract["release"],
            "ubuntu_snapshot": contract["ubuntu_snapshot"],
            "archive_label": args.archive_label,
            "rootfs_sha256": args.rootfs_sha256,
            "builder": {
                "image_id": args.builder_image_id,
                "repo_digests": args.builder_image_digests.split(",") if args.builder_image_digests else [],
                "authority_effect": "NONE",
            },
            "offline_verification": {
                "network_interfaces": interfaces,
                "root_write_probe": write_probe,
                "capabilities": "DROP_ALL_BY_CONTROLLER",
                "no_new_privileges": True,
            },
            "packages": packages,
            "runtime_paths": runtime_paths,
            "claim_ceiling": contract["claim_ceiling"],
            "markers": list(NONAUTHORITY_MARKERS),
            "authorization_effect": "H1_H2_CANDIDATE_ONLY",
        }
        receipt["receipt_sha256"] = hashlib.sha256(
            canonical_bytes(receipt)
        ).hexdigest()
        print(json.dumps(receipt, sort_keys=True, indent=2))
        return 0
    except (CandidateError, KeyError, OSError, UnicodeError) as exc:
        print(f"STOP_INVALID:{exc}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main())
