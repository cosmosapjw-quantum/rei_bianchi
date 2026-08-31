from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "stdlib_closure_audit.py"
SPEC = importlib.util.spec_from_file_location("rei_stdlib_closure_audit", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


PREFIX = "bundle/rust-std/lib/rustlib/x86_64-unknown-linux-gnu/lib/"


class StdlibClosureAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rei-stdlib-audit-test-")
        self.root = Path(self.tmp.name)
        self.stdlib = self.root / "stdlib"
        self.stdlib.mkdir()
        self.members = {
            "libalpha-111.rlib": b"alpha\n",
            "libbeta-222.rmeta": b"beta\n",
        }
        for name, data in self.members.items():
            (self.stdlib / name).write_bytes(data)
        (self.stdlib / "self-contained").mkdir()
        self.archive = self.root / "rust.tar.xz"
        with tarfile.open(self.archive, "w:xz") as bundle:
            for name, data in self.members.items():
                info = tarfile.TarInfo(PREFIX + name)
                info.size = len(data)
                info.mode = 0o644
                bundle.addfile(info, io.BytesIO(data))
        self.archive_sha256 = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        rows = AUDIT._stdlib_rows(self.stdlib)
        self.expected = AUDIT._candidate_digests(rows)["legacy_gnu_sha256sum_transcript"]

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, *, expected: str | None = None, shell_replay: bool = True):
        return AUDIT.run_audit(
            stdlib_dir=self.stdlib,
            rust_archive=self.archive,
            archive_prefix=PREFIX,
            expected_archive_sha256=self.archive_sha256,
            expected_closure_sha256=expected or self.expected,
            reported_observed_sha256=None,
            shell_replay=shell_replay,
        )

    def test_01_matching_members_and_legacy_replay_are_diagnostic_only(self) -> None:
        result = self._run()
        self.assertEqual(result["status"], "PASS_DIAGNOSTIC_ONLY")
        self.assertEqual(result["member_comparison"]["status"], "PASS")
        self.assertEqual(result["python_legacy_replay_sha256"], self.expected)
        self.assertTrue(result["shell_digest_matches_python_legacy"])
        self.assertEqual(result["shell_legacy_replay"]["digest"], self.expected)

    def test_02_locked_digest_mismatch_is_stop_invalid_not_an_implicit_repair(self) -> None:
        result = self._run(expected="0" * 64, shell_replay=False)
        self.assertEqual(result["status"], "STOP_INVALID")
        self.assertEqual(
            result["first_failing_gate"], "RUST_STDLIB_CLOSURE_SHA256_MISMATCH_CONFIRMED"
        )
        self.assertEqual(result["member_comparison"]["status"], "PASS")

    def test_03_archive_member_difference_precedes_aggregate_comparison(self) -> None:
        (self.stdlib / "libalpha-111.rlib").write_bytes(b"mutated\n")
        result = self._run(shell_replay=False)
        self.assertEqual(result["status"], "STOP_INVALID")
        self.assertEqual(result["first_failing_gate"], "RUST_STDLIB_ARCHIVE_MEMBER_MISMATCH")
        self.assertEqual(len(result["member_comparison"]["member_mismatches"]), 1)

    def test_04_symlinked_stdlib_member_is_rejected_before_aggregate_use(self) -> None:
        target = self.stdlib / "target"
        target.write_bytes(b"alpha\n")
        member = self.stdlib / "libalpha-111.rlib"
        member.unlink()
        member.symlink_to(target.name)
        with self.assertRaisesRegex(AUDIT.AuditError, "STDLIB_SYMLINK_FORBIDDEN"):
            self._run(shell_replay=False)

    def test_05_cli_receipt_is_create_only(self) -> None:
        receipt = self.root / "receipt.json"
        arguments = [
            "--stdlib-dir", str(self.stdlib),
            "--rust-archive", str(self.archive),
            "--archive-prefix", PREFIX,
            "--expected-archive-sha256", self.archive_sha256,
            "--expected-closure-sha256", self.expected,
            "--receipt", str(receipt),
            "--skip-shell-replay",
        ]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(AUDIT.main(arguments), 0)
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "PASS_DIAGNOSTIC_ONLY")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(AUDIT.main(arguments), 65)


if __name__ == "__main__":
    unittest.main()
