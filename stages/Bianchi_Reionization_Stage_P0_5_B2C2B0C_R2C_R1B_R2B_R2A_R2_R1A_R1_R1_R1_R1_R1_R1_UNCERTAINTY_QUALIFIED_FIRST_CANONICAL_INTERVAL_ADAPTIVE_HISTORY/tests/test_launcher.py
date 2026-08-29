import os
from pathlib import Path
import subprocess
import tempfile
import unittest


STAGE = Path(__file__).resolve().parents[1]
LAUNCHER = STAGE / "scripts" / "run_local_first_interval.sh"


class Tests(unittest.TestCase):
    def environment(self, root: Path) -> dict[str, str]:
        binary = root / "bin"
        binary.mkdir()
        fake = binary / "python"
        fake.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [[ $1 == *preflight.py ]]; then\n"
            "  shift\n"
            "  [[ $1 == --output ]]\n"
            "  printf 'replacement-preflight\\n' > \"$2\"\n"
            "fi\n"
        )
        fake.chmod(0o755)
        environment = os.environ.copy()
        environment["PATH"] = f"{binary}:{environment['PATH']}"
        return environment

    def test_foreign_owned_directory_is_not_modified_before_validation(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run = root / "run"
            run.mkdir()
            (run / "RUN_OWNER.json").write_text("{}\n")
            preflight = run / "preflight.json"
            preflight.write_text("preserve-foreign-preflight\n")
            subprocess.run(
                [str(LAUNCHER), str(run), "--resume"],
                env=self.environment(root),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(preflight.read_text(), "preserve-foreign-preflight\n")

    def test_controller_identity_options_cannot_be_injected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run = root / "run"
            other = root / "other"
            result = subprocess.run(
                [str(LAUNCHER), str(run), "--run-dir", str(other)],
                env=self.environment(root),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(other.exists())

    def test_pre_owner_crash_reuses_only_an_identical_preflight(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            run = root / "run"
            run.mkdir()
            lock = run / ".RUN.lock"
            lock.write_text("")
            preflight = run / "preflight.json"
            preflight.write_text("replacement-preflight\n")
            result = subprocess.run(
                [str(LAUNCHER), str(run), "--max-accepted", "1"],
                env=self.environment(root),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(preflight.read_text(), "replacement-preflight\n")
            self.assertTrue(lock.is_file())


if __name__ == "__main__":
    unittest.main()
