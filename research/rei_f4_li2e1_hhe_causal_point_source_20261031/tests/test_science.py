#!/usr/bin/env python3
from pathlib import Path
import sys,unittest,json,hashlib,math,tempfile
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
import science
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d,cls.r=science.compute(False)
        cls.p=cls.r['physical_outputs']
    def test_01_input_lock(self):
        for fn in ['PR294_FULL.zip','PR295_FULL.zip']:
            self.assertEqual(science.sha(science.ROOT/'source'/fn),json.loads((science.ROOT/'evidence'/'SOURCE_LOCK.json').read_text())[fn]['sha256'])
    def test_02_real_rows(self):self.assertEqual(len(self.d),192)
    def test_03_clock(self):self.assertLess(self.p['max_relative_proper_interval_mismatch'],1e-11)
    def test_04_eos(self):self.assertLess(self.p['max_relative_Cv_EOS_mismatch'],1e-11)
    def test_05_photo_total(self):
        u=self.d;self.assertTrue(np.allclose(u[['directwindow_LiII_2E1_HI_counts_upper_per_b','directwindow_LiII_2E1_HeI_counts_upper_per_b','directwindow_LiII_2E1_HeII_counts_upper_per_b']].sum(axis=1)+u.directwindow_LiII_2E1_LiI_counts_upper_per_b,self._spin_counts(),rtol=1e-12,atol=1e-28))
    def _spin_counts(self):return science.load()[0].singlet_2E1_directwindow_ionizations_rectangle_splitting_upper.values
    def test_06_nuclear_H(self):self.assertLess(self.p['max_absolute_HHe_nuclear_conservation_error_per_b_s'],1e-36)
    def test_07_electron(self):self.assertLess(self.p['max_absolute_HHe_electron_stoich_error_per_b_s'],1e-36)
    def test_08_Li_excluded(self):
        self.assertTrue((self.d.delta_ne_LiI_excluded_from_REI_HHe_F5_per_b_s>=0).all())
        self.assertAlmostEqual(float((self.d.delta_ne_LiI_excluded_from_REI_HHe_F5_per_b_s*self.d.proper_interval_s).sum()),self.p['Li_I_conditional_photo_events_per_baryon_upper_separate'],places=26)
    def test_09_nonnegative_budget(self):self.assertTrue((self.d.conditional_all_species_primary_e_eV_per_b>=0).all())
    def test_10_thermal_bracket(self):
        self.assertTrue((self.d.delta_Tdot_conservative_lower_K_s<=0).all())
        self.assertTrue((self.d.delta_Tdot_conservative_upper_K_s>=0).all())
        self.assertTrue((self.d.delta_Tdot_frozen_source_if_all_primary_heat_upper_K_s<=self.d.delta_Tdot_conservative_upper_K_s+1e-29).all())
        self.assertTrue((self.d.delta_Tdot_frozen_source_if_all_primary_heat_upper_K_s>=self.d.delta_Tdot_conservative_lower_K_s-1e-29).all())
    def test_11_secondary_energy_cone(self):
        q=self.d.maximum_additional_HHe_secondary_ionizations_per_b_energy_cap*science.CH_REI[0]
        self.assertTrue(np.allclose(q,self.d.conditional_all_species_primary_e_eV_per_b,rtol=1e-13,atol=1e-29))
        self.assertLess(self.p['secondary_HHe_ionizations_energy_ceiling_per_baryon'],1e-9)
    def test_12_threshold_sign(self):
        self.assertTrue((self.d.delta_REI_binding_minus_BASS_HHe_eV_per_b<=1e-25).all())
        self.assertLess(self.p['integrated_source_REI_minus_BASS_threshold_defect_eV_per_b'],0)
    def test_13_energy_source_mismatch(self):
        a=science.load()[0]
        self.assertLess(abs(a.conditional_primary_electron_eV_rectangle_upper.sum()-self.p['all_conditional_primary_e_eV_per_baryon_upper']),1e-26)
    def test_14_not_full_REI17(self):self.assertEqual(self.r['qualifications']['REI_HHe_FJ'].split(';')[0],'SOURCE_TRANSLATED_5STATE_POINT_MODEL_ONLY')
    def test_15_no_ivp(self):self.assertEqual(self.r['input_rows']['new_cosmic_IVP'],0)
    def test_16_reject_tampered_input(self):
        # This executes the same immutable-source rejection guard as science.load.
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/'PR294_FULL.zip'
            bad.write_bytes(b'not-the-original-archive' )
            lock=json.loads((science.ROOT/'evidence'/'SOURCE_LOCK.json').read_text())['PR294_FULL.zip']
            with self.assertRaisesRegex(AssertionError,'SOURCE_LOCK_MISMATCH'):
                science.assert_locked_source(bad,lock['sha256'],lock['bytes'])
    def test_17_nonzero_physics(self):self.assertGreater(self.p['HHe_conditional_photo_events_per_baryon_upper'],0)
    def test_18_parent_not_transformed(self):self.assertEqual(self.r['gates']['CANONICAL_DELTA'],0)
    def test_19_source_heat_not_injected(self):self.assertIn('NOT_INJECTED_IN_NATIVE_FJ',self.d.source_status.iloc[0])
    def test_20_Cv_dimension(self):
        eta=self.d.eta_HHe_particles_per_Href
        self.assertLess(np.max(abs(self.d.HHe_Cv_erg_per_Href_K/(1.5*science.KB_ERG*eta)-1)),1e-11)

    def test_21_target_population_available(self):
        _,_,h,_,_,_=science.load()
        a=h.iloc[:-1]
        d=self.d
        yH=a.nHref_over_nb*(1-a.HII_fraction)
        yHeI=a.nHe4_over_nb*(1-a.HeII_fraction-a.HeIII_fraction)
        yHeII=a.nHe4_over_nb*a.HeII_fraction
        for N,Y in zip([d.directwindow_LiII_2E1_HI_counts_upper_per_b,d.directwindow_LiII_2E1_HeI_counts_upper_per_b,d.directwindow_LiII_2E1_HeII_counts_upper_per_b],[yH,yHeI,yHeII]):
            self.assertTrue((N.values<=Y.values+1e-35).all())
if __name__=='__main__':unittest.main(verbosity=2)
