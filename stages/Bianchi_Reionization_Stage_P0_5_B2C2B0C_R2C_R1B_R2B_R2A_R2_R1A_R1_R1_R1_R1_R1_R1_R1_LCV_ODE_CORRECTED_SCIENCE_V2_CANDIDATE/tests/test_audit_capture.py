from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest


STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
TOOLS = STAGE / "tools"
sys.path.insert(0, str(TOOLS))

try:
    import capture_audit_run as audit
except ModuleNotFoundError:
    audit = None


PYTHON = Path(sys.executable).resolve()
PUBLIC_ENVIRONMENT_NAMES = {
    "LANG",
    "LC_ALL",
    "TZ",
    "PYTHONHASHSEED",
    "PYTHONNOUSERSITE",
    "BLIS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "PATH",
    "VECLIB_MAXIMUM_THREADS",
    "XLA_FLAGS",
    "TMPDIR",
}


class AuditCaptureTests(unittest.TestCase):
    def require_module(self):
        self.assertIsNotNone(audit, "capture_audit_run.py is not implemented")
        return audit

    def test_exact_binary_streams_command_runtime_and_git_are_manifested(self) -> None:
        module = self.require_module()
        stdout = b"A\x00B\n"
        stderr = b"audit-stderr\n"
        script = (
            "import sys;"
            f"sys.stdout.buffer.write({stdout!r});sys.stdout.buffer.flush();"
            f"sys.stderr.buffer.write({stderr!r});sys.stderr.buffer.flush()"
        )
        command = (str(PYTHON), "-c", script)
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "audit"
            result = module.capture_audit_run(
                command=command,
                cwd=REPO,
                output_dir=output,
                timeout_seconds=5.0,
                max_stdout_bytes=1024,
                max_stderr_bytes=1024,
            )
            self.assertEqual((output / "stdout.bin").read_bytes(), stdout)
            self.assertEqual((output / "stderr.bin").read_bytes(), stderr)
            manifest = json.loads((output / "manifest.json").read_text("utf-8"))
            self.assertEqual(manifest, result.manifest)
            self.assertEqual(manifest["classification"], "TEST_ONLY_NOT_SCIENCE")
            self.assertEqual(manifest["command"]["argv"], list(command))
            self.assertFalse(manifest["command"]["shell"])
            self.assertEqual(manifest["command"]["cwd"], str(REPO.resolve()))
            self.assertEqual(
                manifest["command"]["executable"]["resolved"], str(PYTHON)
            )
            self.assertEqual(manifest["process"]["returncode"], 0)
            self.assertIsNone(manifest["process"]["signal"])
            self.assertFalse(manifest["process"]["timed_out"])
            self.assertGreaterEqual(manifest["time"]["duration_monotonic_ns"], 0)
            self.assertEqual(
                manifest["stdout"]["sha256"], hashlib.sha256(stdout).hexdigest()
            )
            self.assertEqual(manifest["stdout"]["size_bytes"], len(stdout))
            self.assertEqual(
                manifest["stderr"]["sha256"], hashlib.sha256(stderr).hexdigest()
            )
            self.assertEqual(
                set(manifest["environment"]["values"]), PUBLIC_ENVIRONMENT_NAMES
            )
            self.assertEqual(manifest["environment"]["explicit_import_roots"], [])
            self.assertNotIn("HOME", manifest["environment"]["values"])
            self.assertEqual(manifest["environment"]["values"]["PATH"], "/usr/bin")
            self.assertEqual(len(manifest["git"]["head"]), 40)
            self.assertEqual(len(manifest["git"]["tree"]), 40)
            self.assertRegex(manifest["git"]["status_sha256"], r"^[0-9a-f]{64}$")
            manifest_bytes = (output / "manifest.json").read_bytes()
            expected_sha = hashlib.sha256(manifest_bytes).hexdigest()
            self.assertEqual(result.manifest_sha256, expected_sha)
            self.assertEqual(
                (output / "manifest.json.sha256").read_text("ascii"),
                f"{expected_sha}  manifest.json\n",
            )

    def test_secret_like_argv_is_rejected_before_launch(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            marker = root / "launched"
            script = f"from pathlib import Path;Path({str(marker)!r}).write_text('bad')"
            output = root / "audit"
            with self.assertRaises(module.AuditPolicyError):
                module.capture_audit_run(
                    command=(str(PYTHON), "-c", script, "--token=super-secret"),
                    cwd=REPO,
                    output_dir=output,
                    timeout_seconds=5.0,
                    max_stdout_bytes=1024,
                    max_stderr_bytes=1024,
                )
            self.assertFalse(marker.exists())
            self.assertFalse(output.exists())

    def test_explicit_import_root_is_resolved_and_manifested(self) -> None:
        module = self.require_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            import_root = root / "imports"
            import_root.mkdir()
            (import_root / "audit_probe_module.py").write_text(
                "VALUE = 'EXPLICIT_IMPORT_OK'\n", encoding="ascii"
            )
            output = root / "audit"
            result = module.capture_audit_run(
                command=(
                    str(PYTHON),
                    "-c",
                    "import audit_probe_module;print(audit_probe_module.VALUE)",
                ),
                cwd=REPO,
                output_dir=output,
                timeout_seconds=5.0,
                max_stdout_bytes=1024,
                max_stderr_bytes=1024,
                pythonpath_roots=(import_root,),
            )
            self.assertEqual((output / "stdout.bin").read_bytes(), b"EXPLICIT_IMPORT_OK\n")
            environment = result.manifest["environment"]
            self.assertEqual(environment["values"]["PYTHONPATH"], str(import_root))
            identity = environment["explicit_import_roots"]
            self.assertEqual(len(identity), 1)
            self.assertEqual(identity[0]["path"], str(import_root))
            self.assertEqual(
                identity[0]["scope"],
                "PATH_AND_DIRECT_LISTING_IDENTITY_NOT_CONTENT_SEAL",
            )

    def test_stdout_hard_cap_hashes_the_exact_captured_prefix(self) -> None:
        module = self.require_module()
        payload = b"x" * 4096
        script = (
            "import sys;"
            f"sys.stdout.buffer.write({payload!r});sys.stdout.buffer.flush()"
        )
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "audit"
            result = module.capture_audit_run(
                command=(str(PYTHON), "-c", script),
                cwd=REPO,
                output_dir=output,
                timeout_seconds=5.0,
                max_stdout_bytes=128,
                max_stderr_bytes=128,
            )
            captured = b"x" * 128
            self.assertEqual((output / "stdout.bin").read_bytes(), captured)
            self.assertEqual(result.manifest["stdout"]["size_bytes"], 128)
            self.assertEqual(
                result.manifest["stdout"]["sha256"],
                hashlib.sha256(captured).hexdigest(),
            )
            self.assertTrue(result.manifest["stdout"]["capped"])
            self.assertEqual(result.manifest["process"]["termination"], "OUTPUT_LIMIT")

    def test_timeout_preserves_and_hashes_partial_output(self) -> None:
        module = self.require_module()
        partial = b"partial-before-timeout\n"
        script = (
            "import sys,time;"
            f"sys.stdout.buffer.write({partial!r});sys.stdout.buffer.flush();"
            "time.sleep(2)"
        )
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "audit"
            started = time.monotonic()
            result = module.capture_audit_run(
                command=(str(PYTHON), "-c", script),
                cwd=REPO,
                output_dir=output,
                timeout_seconds=0.4,
                max_stdout_bytes=1024,
                max_stderr_bytes=1024,
            )
            elapsed = time.monotonic() - started
            self.assertLess(elapsed, 1.8)
            self.assertEqual((output / "stdout.bin").read_bytes(), partial)
            self.assertTrue(result.manifest["process"]["timed_out"])
            self.assertEqual(result.manifest["process"]["termination"], "TIMEOUT")
            self.assertEqual(
                result.manifest["stdout"]["sha256"],
                hashlib.sha256(partial).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
