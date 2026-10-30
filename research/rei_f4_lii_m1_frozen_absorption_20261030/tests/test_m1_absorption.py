import sys,unittest, numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import m1_absorption as m
class TestNativeM1Absorption(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r,cls.d,cls.meta=m.compute()
 def test_epoch_count(self):self.assertEqual(len(self.r),193)
 def test_species_count(self):self.assertEqual(len(self.d),193*21)
 def test_positive_opacity(self):self.assertTrue(all(e['kappa_abs_m_inv']>0 for e in self.r))
 def test_native_thresholds(self):
  a=self.meta['sigma_m2'];self.assertEqual(a['He4III'],0);self.assertEqual(a['Li6II'],0);self.assertGreater(a['He4II'],0)
 def test_native_isotope_symmetry(self):
  a=self.meta['sigma_m2']; self.assertEqual(a['H1I'],a['DI']);self.assertEqual(a['DI'],a['TI']);self.assertEqual(a['He3I'],a['He4I']);self.assertEqual(a['Li6I'],a['Li7I'])
 def test_source_energy(self):self.assertAlmostEqual(self.meta['source_energy_eV'],59.020723673157676,places=12)
 def test_energy_ledger(self):
  self.assertLess(max(abs(e['mean_primary_photoelectron_eV']+e['mean_ion_binding_eV']-m.ENERGY) for e in self.r),1e-12)
 def test_probability_conservation(self):
  for e in self.r:
   self.assertLess(abs(sum(e['first_photoabsorption_'+c+'_fraction'] for c in m.CAT_GROUPS)-1),1e-14)
 def test_channel_rate_normalization(self):
  for e in self.r:
   self.assertLess(abs(sum(e['kappa_'+c+'_m_inv'] for c in m.CAT_GROUPS)-e['kappa_abs_m_inv']),max(1e-42,e['kappa_abs_m_inv']*1e-14))
 def test_hubble_length_identity(self):
  for e in self.r:
   self.assertAlmostEqual(e['tau_one_frozen_Hubble_length'],m.C_SI*e['kappa_abs_m_inv']/e['H_s'],places=9)
 def test_pr280_clock_crosswalk(self):self.assertTrue(all(e['pr280_triplet_accessible_rate_baryon_inv_s']<=e['pr280_K_event_rate_baryon_inv_s'] for e in self.r))
 def test_endpoint_opacity(self):
  self.assertGreater(self.r[0]['tau_one_frozen_Hubble_length'],1e4)
  self.assertTrue(0<self.r[-1]['tau_one_frozen_Hubble_length']<2)
 def test_primary_energy_shift(self):self.assertGreater(self.r[0]['mean_primary_photoelectron_eV'],self.r[-1]['mean_primary_photoelectron_eV'])
if __name__=='__main__':unittest.main()
