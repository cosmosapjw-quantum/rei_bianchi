#!/usr/bin/env python3
"""PR135/136 exact source-locked Sigma pi CMB, massive and ionizing donor adapter."""
import hashlib,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import pr136_sigma_interface as r

class SigmaPi(unittest.TestCase):
    def test_original_frozen_provider_git_blobs(self):
        for name,sha in (
            ("supplier_sigma_pi_PR135.py","c1f8c351a04891085fb6cfdc7fcb2956fa97c8da"),
            ("supplier_bass_hierarchy_PR136.py","7abb53320534203715cd65d909cfa3764396e6d0")):
            content=(HERE/name).read_bytes()
            self.assertEqual(hashlib.sha1(
                 b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest(),sha)

    def test_initial_reference_sigma_not_endpoint_sigma(self):
        p=r.sample(.01,16,0.,0.)
        self.assertEqual(p["orientation"],1)
        self.assertAlmostEqual(p["Sigma_initial_from_BASS_clock"],p["Sigma_ref"],places=12)
        self.assertGreater(p["Sigma_ref"],p["C13_Sigma_at_z4"])
        self.assertAlmostEqual(p["C13_Sigma_at_z4"],.0019999018732169966,places=12)
    def test_real_massless_and_massive_sources_and_ion_photo_pi(self):
        for q,sgn in ((-.01,1),(.01,-1)):
            p=r.sample(q,16,0.,0.)
            self.assertGreater(sgn*p["BASS_cmb_Pi_Pa"],0)
            self.assertGreater(sgn*p["BASS_massive_matter_Pi_Pa"],0)
            self.assertGreater(sgn*p["C13_ionizing_Pi_Pa"],0)
            self.assertLess(p["C13_ionizing_Pi_vs_CMB_Pi"],1e-10)
            self.assertEqual(p["PR136_amp_rad"],0.)
        z=r.sample(0.,16,.2,.4)
        self.assertEqual(z["orientation"],0)
        self.assertGreater(z["BASS_cmb_Pi_Pa"],0)
        self.assertGreater(z["BASS_massive_matter_Pi_Pa"],0)
        # Angular quadrupole cancellation has a 1e-36 Pa binary64 remainder.
        self.assertLess(abs(z["C13_ionizing_Pi_Pa"]),1e-32)
        self.assertTrue(z["source_identity"]["BASS_radiation_I2_to_pi"])
    def test_unphysical_seeded_P2_amplitude_rejected(self):
        with self.assertRaises(ValueError):r.sample(0.,8,3.,0.)
        with self.assertRaises(ValueError):r.sample(0.,8,0.,-2.)

if __name__=="__main__":unittest.main(verbosity=2)
