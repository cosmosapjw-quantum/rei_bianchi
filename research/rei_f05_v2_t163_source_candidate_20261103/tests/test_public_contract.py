import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PublicCandidateContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((ROOT / "results/PUBLIC_CANDIDATE.json").read_text())
        cls.provenance = json.loads((ROOT / "evidence/PROVENANCE.json").read_text())

    def test_candidate_is_not_acceptance_or_production(self):
        self.assertEqual(self.result["candidate_tick"], 163)
        self.assertEqual(self.result["official_V1_accepted_tick"], 160)
        self.assertFalse(self.result["candidate_tick_accepted"])
        self.assertFalse(self.result["production_control_installed"])
        self.assertFalse(self.result["continuum_ode_error_certified"])
        self.assertFalse(self.result["automatic_tick164"])

    def test_original_source_identity_is_pinned(self):
        self.assertEqual(self.provenance["runtime_bound_git_commit"], "a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78")
        self.assertEqual(self.provenance["full_runtime_sha256"], "97b00826f518aa7a2c258dae15d1e92918b44a04b6f928e2014241bbba2f0075")
        self.assertEqual(self.provenance["original_source_tar_sha256"], "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b")
        self.assertEqual(self.provenance["original_kernel_sha256"], "579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644")

    def test_fixed_source_discrete_gates_and_lane_identity(self):
        self.assertLess(self.result["maximum_source_discrete_local_estimator"], 2e-4)
        self.assertLess(self.result["maximum_public_width"], 2e-3)
        self.assertEqual(self.result["native_original_maps"], 9)
        self.assertEqual(self.result["lanes"], 3)
        self.assertEqual(self.result["same_physical_body_across_lanes"], True)
        self.assertEqual(self.result["native_ledgers_per_lane"], 14)
        self.assertEqual(self.result["original_table_events"], 0)

    def test_archive_builder_is_deterministic_and_refuses_overwrite(self):
        builder = ROOT / "scripts/build_archive.py"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            public = root / "public"
            private = root / "private"
            public.mkdir(); private.mkdir()
            (public / "report.txt").write_text("fixed report\n")
            (private / "state.npz").write_bytes(b"immutable-state-bytes")
            a = root / "a.zip"; b = root / "b.zip"
            common = [sys.executable, str(builder), "--public-root", str(public),
                      "--private-root", str(private), "--source-commit",
                      "a2a3ff5d77e6f3b96275b8787f3b4b109c7bbd78"]
            subprocess.run(common + ["--output", str(a)], check=True, capture_output=True)
            subprocess.run(common + ["--output", str(b)], check=True, capture_output=True)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            overwrite = subprocess.run(common + ["--output", str(a)], capture_output=True)
            self.assertNotEqual(overwrite.returncode, 0)

if __name__ == "__main__":
    unittest.main()
