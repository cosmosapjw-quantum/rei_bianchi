from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFY = _load("sealed_verify_bundle", ROOT / "verify_bundle.py")
RENDER = _load("sealed_render_bwrap", ROOT / "render_bwrap_mount_plan.py")


class SealedBundleVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.bundle = self.root / "bundle"
        (self.bundle / "rootfs/usr/bin").mkdir(parents=True)
        (self.bundle / "rootfs/usr/lib").mkdir(parents=True)
        compiler = self.bundle / "rootfs/usr/bin/compiler"
        compiler.write_bytes(b"compiler bytes\n")
        compiler.chmod(0o755)
        library = self.bundle / "rootfs/usr/lib/libnumber.so.1"
        library.write_bytes(b"library bytes\n")
        library.chmod(0o644)
        os.symlink("compiler", self.bundle / "rootfs/usr/bin/cc")
        os.symlink("libnumber.so.1", self.bundle / "rootfs/usr/lib/libnumber.so")
        self.entries = [
            {
                "path": "/usr/bin/cc",
                "type": "symlink",
                "target": "compiler",
                "role": "COMPILER_ALIAS",
            },
            {
                "path": "/usr/bin/compiler",
                "type": "file",
                "sha256": hashlib.sha256(b"compiler bytes\n").hexdigest(),
                "size": len(b"compiler bytes\n"),
                "mode": "0755",
                "role": "COMPILER",
            },
            {
                "path": "/usr/lib/libnumber.so",
                "type": "symlink",
                "target": "libnumber.so.1",
                "role": "LIBRARY_ALIAS",
            },
            {
                "path": "/usr/lib/libnumber.so.1",
                "type": "file",
                "sha256": hashlib.sha256(b"library bytes\n").hexdigest(),
                "size": len(b"library bytes\n"),
                "mode": "0644",
                "role": "LIBRARY",
            },
        ]
        self.status = {
            "classification": "BYTE_IDENTITY_NON_SCIENTIFIC_AUTHORITY_SUPPLEMENT",
            "identity_class": "BYTE_IDENTITY",
            "closure_claim": "PACKAGED_MEMBERS_ONLY_NO_RUNTIME_COMPLETENESS_CLAIM",
            "runtime_boundary": "NOT_RUN",
            "build": "NOT_RUN",
            "native_tests": "NOT_RUN",
            "adapter": "STOP_INVALID",
            "canonical_pilot": "NOT_RUN",
            "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
            "scientific_pass": "NOT_CLAIMED",
            "scientific_publication": "NOT_RUN",
        }
        self.contract = self.root / "CONTRACT.json"
        self.contract.write_text(
            json.dumps(
                {
                    "schema": "rei-sealed-native-build-authority-supplement-contract/v1",
                    "bundle": {
                        "manifest_path": "AUTHORITY_MANIFEST.json",
                        "rootfs_directory": "rootfs",
                        "manifest_schema": "rei-sealed-native-build-authority-bundle/v1",
                    },
                    "required_status": self.status,
                    "required_files": [self.entries[1], self.entries[3]],
                    "required_symlinks": [
                        {"path": self.entries[0]["path"], "target": self.entries[0]["target"]},
                        {"path": self.entries[2]["path"], "target": self.entries[2]["target"]},
                    ],
                }
            ),
            encoding="utf-8",
        )
        self._write_manifest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_manifest(self) -> str:
        manifest = {
            "schema": "rei-sealed-native-build-authority-bundle/v1",
            **self.status,
            "entries": self.entries,
            "source_packages": [],
            "notes": [],
        }
        raw = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
        (self.bundle / "AUTHORITY_MANIFEST.json").write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def _add_file(
        self,
        logical: str,
        data: bytes,
        *,
        actual_mode: int = 0o644,
        manifest_mode: str = "0644",
        manifest_size: int | bool | None = None,
    ) -> None:
        path = self.bundle / "rootfs" / logical.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(actual_mode)
        self.entries.append(
            {
                "path": logical,
                "type": "file",
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data) if manifest_size is None else manifest_size,
                "mode": manifest_mode,
                "role": "EXTRA_TEST_FILE",
            }
        )
        self.entries.sort(key=lambda item: item["path"])

    def _add_symlink(self, logical: str, target: str) -> None:
        path = self.bundle / "rootfs" / logical.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, path)
        self.entries.append(
            {
                "path": logical,
                "type": "symlink",
                "target": target,
                "role": "EXTRA_TEST_SYMLINK",
            }
        )
        self.entries.sort(key=lambda item: item["path"])

    def test_valid_bundle_returns_non_scientific_receipt(self) -> None:
        receipt, _entries = VERIFY._verify_bundle_against_contract(
            self.bundle,
            self.contract,
            self._write_manifest(),
            production_contract=False,
        )
        self.assertEqual(receipt["declared_member_count"], 4)
        self.assertEqual(
            receipt["classification"], "TEST_ONLY_CONTRACT_VERIFICATION_NOT_AUTHORITY"
        )
        self.assertEqual(receipt["runtime_boundary"], "NOT_RUN")
        self.assertEqual(
            receipt["path_stability"],
            "POINT_IN_TIME_NO_CONCURRENT_WRITER_CLAIM",
        )
        self.assertEqual(
            receipt["concurrent_writer_exclusion"],
            "REQUIRED_NOT_KERNEL_ENFORCED",
        )
        self.assertEqual(receipt["scientific_pass"], "NOT_CLAIMED")

    def test_public_verifier_cannot_admit_a_weak_test_contract(self) -> None:
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "REQUIRED_FILE_MISSING"
        ):
            VERIFY.verify_bundle(self.bundle, self._write_manifest())

    def test_rejects_tampered_regular_file(self) -> None:
        expected = self._write_manifest()
        (self.bundle / "rootfs/usr/bin/compiler").write_bytes(b"tampered\n")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "FILE_SHA256_MISMATCH"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle, self.contract, expected, production_contract=False
            )

    def test_rejects_undeclared_member(self) -> None:
        expected = self._write_manifest()
        (self.bundle / "rootfs/usr/bin/extra").write_bytes(b"extra")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "UNDECLARED_BUNDLE_MEMBER"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle, self.contract, expected, production_contract=False
            )

    def test_rejects_undeclared_top_level_member(self) -> None:
        expected = self._write_manifest()
        (self.bundle / "run-me").write_bytes(b"not declared")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError,
            "UNDECLARED_BUNDLE_TOP_LEVEL_MEMBER",
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle, self.contract, expected, production_contract=False
            )

    def test_rejects_wrong_literal_symlink_target(self) -> None:
        expected = self._write_manifest()
        (self.bundle / "rootfs/usr/bin/cc").unlink()
        os.symlink("../lib/libnumber.so.1", self.bundle / "rootfs/usr/bin/cc")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "SYMLINK_TARGET_MISMATCH"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle, self.contract, expected, production_contract=False
            )

    def test_requires_external_manifest_digest(self) -> None:
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "MANIFEST_SHA256_MISMATCH"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle, self.contract, "0" * 64, production_contract=False
            )

    def test_rejects_manifest_path_traversal(self) -> None:
        self.entries[0]["path"] = "/usr/bin/../escape"
        expected = self._write_manifest()
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "INVALID_ROOTFS_PATH"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle, self.contract, expected, production_contract=False
            )

    def test_rejects_duplicate_and_unsorted_entries(self) -> None:
        duplicate = dict(self.entries[0])
        self.entries.insert(1, duplicate)
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "DUPLICATE_ROOTFS_PATH"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )
        self.entries.pop(1)
        self.entries.reverse()
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "MANIFEST_ENTRIES_NOT_SORTED"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )

    def test_rejects_symlink_cycle_and_undeclared_terminal(self) -> None:
        self._add_symlink("/usr/bin/cycle-a", "cycle-b")
        self._add_symlink("/usr/bin/cycle-b", "cycle-a")
        with self.assertRaisesRegex(VERIFY.AuthorityVerificationError, "SYMLINK_CYCLE"):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )
        for name in ("cycle-a", "cycle-b"):
            (self.bundle / "rootfs/usr/bin" / name).unlink()
        self.entries = [
            entry for entry in self.entries if not entry["path"].endswith(("cycle-a", "cycle-b"))
        ]
        self._add_symlink("/usr/bin/missing-terminal", "not-declared")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "SYMLINK_TERMINAL_UNDECLARED"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )

    def test_rejects_special_member_and_symlink_parent(self) -> None:
        os.mkfifo(self.bundle / "rootfs/usr/bin/fifo")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "SPECIAL_MEMBER_FORBIDDEN"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )
        (self.bundle / "rootfs/usr/bin/fifo").unlink()
        os.symlink("usr", self.bundle / "rootfs/alias")
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "SYMLINK_PARENT_FORBIDDEN"
        ):
            VERIFY._check_no_symlink_parents(
                self.bundle / "rootfs",
                self.bundle / "rootfs/alias/bin/cc",
                "/alias/bin/cc",
            )

    def test_rejects_wrong_file_mode_size_and_boolean_size(self) -> None:
        self._add_file("/usr/lib/mode", b"mode", actual_mode=0o600)
        with self.assertRaisesRegex(VERIFY.AuthorityVerificationError, "FILE_MODE_MISMATCH"):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )
        (self.bundle / "rootfs/usr/lib/mode").chmod(0o644)
        mode_entry = next(entry for entry in self.entries if entry["path"] == "/usr/lib/mode")
        mode_entry["size"] += 1
        with self.assertRaisesRegex(VERIFY.AuthorityVerificationError, "FILE_SIZE_MISMATCH"):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )
        mode_entry["size"] = True
        with self.assertRaisesRegex(
            VERIFY.AuthorityVerificationError, "MANIFEST_ENTRY_SIZE_INVALID"
        ):
            VERIFY._verify_bundle_against_contract(
                self.bundle,
                self.contract,
                self._write_manifest(),
                production_contract=False,
            )

    def test_mount_plan_is_explicitly_non_executable(self) -> None:
        receipt, entries = VERIFY._verify_bundle_against_contract(
            self.bundle,
            self.contract,
            self._write_manifest(),
            production_contract=False,
        )
        plan = RENDER._render_verified_entries(self.bundle, receipt, entries)
        self.assertFalse(plan["executable"])
        self.assertEqual(
            plan["source_path_stability"],
            "NOT_KERNEL_ENFORCED_DO_NOT_EXECUTE",
        )
        self.assertTrue(
            any(
                "source-tree immutability" in field
                for field in plan["required_external_plan_fields"]
            )
        )
        self.assertEqual(plan["runtime_boundary"], "NOT_RUN")
        args = plan["bwrap_argv_fragment"]
        self.assertIn("--tmpfs", args)
        self.assertIn("--ro-bind", args)
        self.assertIn("--symlink", args)
        self.assertEqual(plan["adapter"], "STOP_INVALID")
        self.assertEqual(plan["canonical_pilot"], "NOT_RUN")

    def test_mount_plan_uses_verified_entries_not_a_reread_manifest(self) -> None:
        receipt, entries = VERIFY._verify_bundle_against_contract(
            self.bundle,
            self.contract,
            self._write_manifest(),
            production_contract=False,
        )
        self._add_file("/zzz/injected", b"injected", actual_mode=0o755, manifest_mode="0755")
        self._write_manifest()
        plan = RENDER._render_verified_entries(self.bundle, receipt, entries)
        args = plan["bwrap_argv_fragment"]
        self.assertNotIn("/zzz/injected", args)

    def test_production_contract_tracks_locked_build_receipt(self) -> None:
        repository = ROOT.parents[1]
        contract = json.loads((ROOT / "CONTRACT.json").read_text(encoding="utf-8"))
        self.assertEqual(
            hashlib.sha256((ROOT / "CONTRACT.json").read_bytes()).hexdigest(),
            VERIFY.CANONICAL_CONTRACT_SHA256,
        )
        self.assertEqual(
            contract["bundle"]["manifest_schema_role"],
            "INFORMATIONAL_STRUCTURAL_REFERENCE_VERIFIER_IS_NORMATIVE",
        )
        receipt = json.loads(
            (
                repository
                / "stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
                / "rust/BUILD_RECEIPT.json"
            ).read_text(encoding="utf-8")
        )
        required = {entry["role"]: entry for entry in contract["required_files"]}
        toolchain = receipt["toolchain"]
        self.assertEqual(
            required["SEALED_COMPILER_DRIVER"]["sha256"],
            toolchain["compiler_driver_sha256"],
        )
        self.assertEqual(
            required["SEALED_LINK_EDITOR"]["sha256"],
            toolchain["linker_sha256"],
        )
        self.assertEqual(
            required["SEALED_MPFR_4_2_1"]["sha256"],
            toolchain["mpfr_sha256"],
        )
        self.assertEqual(
            required["SEALED_GMP_6_3_0"]["sha256"],
            toolchain["gmp_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
