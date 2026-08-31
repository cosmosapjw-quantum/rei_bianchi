#!/usr/bin/env python3
"""Focused tests for Git-resident small inputs plus one external Rust archive."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MATERIALIZER = Path(__file__).with_name("materialize_small_plus_rust.py")
TRANSPORT_ROOT = Path(__file__).resolve().parent
SMALL_NAMES = (
    "01-physmath-research-harness-gpt56.zip",
    "02-physmath-coding-harness-gpt56.zip",
    "04-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.asc",
    "05-rust_1_94_1_env.sh",
)
RUST_NAME = "08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def entry(name: str, data: bytes) -> dict[str, object]:
    return {"source": name, "destination": name, "size": len(data), "sha256": sha256_bytes(data)}


class MixedAuthorityMaterializerTests(unittest.TestCase):
    def write_fixture(self, root: Path, *, rust_data: bytes, expected_rust: bytes | None = None) -> tuple[Path, Path, Path, dict[str, bytes]]:
        git_small_root = root / "git-small"
        rust_root = root / "rust-download"
        git_small_root.mkdir()
        rust_root.mkdir()
        small_data = {name: f"bytes:{index}".encode("utf-8") for index, name in enumerate(SMALL_NAMES)}
        for name, data in small_data.items():
            (git_small_root / name).write_bytes(data)
        (rust_root / RUST_NAME).write_bytes(rust_data)
        expected = expected_rust if expected_rust is not None else rust_data
        contract = {
            "schema": "rei-host-authority-materialization/v1",
            "classification": "EXACT_EXTERNAL_INPUT_BYTES",
            "files": [*(entry(name, data) for name, data in small_data.items()), entry(RUST_NAME, expected)],
        }
        contract_path = root / "CONTRACT.json"
        contract_path.write_text(json.dumps(contract, sort_keys=True), encoding="utf-8")
        small_manifest = {
            "schema": "rei-host-authority-git-small-inputs/v1",
            "classification": "BYTE_IDENTITY_DIRECT_GIT_BLOBS",
            "files": [
                {"filename": name, "size": len(data), "sha256": sha256_bytes(data)}
                for name, data in small_data.items()
            ],
        }
        small_manifest_path = root / "SMALL_INPUTS_MANIFEST.json"
        small_manifest_path.write_text(json.dumps(small_manifest, sort_keys=True), encoding="utf-8")
        return git_small_root, rust_root, contract_path, small_data | {RUST_NAME: expected}

    def run_materializer(
        self,
        git_small_root: Path,
        rust_root: Path,
        contract: Path,
        small_manifest: Path,
        destination: Path,
        receipt: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(MATERIALIZER),
                "--git-small-root",
                str(git_small_root),
                "--rust-source-root",
                str(rust_root),
                "--contract",
                str(contract),
                "--small-manifest",
                str(small_manifest),
                "--destination-root",
                str(destination),
                "--receipt",
                str(receipt),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_materializes_git_small_inputs_and_external_rust_exactly(self) -> None:
        """The five-file source root must combine four Git blobs and one Rust download."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            git_small_root, rust_root, contract, expected = self.write_fixture(root, rust_data=b"external-rust-archive")
            small_manifest = root / "SMALL_INPUTS_MANIFEST.json"
            destination = root / "source-root"
            receipt = root / "mixed-receipt.json"

            result = self.run_materializer(git_small_root, rust_root, contract, small_manifest, destination, receipt)

            self.assertEqual(result.returncode, 0, result.stderr)
            for name, data in expected.items():
                self.assertEqual((destination / name).read_bytes(), data)
                self.assertEqual(stat.S_IMODE((destination / name).stat().st_mode), 0o444)
            observed_receipt = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(observed_receipt["origins"][RUST_NAME], "external-rust-archive")
            self.assertEqual(observed_receipt["origins"][SMALL_NAMES[0]], "git-resident-small-input")

    def test_rejects_tampered_external_rust_before_writing_destination(self) -> None:
        """The only downloaded large member remains exact-byte fail closed."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            git_small_root, rust_root, contract, _ = self.write_fixture(
                root,
                rust_data=b"tampered",
                expected_rust=b"expected",
            )
            destination = root / "source-root"
            receipt = root / "mixed-receipt.json"

            result = self.run_materializer(
                git_small_root,
                rust_root,
                contract,
                root / "SMALL_INPUTS_MANIFEST.json",
                destination,
                receipt,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("STOP_INVALID_GIT_SMALL_PLUS_RUST", result.stderr)
            self.assertFalse(destination.exists())
            self.assertFalse(receipt.exists())

    def test_rejects_symlinked_git_small_member(self) -> None:
        """Git-resident small inputs must still be real regular files at intake."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            git_small_root, rust_root, contract, _ = self.write_fixture(root, rust_data=b"external-rust-archive")
            replacement = root / "replacement"
            replacement.write_bytes((git_small_root / SMALL_NAMES[0]).read_bytes())
            (git_small_root / SMALL_NAMES[0]).unlink()
            os.symlink(replacement, git_small_root / SMALL_NAMES[0])

            result = self.run_materializer(
                git_small_root,
                rust_root,
                contract,
                root / "SMALL_INPUTS_MANIFEST.json",
                root / "source-root",
                root / "mixed-receipt.json",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("regular non-symlink", result.stderr)

    def test_rejects_destination_nested_in_git_small_source_root(self) -> None:
        """The staging root must never be published inside the Git authority root."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            git_small_root, rust_root, contract, _ = self.write_fixture(root, rust_data=b"external-rust-archive")
            destination = git_small_root / "staged-source-root"
            receipt = root / "mixed-receipt.json"

            result = self.run_materializer(
                git_small_root,
                rust_root,
                contract,
                root / "SMALL_INPUTS_MANIFEST.json",
                destination,
                receipt,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("must not overlap", result.stderr)
            self.assertFalse(destination.exists())
            self.assertFalse(receipt.exists())

    def test_transport_manifest_binds_every_distributed_authority_member(self) -> None:
        """A future unlisted Git input must fail the transport integrity gate."""
        manifest = TRANSPORT_ROOT / "MANIFEST.sha256"
        listed: list[str] = []
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, relative_name = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            self.assertEqual(digest, sha256_bytes((TRANSPORT_ROOT / relative_name).read_bytes()))
            listed.append(relative_name)
        observed = sorted(
            path.relative_to(TRANSPORT_ROOT).as_posix()
            for path in TRANSPORT_ROOT.rglob("*")
            if path.is_file() and path != manifest and "__pycache__" not in path.parts
        )
        self.assertEqual(listed, observed)


if __name__ == "__main__":
    unittest.main()
