from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "materialize_authority.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("rei_authority_materializer", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load authority materializer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class AuthorityMaterializerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = _load_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source = self.root / "source"
        self.destination = self.root / "destination"
        self.source.mkdir()
        self.destination.mkdir()
        self.receipt = self.root / "receipt.json"
        marker = self.root / "SHOULD_NOT_EXIST"
        self.payloads = {
            "archive.zip": b"authority archive bytes\n",
            "environment.sh": f"#!/bin/sh\ntouch '{marker}'\n".encode(),
        }
        for name, payload in self.payloads.items():
            (self.source / name).write_bytes(payload)
        self.contract = self.root / "contract.json"
        self._write_contract()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_contract(self, *, entries: list[dict[str, object]] | None = None) -> None:
        if entries is None:
            entries = [
                {
                    "source": name,
                    "destination": name,
                    "size": len(payload),
                    "sha256": _sha256(payload),
                }
                for name, payload in self.payloads.items()
            ]
        self.contract.write_text(
            json.dumps(
                {
                    "schema": "rei-host-authority-materialization/v1",
                    "classification": "EXACT_EXTERNAL_INPUT_BYTES",
                    "files": entries,
                }
            ),
            encoding="utf-8",
        )

    def _materialize(self):
        return self.module.materialize_test_contract(
            contract_path=self.contract,
            source_root=self.source,
            destination_root=self.destination,
            receipt_path=self.receipt,
        )

    def test_public_materializer_rejects_noncanonical_contract(self) -> None:
        with self.assertRaisesRegex(self.module.MaterializationError, "canonical contract"):
            self.module.materialize(
                contract_path=self.contract,
                source_root=self.source,
                destination_root=self.destination,
                receipt_path=self.receipt,
            )

        self.assertEqual(list(self.destination.iterdir()), [])
        self.assertFalse(self.receipt.exists())

    def test_materializes_exact_bytes_and_writes_bound_receipt_without_execution(self) -> None:
        marker = self.root / "SHOULD_NOT_EXIST"

        receipt = self._materialize()

        self.assertEqual(receipt["status"], "AUTHORITY_BYTES_MATERIALIZED")
        self.assertEqual(
            receipt["path_stability"],
            "POINT_IN_TIME_NO_CONCURRENT_WRITER_CLAIM",
        )
        self.assertEqual(
            receipt["concurrent_writer_exclusion"],
            "REQUIRED_NOT_KERNEL_ENFORCED",
        )
        self.assertEqual(receipt["contract_sha256"], _sha256(self.contract.read_bytes()))
        self.assertEqual(
            [entry["destination"] for entry in receipt["files"]],
            list(self.payloads),
        )
        for name, payload in self.payloads.items():
            installed = self.destination / name
            self.assertEqual(installed.read_bytes(), payload)
            self.assertFalse(installed.stat().st_mode & stat.S_IXUSR)
        self.assertFalse(marker.exists())
        self.assertEqual(json.loads(self.receipt.read_text(encoding="utf-8")), receipt)

    def test_accepts_an_already_materialized_exact_destination(self) -> None:
        for name, payload in self.payloads.items():
            (self.destination / name).write_bytes(payload)

        self._materialize()

        self.assertTrue(self.receipt.is_file())

    def test_rejects_a_symlink_source(self) -> None:
        target = self.source / "real.zip"
        target.write_bytes(self.payloads["archive.zip"])
        (self.source / "archive.zip").unlink()
        (self.source / "archive.zip").symlink_to(target)

        with self.assertRaisesRegex(self.module.MaterializationError, "regular non-symlink"):
            self._materialize()

        self.assertFalse(self.receipt.exists())

    def test_rejects_a_symlink_in_a_source_parent(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        payload = b"outside authority bytes"
        (outside / "authority.bin").write_bytes(payload)
        (self.source / "nested").symlink_to(outside, target_is_directory=True)
        self._write_contract(
            entries=[
                {
                    "source": "nested/authority.bin",
                    "destination": "authority.bin",
                    "size": len(payload),
                    "sha256": _sha256(payload),
                }
            ]
        )

        with self.assertRaisesRegex(self.module.MaterializationError, "symlink component"):
            self._materialize()

        self.assertFalse((self.destination / "authority.bin").exists())

    def test_rejects_a_nonregular_source(self) -> None:
        (self.source / "archive.zip").unlink()
        (self.source / "archive.zip").mkdir()

        with self.assertRaisesRegex(self.module.MaterializationError, "regular non-symlink"):
            self._materialize()

    def test_rejects_wrong_size_before_copying_any_file(self) -> None:
        entries = json.loads(self.contract.read_text(encoding="utf-8"))["files"]
        entries[1]["size"] += 1
        self._write_contract(entries=entries)

        with self.assertRaisesRegex(self.module.MaterializationError, "size mismatch"):
            self._materialize()

        self.assertEqual(list(self.destination.iterdir()), [])

    def test_rejects_wrong_hash_before_copying_any_file(self) -> None:
        entries = json.loads(self.contract.read_text(encoding="utf-8"))["files"]
        entries[1]["sha256"] = "0" * 64
        self._write_contract(entries=entries)

        with self.assertRaisesRegex(self.module.MaterializationError, "SHA-256 mismatch"):
            self._materialize()

        self.assertEqual(list(self.destination.iterdir()), [])

    def test_rejects_a_conflicting_destination_before_copying_any_file(self) -> None:
        (self.destination / "environment.sh").write_bytes(b"conflict")

        with self.assertRaisesRegex(self.module.MaterializationError, "destination conflict"):
            self._materialize()

        self.assertFalse((self.destination / "archive.zip").exists())
        self.assertFalse(self.receipt.exists())

    def test_rejects_a_symlink_destination(self) -> None:
        outside = self.root / "outside"
        outside.write_bytes(self.payloads["archive.zip"])
        (self.destination / "archive.zip").symlink_to(outside)

        with self.assertRaisesRegex(self.module.MaterializationError, "destination conflict"):
            self._materialize()

    def test_rejects_relative_path_escape_in_contract(self) -> None:
        payload = self.payloads["archive.zip"]
        self._write_contract(
            entries=[
                {
                    "source": "archive.zip",
                    "destination": "../escaped.zip",
                    "size": len(payload),
                    "sha256": _sha256(payload),
                }
            ]
        )

        with self.assertRaisesRegex(self.module.MaterializationError, "safe relative path"):
            self._materialize()

        self.assertFalse((self.root / "escaped.zip").exists())

    def test_rejects_unsorted_contract_entries(self) -> None:
        entries = json.loads(self.contract.read_text(encoding="utf-8"))["files"]
        self._write_contract(entries=list(reversed(entries)))

        with self.assertRaisesRegex(self.module.MaterializationError, "sorted"):
            self._materialize()

        self.assertEqual(list(self.destination.iterdir()), [])

    def test_production_contract_matches_input_lock_and_frozen_sizes(self) -> None:
        contract = json.loads((HERE / "CONTRACT.json").read_text(encoding="utf-8"))
        self.assertEqual(
            self.module.CANONICAL_CONTRACT_SHA256,
            _sha256((HERE / "CONTRACT.json").read_bytes()),
        )
        repository = HERE.parents[1]
        lock = json.loads(
            (
                repository
                / "stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/INPUT_LOCK.json"
            ).read_text(encoding="utf-8")
        )
        expected = {
            Path(item["available_copy"]).name: item["sha256"]
            for item in lock["harnesses"]
        }
        for role in ("archive", "signature", "environment_script"):
            record = lock["rust_authority"][role]
            expected[Path(record["path"]).name] = record["sha256"]
        observed = {
            item["source"]: (item["destination"], item["size"], item["sha256"])
            for item in contract["files"]
        }
        frozen_sizes = {
            "01-physmath-research-harness-gpt56.zip": 32648,
            "02-physmath-coding-harness-gpt56.zip": 25533,
            "04-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz.asc": 801,
            "05-rust_1_94_1_env.sh": 240,
            "08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz": 192287020,
        }
        self.assertEqual(list(observed), sorted(observed))
        self.assertEqual(set(observed), set(expected))
        for name, (destination, size, digest) in observed.items():
            self.assertEqual(destination, name)
            self.assertEqual(size, frozen_sizes[name])
            self.assertEqual(digest, expected[name])

    def test_continuation_contract_preserves_checkpoint_and_claim_ceiling(self) -> None:
        continuation = json.loads(
            (HERE / "CONTINUATION_CONTRACT.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            continuation["continuation_base"]["commit"],
            "59c3c9d135860cf3d359a0b70c370eb65b918898",
        )
        self.assertNotEqual(
            continuation["continuation_base"]["commit"],
            continuation["reported_checkpoint"]["commit"],
        )
        self.assertFalse(continuation["reported_checkpoint"]["usable_as_base"])
        self.assertEqual(continuation["terminal_state"]["adapter"], "STOP_INVALID")
        self.assertEqual(continuation["terminal_state"]["canonical_pilot"], "NOT_RUN")
        self.assertEqual(
            continuation["terminal_state"]["first_interval"],
            "NO_PASS_FIRST_CANONICAL_INTERVAL",
        )
        supplement = continuation["sealed_native_authority"]
        self.assertEqual(supplement["build_replay"], "NOT_RUN")
        self.assertEqual(supplement["runtime_boundary"], "NOT_RUN")

    def test_handoff_manifest_has_exact_complete_file_coverage(self) -> None:
        manifest = HERE / "MANIFEST.sha256"
        listed = []
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            self.assertEqual(digest, _sha256((HERE / name).read_bytes()))
            listed.append(name)
        observed = sorted(
            path.name
            for path in HERE.iterdir()
            if path.is_file() and path.name != manifest.name
        )
        self.assertEqual(listed, observed)

    def test_rejects_overlapping_source_and_destination_roots(self) -> None:
        nested_destination = self.source / "materialized"

        with self.assertRaisesRegex(self.module.MaterializationError, "must not overlap"):
            self.module.materialize_test_contract(
                contract_path=self.contract,
                source_root=self.source,
                destination_root=nested_destination,
                receipt_path=self.receipt,
            )

        self.assertFalse(nested_destination.exists())

    def test_rejects_destination_prefix_collisions_before_copying(self) -> None:
        payload = self.payloads["archive.zip"]
        self._write_contract(
            entries=[
                {
                    "source": "archive.zip",
                    "destination": "prefix",
                    "size": len(payload),
                    "sha256": _sha256(payload),
                },
                {
                    "source": "environment.sh",
                    "destination": "prefix/child",
                    "size": len(self.payloads["environment.sh"]),
                    "sha256": _sha256(self.payloads["environment.sh"]),
                },
            ]
        )

        with self.assertRaisesRegex(self.module.MaterializationError, "ancestor collision"):
            self._materialize()

        self.assertEqual(list(self.destination.iterdir()), [])

    def test_rejects_receipt_destination_ancestry_collision_before_copying(self) -> None:
        self.receipt = self.destination / "archive.zip" / "receipt.json"

        with self.assertRaisesRegex(self.module.MaterializationError, "receipt path conflicts"):
            self._materialize()

        self.assertEqual(list(self.destination.iterdir()), [])

    def test_rejects_preexisting_conflicting_receipt(self) -> None:
        self.receipt.write_text("not the receipt", encoding="utf-8")

        with self.assertRaisesRegex(self.module.MaterializationError, "receipt conflict"):
            self._materialize()

    def test_removes_copy_temporary_file_after_write_failure(self) -> None:
        with mock.patch.object(self.module.os, "write", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                self._materialize()

        self.assertEqual(list(self.destination.iterdir()), [])

    def test_removes_receipt_temporary_file_after_write_failure(self) -> None:
        for name, payload in self.payloads.items():
            (self.destination / name).write_bytes(payload)

        with mock.patch.object(self.module.os, "write", side_effect=OSError("injected")):
            with self.assertRaises(OSError):
                self._materialize()

        self.assertFalse(self.receipt.exists())
        self.assertEqual(list(self.root.glob(".*.rei-receipt-*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
