import unittest,zipfile,hashlib,sys,pathlib,json,numpy as np,pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import compute_theory as t

class HeIIOriginalSourceAndScience(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.z=zipfile.ZipFile(t.CURTIN_ZIP)
  cls.tab=t.load_heii();cls.result=json.loads((ROOT/'results/RESULTS.json').read_text())
  cls.bands=pd.read_csv(ROOT/'results/HeII_16CHANNEL_SOURCE_BANDS_3840.csv')
  cls.arrival=pd.read_csv(ROOT/'results/HeII_16CHANNEL_ARRIVAL_192.csv')
  cls.mono=pd.read_csv(ROOT/'results/HeII_16CHANNEL_MONO_1544.csv')
 def test_01_source_sha(self):self.assertEqual(t.sha(t.CURTIN_ZIP),t.EXACT_CURTIN_UPLOAD_SHA)
 def test_02_parent_master_sha(self):self.assertEqual(t.sha(t.PARENT_ARCHIVE),t.PARENT_ORIGINAL_SHA)
 def test_03_source_crc(self):self.assertIsNone(self.z.testzip())
 def test_04_helium_count(self):self.assertEqual(len(self.tab),10)
 def test_05_reader_semantics(self):
  s=self.z.read('README').decode();self.assertIn('4F.2P is for nf=4',s)
  self.assertIn('TICS is the Total Ionisation',s)
 def test_06_n2_level_resolved_sum(self):
  s=t.table(self.z,'2S.1S');p=t.table(self.z,'2P.1S');a=self.tab[0]
  np.testing.assert_allclose(a[:,1],s[:,1]+p[:,1],atol=7e-17,rtol=0)
 def test_07_detailed_balance_2s_2p(self):
  # Pair using fourth column's identical original total collision energy key.
  for lev,g in [('2S',1.),('2P',3.)]:
   def parse(name):
    out={}
    for line in self.z.read(name).decode().splitlines():
     if line.startswith('#'):continue
     p=line.split()
     if len(p)>=4:out[p[3]]=(float(p[0]),float(p[1]))
    return out
   up=parse(lev+'.1S');down=parse('1S.'+lev)
   err=[]
   for key in up.keys() & down.keys():
    Ei,si=up[key];Ef,sf=down[key]
    if Ei<=0 or si<=0:continue
    predicted=g*Ef/Ei*sf
    err.append(abs(predicted-si)/si)
   self.assertGreater(len(err),800)
   self.assertLess(np.percentile(err,95),3.6e-4)
   self.assertLess(max(err),6.e-4)
 def test_08_duplicate_outside_source_energy_domain(self):
  raw=[s for s in self.z.read(':.1').decode().splitlines() if not s.startswith('#')]
  self.assertEqual(float(raw[-1].split()[0]),10290.)
  self.assertEqual(float(raw[-2].split()[0]),10290.)
  self.assertLess(t.calc_thresholds()[-1],100)
 def test_09_threshold_zero_for_ion(self):
  a=t.heii_sigma(np.array([54.40,54.4232,54.52]),self.tab)
  self.assertEqual(a[-1,0],0.)
  self.assertEqual(a[-1,1],0.)
  self.assertGreater(a[-1,-1],0.)
 def test_10_counts(self):
  self.assertEqual(len(self.arrival),192)
  self.assertEqual(len(self.bands),3840)
  self.assertEqual(len(self.mono),193*8)
  self.assertEqual(self.result['original_193_epochs'],193)
 def test_11_probability_physical(self):
  a=self.mono
  self.assertTrue((a.P_HeII_any>=-1e-15).all())
  self.assertTrue((a.P_HeII_any<=a.P_all_16+1e-12).all())
  self.assertTrue((a.P_all_16<=1+1e-12).all())
  self.assertTrue((a.P_all_16+a.P_survival-1).abs().max()<3e-13)
 def test_12_heii_e_cutoffs(self):
  a=self.mono
  self.assertTrue((a[a.E_eV<40.8174].P_HeII_any==0).all())
  self.assertTrue((a[a.E_eV<54.4232].P_HeII_ion==0).all())
 def test_13_source_band_positive_and_bound(self):
  for k in ('HeII_any','HeII_n2','HeII_n3to10','HeII_ion','all_any','HeII_binding_eV'):
   x=self.bands[[k+'_low_per_b',k+'_mean_per_b',k+'_high_per_b']].to_numpy()
   self.assertGreaterEqual(x.min(),-1e-33)
   self.assertLessEqual(np.max(x[:,0]-x[:,1]),1e-27)
   self.assertLessEqual(np.max(x[:,1]-x[:,2]),1e-27)
 def test_14_source_moments(self):
  self.assertAlmostEqual(self.arrival.source_N_per_b.sum(),4.374110632809567e-12,delta=1e-23)
  self.assertAlmostEqual(self.arrival.source_M_eV_per_b.sum(),6.749242464433258e-11,delta=1e-22)
 def test_15_sum_competing_not_added(self):
  a=self.arrival
  self.assertLess(abs(a.new_CCC6_first_mean_per_b.sum()+a.HeII_any_channel_mean_per_b.sum()-a.all_any_mean_per_b.sum()),3e-26)
  self.assertLess(abs(a.HeII_any_mean_per_b.sum()-a.HeII_any_channel_mean_per_b.sum()),3e-27)
 def test_16_original_initial_charge_bath(self):
  v=self.arrival
  self.assertTrue((v.ne_all_BASS_cm3>0).all())
  self.assertTrue((v.nHeII_cm3>=0).all())
 def test_17_witness_source_types(self):
  self.assertEqual(set(self.bands.first_absorber),{'H_I','He_I','He_II','Li_I'})
  self.assertEqual(len(self.bands.groupby(['arrival_interval','first_absorber','energy_band'])),3840)
 def test_18_first_event_threshold_energy(self):
  self.assertAlmostEqual(t.calc_thresholds()[0],40.8174,places=7)
  self.assertAlmostEqual(t.calc_thresholds()[-1],54.4232,places=7)
 def test_19_energy_closure(self):
  self.assertLess(self.result['max_mono_energy_closure_eV'],2e-13)
  self.assertLess(self.result['probability_normalization_max'],3e-13)
 def test_20_source_finite_and_mean_upper(self):
  a=self.result['source_first_event_bounds']
  self.assertGreater(a['HeII_any']['high'],a['HeII_any']['mean'])
  self.assertLess(a['HeII_any']['high'],a['all_any']['high'])
  self.assertLess(a['HeII_ion']['high'],a['HeII_any']['high'])
 def test_21_constitutive_nonpromotions(self):
  self.assertTrue(self.result['source_conditional'])
  self.assertFalse(self.result['full_secondary_cascade'])
  self.assertEqual(self.result['production'],'HOLD')
  self.assertEqual(self.result['canonical_delta'],0)

if __name__=='__main__':unittest.main()
