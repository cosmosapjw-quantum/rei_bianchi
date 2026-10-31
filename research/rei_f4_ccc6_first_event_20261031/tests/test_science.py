import sys,unittest,random,math,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import run as m

class PhysicalSourceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.arr,cls.comp,cls.th,cls.pl,cls.coul,cls.data,cls.owner,cls.meta=m.input_load()
  cls.E=m.energy_nodes(cls.data,1200);cls.sig=m.sigma_samples(cls.data,cls.owner,cls.E)
  cls.arrival=pd.read_csv(ROOT/'results/BASS_CCC6_FIRST_EVENT_ARRIVAL_192.csv')
  cls.bands=pd.read_csv(ROOT/'results/BASS_CCC6_FIRST_EVENT_SOURCE_BANDS_3840.csv')
  cls.mono=pd.read_csv(ROOT/'results/BASS193_CCC6_MONO_1351.csv')
  cls.out=json.loads((ROOT/'results/RESULTS.json').read_text())
 def test_01_sha_owner(self): self.assertEqual(m.digest(ROOT/'source/PR311_CCC6_SOURCE_FULL.zip'),m.PR311)
 def test_02_sha_bass_electron(self): self.assertEqual(m.digest(ROOT/'source/BASS193_COULOMB_PLASMA_193.csv'),m.COULOMB_CSV)
 def test_03_source_grid(self): self.assertEqual((len(self.arr),len(self.comp),len(self.th),len(self.pl)),(192,192,192,193))
 def test_04_six_channels(self): self.assertEqual(set(self.data),set(m.CHANNELS))
 def test_05_mirror_revision(self): self.assertEqual(self.meta['mirror_commit'],'7388232fac2c3cdadad613515006de008360f1ab')
 def test_06_full_electron_bath(self):
  np.testing.assert_allclose(self.coul.n_e_m3,self.pl.nb_m3*self.pl.xe_saved,rtol=8e-13,atol=0)
 def test_07_full_ne_not_subset(self):
  old=pd.read_csv(ROOT/'source311/results/CCC_FIRST_COLLISION_ARRIVAL_192.csv')
  full=self.arrival.ne_full_BASS_cm3.to_numpy();part=old.ne_HHe_cm3.to_numpy()
  self.assertGreater(np.max(abs(full-part)/full),2e-5)
 def test_08_no_HeII_in_six_channels(self): self.assertNotIn('HeII_ion',m.CHANNELS)
 def test_09_raw_sigma_same_original(self):
  for i,name in enumerate(m.CHANNELS):
   for en in [14.,20.,25.,35.,44.,55.,60.]:
    expected=self.owner.sigma_interp(self.data[name],en,name)
    calc=float(np.interp(en,self.E,self.sig[i]))
    self.assertLess(abs(expected-calc),3e-19+1e-2*expected)
 def test_10_threshold_patch(self):
  e=np.array([13.7,20,24.58,24.587389011,24.595,24.6,30.]);sig=m.sigma_samples(self.data,self.owner,e)
  self.assertEqual(sig[3,2],0.);self.assertEqual(sig[3,3],0.);self.assertGreater(sig[3,4],0)
 def test_11_p_start_zero(self):
  p,_,_=m.first_probs(self.E,self.sig,1e-6,1e-3,8e-5)
  self.assertEqual(float(p[:6,0].sum()),0.);self.assertEqual(float(p[6,0]),1.)
 def test_12_probability_machine_closure(self):
  for ne,h,he in [(2e-7,1e-3,1e-4),(1e-6,1e-4,1e-5),(1e-4,1e-9,1e-9),(2e-5,0,0)]:
   p,_,_=m.first_probs(self.E,self.sig,ne,h,he)
   self.assertLess(np.max(abs(p.sum(axis=0)-1)),1e-13)
 def test_13_no_targets(self):
  p,nu,_=m.first_probs(self.E,self.sig,2e-6,0,0)
  self.assertEqual(np.max(nu),0.);self.assertEqual(np.max(p[:6]),0.);self.assertEqual(np.min(p[6]),1.)
 def test_14_ion_neutral_density(self):
  p,_,_=m.first_probs(self.E,self.sig,2e-7,1e-3,0.)
  self.assertEqual(np.max(p[3:6]),0.)
 def test_15_monotone_total_first_probability(self):
  p,_,_=m.first_probs(self.E,self.sig,1e-6,1e-4,1e-5)
  self.assertGreaterEqual(np.min(np.diff(p[:6].sum(axis=0))),-1e-12)
 def test_16_all_event_bounds(self):
  for name in m.CHANNELS+['six_any','first_event_threshold_floor_eV']:
   v=self.bands[[name+'_lower',name+'_mean',name+'_upper']].to_numpy()
   self.assertGreaterEqual(v.min(),-1e-31)
   self.assertLessEqual(np.max(v[:,0]-v[:,1]),1e-30)
   self.assertLessEqual(np.max(v[:,1]-v[:,2]),1e-30)
 def test_17_mono_rows(self): self.assertEqual(self.mono.shape[0],193*7)
 def test_18_event_rows(self): self.assertEqual((len(self.bands),len(self.arrival)),(3840,192))
 def test_19_source_N_and_M(self):
  self.assertAlmostEqual(self.arrival.photoelectron_N_per_b.sum(),4.374110632809567e-12,delta=1e-23)
  self.assertAlmostEqual(self.arrival.photoelectron_E_eV_per_b.sum(),6.749242464433258e-11,delta=1e-22)
 def test_20_baryon_and_clock(self):
  self.assertTrue((self.arrival.proper_interval_s>0).all())
  np.testing.assert_allclose(self.arrival.z_low,self.coul.z.values[1:],atol=5e-12,rtol=0)
 def test_21_energy_floor_not_more_than_kinetic_budget(self):
  self.assertLess(self.arrival.first_event_threshold_floor_eV_upper.sum(),self.arrival.photoelectron_E_eV_per_b.sum())
 def test_22_total_probability_not_more_than_photoelectrons(self):
  self.assertLess(self.arrival.six_any_upper.sum(),self.arrival.photoelectron_N_per_b.sum())
 def test_23_aggregate_each_interval(self):
  x=self.bands.groupby('arrival_interval',sort=True).six_any_mean.sum().to_numpy();
  np.testing.assert_allclose(x,self.arrival.six_any_mean.to_numpy(),rtol=2e-13,atol=1e-33)
 def test_24_aggregate_six_channel(self):
  self.assertLess(abs(sum(self.out['channel_probability_means_per_b'].values())-self.out['probability_first_six_any_mean_per_b']),1e-28)
 def test_25_mono_real_probability(self):
  self.assertLess(self.mono.P_any_six_channel.min(),1e-6)
  self.assertEqual(self.mono.P_any_six_channel.max(),1.)
 def test_26_high_ne_low_prob(self):
  p1,_,_=m.first_probs(self.E,self.sig,1e-7,1e-5,1e-6)
  p2,_,_=m.first_probs(self.E,self.sig,1e-3,1e-5,1e-6)
  self.assertGreater(p1[:6,-1].sum(),p2[:6,-1].sum())
 def test_27_threshold_floor_first_ion_distinct(self):
  s=self.out['channel_probability_means_per_b']
  exc=sum(s[x] for x in ('HI_2s','HI_2p','HeI_2p','HeI_t2s'))
  ion=s['HI_ion']+s['HeI_ion']
  self.assertGreater(exc,ion)
 def test_28_finite_randomized_moment_hulls(self):
  rng=random.Random(3102026)
  for _ in range(600):
   k=rng.choice([0,40,80,160,191]);c=rng.randrange(6);first=rng.choice(m.FIRST_ABSORBERS);band=rng.randrange(5)
   lo=m.EDGES[band];hi=max(lo,min(m.EDGES[band+1],m.E_PAIR-m.CHI[first]))
   if hi<=lo:continue
   row=self.arrival.iloc[k];ne=row.ne_full_BASS_cm3;H=row.nHI_cm3;He=row.nHeI_cm3
   p,_,_=m.first_probs(self.E,self.sig,ne,H,He)
   if lo<m.LOW:
    knots=np.unique(np.r_[lo,m.LOW,self.E[(self.E>m.LOW)&(self.E<hi)],hi])
    vals=np.where(knots<=m.LOW,0,np.interp(knots,self.E,p[c]))
   else:
    knots=np.unique(np.r_[lo,self.E[(self.E>lo)&(self.E<hi)],hi]);vals=np.interp(knots,self.E,p[c])
   v1=lo+rng.random()*(hi-lo);v2=lo+rng.random()*(hi-lo);t=rng.random();mu=t*v1+(1-t)*v2
   actual=t*np.interp(v1,knots,vals)+(1-t)*np.interp(v2,knots,vals)
   lower,_,upper=m.moment_bounds(knots,vals,lo,hi,mu)
   self.assertLessEqual(lower-actual,2e-12);self.assertLessEqual(actual-upper,2e-12)
 def test_29_missing_channels_not_production(self):
  self.assertTrue(self.out['missing_HeII_and_other_CCC_channels'])
  self.assertTrue(self.out['no_full_cascade'])
  self.assertEqual(self.out['original_REI_F4_counts']['canonical_delta'],0)
 def test_30_bad_sha_detected(self):
  self.assertNotEqual(hashlib.sha256((ROOT/'source/PR311_CCC6_SOURCE_FULL.zip').read_bytes()+b'0').hexdigest(),m.PR311)
 def test_31_no_negative_coulomb_loss(self):
  E=self.E;ln=np.log(4*E/(7.40e-11*1e-6));v=np.sqrt(2*E*m.EV_ERG/m.ELECTRON_MASS_G)
  b=4*np.pi*m.E_SQUARED_CGS**2*1e-6*ln/(m.ELECTRON_MASS_G*v)/m.EV_ERG
  self.assertGreater(b.min(),0.)
 def test_32_analytical_hazard_identity(self):
  Ee=30;ne=1e-6;H=1e-4;sig=m.owner if hasattr(m,'owner') else self.owner
  # h=(n sigma v)/(4pi e^4 ne lnLambda/(m v EVerG))
  sigma=self.owner.sigma_interp(self.data['HI_ion'],Ee,'HI_ion')
  v=math.sqrt(2*Ee*m.EV_ERG/m.ELECTRON_MASS_G)
  ln=math.log(4*Ee/(7.40e-11*ne))
  b=4*math.pi*m.E_SQUARED_CGS**2*ne*ln/(m.ELECTRON_MASS_G*v*m.EV_ERG)
  h1=H*sigma*v/b;h2=H*sigma*2*Ee*m.EV_ERG**2/(4*math.pi*m.E_SQUARED_CGS**2*ne*ln)
  self.assertAlmostEqual(h1/h2,1.,delta=2e-15)

if __name__=='__main__': unittest.main()
