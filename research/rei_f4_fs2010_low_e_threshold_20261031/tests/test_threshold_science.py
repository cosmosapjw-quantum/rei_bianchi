#!/usr/bin/env python3
"""Scoped scientific acceptance on actual frozen PR287/297 source numerical rows."""
from pathlib import Path
import unittest,hashlib,sys,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import thresholds
SEL=json.loads((ROOT/'evidence'/'SELECTION.json').read_text())
RES=json.loads((ROOT/'results'/'RESULT.json').read_text())
P=RES['physics'];Q=RES['qualification']
D=pd.read_csv(ROOT/'results'/'FS2010_THRESHOLD_SELECTED_ARRIVAL_192.csv')
K=pd.read_csv(ROOT/'results'/'FS2010_THRESHOLD_SELECTED_KERNEL.csv')
GROUPS=['H_I','He_I','He_II','Li_I']
BINS=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
class TestPhysics(unittest.TestCase):
 def test_01_original_input_source_sha256(self):thresholds.check_sources()
 def test_02_source_selection(self):
  self.assertEqual(len(SEL['indices']),30);self.assertEqual(len(set(SEL['indices'])),30)
  self.assertGreater(SEL['coverage_fraction'],.994);self.assertLess(SEL['coverage_fraction'],1)
 def test_03_actual_epoch_counts(self):
  self.assertEqual(len(D),192);self.assertEqual(len(K),sum(192-k for k in SEL['indices']))
  self.assertEqual(len(K),3554)
 def test_04_kernel_ids_no_duplicates(self):
  self.assertFalse(K.duplicated(['emission_epoch','arrival_interval']).any())
  self.assertEqual(sorted(K.emission_epoch.unique()),SEL['indices'])
  self.assertTrue(np.all(K.arrival_interval>=K.emission_epoch))
 def test_05_all_arrivals_boundaries(self):
  self.assertEqual(D.arrival_interval.tolist(),list(range(192)))
  self.assertTrue((D.z_high>D.z_low).all())
 def test_06_positive_energy_by_bins(self):
  for g in GROUPS:
   for s in BINS:
    self.assertGreaterEqual(float(D[f'{g}_{s}_counts_per_b'].min()),-1e-25)
    self.assertGreaterEqual(float(D[f'{g}_{s}_primary_e_eV_per_b'].min()),-1e-24)
 def test_07_energy_sum_by_bins(self):
  per_arr=np.zeros(len(D))
  for g in GROUPS:
   for s in BINS:per_arr+=D[f'{g}_{s}_primary_e_eV_per_b'].to_numpy()
  np.testing.assert_allclose(per_arr,D.total_primary_e_eV_per_b,rtol=2e-12,atol=2e-24)
 def test_08_counts_sum_by_bins(self):
  per_arr=np.zeros(len(D))
  for g in GROUPS:
   for s in BINS:per_arr+=D[f'{g}_{s}_counts_per_b'].to_numpy()
  np.testing.assert_allclose(per_arr,D.total_absorbed_ionizations_per_b,rtol=2e-12,atol=2e-25)
 def test_09_parent_hydrogen_photon_replay(self):
  for g in GROUPS:self.assertLess(abs(P['parent_AGG_photon_counts_reference_residuals'][g]['relative_residual']),1e-12)
 def test_10_parent_photo_energy_replay(self):self.assertLess(abs(P['parent_AGG_total_electron_energy_relative_residual']),1e-12)
 def test_11_parent_count_replay(self):self.assertLess(abs(P['parent_AGG_photo_counts_relative_residual']),1e-12)
 def test_12_positive_omitted_source(self):
  self.assertGreater(P['missing_primary_eV_per_b_parent_provenance'],0)
  self.assertAlmostEqual(P['missing_primary_eV_per_b_parent_provenance']+P['computed_covered_primary_eV_per_b'],P['PR297_total_primary_eV_per_b'],places=21)
 def test_13_fs_terminal_heating_bounds(self):
  low,high=P['FS_assigned_sub10p2_global_energy_bracket_eV_per_b']
  self.assertGreater(low,0);self.assertGreaterEqual(high,low)
  self.assertLessEqual(high,P['PR297_total_primary_eV_per_b'])
  self.assertAlmostEqual(low,float(D.FS_low_e_heat_kinematic_eV_per_b.sum()),places=21)
 def test_14_fraction_bounds(self):
  lo,hi=P['FS_assigned_sub10p2_global_heat_fraction_bracket']
  self.assertGreater(lo,.12);self.assertLess(hi,.14);self.assertLess(lo,hi)
 def test_15_secondary_tightening(self):
  self.assertLess(P['global_discrete_H_ionization_secondary_ceiling_per_b'],P['global_continuous_secondary_ceiling_PR297_per_b'])
  self.assertGreater(P['covered_LiI_fourth_secondary_worstcase_addendum_per_b'],0)
 def test_16_heii_secondary_hhe_excluded(self):
  self.assertEqual(P['covered_secondary_HeII_kinematically_eligible_events_from_HHe_primary_per_b'],0)
  self.assertTrue(P['HHe_absorber_primary_cannot_secondary_HeII'])
 def test_17_rare_lii_fourth_channel_preserved(self):
  self.assertGreater(P['covered_secondary_HeII_kinematically_eligible_events_from_LiI_primary_per_b'],0)
  self.assertFalse(P['all_absorbers_secondary_HeII_impossible'])
 def test_18_frozen_production_and_dag(self):
  self.assertEqual(Q['DAG']['WORKING'],'33/88');self.assertEqual(Q['DAG']['CENTRAL'],'28/88');self.assertEqual(Q['DAG']['F4_FAST'],'4/7');self.assertEqual(Q['DAG']['CANONICAL_DELTA'],0)
  self.assertTrue(Q['no_new_IVP']);self.assertEqual(Q['production'],'HOLD')
 def test_19_no_fs_high_E_table_fabrication(self):
  self.assertIn('sub-10.2',Q['model']);self.assertIn('NOT_ACQUIRED',Q['FS_ambient_ion_fraction'])
 def test_20_fst_threshold_exact(self):
  self.assertEqual(float(thresholds.THRESHOLDS[0]),10.2)
  self.assertAlmostEqual(P['max_HHe_initial_primary_e_eV'],47.32412484785,places=10)
 def test_21_nonnegative_rate(self):
  self.assertTrue((D.total_primary_e_eV_per_b>=0).all());self.assertTrue((D.total_absorbed_ionizations_per_b>=0).all())
 def test_22_multiple_original_physical_events(self):
  self.assertGreater(float(D.total_absorbed_ionizations_per_b.sum()),1e-12)
if __name__=='__main__':unittest.main(verbosity=2)
