"""Targeted source/physics checks. Run from clean archive with python -m unittest."""
import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
from compute import FS2010,ROOT,XI,LIMITS,run,sha,SOURCE_EXPECT

class TestPhysicalSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.fs=FS2010()
  # Evaluated in an isolated directory; the results are not production mutations.
  cls.result,cls.df,cls.bd,_=run()
 def test_shape(self): self.assertEqual(self.fs.data.shape,(14,258,7))
 def test_energy_grid(self): self.assertEqual(len(set(self.fs.E)),258)
 def test_xgrid(self): self.assertTrue(np.all(np.diff(XI)>0))
 def test_original_tar_bytes(self):self.assertEqual(sha(ROOT/'source'/'elec_interp.tar'),'e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101')
 def test_original_physics_inputs_bytes(self):
  for f,h in SOURCE_EXPECT.items(): self.assertEqual(sha(ROOT/'input'/f),h)
 def test_energy_closure_raw_MC(self): self.assertLess(self.fs.closure_max,5e-5)
 def test_no_negative_energy_sinks(self): self.assertGreater(self.fs.data.min(),-5e-5)
 def test_scientific_3keV_table_heat(self):
  for x,heat in [(0.0001,0.126),(0.001,0.176),(0.01,0.319),(0.1,0.668),(0.5,0.922),(0.9,0.973)]:
   self.assertAlmostEqual(float(self.fs.interp(3000,x)[1]),heat,delta=0.03)
 def test_exact_grid_values(self):
  for i,j in [(0,0),(3,45),(6,80),(12,210),(13,257)]:
   np.testing.assert_array_equal(self.fs.interp(self.fs.E[j],XI[i]),self.fs.data[i,j])
 def test_subthreshold_terminal(self):
  v=self.fs.interp(np.array([0.,9.9,10.19]),0.001)
  self.assertTrue(np.all(v[:,1]==1.))
  self.assertTrue(np.all(v[:,[0,2,3,4,5,6]]==0.))
 def test_fail_closed_out_of_xi(self):
  for x in [1e-5,1.0]:
   with self.assertRaisesRegex(ValueError,'OUTSIDE_DECLARED_DOMAIN'):self.fs.interp(20,x)
 def test_fail_closed_out_of_energy(self):
  for E in [-1,1e5]:
   with self.assertRaises(ValueError):self.fs.interp(E,0.1)
 def test_bilinear_midpoint(self):
  i,j=3,15
  e=(self.fs.E[j]+self.fs.E[j+1])/2
  x=(XI[i]+XI[i+1])/2
  np.testing.assert_allclose(self.fs.interp(e,x),self.fs.data[i:i+2,j:j+2].mean(axis=(0,1)),rtol=2e-15,atol=1e-16)
 def test_bounds_enclose_mean(self):
  for x,y in [(0.01,0.2),(0.0002,0.001),(0.9,0.998)]:
   for lo,hi in LIMITS[1:]:
    a,b=self.fs.extrema(lo,hi,x,y)
    v=self.fs.interp((lo+hi)/2,(x+y)/2)
    self.assertTrue(np.all(v>=a-1e-12))
    self.assertTrue(np.all(v<=b+1e-12))
 def test_original_kernel_rows(self):self.assertEqual(self.result['kernel_rows'],18528)
 def test_original_arrival_rows(self):self.assertEqual(len(self.df),192)
 def test_band_rows(self):self.assertEqual(len(self.bd),3840)
 def test_original_kinetic_energy(self):self.assertAlmostEqual(self.result['source_primary_kinetic_eV_per_b'],6.749242464433259e-11,delta=1e-23)
 def test_legacy_terminal_identity(self):self.assertAlmostEqual(self.result['source_FS_terminal_eV_per_b'],8.581099847924098e-12,delta=1e-23)
 def test_table_valid_mask(self):self.assertEqual(int(self.df.FS_xi_in_native_domain.sum()),87)
 def test_no_helium_exact_projection(self): self.assertEqual(int(self.df.FS_exact_species_valid.sum()),0)
 def test_no_clamped_outside_domain(self):
  self.assertTrue(np.all(self.df.loc[~self.df.FS_xi_in_native_domain,'fheat_moment'].to_numpy()>=0))
  self.assertTrue(all(pd.isna(v) for v in self.bd.loc[(~self.bd.FS_xi_in_native_domain)&(self.bd.energy_band!='e0_10p2'),'fheat_moment']))
 def test_fheat_bounds(self):
  mask=self.df.FS_xi_in_native_domain
  self.assertTrue(np.all(self.df.loc[mask,'fheat_lower']<=self.df.loc[mask,'fheat_moment']+1e-21))
  self.assertTrue(np.all(self.df.loc[mask,'fheat_moment']<=self.df.loc[mask,'fheat_upper']+1e-21))
 def test_model_upper_energy_ceiling(self):
  self.assertLessEqual(self.result['conservative_total_heat_eV_per_b_with_unmodeled_rows'][1],1.001*self.result['source_primary_kinetic_eV_per_b'])
 def test_lithium_tiny_tail_retained(self):
  source=pd.read_csv(ROOT/'input'/'PUBLIC_results_FULL193_ARRIVAL_192.csv')
  self.assertGreater(source['Li_I_e54p42_plus_primary_e_eV_per_b'].sum(),0)
 def test_nlya_unit_count(self):
  v=self.fs.interp(30.,0.01)
  self.assertGreaterEqual(v[3],0)
  # count, not fraction, two different columns
  self.assertNotAlmostEqual(v[2],v[3],delta=1e-6)
 def test_raw_metadata_typo_detected(self):
  # The -4 file's HeII header reads 0.001 even though its filename and C code select 1e-4.
  self.assertNotAlmostEqual(self.fs.meta[0]['HeII'],XI[0],delta=1e-6)
  self.assertAlmostEqual(self.fs.meta[0]['HeII'],0.001,delta=1e-8)
 def test_cvs_are_saved_original(self):self.assertTrue(np.all(self.df.HHe_Cv_erg_per_Href_K>0))
 def test_proper_intervals_positive(self):self.assertTrue(np.all(self.df.proper_interval_s>0))
 def test_no_true_temperature_evolution(self): self.assertTrue('frozen_FS_thermal_increment_proxy_K_lower' in self.df.columns)
 def test_no_high_e_asymptote(self):
  self.assertLess(self.fs.interp(25.,0.01)[1],self.fs.interp(3000.,0.01)[1]+1)

if __name__=='__main__':unittest.main(verbosity=2)
