#!/usr/bin/env python3
"""Independent source-owner validations of source-complete threshold full193 computed data."""
import io,sys,json,hashlib,zipfile,unittest
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'code'))
import run_full,thermal_port
B=run_full.BINS;G=run_full.GROUPS
class TestFull(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  run_full.lock()
  cls.D=pd.read_csv(ROOT/'results'/'FS2010_FULL193_ARRIVAL_192.csv')
  cls.K=pd.read_csv(ROOT/'results'/'FS2010_FULL193_KERNEL_18528.csv')
  cls.T=pd.read_csv(ROOT/'results'/'FS2010_FULL193_HHE_TERMINAL_THERMAL_192.csv')
  cls.R=json.loads((ROOT/'results'/'RESULT.json').read_text())
  cls.inner,cls.em,cls.old=run_full.thresholds.unpack_owner()
  with zipfile.ZipFile(io.BytesIO(cls.inner)) as z:
   cls.orig=pd.read_csv(io.BytesIO(z.read('REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030/results/FIRST_FLIGHT_KERNEL.csv')))
  cls.w=cls.em.measuredwindow_2E1_emitted_pairs_rectangle_upper.to_numpy()
 def test_01_exact_parent_zip(self):
  self.assertEqual(hashlib.sha256((ROOT/'source'/'PR300_FULL.zip').read_bytes()).hexdigest(),run_full.EMBED_SHA)
 def test_02_actual_193_source_epochs_all(self):
  self.assertEqual(len(self.w),193);self.assertEqual(len(self.D),192);self.assertEqual(len(self.K),18528)
  self.assertEqual(len(set(self.K.emission_epoch)),192)
  self.assertEqual(set(self.K.emission_epoch),set(range(192)))
  self.assertFalse(self.K.duplicated(['emission_epoch','arrival_interval']).any())
  self.assertEqual(len(self.K),sum(192-i for i in range(192)))
 def test_03_zero_source_epoch0(self):
  self.assertEqual(self.w[0],0.0)
  x=self.K.loc[self.K.emission_epoch==0]
  self.assertEqual(len(x),192)
  for g in G:
   self.assertEqual(float(x[[f'{g}_{b}_counts_per_pair' for b in B]].to_numpy().sum()),0)
 def test_04_last_source_no_arrival(self):
  self.assertGreater(self.w[192],0.0)
  self.assertFalse((self.K.emission_epoch==192).any())
 def test_05_readonly_original_kernel_alignment(self):
  self.assertTrue(np.array_equal(self.K.emission_epoch.to_numpy(),self.orig.emission_epoch.to_numpy()))
  self.assertTrue(np.array_equal(self.K.arrival_interval.to_numpy()+1,self.orig.arrival_epoch.to_numpy()))
 def test_06_exact_187xx_original_species_counts(self):
  w=self.w[self.K.emission_epoch.to_numpy(dtype=int)]
  for g in G:
   n=sum(self.K[f'{g}_{b}_counts_per_pair'].to_numpy() for b in B)
   ref=self.orig[f'conditional_first_abs_{g}'].to_numpy()
   self.assertLess(float(np.max(abs((n-ref)*w))),2e-27)
   self.assertLess(abs(float(np.sum(n*w)/np.sum(ref*w)-1)),2e-13)
 def test_07_original_row_energy(self):
  w=self.w[self.K.emission_epoch.to_numpy(dtype=int)]
  n=sum(self.K[f'{g}_{b}_primary_e_eV_per_pair'].to_numpy() for g in G for b in B)
  ref=self.orig.conditional_primary_e_eV.to_numpy()
  self.assertLess(float(np.max(abs((n-ref)*w))),2e-26)
  self.assertLess(abs(float(np.sum(n*w)/np.sum(ref*w)-1)),1e-12)
 def test_08_arrival_positive_and_closed(self):
  n=sum(self.D[f'{g}_{b}_counts_per_b'].to_numpy() for g in G for b in B)
  e=sum(self.D[f'{g}_{b}_primary_e_eV_per_b'].to_numpy() for g in G for b in B)
  np.testing.assert_allclose(n,self.D.total_absorbed_ionizations_per_b,rtol=1e-12,atol=1e-24)
  np.testing.assert_allclose(e,self.D.total_primary_e_eV_per_b,rtol=1e-12,atol=1e-23)
  self.assertTrue(np.all(n>=0))
 def test_09_source_all_total(self):
  r=self.R['physics']
  self.assertLess(abs(r['relative_parent_energy_residual']),1e-12)
  self.assertLess(abs(r['relative_parent_event_residual']),1e-12)
  self.assertTrue(r['original_full_193_photoepoch_source_covered'])
 def test_10_fs_terminal_is_fraction_not_real_heat(self):
  heat=float(self.D.FS_low_e_heat_kinematic_eV_per_b.sum())
  e=float(self.D.total_primary_e_eV_per_b.sum())
  self.assertLess(abs(heat-8.581099847924098e-12)/heat,1e-12)
  self.assertLess(heat/e,1.0)
  self.assertIn('no E-x_i grid',self.R['qualifications']['FS2010'])
 def test_11_improved_previous_parent_bounds(self):
  self.assertGreater(float(self.D.FS_low_e_heat_kinematic_eV_per_b.sum()),8.54068904110878e-12)
  self.assertLess(float(self.D.FS_low_e_heat_kinematic_eV_per_b.sum()),8.875219810911833e-12)
  self.assertLess(self.R['physics']['secondary_H_I_event_discrete_safe_ceiling_per_baryon'],2.953300056205549e-12)
 def test_12_secondary_and_LiI_counterexample(self):
  self.assertGreater(self.R['physics']['LiI_worst_case_fourth_count_addendum_per_baryon'],0)
  self.assertLess(self.R['physics']['secondary_H_I_event_discrete_safe_ceiling_per_baryon'],self.R['physics']['secondary_H_I_energy_relaxed_bound_per_baryon'])
  self.assertGreater(float(self.D.Li_I_e54p42_plus_counts_per_b.sum()),0)
  self.assertEqual(sum(float(self.D[f'{g}_e54p42_plus_counts_per_b'].sum()) for g in G if g!='Li_I'),0.0)
 def test_13_thermal_eos_point_port_still_not_injected(self):
  x,s=thermal_port.compute()
  self.assertEqual(len(x),192)
  self.assertTrue((x.FS_model_terminal_temperature_rhs_coefficient_K_s>=0).all())
  self.assertTrue((x.FS_model_terminal_temperature_rhs_coefficient_K_s<=x.original_all_primary_unit_heat_temperature_rhs_cap_K_s+1e-25).all())
  self.assertLess(abs(s['whole_source_terminal_eV_per_baryon']-self.R['physics']['FS_model_terminal_sub10p2_heat_eV_per_baryon']),1e-23)
  self.assertIn('NOT_INJECTED_IN_FJ',x.source_status.iloc[-1])
 def test_14_no_dag_production_promote(self):
  x=self.R['qualifications']
  self.assertEqual(x['DAG']['CENTRAL'],'28/88');self.assertEqual(x['DAG']['WORKING'],'33/88')
  self.assertEqual(x['DAG']['F4_FAST'],'4/7');self.assertEqual(x['DAG']['CANONICAL_DELTA'],0)
  self.assertEqual(x['production'],'HOLD');self.assertEqual(x['IVP'],0)
 def test_15_original_no_merge_source(self):
  self.assertEqual(self.R['input_head'],'0e9024f92682bc3b7a0080cc86855cbddca8b0d9')
 def test_16_thermal_unit_conversion(self):
  ratio=self.T.FS_model_terminal_erg_per_Href_s*self.T.proper_interval_s*self.T.nHref_over_nb / 1.602176634e-12
  np.testing.assert_allclose(ratio,self.D.FS_low_e_heat_kinematic_eV_per_b,rtol=1e-13,atol=1e-25)
if __name__=='__main__':unittest.main(verbosity=2)
