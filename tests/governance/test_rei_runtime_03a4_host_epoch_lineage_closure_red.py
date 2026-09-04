#!/usr/bin/env python3
"""Second intentional RED: bind H1A lineage and the full runtime closure.

This suite is static.  It must not invoke Docker, mutate the host, create an
attempt ref, or enter the REI native runtime.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_host_epoch_docker_bootstrap_20260904"
CONTRACT = PACKAGE / "CONTRACT.json"
BUILDER = PACKAGE / "build_host_epoch_candidate.sh"
VERIFIER = PACKAGE / "verify_candidate.py"
INDEX = PACKAGE / "PACKAGE_INDEX.json"

H1A_AUDIT_SHA = "5d344fbfc8a68368386dfcc1ef0ef882813c819e8a263f5a589ab41100d7c9b6"
H1A_POST_MANIFEST_SHA = "d1054f80c3d6b48918d840b4b0ad479a8df7381350e1ee9cfacbd1086427eb26"
SEED_DIGEST = "ubuntu@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517"
SEED_IMAGE_ID = "sha256:a6f81fb630d51837271b89f8193810a5fc493fa4f30a55d7ebcdb3a66f3cc63a"
SNAPSHOT = "20250115T120000Z"

FULL_OS_RUNTIME_CLOSURE = {
    "cc_sha256": "6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234",
    "ld_sha256": "5b674ea1d7017c2929f3c52c43487478bb240ecdd7197a25cce3813a70329a5c",
    "python_sha256": "a92f0f95e883390c7256b2e441484aac06b1002dbe1d924141a77c8d82f96223",
    "mpfr_sha256": "2156351fa3dedd04a7381c6ac7a8a26efa2d6fb08b80f8a2d644ccdd653710ae",
    "gmp_sha256": "0ccdfb6d6f5c039465f6d002cf7e4c072d48ac6a2cffc8dd6c748dec31592804",
    "git_sha256": "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668",
    "ldd_sha256": "429938a30ba5d51f4cdba476e8f8f8b1595d51b14a665ab6edf642454ff662ea",
    "readelf_sha256": "6d54602a1ee13f1214973086bd60efe2dae4363f8f5ab7516eaaf3e259dca90e",
    "elf_interpreter_sha256": "6222a16be7f2d458d6870efe6e715fc0c8d45766fb79cf7dcc3125538d703e28",
    "libc_sha256": "511f825ee075610ac9c0f7f91e2c13de2000d0f7b859f6461137e809a0a009d0",
    "libgcc_s_sha256": "d93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb",
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


class HostEpochLineageClosureExpectedRed(unittest.TestCase):
    def test_green_package_surface_is_still_absent(self) -> None:
        self.assertTrue(
            all(path.is_file() for path in (CONTRACT, BUILDER, VERIFIER, INDEX)),
            "P0_H1B_GREEN_PACKAGE_ABSENT",
        )

    def test_h1a_durable_chain_and_exact_seed_are_bound(self) -> None:
        h1a = _json(CONTRACT).get("upstream_h1a", {})
        self.assertEqual(
            h1a,
            {
                "operation_status": "PASS_REI_03A4_H1A_DOCKER_ADMISSION",
                "independent_audit_status": "PASS_H1A_DOCKER_ADMISSION_INDEPENDENT_AUDIT",
                "durable_closeout_status": "PASS_H1A_DURABLE_AUDIT_CLOSEOUT",
                "independent_audit_receipt_sha256": H1A_AUDIT_SHA,
                "post_audit_manifest_sha256": H1A_POST_MANIFEST_SHA,
                "seed_repo_digest": SEED_DIGEST,
                "seed_image_id": SEED_IMAGE_ID,
                "snapshot": SNAPSHOT,
                "authority_effect": "NONE",
            },
            "P0_H1A_DURABLE_CHAIN_UNBOUND",
        )

    def test_h1a_verifier_provenance_limit_is_typed(self) -> None:
        limitations = _json(CONTRACT).get("known_upstream_limitations", {})
        self.assertEqual(
            (
                limitations.get("h1a_external_verifier_source_transitively_bound"),
                limitations.get("h1a_role"),
                limitations.get("h1b_must_revalidate_input_manifests"),
            ),
            (False, "ISOLATION_MECHANISM_ADMISSION_ONLY", True),
            "P1_H1A_VERIFIER_PROVENANCE_LIMIT_NOT_TYPED",
        )

    def test_docker_context_and_daemon_locality_are_bound(self) -> None:
        policy = _json(CONTRACT).get("docker_context_policy", {})
        source = _text(BUILDER)
        self.assertEqual(
            (
                policy.get("remote_daemons_forbidden"),
                policy.get("allowed_endpoint_schemes"),
                policy.get("docker_host_override_forbidden"),
                policy.get("record_context_and_daemon_identity"),
            ),
            (True, ["unix"], True, True),
            "P0_DOCKER_DAEMON_LOCALITY_UNBOUND",
        )
        for token in (
            "docker context show",
            "docker context inspect",
            "DOCKER_HOST",
            "REMOTE_DOCKER_DAEMON_FORBIDDEN",
        ):
            self.assertIn(token, source, "P0_DOCKER_DAEMON_LOCALITY_UNBOUND")

    def test_builder_uses_only_the_exact_admitted_seed(self) -> None:
        source = _text(BUILDER)
        for token in (SEED_DIGEST, SEED_IMAGE_ID, "--pull never", "--platform linux/amd64"):
            self.assertIn(token, source, "P0_IMMUTABLE_H1A_SEED_NOT_ENFORCED")

    def test_builder_has_no_host_bind_socket_or_privileged_escape(self) -> None:
        combined = _text(CONTRACT) + _text(BUILDER)
        required = (
            "HOST_BIND_MOUNTS_FORBIDDEN",
            "DOCKER_SOCKET_MOUNT_FORBIDDEN",
            "PRIVILEGED_BUILDER_FORBIDDEN",
            "HOST_NAMESPACE_SHARING_FORBIDDEN",
            "HOST_PACKAGE_MUTATION_FORBIDDEN",
        )
        self.assertTrue(
            all(token in combined for token in required),
            "P0_BUILDER_HOST_BOUNDARY_UNDERBOUND",
        )
        invocation_lines = "\n".join(
            line for line in _text(BUILDER).splitlines()
            if "docker run" in line or line.lstrip().startswith("--")
        )
        for pattern in (r"--privileged(?:\s|$)", r"--network[ =]+host", r"docker\.sock", r"(?:^|\s)-v(?:\s|$)"):
            self.assertIsNone(
                re.search(pattern, invocation_lines),
                "P0_BUILDER_HOST_BOUNDARY_UNDERBOUND",
            )

    def test_snapshot_metadata_is_signature_verified_and_hashed(self) -> None:
        trust = _json(CONTRACT).get("snapshot_trust", {})
        source = _text(BUILDER) + _text(VERIFIER)
        self.assertEqual(
            (
                trust.get("signed_inrelease_required"),
                trust.get("ubuntu_archive_keyring_identity_required"),
                trust.get("packages_index_hashes_required"),
                trust.get("trusted_yes_forbidden"),
                trust.get("no_check_gpg_forbidden"),
            ),
            (True, True, True, True, True),
            "P0_SIGNED_SNAPSHOT_METADATA_UNBOUND",
        )
        for token in ("gpgv", "InRelease", "ubuntu-archive-keyring", "Packages"):
            self.assertIn(token, source, "P0_SIGNED_SNAPSHOT_METADATA_UNBOUND")

    def test_complete_os_and_prestart_runtime_closure_is_pinned(self) -> None:
        observed = _json(CONTRACT).get("os_runtime_closure_sha256")
        self.assertEqual(
            observed,
            FULL_OS_RUNTIME_CLOSURE,
            "P0_PRESTART_RUNTIME_CLOSURE_INCOMPLETE",
        )

    def test_package_deb_path_and_installed_file_provenance_are_emitted(self) -> None:
        source = _text(BUILDER) + _text(VERIFIER)
        for token in (
            "dpkg-query",
            "DEB_SHA256_MANIFEST",
            "CANONICAL_PATH_MAP",
            "INSTALLED_FILE_SHA256_MANIFEST",
            "Path.resolve",
            "RUNTIME_TOOLCHAIN_PATH_MISMATCH",
            "RUNTIME_TOOLCHAIN_HASH_MISMATCH",
        ):
            self.assertIn(
                token,
                source,
                "P1_PACKAGE_AND_CANONICAL_PATH_PROVENANCE_INCOMPLETE",
            )

    def test_rootfs_transport_archive_is_deterministic_but_non_authoritative(self) -> None:
        archive = _json(CONTRACT).get("rootfs_archive_policy", {})
        source = _text(BUILDER)
        self.assertEqual(
            (
                archive.get("deterministic_transport_archive"),
                archive.get("installed_file_manifest_is_authority"),
                archive.get("archive_authority_effect"),
            ),
            (True, True, "NONE"),
            "P1_ROOTFS_ARCHIVE_AND_CONTENT_IDENTITY_UNBOUND",
        )
        for token in (
            "--sort=name",
            "--numeric-owner",
            "--owner=0",
            "--group=0",
            "--mtime=@0",
            "ROOTFS_CONTENT_MANIFEST",
        ):
            self.assertIn(token, source, "P1_ROOTFS_ARCHIVE_AND_CONTENT_IDENTITY_UNBOUND")

    def test_h1b_h2_remain_non_authoritative_for_attempt_and_physics(self) -> None:
        combined = _text(CONTRACT) + _text(BUILDER) + _text(VERIFIER)
        for token in (
            "H3_RUST_CLOSURE_NOT_RUN",
            "SECTION0_NOT_RUN",
            "GLOBAL_ATTEMPT_REF_FORBIDDEN",
            "LOCAL_LEASE_FORBIDDEN",
            "CONTROLLER_FORBIDDEN",
            "NATIVE_RUNTIME_FORBIDDEN",
            "FIRST_CANONICAL_INTERVAL_NOT_RUN",
            "PROVIDER_NOT_AUTHORIZED",
            "SCIENTIFIC_PASS_NOT_CLAIMED",
        ):
            self.assertIn(token, combined, "P0_RUNTIME_AND_PHYSICS_NONAUTHORITY_UNDERBOUND")


if __name__ == "__main__":
    unittest.main(verbosity=2)
