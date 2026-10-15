"""Regressions against source-recorded original crate frozen gas A/B experiment."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import unittest

from analyze_ab import (load,analyse,numeric_identity,THRESHOLDS,
                        SOURCE_PACKET_PER_H,F_HE)

ROOT=Path(__file__).resolve().parent
RESULT=ROOT/"results"


def pair(dataset,q,eta,idx,steps):
    for key,arms in dataset.items():
        if (float(key[0]),float(key[1]),int(key[2]),int(key[3]))==(
                float(q),float(eta),int(idx),int(steps)):
            return arms
    raise KeyError((q,eta,idx,steps))


class TestFrozenHHeAB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load(RESULT/"CANONICAL_CACHED_SERIAL.csv")
        cls.result,cls.samples=analyse(RESULT/"CANONICAL_CACHED_SERIAL.csv",
                                     RESULT/"CANONICAL_CACHED_PARALLEL2.csv")

    def test_108_source_cases_and_216_arm_rows(self):
        self.assertEqual(len(self.data),108)
        self.assertEqual(self.result["separate_ab_cases"],108)
        self.assertEqual(self.result["individual_lanes"],216)

    def test_uncached_canonical_and_cached_result_bitwise_parity(self):
        self.assertTrue(numeric_identity(RESULT/"CANONICAL_UNCACHED.csv",
                                         RESULT/"CANONICAL_CACHED_SERIAL.csv"))
        self.assertTrue(numeric_identity(RESULT/"CANONICAL_UNCACHED.csv",
                                         RESULT/"CANONICAL_CACHED_PARALLEL2.csv"))

    def test_heii_threshold_atom_original_native_provider(self):
        with (RESULT/"HEII_PROVIDER_THRESHOLD.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),9)
        for x in rows:
            self.assertAlmostEqual(float(x["initial_energy_ev"]),54.42,places=13)
            self.assertLess(float(x["exact_first_mid_energy_ev"]),54.42)
            self.assertGreater(float(x["sigma_heii_at_node_cm2"]),1e-18)
            self.assertEqual(float(x["sigma_heii_at_exact_mid_cm2"]),0.)

    def test_spurious_heii_events_in_all_signed_high_resolution_cases(self):
        for q in (-.005,0,.005):
            p=pair(self.data,q,1e-5,32,256)
            a,b=p["PROJECTED"],p["COVARIANT"]
            self.assertGreater(float(a["HeII_absorbed_per_initial"]),.0019)
            self.assertEqual(float(b["HeII_absorbed_per_initial"]),0.)
            self.assertLess(float(b["exact_final_energy_eV"]),54.42)

    def test_true_above_heii_threshold_positive_control(self):
        for q in (-.005,0,.005):
            p=pair(self.data,q,1e-5,33,256)
            for r in p.values():
                self.assertGreater(float(r["HeII_absorbed_per_initial"]),.002)

    def test_below_heii_threshold_negative_control(self):
        for idx in (5,20):
            p=pair(self.data,0,1e-5,idx,256)
            for r in p.values():
                self.assertEqual(float(r["HeII_absorbed_per_initial"]),0.)

    def test_transparent_gas_has_no_photo_events(self):
        for key,p in self.data.items():
            if float(key[1])!=0: continue
            for row in p.values():
                self.assertEqual(float(row["binding_eV_per_initial"]),0.)
                self.assertEqual(float(row["heating_eV_per_initial"]),0.)
                self.assertEqual(float(row["HI_absorbed_per_initial"]),0.)
                self.assertEqual(float(row["HeI_absorbed_per_initial"]),0.)
                self.assertEqual(float(row["HeII_absorbed_per_initial"]),0.)

    def test_grid_support_boundary_loss_without_physical_absorption(self):
        for q in (-.005,0,.005):
            arm=pair(self.data,q,0,5,256)
            self.assertGreater(float(arm["PROJECTED"]["grid_boundary_photons_per_initial"]),8e-6)
            self.assertEqual(float(arm["COVARIANT"]["grid_boundary_photons_per_initial"]),0.)

    def test_source_gas_HeII_reservoir_not_violated(self):
        for key,p in self.data.items():
            eta=float(key[1])
            available=eta*F_HE/2
            for arm in p.values():
                used=float(arm["HeII_absorbed_per_initial"])*SOURCE_PACKET_PER_H
                self.assertLessEqual(used,available+1e-30)

    def test_event_binding_matches_original_species_thresholds(self):
        for p in self.data.values():
            for row in p.values():
                value=sum(float(row[key])*threshold for key,threshold in zip(
                    ("HI_absorbed_per_initial","HeI_absorbed_per_initial",
                     "HeII_absorbed_per_initial"),THRESHOLDS))
                self.assertLess(abs(float(row["binding_eV_per_initial"])-value),5e-12)

    def test_native_ledger_all_216_arms_closes(self):
        self.assertLess(max(self.result["max_absolute_normalized_ledger_residuals"].values()),
                        3e-15)

    def test_float_summary_cases_are_source_scoped_not_eor_predictions(self):
        self.assertFalse(self.result["original_source_ODE_replayed"])
        self.assertTrue(self.result["positive_threshold_controls_pass"])
        self.assertEqual(self.result["native_steps"],[1,32,256])

    def test_invalid_incomplete_case_failure(self):
        from tempfile import TemporaryDirectory
        rows=(RESULT/"CANONICAL_CACHED_SERIAL.csv").read_text().splitlines()
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"short.csv"
            path.write_text("\n".join(rows[:-1])+"\n")
            with self.assertRaises(ValueError):
                load(path)

    def test_heii_ghost_events_persist_across_three_step_counts(self):
        vals=[float(pair(self.data,0,1e-5,32,n)["PROJECTED"]["HeII_absorbed_per_initial"])
              for n in (1,32,256)]
        self.assertTrue(all(v>.0024 for v in vals))
        for n in (1,32,256):
            self.assertEqual(float(pair(self.data,0,1e-5,32,n)["COVARIANT"]
                                   ["HeII_absorbed_per_initial"]),0.)

    def test_frame_roundtrip_ulps_cause_false_negative_at_native_edge(self):
        old=load(RESULT/"FRAME_ROUNDTRIP_SERIAL.csv")
        for q in (-.005,.005):
            original=pair(old,q,1e-5,32,1)["PROJECTED"]
            canonical=pair(self.data,q,1e-5,32,1)["PROJECTED"]
            self.assertEqual(float(original["HeII_absorbed_per_initial"]),0.)
            self.assertGreater(float(canonical["HeII_absorbed_per_initial"]),.0024)

    def test_12_tested_atomic_transport_functions_match_original_and_rlib(self):
        doc=json.loads((RESULT/"ATOMIC_SOURCE_SURFACE_IDENTITY.json").read_text())
        self.assertEqual(doc["source_function_count"],12)
        self.assertTrue(doc["all_twelve_tested_function_bodies_equal"])
        self.assertFalse(doc["full_source_epochs_identical"])
        surface={d["function"] for d in doc["function_surfaces"]}
        self.assertIn("pub fn cross_section(",surface)
        self.assertIn("pub fn controlled_fixture(",surface)

    def test_same_frame_threshold_roundtrip_changes_rate_by_one_ulp(self):
        with (RESULT/"FRAME_ROUNDOFF_THRESHOLD.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),9)
        self.assertTrue(any(float(row["reconstructed_minus_native_eV"])<0
                            and float(row["heii_sigma_from_packet_E"])==0 for row in rows))
        self.assertTrue(all(float(row["heii_sigma_from_native_E"])>0 for row in rows))


    def test_formatted_final_binary_matches_canonical_physics(self):
        self.assertTrue(numeric_identity(
            RESULT/"CANONICAL_UNCACHED.csv",
            RESULT/"CANONICAL_FINAL_PARALLEL2.csv"))

    def test_all_source_evidence_hashes_and_model_scope(self):
        from hashlib import sha256
        doc=json.loads((ROOT/"DELIVERY_EVIDENCE_MANIFEST.json").read_text())
        self.assertEqual(doc["run_case_count"],108)
        self.assertEqual(doc["individual_transport_arms"],216)
        self.assertEqual(doc["source_function_byte_equal_count"],12)
        self.assertFalse(doc["native_ode_global_error_certified"])
        for row in doc["files"]:
            p=ROOT/row["path"]
            self.assertTrue(p.is_file())
            self.assertEqual(p.stat().st_size,row["bytes"])
            self.assertEqual(sha256(p.read_bytes()).hexdigest(),row["sha256"])


if __name__=="__main__":
    unittest.main()
