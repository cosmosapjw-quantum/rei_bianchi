#!/usr/bin/env python3
"""Intentional RED for Docker-backed REI 03A4 host-epoch reconstruction."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_host_epoch_docker_bootstrap_20260904"
CONTRACT = PACKAGE / "CONTRACT.json"
BUILDER = PACKAGE / "build_host_epoch_candidate.sh"
VERIFIER = PACKAGE / "verify_candidate.py"
INDEX = PACKAGE / "PACKAGE_INDEX.json"

EXPECTED_HEAD = "ab1ea23fd8e3ebe17f46d13d5496bb1db3eba08b"
EXPECTED_TREE = "779c06d1e4bf9c54292ad22030cb1b47906af988"
EXPECTED_SNAPSHOT = "20250115T120000Z"
EXPECTED_HASHES = {
    "cc_sha256": "6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234",
    "ld_sha256": "5b674ea1d7017c2929f3c52c43487478bb240ecdd7197a25cce3813a70329a5c",
    "python_sha256": "a92f0f95e883390c7256b2e441484aac06b1002dbe1d924141a77c8d82f96223",
    "mpfr_sha256": "2156351fa3dedd04a7381c6ac7a8a26efa2d6fb08b80f8a2d644ccdd653710ae",
    "gmp_sha256": "0ccdfb6d6f5c039465f6d002cf7e4c072d48ac6a2cffc8dd6c748dec31592804",
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


class HostEpochDockerBootstrapExpectedRed(unittest.TestCase):
    def test_required_package_surface_exists(self) -> None:
        self.assertTrue(
            all(path.is_file() for path in (CONTRACT, BUILDER, VERIFIER, INDEX)),
            "P0_DOCKER_BOOTSTRAP_PACKAGE_ABSENT",
        )

    def test_contract_pins_release_snapshot_and_hashes(self) -> None:
        contract = _json(CONTRACT)
        observed = {
            "head": contract.get("release", {}).get("head"),
            "tree": contract.get("release", {}).get("tree"),
            "snapshot": contract.get("ubuntu_snapshot", {}).get("id"),
            "hashes": contract.get("h2_lock"),
        }
        self.assertEqual(
            observed,
            {
                "head": EXPECTED_HEAD,
                "tree": EXPECTED_TREE,
                "snapshot": EXPECTED_SNAPSHOT,
                "hashes": EXPECTED_HASHES,
            },
            "P0_SNAPSHOT_AND_RELEASE_IDENTITY_UNBOUND",
        )

    def test_docker_is_a_typed_fallback_not_runtime_authority(self) -> None:
        docker = _json(CONTRACT).get("docker_fallback", {})
        self.assertEqual(
            (
                docker.get("allowed_when_host_bootstrap_absent"),
                docker.get("builder_authority_effect"),
                docker.get("required_verification_network"),
            ),
            (True, "NONE", "NONE"),
            "P0_DOCKER_FALLBACK_NOT_TYPED",
        )

    def test_host_mutation_and_host_usr_bind_are_forbidden(self) -> None:
        combined = _text(CONTRACT) + _text(BUILDER)
        required = (
            "HOST_APT_INSTALL_FORBIDDEN",
            "HOST_DPKG_INSTALL_FORBIDDEN",
            "HOST_ALTERNATIVES_MUTATION_FORBIDDEN",
            "HOST_USR_BIND_FORBIDDEN",
        )
        self.assertTrue(
            all(token in combined for token in required),
            "P0_HOST_MUTATION_SURFACE_NOT_FORBIDDEN",
        )

    def test_builder_streams_snapshot_rootfs_outside_authority_roots(self) -> None:
        source = _text(BUILDER)
        required = (
            "snapshot.ubuntu.com/ubuntu/${SNAPSHOT_ID}",
            "debootstrap",
            "rootfs.tar",
            "REI_HOST_EPOCH_ROOT",
            "ATTEMPT_STATE_ROOT",
            "tar --numeric-owner",
        )
        self.assertTrue(
            all(token in source for token in required),
            "P0_ROOTFS_STREAM_AND_CANONICAL_PATH_BUILD_ABSENT",
        )

    def test_verification_is_offline_read_only_and_capability_minimal(self) -> None:
        source = _text(BUILDER)
        required = (
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "no-new-privileges",
            "docker import",
        )
        self.assertTrue(
            all(token in source for token in required),
            "P0_OFFLINE_READ_ONLY_VERIFICATION_ABSENT",
        )

    def test_isolated_verifier_checks_paths_hashes_packages_and_write_block(self) -> None:
        source = _text(VERIFIER)
        required = (
            "Path.resolve",
            "sha256_file",
            "gcc-13-x86-64-linux-gnu",
            "RUNTIME_TOOLCHAIN_PATH_MISMATCH",
            "RUNTIME_TOOLCHAIN_HASH_MISMATCH",
            "ROOT_FILESYSTEM_NOT_READ_ONLY",
            "NON_LOOPBACK_NETWORK_INTERFACE_PRESENT",
        )
        self.assertTrue(
            all(token in source for token in required),
            "P0_H2_HASH_AND_PACKAGE_VALIDATOR_ABSENT",
        )

    def test_h1_h2_cannot_create_attempt_or_claim_runtime(self) -> None:
        combined = _text(CONTRACT) + _text(BUILDER) + _text(VERIFIER)
        required = (
            "GLOBAL_ATTEMPT_REF_FORBIDDEN",
            "LOCAL_LEASE_FORBIDDEN",
            "NATIVE_RUNTIME_FORBIDDEN",
            "H3_RUST_CLOSURE_NOT_RUN",
            "SECTION0_NOT_RUN",
            "SCIENTIFIC_PASS_NOT_CLAIMED",
        )
        self.assertTrue(
            all(token in combined for token in required),
            "P0_RUNTIME_ATTEMPT_NONAUTHORITY_ABSENT",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
