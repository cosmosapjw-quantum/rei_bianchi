#!/usr/bin/env python3
"""Scoped original-source and adversarial regression checks for PR312 candidate."""
import sys, unittest, math, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from competing_first import (load_physics,density_193,solve,sigma_kim,
    sigma_ccc_1d,moment_bounds,E_LOW,E_TOP,INPUT_SHA,INPUT,sha,ROOT as CODE_ROOT)

class TestPhysics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.meta=json.loads((ROOT/'results/RESULTS.json').read_text())
  cls.arr=pd.read_csv(ROOT/'results/FIRST_EVENT_ARRIVAL_192.csv')
  cls.bands=pd.read_csv(ROOT/'results/FIRST_EVENT_SOURCE_BANDS_3840.csv')
  cls.spectrum=pd.read_csv(ROOT/'results/ORIGINAL_BASS193_FIRST_EVENT_SPECTRUM.csv')
  cls.tables,cls.table_meta,cls.src,cls.spec,cls.thermal,cls.plasma=load_physics()

 def test_01_source_identity(self):
  for key,h in INPUT_SHA.items():self.assertEqual(sha(INPUT/key),h)
 def test_02_source_shapes(self):
  self.assertEqual((len(self.src),len(self.spec),len(self.thermal),len(self.plasma)),(192,192,192,193))
 def test_03_result_shapes(self):
  self.assertEqual((len(self.arr),len(self.bands),len(self.spectrum)),(192,3840,16598))
 def test_04_exact_source_electrons(self):
  self.assertAlmostEqual(self.arr.source_photoelectron_N_per_b.sum()/4.374110632809567e-12,1.,places=12)
 def test_05_exact_source_energy(self):
  self.assertAlmostEqual(self.arr.source_photoelectron_M_eV_per_b.sum()/6.749242464433258e-11,1.,places=12)
 def test_06_plasma_bath_charge_impact(self):
  d=density_193(self.spec,self.thermal,self.plasma)
  self.assertTrue(np.all(d['ne']>0))
  self.assertGreater(d['ne_extra_fraction'].min(),-1e-8)
  self.assertLess(d['ne_extra_fraction'].max(),1e-3)
 def test_07_ccc_ground_state_unit(self):
  self.assertEqual(set(self.tables),{'HI_ion','HI_2p','HI_2s','HeI_ion','HeI_2p','HeI_t2s'})
  self.assertGreater(self.tables['HI_ion'][:,1].max(),1e-17)
 def test_08_heI_true_edge_hard_zero(self):
  t=self.tables['HeI_ion']
  for e in [20.,24.58,24.5873890109]:self.assertEqual(sigma_ccc_1d(t,[e],'HeI_ion')[0],0.)
  self.assertGreater(sigma_ccc_1d(t,[24.59],'HeI_ion')[0],0.)
 def test_09_HI_ion_edge(self):
  t=self.tables['HI_ion']
  self.assertEqual(sigma_ccc_1d(t,[13.6],'HI_ion')[0],0.)
  self.assertGreater(sigma_ccc_1d(t,[13.7],'HI_ion')[0],0.)
 def test_10_kim_below_threshold(self):
  for k in [(13.61,.7576,-5.521,5.867,2.948),(24.58,.7326,-5.117,3.295,2.468)]:
   self.assertEqual(float(sigma_kim([k[0]],k)[0]),0)
 def test_11_kim_physical_positive(self):
  for coeff in [(13.61,.7576,-5.521,5.867,2.948),(24.58,.7326,-5.117,3.295,2.468),(54.42,.06233,-.2982,.2835,.327)]:
   self.assertGreaterEqual(float(sigma_kim([60.9],coeff)[0]),0.)
 def test_12_zero_hazard_prob(self):
  p,q,L,S=solve(np.array([E_LOW,E_LOW+1]),np.zeros((1,1,2)))
  self.assertAlmostEqual(float(S[0,-1]),1.)
  self.assertTrue(np.array_equal(p,np.zeros_like(p)))
  self.assertAlmostEqual(float(L[0,-1]),1.)
 def test_13_constant_hazard_two_competing_channels(self):
  tau=np.array([[[1.,2.]]])
  p,q,L,S=solve(np.array([E_LOW,E_LOW+1]),tau)
  self.assertAlmostEqual(float(p[0,-1,0]),(-math.expm1(-3))/3,places=14)
  self.assertAlmostEqual(float(p[0,-1,1]),2*(-math.expm1(-3))/3,places=14)
  self.assertAlmostEqual(float(S[0,-1]),math.exp(-3),places=14)
 def test_14_large_optical_depth_safe(self):
  p,q,L,S=solve(np.array([E_LOW,E_LOW+1]),np.array([[[1000.,0.]]]))
  self.assertAlmostEqual(float(p[0,-1,0]),1.)
  self.assertAlmostEqual(float(S[0,-1]),0.)
  self.assertLess(float(L[0,-1]),0.002)
 def test_15_energy_ledger_analytic(self):
  energies=np.array([13.7,14.0,15.2,16.])
  tau=np.array([[[.1,.2],[10.,.001],[.03,4.]]])
  p,q,L,S=solve(energies,tau)
  self.assertLess(float(np.max(abs(energies-(L[0]+q[0].sum(axis=1)+E_LOW*S[0])))),5e-13)
 def test_16_all_original_arrival_valid(self):
  self.assertTrue(np.array_equal(self.arr.arrival_interval.to_numpy(),np.arange(192)))
  self.assertTrue((self.arr.proper_interval_s>0).all())
 def test_17_partial_probability_normalization(self):
  a=self.spectrum
  self.assertLess((abs(a.CCC6_first_total+a.CCC6_survivor_to_13p7-1)).max(),3e-12)
 def test_18_all_channel_energy_ledger(self):
  self.assertLess(abs(self.spectrum.CCC6_energy_ledger_residual_eV).max(),5e-10)
 def test_19_nonnegative_first_events(self):
  for col in ['CCC6_first_total','CCC6_first_HI_ion','CCC6_first_HeI_ion',
      'CCC6_first_HI_exc_n2','Kim3_first_ion_total']:
   self.assertTrue((self.spectrum[col]>=-1e-14).all())
   self.assertTrue((self.spectrum[col]<=1+1e-13).all())
 def test_20_first_total_equals_components(self):
  a=self.spectrum
  self.assertLess((abs(a.CCC6_first_total -
     (a.CCC6_first_HI_ion+a.CCC6_first_HeI_ion+a.CCC6_first_HI_exc_n2+a.CCC6_first_HeI_exc))).max(),1e-11)
 def test_21_source_band_hull(self):
  # all individual moment enclosures contain own mean-energy colocation
  a=self.bands
  for k in ['CCC6_first_total','CCC6_first_HI_ion','CCC6_Coulomb_loss_before_first_eV','Kim3_first_ion_total']:
   tol=2e-25 if k!='CCC6_Coulomb_loss_before_first_eV' else 2e-24
   self.assertTrue((a[k+'_lower_per_b']<=a[k+'_mean_per_b']+tol).all(),k)
   self.assertTrue((a[k+'_mean_per_b']<=a[k+'_upper_per_b']+tol).all(),k)
 def test_22_collisional_competition_reduces_ion(self):
  a=self.spectrum
  self.assertTrue((a.CCC6_first_HI_ion+a.CCC6_first_HeI_ion<=a.CCC2_first_ion_total+1e-11).all())
 def test_23_kim_two_vs_three(self):
  a=self.spectrum
  self.assertTrue((a.Kim3_first_ion_total+1e-14>=a.Kim2_first_ion_total).all())
 def test_24_nist_publication_benchmark(self):
  r=self.meta['event_probability_examples']['192']
  self.assertLess(abs(r['Kim3_total']/3.54987989e-8-1),0.0001)
 def test_25_ref_source_helium_mismatch(self):
  a=self.spec
  self.assertGreater(float(np.max(abs(a.xHII_end-a.xHeII_end))),0.01)
 def test_26_random_moment_enclosures(self):
  rng=np.random.default_rng(20261031)
  sample=self.spectrum
  for _ in range(300):
   epoch=int(rng.integers(193))
   data=sample[sample.epoch==epoch].sort_values('initial_E_eV')
   x=data.initial_E_eV.to_numpy(float);y=data.CCC6_first_total.to_numpy(float)
   i,j=sorted(rng.choice(np.arange(len(x)),size=2,replace=False));a=float(x[i]);b=float(x[j]);w=float(rng.random());mu=w*a+(1-w)*b
   l,ref,u=moment_bounds(x,y,a,b,mu)
   obs=w*y[i]+(1-w)*y[j]
   self.assertLessEqual(l,obs+1e-10)
   self.assertLessEqual(obs,u+1e-10)
 def test_27_model_scope(self):
  r=self.meta
  self.assertEqual(r['dag']['canonical_delta'],0)
  self.assertEqual(r['new_cosmology_ivps'],0)
  self.assertEqual(r['dag']['production'],'HOLD')
 def test_28_three_way_difference(self):
  a=self.meta['source_event_aggregates']
  self.assertGreater(a['CCC6_first_total']['mean'],a['CCC6_first_HI_ion']['mean'])
  self.assertGreater(a['Kim3_first_ion_total']['mean'],0)
 def test_29_top_photon_energy(self):
  self.assertEqual(E_TOP,60.922559447552)
 def test_30_spectrum_sample(self):
  self.assertEqual(len(self.spectrum),193*86)
 def test_31_extra_competing_channel_monotonic_total_not_partial(self):
  e=np.array([E_LOW,E_LOW+1])
  p1,_,_,s1=solve(e,np.array([[[0.2,0.0]]]))
  p2,_,_,s2=solve(e,np.array([[[0.2,1.0]]]))
  self.assertGreater(p2.sum(),p1.sum())
  self.assertLess(p2[0,-1,0],p1[0,-1,0])

if __name__=='__main__':unittest.main()
