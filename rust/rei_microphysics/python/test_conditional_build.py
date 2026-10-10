"""Prelaunch regression tests: no native executable or solver is launched."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import conditional_build as build
import source_bound_interval as production


class BuildGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.crate = self.root / "crate"
        for name, contents in {
            "Cargo.toml": b"fixture manifest", "Cargo.lock": b"fixture lock",
            "src/lib.rs": b"fixture library",
            "src/bin/axisym_conditional.rs": b"fixture binary source",
            "python/source_bound_interval.py": b"fixture runner",
            "python/conditional_build.py": b"fixture gate",
        }.items():
            path = self.crate / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
        self.binary = self.root / "axisym_conditional"
        # A protocol-shaped fixture would answer BIND if launched. No test
        # launches it; the negative checks must stop before Popen.
        self.binary.write_text("#!/bin/sh\nwhile read line; do echo 'OK 1'; done\n")
        self.binary.chmod(0o755)
        self.receipt = self.root / "BUILD_RECEIPT.json"
        self.data = {
            "schema": build.SCHEMA, "status": "BUILD_PASS",
            "revision": {"commit": "a" * 40, "tree": "b" * 40, "clean": True},
            "build": {"exit_code": 0, "fresh_target": True},
            "source_sha256": build.source_hashes(self.crate),
            "binary": {"sha256": build.sha256(self.binary)},
        }
        self.receipt.write_text(json.dumps(self.data))

    def run_without_launch(self, expected_error=None):
        args = ["--binary", str(self.binary), "--build-receipt", str(self.receipt),
                "--check-build-only"]
        with patch.object(production, "CRATE", self.crate), \
                patch.object(production.subprocess, "Popen") as popen, \
                patch.object(production, "ProductionInterval") as interval, \
                patch.object(production, "load_provider") as provider, \
                patch.object(production, "solve_ivp") as solver, \
                patch.object(production, "preflight", return_value={"identities": {}}) as inputs, \
                contextlib.redirect_stdout(io.StringIO()) as stdout:
            if expected_error is None:
                production.main(args)
                result = json.loads(stdout.getvalue())
                self.assertEqual(result["build"]["status"], "PRELAUNCH_BUILD_PASS")
                self.assertEqual(result["binary_launches"], 0)
                self.assertEqual(result["solver_intervals"], 0)
                inputs.assert_called_once()
            else:
                with self.assertRaisesRegex(ValueError, expected_error):
                    production.main(args)
                inputs.assert_not_called()
            popen.assert_not_called()
            interval.assert_not_called()
            provider.assert_not_called()
            solver.assert_not_called()

    def test_missing_receipt_fails_before_any_launch(self):
        self.receipt.unlink()
        self.run_without_launch("BUILD_RECEIPT_REQUIRED")

    def test_protocol_compatible_stale_binary_fails_before_any_launch(self):
        self.binary.write_text(self.binary.read_text() + "# stale executable\n")
        self.run_without_launch("BUILD_BINARY_SHA_MISMATCH")

    def test_source_drift_fails_before_any_launch(self):
        for name in ("src/lib.rs", "Cargo.lock", "python/source_bound_interval.py"):
            path = self.crate / name
            original = path.read_bytes()
            with self.subTest(source=name):
                path.write_bytes(original + b" changed")
                self.run_without_launch("BUILD_SOURCE_SHA_MISMATCH")
            path.write_bytes(original)

    def test_added_consumed_source_fails_before_any_launch(self):
        (self.crate / "src/new.rs").write_text("new source")
        self.run_without_launch("BUILD_SOURCE_SHA_MISMATCH")

    def test_positive_gate_only_does_not_launch(self):
        self.run_without_launch()

    def test_native_constructor_cannot_skip_receipt(self):
        with patch.object(production, "CRATE", self.crate), \
                patch.object(production.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(ValueError, "BUILD_RECEIPT_REQUIRED"):
                production.NativeConsumer(self.binary, {})
            popen.assert_not_called()

    def test_dirty_source_is_rejected_before_build(self):
        with patch.object(build, "_git", side_effect=[str(self.root), " M source"]), \
                patch.object(build, "_command") as command:
            with self.assertRaisesRegex(ValueError, "CLEAN_BUILD_REQUIRES_CLEAN_COMMITTED_REVISION"):
                build.build_receipt(self.crate, self.root / "output")
            command.assert_not_called()
            self.assertFalse((self.root / "output").exists())

    def test_failed_or_incomplete_receipt_is_rejected(self):
        self.data["build"]["exit_code"] = 101
        self.receipt.write_text(json.dumps(self.data))
        self.run_without_launch("BUILD_RECEIPT_NOT_PASS")


if __name__ == "__main__":
    unittest.main()
