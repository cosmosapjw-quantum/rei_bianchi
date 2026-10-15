#!/usr/bin/env python3
"""Actual five-project supplier execution on original rei_bianchi C11 Git head."""
from pathlib import Path
import hashlib,sys,unittest
from decimal import Decimal

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import crossrepo_integration as x

class FiveSupplierIntake(unittest.TestCase):
    def test_all_mirrors_exact_git_blobs(self):
        meta=x.validate_mirror()
        self.assertEqual(meta["file_count"],16)
        self.assertEqual(set(meta["suppliers"]),{"BASS_HE","WU088_HH","bass","bass_cr","rec_bianchi"})
        self.assertTrue(meta["all_downloaded_git_blobs_match"])
    def test_real_bass_AX03_killing_proper_clock(self):
        m=x.background_photon_source()
        self.assertEqual(m["count"],15)
        self.assertLess(m["max_rel_source_H"],1e-13)
        self.assertLess(m["max_phase_volume_residual"],1e-12)
        self.assertGreater(m["sample"][0]["proper_dt_s"],0.)
    def test_bass_cr_actual_packet_oracle_6_bounds(self):
        r=x.source_packet_envelopes()
        self.assertEqual(r["n_packets"],24)
        self.assertTrue(r["mass_energy_conserved_exact_dyadics"])
        self.assertEqual(r["precision_admission"],"HOLD_PRECISION_TARGET")
        for value,(lower,upper) in zip(r["oracle_events_and_heat"],r["final"]["event"]+r["final"]["heat"]):
            self.assertLessEqual(lower-1e-12,value)
            self.assertLessEqual(value,upper+1e-12)
        self.assertTrue(all(b<=a for a,b in zip(r["initial"]["widths"],r["final"]["widths"])))
    def test_rec_HyRec_source_IC_declined_but_recomputed(self):
        v=x.recombination_initial_counterfactual()
        self.assertEqual(v["donor_REI_zbar"],20.)
        self.assertFalse(v["ionizing_stock_changed"])
        self.assertFalse(v["production_IC_changed"])
        self.assertGreater(v["relative_thomson_rate_delta"],0.05)
        self.assertLess(v["relative_thomson_rate_delta"],0.053)
        self.assertGreater(v["donor_conditional"]["temperature_K"],v["baseline"]["temperature_K"])
    def test_WU_HH_original_negative_admission(self):
        g=x.wu_coulomb_source_guard()
        self.assertTrue(g["unit_test_without_approval_refused"])
        self.assertEqual(g["status"],"ACTUAL_WU_GUARD_EXECUTED_HH_PHYSICAL_RATE_HOLD")
        self.assertEqual(g["consumer_source_identity"],"MD14_Z002_FESC_BB50K_13P6_100_V1")
    def test_HE_warm_independent_tau_and_prob(self):
        m=x.he_tau_source_bound()
        self.assertTrue(m["no_cold_C10_observable_transfer"])
        self.assertEqual(m["cells"],16)
        lo,hi=map(Decimal,m["tau_interval"])
        self.assertTrue(Decimal(0)<lo<hi<Decimal("1.3e-7"))
        p=Decimal(m["single_collision_probability"])
        self.assertGreater(p,0)
        self.assertLess(p,hi)

if __name__=="__main__":unittest.main(verbosity=2)
