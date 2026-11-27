from __future__ import annotations
import unittest, math,csv,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from exfor_source import (get_datasets,cross_section_rows,normalized_catalog,checksum,raw_source_metadata)
from physics_from_exfor import (prior_sigma_nb, measured_model_comparison,anchored_local_physics,
     obs_absorption_fraction, model_1958_integrated, polarization_energy_near_90,
     absorption_anchored_first_hit,model_photoabsorption_gap)
WORK=ROOT.parents[1];S=WORK/'private_source';D=ROOT/'data'

class TestSourceOwned(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.ds=get_datasets((S/'X4sShowX4StdOut.txt').read_text(errors='replace'))
    cls.obs=cross_section_rows(cls.ds,'M0484003')+cross_section_rows(cls.ds,'M0475003')
    cls.abs=cross_section_rows(cls.ds,'M0520002')
  def test_primary_hashes(self):
    self.assertEqual(checksum(S/'X4sShowX4StdOut.txt'),'09df36e79f6c050dd7b0c6ae434805a4957bedd2e5a7132479c1c94daa90dd5d')
    self.assertEqual(checksum(S/'e_007_04_0600.pdf'),'7cb9676493bfc68579e0ff015cc841c4f0d1a8b0c70b1e8b22a0ce90cc36b420')
  def test_exfor_structure(self):
    self.assertEqual(len(self.ds),84)
    self.assertEqual(len(normalized_catalog(self.ds)),2270)
    self.assertEqual(len(self.ds['L0138002']['rows']),216)
  def test_exact_direct_source_rows(self):
    a=cross_section_rows(self.ds,'M0475003');b=cross_section_rows(self.ds,'M0484003')
    self.assertEqual([(r['E_MeV'],r['sigma_nb']) for r in a],[(201.,2.41),(225.,1.29)])
    self.assertEqual([(r['E_MeV'],r['sigma_nb']) for r in b],[(223.,3520.),(239.,3040.)])
    self.assertAlmostEqual(b[0]['sys_nb'],176.,places=12)
  def test_non_cross_section_reaction_rejected(self):
    with self.assertRaises(ValueError):cross_section_rows(self.ds,'G4081002')
    with self.assertRaises(ValueError):cross_section_rows(self.ds,'L0138008')
  def test_inclusive_only_and_duplicate_versions(self):
    self.assertEqual([r['E_MeV'] for r in self.abs],[204.,216.,228.,240.])
    a={(r['EN'],r['DATA'],r['ERR-S']) for r in self.ds['M0520002']['rows']}
    b={(r['EN'],r['DATA'],r['ERR-S']) for r in self.ds['M0546002']['rows']}
    self.assertEqual((len(a),len(b),len(a&b),len(a-b),len(b-a)),(57,56,53,4,3))
    self.assertIn((395.,1332.,4.),a-b)
  def test_1958_original_table_sum_not_independent(self):
    q=model_1958_integrated();d={(r['channel'],r['energy_interval_MeV']):r for r in q}
    for c in ('npD','pT_plus_nHe3'):
      self.assertAlmostEqual(d[c,'<75']['observed_integrated_mb_MeV']+d[c,'75-170']['observed_integrated_mb_MeV'],d[c,'<170']['observed_integrated_mb_MeV'])
      self.assertIsNone(d[c,'<75']['cyburt2003_integrated_mb_MeV'])
    self.assertAlmostEqual(d['npD','75-170']['cyburt2003_integrated_mb_MeV'],2.809260518441752,places=8)
    self.assertAlmostEqual(d['pT_plus_nHe3','75-170']['cyburt2003_integrated_mb_MeV'],7.647646732784837,places=8)
  def test_model_source_ratios(self):
    d=measured_model_comparison(self.obs);m={(x['channel'],x['E_MeV']):x for x in d}
    self.assertAlmostEqual(m['pT',223.]['observed_over_model'],0.9475336395624201,places=9)
    self.assertAlmostEqual(m['dd',225.]['observed_over_model'],1.29/4.34,places=14)
    self.assertTrue(m['dd',225.]['source_sys_unreported'])
  def test_first_hit_physical_dimensions(self):
    r=anchored_local_physics(self.obs);self.assertEqual(len(r),12)
    for v in r:
      self.assertGreater(v['Gamma_competing_model_per_s'],0)
      self.assertGreater(v['H_per_s'],0)
      self.assertTrue(0<v['P_first_local_measured_channel']<1)
      self.assertGreaterEqual(v['P_first_stat_sigma'],0)
      self.assertTrue(v['not_cosmological_R_event'])
      if v['reaction']=='dd':self.assertAlmostEqual(v['N_D_first_local_per_gamma'],2*v['P_first_local_measured_channel'])
  def test_measured_inclusive_interpolated_shares(self):
    r=obs_absorption_fraction(self.obs,self.abs);self.assertEqual(len(r),3)
    byE={x['E_MeV']:x for x in r}
    self.assertAlmostEqual(byE[223.]['exclusive_to_inclusive_share'],3520/955416.6666666667,places=12)
    self.assertAlmostEqual(byE[225.]['exclusive_to_inclusive_share'],1.29/977250,places=16)
    self.assertTrue(byE[223.]['denominator_sys_treated_fully_correlated_within_1997'])
  def test_inclusive_alpha_sink(self):
    x=absorption_anchored_first_hit(self.obs,self.abs);self.assertEqual(len(x),9)
    for y in x:
      self.assertTrue(y['incl_interpolated_not_measured_exact_E'])
      self.assertGreater(y['source_inclusive_interp_nb'],y['source_exclusive_measured_nb'])
      self.assertLess(y['P_first_measured_exclusive_competing_all_alpha'],y['P_first_source_only_7channel'])
  def test_competing_model_incompleteness(self):
    q=model_photoabsorption_gap(self.obs,self.abs);self.assertEqual(len(q),3)
    self.assertTrue(all(.98<x['missing_fraction_if_four_models_assumed']<1. for x in q))
    self.assertTrue(all(x['unknown_other_channels_cannot_be_positively_estimated_from_this_without_valid_models'] for x in q))
  def test_compiler_polarization_sign_and_angles(self):
    p,delta=polarization_energy_near_90(self.ds);self.assertEqual(len(p),4)
    self.assertEqual(p[1]['A_compiler_signed'],-.8418)
    self.assertEqual(p[-1]['A_compiler_signed'],-.3063)
    self.assertAlmostEqual(delta['delta_A_250_minus_150_compiler_sign'],.5355)
    self.assertTrue(delta['unknown_source_covariance'])
    self.assertLess(abs(delta['theta_difference_deg']),1.)
  def test_emission_channel_not_pion(self):
    neutral=cross_section_rows(self.ds,'L0138002');self.assertEqual(len(neutral),87)
    self.assertTrue(all(150<=x['E_MeV']<=250 for x in neutral))
    self.assertEqual(self.ds['L0138002']['meta']['reaction'],'2-HE-4(G,X)0-P0-0,,SIG')
  def test_source_1958_metadata_not_assumed_valid(self):
    raw=raw_source_metadata((S/'X4sShowData.txt').read_text(errors='replace'),'M0999002')
    self.assertIn('CURVE',raw['first_360'])
  def test_source_data_outputs_exist(self):
    for f in ('EXFOR_CATALOG_2270.csv','MEASURED_EXCLUSIVE_4.csv','LOCAL_FIRST_HIT_SOURCE_ANCHORED_12.csv','INCLUSIVE_ABSORPTION_FIRST_HIT_9.csv','MODEL_VS_INCLUSIVE_GAP_3.csv','SCIENTIFIC_SUMMARY.json'):
      self.assertTrue((D/f).is_file(),f)
  def test_inherited_original_identity(self):
    from physics_from_exfor import ROOT
    import hashlib
    p=ROOT/'he_dd_flrw_firstcollision_20261031'/'src'/'physics_pr131.py'
    q=ROOT/'he_dd_flrw_firstcollision_20261031'/'src'/'transport.py'
    self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'cccdc3eeb3d4495c9648ce02d202af0f1d97bc85015a278b0696400d5ccb0345')
    self.assertEqual(hashlib.sha256(q.read_bytes()).hexdigest(),'ee9ec2e9190639dd12831ef9c75df0d9bec463602a9a90150ff2c4470a2483a9')
  def test_same_frozen_input_reproducible(self):
    r=anchored_local_physics(self.obs);s=anchored_local_physics(self.obs)
    self.assertEqual(r,s)

if __name__=='__main__':unittest.main()
