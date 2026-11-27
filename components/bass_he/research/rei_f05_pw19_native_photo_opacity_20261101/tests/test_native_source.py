#!/usr/bin/env python3
"""Tests require exact REC191 original source bundle, not CI source-free receipt."""
import csv,gzip,hashlib,json,math,os,sys,tempfile,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import native_photo_opacity as m

class OriginalNativeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=os.environ.get("REC191_FULL_SOURCE_ZIP")
        if not source or not Path(source).is_file():
            raise RuntimeError("Full-source tests require REC191_FULL_SOURCE_ZIP")
        cls.source=Path(source)
        cls.V,cls.pl,cls.pu=m.src_intake(cls.source)
        cls.ker,cls.record=m.spectral_moments()
        cls.result=json.loads((HERE/"results/SCIENCE_RESULT.json").read_text())
        with gzip.open(HERE/"results/ORIGINAL_REI_T160_PW19_LOCAL_PHOTO_OPACITY_46080.csv.gz","rt") as f:
            cls.rows=list(csv.DictReader(f))
    def test_full_original_zip_sha(self):
        self.assertEqual(m.digest(self.source.read_bytes()),m.REC_SHA)
    def test_full_native_populations(self):
        self.assertEqual(self.pl.shape,(46080,3))
        self.assertEqual(self.pu.shape,(46080,3))
        self.assertTrue(np.isfinite(self.pl).all())
        self.assertTrue(np.all(self.pl>=0))
        self.assertTrue(np.all(self.pl<=self.pu))
    def test_native_proper_cell_volumes(self):
        self.assertTrue(np.all(self.V>0))
        self.assertTrue(math.isclose(float(np.sum(self.V)),8.75179672498994384e70,rel_tol=1e-14))
    def test_exact_published_626_bin_spectrum_replayed(self):
        self.assertEqual(len(m.sp.read_source()[5.807]["E"]),626)
        self.assertEqual(len(self.ker),3)
        self.assertEqual([x["name"] for x in self.ker],list(m.BANDS))
    def test_native_hydrogen_band_absorption_support(self):
        self.assertEqual(self.ker[0]["mu"][1],0)
        self.assertEqual(self.ker[0]["mu"][2],0)
        self.assertEqual(self.ker[1]["mu"][2],0)
        self.assertGreater(self.ker[2]["mu"][2],0)
    def test_single_photo_energy_owner_exact(self):
        x=self.record["science"]["z5p95_log"]["bands_16_substeps"]
        for band in x:
            for s in m.SPECIES:
                g=band[f"gamma_{s}_per_s"]
                h=band[f"heat_{s}_erg_per_atom_s"]
                if g==0:
                    self.assertEqual(h,0)
                    continue
                self.assertGreater(h,0)
                ab=h+m.sp.CHI[s]*m.EV_ERG*g
                self.assertGreater(ab,0)
    def test_genuine_native_46080_rows(self):
        self.assertEqual(len(self.rows),46080)
        self.assertEqual([int(v["node"]) for v in self.rows],list(range(46080)))
        self.assertEqual(m.digest((HERE/"results/ORIGINAL_REI_T160_PW19_LOCAL_PHOTO_OPACITY_46080.csv.gz").read_bytes()),
                         self.result["data_csv_sha256"])
    def test_source_cell_kappa_bounds(self):
        for i in (0,100,5151,1252,26880,33255,35808,46079):
            rec=self.rows[i]
            for band in self.ker:
                lo=float(rec[f'{band["name"]}_kappa_lo_inv_cm'])
                hi=float(rec[f'{band["name"]}_kappa_hi_inv_cm'])
                direct_lo=float((self.pl[i]/self.V[i])@band["mu"])
                direct_hi=float((self.pu[i]/self.V[i])@band["mu"])
                self.assertTrue(math.isclose(lo,direct_lo,rel_tol=3e-14))
                self.assertTrue(math.isclose(hi,direct_hi,rel_tol=3e-14))
                self.assertGreater(lo,0)
                self.assertLessEqual(lo,hi)
    def test_true_photo_mfp_inverse(self):
        for i in (0,1252,6476,26880,46079):
            rec=self.rows[i]
            for name in m.BANDS:
                lo=float(rec[name+"_kappa_lo_inv_cm"])
                hi=float(rec[name+"_kappa_hi_inv_cm"])
                self.assertTrue(math.isclose(float(rec[name+"_mfp_lo_cm"])*hi,1.,rel_tol=2e-14))
                self.assertTrue(math.isclose(float(rec[name+"_mfp_hi_cm"])*lo,1.,rel_tol=2e-14))
    def test_true_spectral_variance_positive(self):
        for k in self.ker:
            for i in (0,100,5151,26880,46079):
                n=(self.pl[i]+self.pu[i])/(2*self.V[i])
                var=float(n@k["cov"]@n)
                self.assertGreaterEqual(var,-1e-13*float(n@k["mu"])**2)
                self.assertGreaterEqual(float(self.rows[i][k["name"]+"_CV2_mid"]),0)
    def test_genuine_heii_hard_opacity_fraction(self):
        v=self.result["helium_HeII_hard_band_volume_weighted_share"]
        self.assertGreater(v,.999)
        self.assertLess(v,1.)
        self.assertGreater(self.result["helium_HeII_hard_band_cell_share_quantiles"][0],.90)
    def test_jensen_finite_spectral_hardening(self):
        for row in self.result["Jensen_one_local_mfp_diagnostics"]:
            self.assertTrue(math.isclose(row["grey_transmission"],math.exp(-1),rel_tol=1e-15))
            self.assertGreaterEqual(row["frequency_resolved_transmission"],row["grey_transmission"]-1e-12)
            self.assertLessEqual(row["frequency_resolved_transmission"],1)
        h=[x for x in self.result["Jensen_one_local_mfp_diagnostics"] if x["band"]=="all_three"]
        self.assertTrue(all(z["frequency_resolved_transmission"]>.8 for z in h))
    def test_global_original_events_include_previous_donor(self):
        lo,hi=self.result["native_PW19_rate_inherited_total_interval"]
        self.assertLess(lo,self.result["native_PW19_donor_point_total"])
        self.assertLess(self.result["native_PW19_donor_point_total"],hi)
        self.assertGreater(lo,0)
    def test_no_canonical_promotion(self):
        self.assertEqual(self.result["central_DAG"],"28/88_REPORTED")
        self.assertEqual(self.result["BASS_HE_physical_DAG"],"14/18_REPORTED")
        self.assertEqual(self.result["canonical_delta"],0)
        self.assertEqual(self.result["production"],"HOLD")
        self.assertFalse(self.result["official_tick161"])
    def test_fail_closed_wrong_source_sha(self):
        orig=m.REC_SHA
        try:
            m.REC_SHA="0"*64
            with self.assertRaisesRegex(ValueError,"identity"):m.src_intake(self.source)
        finally:m.REC_SHA=orig
    def test_source_equal_replay_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=m.compute(self.source,tmp)
            self.assertEqual(r["data_csv_sha256"],self.result["data_csv_sha256"])
            self.assertEqual(m.digest((Path(tmp)/"SCIENCE_RESULT.json").read_bytes()),
                             m.digest((HERE/"results/SCIENCE_RESULT.json").read_bytes()))

if __name__=="__main__":unittest.main(verbosity=2)
