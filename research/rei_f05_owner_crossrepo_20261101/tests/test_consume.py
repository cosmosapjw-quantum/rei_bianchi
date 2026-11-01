#!/usr/bin/env python3
"""Physical algebra, unit, negative source and frozen-receipt regressions."""
from __future__ import annotations
from decimal import Decimal as D
import hashlib,json,math,sys,tempfile
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import owner_consume as c
import source_intake as si

class OwnerSourcePhysics(unittest.TestCase):
    def test_ionization_energy_is_species_sensitive(self):
        # H I -> H II, He I -> He II, He II -> He III each creates 1 e.
        h=c.EV*c.CHI_H
        hefirst=c.EV*c.CHI_HE1
        hesecond=c.EV*c.CHI_HE2
        self.assertTrue(h<hefirst<hesecond)
        # Second helium reaction: Delta HeII=-1, Delta HeIII=+1
        delta_e=D(-1)+D(2)*D(1)
        delta_b=c.EV*(c.CHI_HE1*D(-1)+(c.CHI_HE1+c.CHI_HE2)*D(1))
        self.assertEqual(delta_e,D(1))
        self.assertEqual(delta_b,hesecond)
        self.assertNotEqual(delta_b,h)

    def test_he_correction_identity(self):
        for h,he2,he3 in [(D(-2),D(1),D(-1)),(D("0.1"),D("-0.3"),D("0.4"))]:
            de=h+he2+2*he3
            db=c.EV*(c.CHI_H*h+c.CHI_HE1*he2+(c.CHI_HE1+c.CHI_HE2)*he3)
            right=c.EV*((c.CHI_HE1-c.CHI_H)*he2+(c.CHI_HE1+c.CHI_HE2-2*c.CHI_H)*he3)
            self.assertEqual(db-c.EV*c.CHI_H*de,right)

    def test_source_interval_arithmetic_negative_and_positive(self):
        self.assertEqual(c.mul((D(2),D(3)),(D(-4),D(-1))),(D(-12),D(-2)))
        self.assertEqual(c.scalar((D(-2),D(1)),D(-2)),(D(-2),D(4)))
        self.assertTrue(c.contains_overlap((D(-2),D(-1)),(D("-1.5"),D("0.25"))))
        self.assertFalse(c.contains_overlap((D(-2),D(-1)),(D(1),D(2))))

    def test_invalid_or_inverted_intervals_hard_fail(self):
        with self.assertRaisesRegex(ArithmeticError,"INVALID_ORIGINAL_INTERVAL"):
            c.interval({"a_lower":"NaN","a_upper":"1"},"a")
        with self.assertRaisesRegex(ArithmeticError,"INVALID_ORIGINAL_INTERVAL"):
            c.interval({"a_lower":"2","a_upper":"1"},"a")

    def test_source_archive_tamper_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"corrupted.zip";p.write_bytes(b"NOT_A_REAL_ORIGINAL_SOURCE")
            with self.assertRaisesRegex(AssertionError,"HE_SOURCE_ARCHIVE_MISMATCH"):
                si.main(p,p,Path(tmp)/"false_pass.json")

    def test_owner_result_freezes_original_tick_not_tau(self):
        r=json.loads((ROOT/"results/OWNER_HHE_ENERGY_CHARGE_THOMSON.json").read_text())
        self.assertEqual(r["original_accepted_tick"],"160/131072")
        self.assertEqual(r["candidate_tick161"],"NOT_ACCEPTED")
        self.assertEqual(r["central_DAG"],"28/88_REPORTED")
        self.assertEqual(r["canonical_delta"],0)
        self.assertTrue(r["no_rei_F08_line_of_sight_tau"])
        self.assertTrue(r["no_latent_energy_to_photoheat_conversion"])
        self.assertFalse(r["no_original_source_override"] is False)
        self.assertTrue(all(x==0 for x in r["verification"]["sibling_binding_row_disjoint_counts"].values()))

    def test_native_sibling_ledger_signs_and_energy_ratio(self):
        r=json.loads((ROOT/"results/OWNER_HHE_ENERGY_CHARGE_THOMSON.json").read_text())
        p=r["physics"]
        a=p["ionization_storage_energy_loss_per_lost_electron_eV"]
        self.assertLess(a[0],a[1])
        self.assertGreater(a[0],13)
        self.assertLess(a[1],16)
        h=p["direct_original_helium_threshold_correction_erg"]
        self.assertLess(h[1],0)
        self.assertTrue(c.contains_overlap((D(h[0]),D(h[1])),
                                           (D(p["helium_threshold_correction_to_H_only_energy_erg"][0]),
                                            D(p["helium_threshold_correction_to_H_only_energy_erg"][1]))))

if __name__=="__main__":
    unittest.main()
