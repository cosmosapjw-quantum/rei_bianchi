"""Additive CLI contract, including detached output observation invariance.

Run with a built example in IGM_ADAPTIVE_EXE. With that variable unset, the
integration tests skip so the existing dependency-free Python suite stays usable.
For a recorded RED run set it to the legacy igm_continuous executable.
"""
import csv
import json
import hashlib
import struct
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EXE = os.environ.get("IGM_ADAPTIVE_EXE")


@unittest.skipUnless(EXE, "set IGM_ADAPTIVE_EXE to the built igm_adaptive example")
class AdaptiveCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="igm-adaptive-cli-")
        self.root = Path(self.tmp.name)
        config = (ROOT / "configs/igm_manufactured_v1.cfg").read_text()
        self.config_text = config.replace("z_end=11.5", "z_end=11.98")
        self.config = self.root / "short.cfg"
        self.config.write_text(self.config_text)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, name, panels=20, extra=(), config=None, spectral_panels=2, output_times=None):
        output = self.root / name
        args = [EXE, "--config", str(config or self.config), "--output", str(output),
                "--spectral-panels", str(spectral_panels), "--rtol", "0.001", "--atol-scale", "1"]
        args += (["--output-times", str(output_times)] if output_times is not None
                 else ["--output-panels", str(panels)])
        result = subprocess.run(args + list(extra), text=True, capture_output=True, timeout=90)
        return result, output

    @staticmethod
    def read_rows(output, filename="history.csv"):
        with (output / filename).open(newline="") as f:
            return list(csv.DictReader(f))

    def test_adaptive_flags_and_manifest_are_explicit(self):
        result, output = self.run_cli("manifest")
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads((output / "status.json").read_text())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertTrue(status["complete"])
        self.assertEqual(manifest["schema"], "igm_adaptive_manifest_v1")
        self.assertEqual(manifest["microstep_policy"], "strict")
        self.assertEqual(manifest["tolerances"]["relative"], 0.001)
        for family in ("fraction_atol", "temperature_atol", "energy_atol", "count_atol", "gamma_atol", "heat_atol"):
            self.assertTrue(math.isfinite(manifest["tolerances"][family]))
            self.assertGreater(manifest["tolerances"][family], 0)
        for key in ("config_sha256", "effective_config_sha256", "source_sha256"):
            self.assertRegex(manifest[key], r"^[a-f0-9]{64}$")
        self.assertEqual(manifest["config_sha256"], hashlib.sha256(self.config.read_bytes()).hexdigest())
        self.assertEqual(manifest["effective_config_sha256"],
                         hashlib.sha256((output / "effective_config_identity.txt").read_bytes()).hexdigest())
        self.assertIn("unestimated", manifest["microstep_exception"])
        self.assertEqual(status["primary"]["guarded_microsteps"], 0)
        self.assertFalse(status["primary"]["last_was_guarded"])
        self.assertEqual(status["primary"]["microsteps"], [])
        self.assertGreater(manifest["controller"]["max_trial_evaluations"], 0)
        self.assertGreater(status["observation"]["samples"], 0)

    def test_output_grid_cannot_change_primary_or_common_rows(self):
        result20, output20 = self.run_cli("rows21", panels=20)
        result80, output80 = self.run_cli("rows81", panels=80)
        self.assertEqual(result20.returncode, 0, result20.stderr)
        self.assertEqual(result80.returncode, 0, result80.stderr)
        rows21, rows81 = self.read_rows(output20), self.read_rows(output80)
        self.assertEqual(len(rows21), 21)
        self.assertEqual(len(rows81), 81)
        # Exact string equality is stronger than f64 equality and captures every
        # physical and deterministic primary diagnostic CSV column.
        self.assertEqual(rows21, rows81[::4])
        for filename in ("primary_state.csv", "nodes_final.csv"):
            self.assertEqual((output20 / filename).read_bytes(), (output80 / filename).read_bytes())
        status20 = json.loads((output20 / "status.json").read_text())
        status80 = json.loads((output80 / "status.json").read_text())
        self.assertEqual(status20["primary"], status80["primary"])
        self.assertGreater(status80["observation"]["samples"], status20["observation"]["samples"])
        self.assertGreater(status80["observation"]["trial_evaluations"], status20["observation"]["trial_evaluations"])
        self.assertEqual(rows21[-1], self.read_rows(output20, "primary_state.csv")[0])

    def test_failure_reports_last_accepted_primary(self):
        config = self.root / "limited.cfg"
        config.write_text(self.config_text.replace("max_steps=200000", "max_steps=2"))
        result, output = self.run_cli("limited", config=config)
        self.assertNotEqual(result.returncode, 0)
        status = json.loads((output / "status.json").read_text())
        self.assertFalse(status["complete"])
        self.assertEqual(status["failure_scope"], "primary")
        self.assertTrue(status["error"])
        self.assertIsNotNone(status["failed_attempt"])
        primary = self.read_rows(output, "primary_state.csv")[0]
        self.assertEqual(float(primary["ln_a"]), status["primary"]["ln_a"])
        self.assertLess(float(primary["ln_a"]), -math.log1p(11.98))
        self.assertEqual(int(primary["accepted_steps"]), status["primary"]["accepted_steps"])
        self.assertTrue((output / "nodes_final.csv").is_file())

    def test_unrepresentable_sample_is_a_visible_observation_failure(self):
        config = self.root / "tiny.cfg"
        config.write_text(self.config_text.replace("z_end=11.98", "z_end=11.9999999999999")
                          .replace("max_dln_a=0.0002", "max_dln_a=5e-15")
                          .replace("min_dln_a=1e-12", "min_dln_a=1e-20")
                          .replace("source_rate=1e-15", "source_rate=0")
                          .replace("x_hii=2e-4", "x_hii=0"))
        for panels, error in [(100, "IGM_ADAPTIVE_OUTPUT_NO_REPRESENTABLE_PROGRESS"),
                              (20, "ADAPTIVE_UNSPLITTABLE_EVENT")]:
            with self.subTest(panels=panels):
                result, output = self.run_cli(f"tiny-{panels}", panels=panels, config=config)
                self.assertNotEqual(result.returncode, 0)
                status = json.loads((output / "status.json").read_text())
                self.assertFalse(status["complete"])
                self.assertEqual(status["failure_scope"], "observation")
                self.assertEqual(status["error"], error)
                self.assertGreater(status["primary"]["ln_a"], -math.log1p(12.0))
                self.assertEqual(float(self.read_rows(output, "primary_state.csv")[0]["ln_a"]),
                                 status["primary"]["ln_a"])
                if panels == 20:
                    self.assertIsNotNone(status["failed_attempt"])
                    self.assertEqual(status["observation"]["samples"], 1)

    def test_guarded_research_is_an_explicit_opt_in(self):
        result, output = self.run_cli("guarded", extra=("--microstep-policy", "guarded-research"))
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["microstep_policy"], "guarded-research")

    def test_event_microsteps_keep_explicit_guard_evidence(self):
        config = self.root / "neutral.cfg"
        config.write_text((ROOT / "configs/igm_manufactured_v1.cfg").read_text()
                          .replace("source_rate=1e-15", "source_rate=0")
                          .replace("x_hii=2e-4", "x_hii=0"))
        base = ("--spectral-grid", "threshold-bands")
        strict, strict_output = self.run_cli("neutral-strict", panels=1, config=config,
                                            spectral_panels=1, extra=base)
        self.assertNotEqual(strict.returncode, 0)
        status = json.loads((strict_output / "status.json").read_text())
        self.assertEqual(status["error"], "ADAPTIVE_UNSPLITTABLE_EVENT")
        guarded, guarded_output = self.run_cli("neutral-guarded", panels=1, config=config,
                                              spectral_panels=1,
                                              extra=base + ("--microstep-policy", "guarded-research"))
        self.assertEqual(guarded.returncode, 0, guarded.stderr)
        status = json.loads((guarded_output / "status.json").read_text())
        records = status["primary"]["microsteps"]
        self.assertGreater(len(records), 0)
        self.assertEqual(len(records), status["primary"]["guarded_microsteps"])
        self.assertEqual(status["observation"]["guarded_microsteps"], 0)
        for record in records:
            for endpoint in ("start", "end"):
                bits = struct.unpack(">Q", struct.pack(">d", record[endpoint]))[0]
                self.assertEqual(record[endpoint + "_bits"], f"{bits:016x}")
            self.assertGreater(record["proper_dt"], 0)
            self.assertLessEqual(record["max_motion_ratio"], 1)
            self.assertTrue(record["post_event_rate_guard"])
            self.assertEqual(len(record["fraction_equation_defect"]), 3)
            self.assertTrue(math.isfinite(record["energy_equation_defect"]))
            self.assertGreater(len(record["field_motion"]), 0)
            for field in record["field_motion"]:
                self.assertTrue(field["name"])
                self.assertGreaterEqual(field["bound"], 0)
                self.assertLessEqual(field["ratio"], 1)

    def test_explicit_nonuniform_schedule_preserves_primary_and_common_rows(self):
        regular, regular_output = self.run_cli("regular-schedule")
        self.assertEqual(regular.returncode, 0, regular.stderr)
        regular_rows = self.read_rows(regular_output)
        start, end = float(regular_rows[0]["ln_a"]), float(regular_rows[-1]["ln_a"])
        times = [start, float(regular_rows[3]["ln_a"]), start + (end-start)*0.271,
                 float(regular_rows[7]["ln_a"]), float(regular_rows[13]["ln_a"]), end]
        file = self.root / "times.txt"
        file.write_text("\n".join(repr(t) for t in times) + "\n")
        explicit, output = self.run_cli("explicit-schedule", output_times=file)
        self.assertEqual(explicit.returncode, 0, explicit.stderr)
        rows = self.read_rows(output)
        self.assertEqual(len(rows), len(times))
        self.assertEqual([float(row["ln_a"]) for row in rows], times)
        self.assertEqual([rows[i] for i in [0, 1, 3, 4, 5]],
                         [regular_rows[i] for i in [0, 3, 7, 13, 20]])
        status = json.loads((output / "status.json").read_text())
        regular_status = json.loads((regular_output / "status.json").read_text())
        self.assertEqual(status["primary"], regular_status["primary"])
        for filename in ("primary_state.csv", "nodes_final.csv"):
            self.assertEqual((output / filename).read_bytes(), (regular_output / filename).read_bytes())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["output_schedule"], "explicit")
        self.assertEqual(manifest["output_time_count"], len(times))
        self.assertEqual((output / "output_times.txt").read_bytes(), file.read_bytes())
        self.assertEqual(manifest["output_times_sha256"], hashlib.sha256(file.read_bytes()).hexdigest())
        self.assertEqual(manifest["source_sha256"], json.loads((regular_output / "manifest.json").read_text())["source_sha256"])

    def test_explicit_times_accepts_literal_csv_header(self):
        config = self.root / "neutral-short.cfg"
        config.write_text(self.config_text.replace("source_rate=1e-15", "source_rate=0")
                          .replace("x_hii=2e-4", "x_hii=0"))
        file = self.root / "header-times.csv"
        file.write_text(f"ln_a\n{-math.log1p(12.0)}\n{-math.log1p(11.98)}\n")
        result, output = self.run_cli("header-times", output_times=file, config=config)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.read_rows(output)), 2)
        self.assertEqual((output / "output_times.txt").read_bytes(), file.read_bytes())
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(manifest["output_times_sha256"], hashlib.sha256(file.read_bytes()).hexdigest())

    def test_explicit_schedule_rejects_bad_epochs_before_output_creation(self):
        start, end = -math.log1p(12.0), -math.log1p(11.98)
        for index, epochs in enumerate([
                [start], [start, start, end], [start, end, start],
                [math.nextafter(start, math.inf), end], [start, math.nextafter(end, -math.inf)],
                [start, math.nan, end], [start, math.inf, end], [start, end+0.1],
                [start, (start+end)/2, start+0.1, end]]):
            with self.subTest(epochs=epochs):
                file = self.root / f"bad-times-{index}.txt"
                file.write_text("\n".join(repr(t) for t in epochs))
                result, output = self.run_cli(f"bad-schedule-{index}", output_times=file)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
        file = self.root / "valid-times.txt"
        file.write_text(f"{start}\n{end}\n")
        result, output = self.run_cli("both-schedules", extra=("--output-times", str(file)))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_invalid_options_do_not_create_run(self):
        cases = [("--microstep-policy", "silent"), ("--spectral-grid", "wrong"),
                 ("--unknown", "1"), ("--rtol", "1"), ("--output-panels", "3"),
                 ("--max-dln-a", "nan"), ("--max-dln-a", "0")]
        for index, extra in enumerate(cases):
            with self.subTest(extra=extra):
                result, output = self.run_cli(f"invalid-{index}", extra=extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
        for option, value in [("--rtol", "0"), ("--rtol", "nan"),
                              ("--atol-scale", "-1"), ("--atol-scale", "inf")]:
            with self.subTest(option=option, value=value):
                output = self.root / f"bad-{option}-{value}"
                result = subprocess.run([EXE, "--config", str(self.config), "--output", str(output),
                                         "--spectral-panels", "2", option, value],
                                        text=True, capture_output=True, timeout=90)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
