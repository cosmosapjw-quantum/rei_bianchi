from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import contextlib
import io
import tempfile
import unittest


RUNNER_PATH = Path(__file__).with_name("runtime_bridge_runner.py")


def _load_runner():
    spec = importlib.util.spec_from_file_location("rei_runtime_bridge_runner_test", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeBridgeRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = _load_runner()

    def test_manifest_is_closed_and_hashes_every_package_file(self) -> None:
        self.runner.verify_manifest()

    def test_section0_receipt_requires_exact_bytes_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "section0.json"
            path.write_text(
                json.dumps({"status": "PASS_IMMUTABLE_SECTION_0"}), encoding="utf-8"
            )
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            observed = self.runner.load_section_0_receipt(
                path, digest, "PASS_IMMUTABLE_SECTION_0"
            )
            self.assertEqual(observed["status"], "PASS_IMMUTABLE_SECTION_0")
            with self.assertRaisesRegex(self.runner.HandoffError, "IDENTITY_MISMATCH"):
                self.runner.load_section_0_receipt(path, "0" * 64, "PASS_IMMUTABLE_SECTION_0")
            with self.assertRaisesRegex(self.runner.HandoffError, "STATUS_MISMATCH"):
                self.runner.load_section_0_receipt(path, digest, "OTHER")

    def test_contract_preserves_the_explicit_process_boundary_residual(self) -> None:
        contract = self.runner.load_contract()
        self.assertEqual(
            contract["residual_blockers"]["process_boundary"],
            "RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING",
        )
        self.assertEqual(
            contract["residual_blockers"]["prestart_runtime"],
            "BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED",
        )
        self.assertEqual(contract["rust_backend"]["rounding_policy"], "MPFR_RNDD_RNDU")
        self.assertEqual(contract["claim_ceiling"]["adapter"], "STOP_INVALID")

    def test_unexpected_runtime_error_is_still_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stderr(
            io.StringIO()
        ) as captured:
            status = self.runner.main(
                [
                    "--repo",
                    str(Path(temporary) / "missing-repo"),
                    "--section0-receipt",
                    str(Path(temporary) / "missing-receipt.json"),
                    "--evidence-root",
                    str(Path(temporary) / "evidence"),
                ]
            )
        self.assertEqual(status, 65)
        self.assertIn("STOP_INVALID", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
