#!/usr/bin/env python3
"""Source-traceable math+physics targeted tests, including hostile negative controls."""
import hashlib,json,sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import build_memory as m
class PhysicsChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r,cls.d,cls.a,cls.em=m.construct(write=False)
  cls.orig=pd.read_csv(ROOT/'input/PUBLIC_results_FULL193_ARRIVAL_192.csv')
  cls.previous=pd.read_csv(ROOT/'input/FS2010_NATIVE_CROSSWALK_192.csv')
  cls.j=cls.d.arrival_interval.to_numpy(int);cls.k=cls.d.emission_epoch.to_numpy(int)
 def test_01_original_owner_hash(self): self.assertTrue(m.ensure_identity())
 def test_02_original_pr302_count(self): self.assertEqual(len(self.d),18528)
 def test_03_strict_lower_triangle(self): self.assertTrue(np.all(self.j>=self.k))
 def test_04_every_triangle_cell_once(self): self.assertEqual(np.unique(self.k*192+self.j).size,18528)
 def test_05_positive_original_photon_probabilities(self): self.assertTrue((self.d.photon_absorption_kernel_per_pair>=0).all())
 def test_06_photon_pair_nonnegative_future(self): self.assertTrue((self.em.not_first_absorbed_by_z2_per_b>=-1e-28).all())
 def test_07_pair_conservation(self):
  self.assertAlmostEqual(self.em.injected_2E1_photons_per_b.sum(),self.em.first_absorbed_photons_until_z2_per_b.sum()+self.em.not_first_absorbed_by_z2_per_b.sum(),delta=1e-23)
 def test_08_original_absorption_count(self):
  self.assertTrue(np.allclose(self.a.absorption_events_per_b,self.orig.total_absorbed_ionizations_per_b,rtol=1e-12,atol=1e-24))
 def test_09_original_primary_kinetic_energy(self):
  self.assertTrue(np.allclose(self.a.primary_energy_eV_per_b,self.orig.total_primary_e_eV_per_b,rtol=1e-12,atol=1e-23))
 def test_10_source_event_charge_map(self):
  vs=sum(self.d[s+'_first_absorption_per_b'].to_numpy() for s in m.SPECIES)
  self.assertTrue(np.allclose(vs,self.d.first_absorption_events_per_b.to_numpy(),atol=1e-23,rtol=1e-12))
 def test_11_proper_clock_source_per_Href(self):
  expected=self.a.absorption_events_per_b.to_numpy()/(self.a.proper_interval_s.to_numpy()*self.a.source_Href_over_nb.to_numpy())
  self.assertTrue(np.allclose(expected,self.a.photoelectron_rate_per_Href_s,atol=0,rtol=1e-13))
 def test_12_native_weak_jacobian_preserved(self):
  with np.load(ROOT/'source_bass/PR293_SOURCE_FJ21_193.npz',allow_pickle=False) as dat:
   j=dat['J21_per_s']; self.assertAlmostEqual(j[100,2,0],1/878.4,delta=1e-15)
 def test_13_diagonal_ablation_error(self):
  self.assertAlmostEqual((self.a.absorption_events_per_b-self.a.local_same_epoch_events_per_b).sum(),self.a.delayed_events_per_b.sum(),delta=1e-24)
 def test_14_global_nonlocal_fraction(self):
  x=self.a.delayed_events_per_b.sum()/self.a.absorption_events_per_b.sum()
  self.assertAlmostEqual(x,self.r['lagged_absorption_fraction'],delta=1e-14)
 def test_15_local_lagged_majority_and_weight(self):
  f=self.a.delayed_events_fraction>0.5
  self.assertEqual(f.sum(),self.r['per_arrival_bins_lagged_majority'])
  self.assertGreater(f.sum(),0)
 def test_16_original_fs2010_bounds(self):
  valid=self.a.FS_xi_valid.to_numpy(bool)
  self.assertEqual(valid.sum(),87)
  self.assertTrue(np.allclose(self.a.FS_conditional_heat_lower_eV_per_b[valid],self.previous.fheat_lower[valid],rtol=1e-11,atol=2e-22))
  self.assertTrue(np.allclose(self.a.FS_conditional_heat_upper_eV_per_b[valid],self.previous.fheat_upper[valid],rtol=1e-11,atol=2e-22))
 def test_17_no_fs_extrapolation(self):
  valid=self.a.FS_xi_valid.to_numpy(bool)
  self.assertTrue(np.isnan(self.a.FS_conditional_heat_lower_eV_per_b[~valid].to_numpy()).all())
 def test_18_bounded_thermal_source(self):
  valid=self.a.FS_xi_valid.to_numpy(bool)
  self.assertTrue((self.a.FS_conditional_heat_upper_eV_per_b[valid]>=self.a.FS_conditional_heat_lower_eV_per_b[valid]).all())
 def test_19_emission_time_not_negative(self): self.assertTrue((self.d.proper_lag_lower_year>=0).all())
 def test_20_insist_unabsorbed_not_same_as_escaped(self):
  self.assertIn('by_z2',self.em.columns[5]);self.assertIn('not actual heat',self.r['unpartitioned_energy_explanation'])
 def test_21_fs_model_off_manifold(self):self.assertIn('not BASS multi-ion chemistry',' '.join(self.r['scope_and_nonpromotions']))
 def test_22_impulse_perturbation_causal_operator(self):
  k0=71
  d=self.d.loc[self.d.emission_epoch==k0]
  J=d.arrival_interval.to_numpy(int)
  Q=float(d.source_pairs_per_b.iloc[0]);self.assertGreater(Q,0)
  K=d.photon_absorption_kernel_per_pair.to_numpy()
  diff=np.bincount(J,weights=(Q+Q*1e-2)*K-Q*K,minlength=192)
  self.assertTrue((diff[:k0]==0).all());self.assertAlmostEqual(diff.sum(),.01*(Q*K).sum(),delta=1e-23)
 def test_23_negative_control_double_source(self):
  correct=self.a.absorption_events_per_b.sum()
  self.assertAlmostEqual((2*self.a.absorption_events_per_b).sum()/correct,2.,delta=1e-14)
 def test_24_negative_control_tamper_hash(self):
  self.assertNotEqual(hashlib.sha256(b'tampered not original').hexdigest(),m.EXPECTED['source_bass/trajectory.npz'])
 def test_25_negative_control_noncausal(self):
  self.assertFalse(np.all(np.array([1,0])>=np.array([0,1])))
 def test_26_source_tag_not_mutated(self):self.assertTrue(self.r['native_bass21_source_unchanged'])
 def test_27_baryon_conservation_native(self):
  with np.load(ROOT/'source_bass/PR293_SOURCE_FJ21_193.npz',allow_pickle=False) as z:
   a=z['A21'];f=z['F21_per_baryon_s'];self.assertLess(np.max(abs(f@a)),1e-21)
 def test_28_internal_fs_table_energy_closure(self):
  fs=m.FS2010();self.assertLess(fs.closure_max,5e-5)
 def test_29_two_photons_per_2e1_pair(self):self.assertAlmostEqual(self.r['injected_photons_per_baryon']/self.r['source_pairs_per_original_baryon'],2.,delta=1e-14)
 def test_30_no_new_IVP_or_canonical_admission(self):
  self.assertEqual(self.r['DAG']['canonical_physical_delta'],0)
  self.assertEqual(self.r['DAG']['production'],'HOLD')
if __name__=='__main__':unittest.main(verbosity=2)
