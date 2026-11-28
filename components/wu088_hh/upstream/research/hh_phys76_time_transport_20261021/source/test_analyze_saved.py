"""Manufactured stitching and input-identity tests; no real trajectory run."""
from pathlib import Path
import csv
import hashlib
import json
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from analyze_saved import (LANES, TAIL_SCOPE, analyze, canonical_sha256,
                           load_old, load_tail, sha256, stitch_segments,
                           validate_tail_identity)
from cumulative_memory import cumulative_memory_budget


def values(x, offset=0.0):
    H = np.exp(-3.0 * x)
    Pm, Pr = 2.0 * x + 1.0, -0.5 * x
    S = 0.2 + 0.75 * x**2 + x + offset
    return np.stack((H, S, Pm, Pr))[None, :, :]


def write_npz(path, x, v, **extra):
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, x=x, zbar=21.0 * np.exp(-x) - 1.0,
                        H_per_s=v[0], s_over_H=v[1] / np.sqrt(3.0),
                        signed_Pi_m=v[2], signed_Pi_r=v[3], **extra)


class SavedAnalysisTests(unittest.TestCase):
    def test_distinct_uniform_segments_and_propagated_old_defect(self):
        x = np.linspace(0.0, 1.0, 5)
        t = np.linspace(1.0, 1.6, 5)
        old, tail = values(x), values(t, offset=0.01)
        old[:, 1, -1] += 0.01
        xx, vv, result, budget = stitch_segments(x, old, t, tail)
        self.assertEqual(len(xx), 9)
        assert_array_equal(vv[:, :, :5], old)
        assert_allclose(budget["transport_factor"], 1.0, atol=3e-15)
        assert_allclose(budget["local_closure_defect"], 0.0, atol=3e-15)
        assert_allclose(budget["transported_old_closure_defect"], 0.01, atol=3e-15)
        assert_allclose(result["closure_defect"][:, 4:], 0.01, atol=3e-15)
        assert_allclose(budget["stitch_identity_defect"], 0.0, atol=3e-15)
        with self.assertRaisesRegex(ValueError, "UNIFORM"):
            cumulative_memory_budget(xx, *[vv[:, k] for k in range(4)])

    def test_even_length_segment_and_boundary_mismatch_rejected(self):
        x = np.linspace(0.0, 1.0, 5)
        t = np.linspace(1.0, 1.6, 4)
        with self.assertRaisesRegex(ValueError, "ODD"):
            stitch_segments(x, values(x), t, values(t))
        t = np.linspace(1.0, 1.6, 5)
        bad = values(t)
        bad[:, 2, 0] += 1e-6
        with self.assertRaisesRegex(ValueError, "OBSERVED_BOUNDARY"):
            stitch_segments(x, values(x), t, bad)
        with self.assertRaisesRegex(ValueError, "COORDINATE_BOUNDARY"):
            stitch_segments(x, values(x), t + 0.001, values(t))

    def test_explicit_identity_binding_rejects_stale_or_relabelled_tail(self):
        old = {"case_id": "case", "source_lane": "radiation_slice", "source_sha256": "a" * 64}
        valid = {"status": "COMPLETED", "case_id": "case", "source_lane": "radiation_slice",
                 "old_source_sha256": "a" * 64, "identity": {"model_sha256": "b" * 64}}
        validate_tail_identity(valid, old)
        for key, value in (("case_id", "other"), ("old_source_sha256", "c" * 64),
                           ("source_lane", "warm"), ("identity", {}), ("status", "PENDING")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_tail_identity({**valid, key: value}, old)

    def _fixture(self, base, native=False):
        x = np.linspace(0.0, np.log(21.0 / 5.0), 5)
        for i, (lane, relative) in enumerate(LANES):
            path = base / relative / ("synthetic_" + str(i) + ".npz")
            state = np.arange(8 * len(x), dtype=np.float64).reshape(8, len(x)) / 100.0
            write_npz(path, x, values(x)[0], **({"state": state} if native and i == 1 else {}))
            with (path.parent.parent / "endpoints.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["id", "lane"])
                writer.writeheader()
                writer.writerow({"id": path.stem, "lane": "RADIATION_SLICE" if i == 0 else "MATTER_SLICE"})
            if native:
                raw_path = (base / "results/pilot/cases" / path.name if i == 0 else path)
                if i == 0:
                    write_npz(raw_path, x, values(x)[0], state=state)
                raw_path.with_suffix(".json").write_text(json.dumps(
                    {"status": "COMPLETED", "case": {"id": path.stem}, "identity": {"fixture": True}}))
        return x

    def _native_fixture(self, base):
        self._fixture(base / "old", native=True)
        x, _, old_values, records = load_old(base / "old", (1, 1))
        t = np.linspace(x[-1], np.log(7.0), 33)
        owner_file = base / "old/manufactured_owner.py"
        owner_file.write_text("# Manufactured data only; this source is not executed.\n")
        run = {"schema": "PHYS76_NEW_TAIL_IDENTITY_V1", "scope": TAIL_SCOPE,
               "target_z": 2.0, "target_x": float(t[-1]), "tail_samples_including_restart": 33,
               "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
               "runner_sha256": sha256(Path(__file__).with_name("continue_saved.py")),
               "owner_files": {owner_file.name: sha256(owner_file)},
               "solver": {"method": "manufactured_no_solver"}}
        (base / "tail").mkdir()
        (base / "tail/run_identity.json").write_text(json.dumps(run, indent=2))
        for j, record in enumerate(records):
            radiation = record["source_lane"] == "radiation_slice"
            cid = record["case_id"]
            raw_relative = "results/pilot/cases/" + cid + ".npz" if radiation else record["source_path"]
            raw_path = base / "old" / raw_relative
            with np.load(raw_path, allow_pickle=False) as archive:
                state = archive["state"]
            restart_hash = hashlib.sha256(np.asarray(state[:, -1], dtype="<f8").tobytes(order="C")).hexdigest()
            source = {"npz_path": record["source_path"], "npz_sha256": record["source_sha256"],
                      "kind": "IMMUTABLE_COMPONENT_DECOMPOSITION_OF_RAW_TRAJECTORY" if radiation else "RAW_COMPONENT_TRAJECTORY"}
            identity = {"run_identity_sha256": canonical_sha256(run), "case_id": cid,
                        "group": "radiation625" if radiation else "matter600_mixed6",
                        "lane": "RADIATION_SLICE" if radiation else "MATTER_SLICE",
                        "npz_sha256": sha256(raw_path), "receipt_sha256": sha256(raw_path.with_suffix(".json")),
                        "restart_diagnostics_source": source, "restart_state_sha256": restart_hash,
                        "x_start": float(x[-1]), "target_z": 2.0, "target_x": float(t[-1]),
                        "solver": run["solver"], "tail_samples_including_restart": 33}
            identity_hash = canonical_sha256(identity)
            path = base / "tail/cases" / cid / "history.npz"
            v = values(t)[0]
            v[:, 0] = old_values[j, :, -1]
            write_npz(path, t, v, state=np.repeat(state[:, -1, None], 33, axis=1),
                      identity_sha256=np.array(identity_hash), scope=np.array(TAIL_SCOPE))
            boundary = {"status": "BIT_IDENTICAL_TO_SAVED_DIAGNOSTICS", "checked_fields": 6,
                        "source": source, "recomputation_max_abs_difference": 0.0}
            receipt = {"schema": "PHYS76_TAIL_CASE_RECEIPT_V1", "status": "COMPLETED",
                       "identity": identity, "identity_sha256": identity_hash, "history_sha256": sha256(path),
                       "scope": TAIL_SCOPE, "case": {"id": cid}, "new_tail_only": True,
                       "old_trajectories_rerun": 0, "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
                       "restart_boundary_before_solver": boundary, "restart_boundary_after_solver": boundary}
            path.with_name("COMPLETED.json").write_text(json.dumps(receipt))
        return records

    def test_native_runner_layout_binds_diagnostics_and_raw_restart_separately(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            records = self._native_fixture(base)
            x, z, data, receipts = load_tail(base / "tail", records, base / "old")
            self.assertEqual(data.shape, (2, 4, 33))
            self.assertAlmostEqual(z[-1], 2.0)
            radiation = receipts[0]["native_binding"]
            self.assertNotEqual(radiation["original_raw_restart"]["npz_sha256"],
                                radiation["restart_diagnostics_source"]["npz_sha256"])
            matter = receipts[1]["native_binding"]
            self.assertEqual(matter["original_raw_restart"]["npz_sha256"],
                             matter["restart_diagnostics_source"]["npz_sha256"])
            summary = analyze(base / "old", base / "analysis", base / "tail", (1, 1))
            self.assertTrue(summary["coverage_target_z2_complete"])
            self.assertEqual(summary["display_samples_per_case"], 37)
            self.assertEqual(summary["new_ode_integrations_by_this_analysis"], 0)

    def test_native_identity_chain_and_boundary_binding_reject_mutations(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            records = self._native_fixture(base)
            path = base / "tail/cases" / records[0]["case_id"] / "COMPLETED.json"
            original = json.loads(path.read_text())
            mutations = (("run_identity_sha256", "0" * 64, "RUN_IDENTITY_HASH"),
                         ("npz_sha256", "0" * 64, "ORIGINAL_RAW_RESTART_HASH"),
                         ("restart_diagnostics_source", {}, "RESTART_DIAGNOSTIC_IDENTITY"))
            for key, value, message in mutations:
                with self.subTest(key=key):
                    receipt = json.loads(json.dumps(original))
                    receipt["identity"][key] = value
                    receipt["identity_sha256"] = canonical_sha256(receipt["identity"])
                    path.write_text(json.dumps(receipt))
                    with self.assertRaisesRegex(ValueError, message):
                        load_tail(base / "tail", records, base / "old")
            receipt = json.loads(json.dumps(original))
            receipt["restart_boundary_after_solver"]["source"] = {}
            path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "RESTART_BOUNDARY_RECEIPT"):
                load_tail(base / "tail", records, base / "old")
            path.write_text(json.dumps(original))
            history_path = path.with_name("history.npz")
            with np.load(history_path, allow_pickle=False) as archive:
                fields = {name: archive[name].copy() for name in archive.files}
            fields["identity_sha256"] = np.array("0" * 64)
            np.savez_compressed(history_path, **fields)
            original["history_sha256"] = sha256(history_path)
            path.write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError, "EMBEDDED_IDENTITY_HASH"):
                load_tail(base / "tail", records, base / "old")

    def test_no_tail_packet_reports_actual_z4_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self._fixture(base / "old")
            summary = analyze(base / "old", base / "analysis", expected_counts=(1, 1))
            self.assertFalse(summary["coverage_target_z2_complete"])
            self.assertAlmostEqual(summary["z_end"], 4.0)
            self.assertEqual(summary["new_ode_integrations_by_this_analysis"], 0)
            with np.load(base / "analysis/TIME_PACKET.npz", allow_pickle=False) as packet:
                self.assertEqual(packet["values"].shape, (2, 4, 5))
                self.assertEqual(int(packet["tail_samples"]), 0)

    def test_saved_tail_hash_and_case_coverage_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self._fixture(base / "old")
            x, z, old_values, records = load_old(base / "old", (1, 1))
            t = np.linspace(x[-1], np.log(21.0 / 3.0), 5)
            for j, record in enumerate(records):
                v = values(t)[0]
                # Exact stored diagnostics at the interface; no model solve.
                v[:, 0] = old_values[j, :, -1]
                p = base / "tail/cases" / (record["case_id"] + ".npz")
                write_npz(p, t, v)
                receipt = {"status": "COMPLETED", "case_id": record["case_id"],
                           "source_lane": record["source_lane"],
                           "old_source_sha256": record["source_sha256"],
                           "npz_sha256": sha256(p), "identity": {"model": "manufactured"}}
                p.with_suffix(".json").write_text(json.dumps(receipt))
            tx, tz, tv, receipts = load_tail(base / "tail", records)
            self.assertEqual(len(receipts), 2)
            self.assertAlmostEqual(tz[-1], 2.0)
            summary = analyze(base / "old", base / "analysis", base / "tail", expected_counts=(1, 1))
            self.assertTrue(summary["coverage_target_z2_complete"])
            self.assertAlmostEqual(summary["z_end"], 2.0)
            self.assertEqual(summary["display_samples_per_case"], 9)
            self.assertLess(summary["tail_residual_budget"]["max_abs_stitch_identity_defect_F"], 1e-13)
            p = base / "tail/cases" / (records[0]["case_id"] + ".json")
            receipt = json.loads(p.read_text())
            receipt["npz_sha256"] = "0" * 64
            p.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
                load_tail(base / "tail", records)


if __name__ == "__main__":
    unittest.main(verbosity=2)
