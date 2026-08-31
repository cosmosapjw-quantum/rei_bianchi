from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "materialize_missing_components.py"
SPEC = importlib.util.spec_from_file_location("rei_materialize_missing_components", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
REPAIR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REPAIR
SPEC.loader.exec_module(REPAIR)


BASE_PREFIX = "bundle/rust-std/lib/rustlib/target/lib/"
SUPPLEMENT_PREFIX = "bundle/llvm-tools/lib/rustlib/target/lib/"


def _digest(rows: list[tuple[str, bytes]]) -> str:
    lines = []
    for name, data in sorted(rows):
        lines.append(f"{hashlib.sha256(data).hexdigest()}  ./{name}\n".encode("ascii"))
    return hashlib.sha256(b"".join(lines)).hexdigest()


class MaterializeMissingComponentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rei-stdlib-repair-test-")
        self.root = Path(self.tmp.name)
        self.stdlib = self.root / "stdlib"
        self.stdlib.mkdir()
        self.base = {"libbase-a.rlib": b"base a\n", "libbase-b.rmeta": b"base b\n"}
        self.supplement = {
            "libLLVM-a.so": b"supplement a\n",
            "libLLVM-b.so": b"supplement b\n",
        }
        for name, data in self.base.items():
            (self.stdlib / name).write_bytes(data)
        self.archive = self.root / "rust.tar.xz"
        with tarfile.open(self.archive, "w:xz") as bundle:
            for prefix, members in ((BASE_PREFIX, self.base), (SUPPLEMENT_PREFIX, self.supplement)):
                for name, data in members.items():
                    info = tarfile.TarInfo(prefix + name)
                    info.size = len(data)
                    info.mode = 0o644
                    bundle.addfile(info, io.BytesIO(data))
        archive_sha = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.contract = self.root / "CONTRACT.json"
        payload = {
            "schema": "rei-rust-stdlib-closure-repair-contract/v1",
            "rust_archive": {"sha256": archive_sha, "base_prefix": BASE_PREFIX},
            "supplements": [
                {
                    "archive_path": SUPPLEMENT_PREFIX + name,
                    "target_name": name,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size_bytes": len(data),
                }
                for name, data in sorted(self.supplement.items())
            ],
            "expected_closure_sha256": _digest(list(self.base.items()) + list(self.supplement.items())),
        }
        self.contract.write_text(json.dumps(payload), encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _repair(self, *, apply: bool):
        return REPAIR.repair(
            stdlib_dir=self.stdlib,
            rust_archive=self.archive,
            contract_path=self.contract,
            apply=apply,
        )

    def test_01_dry_run_is_read_only_and_identifies_exact_missing_members(self) -> None:
        result = self._repair(apply=False)
        self.assertEqual(result["status"], "REPAIR_READY_DRY_RUN")
        self.assertEqual(result["missing_target_names"], sorted(self.supplement))
        self.assertFalse(any((self.stdlib / name).exists() for name in self.supplement))

    def test_02_apply_materializes_exact_members_and_reproduces_closure(self) -> None:
        result = self._repair(apply=True)
        self.assertEqual(result["status"], "APPLIED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY")
        self.assertEqual(result["post_repair_closure_sha256"], result["expected_closure_sha256"])
        for name, data in self.supplement.items():
            target = self.stdlib / name
            self.assertEqual(target.read_bytes(), data)
            self.assertEqual(target.stat().st_mode & 0o777, 0o444)

    def test_03_base_member_drift_is_rejected_before_any_write(self) -> None:
        (self.stdlib / "libbase-a.rlib").write_bytes(b"mutated\n")
        with self.assertRaisesRegex(REPAIR.RepairError, "BASE_MEMBER_MISMATCH"):
            self._repair(apply=True)
        self.assertFalse(any((self.stdlib / name).exists() for name in self.supplement))

    def test_04_conflicting_preexisting_target_is_rejected_before_any_write(self) -> None:
        (self.stdlib / "libLLVM-a.so").write_bytes(b"wrong\n")
        with self.assertRaisesRegex(REPAIR.RepairError, "SUPPLEMENT_TARGET_CONFLICT"):
            self._repair(apply=True)
        self.assertFalse((self.stdlib / "libLLVM-b.so").exists())

    def test_05_second_apply_is_idempotent_and_does_not_overwrite(self) -> None:
        first = self._repair(apply=True)
        second = self._repair(apply=True)
        self.assertEqual(first["status"], "APPLIED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY")
        self.assertEqual(second["status"], "ALREADY_MATERIALIZED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY")

    def test_06_archive_identity_mismatch_is_rejected_before_any_write(self) -> None:
        with self.archive.open("ab") as stream:
            stream.write(b"authority drift")
        with self.assertRaisesRegex(REPAIR.RepairError, "ARCHIVE_SHA256_MISMATCH"):
            self._repair(apply=True)
        self.assertFalse(any((self.stdlib / name).exists() for name in self.supplement))


if __name__ == "__main__":
    unittest.main()
