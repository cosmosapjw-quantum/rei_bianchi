import csv,hashlib,json,math,unittest
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
from src.reconcile import compute, EH_J,KB_J

class SourcePhysicsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.res=ROOT/'results'
  cls.old=ROOT/'inputs/finite_difference'
  cls.sp=ROOT/'inputs/spectral'
  cls.summary=json.loads((cls.res/'SUMMARY.json').read_text())
  def read(p):
   with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
  cls.read=staticmethod(read)

 def test_both_source_archives_sha_are_recorded(self):
  provenance=json.loads((ROOT/'evidence/PROVENANCE.json').read_text())
  self.assertEqual(provenance['R38_spectral_SHA256'],'94a70bae5d7e2639b9ca99cb4433567e52f90baa01d4c9ad1eab354eef545be4')
  self.assertEqual(provenance['R38_finite_difference_SHA256'],'0b259c1ff0e619b56cf712e6729c970b1531daba2c4278f2455526e09a5a61b0')
  self.assertEqual(provenance['EPAPS_h3plus_SHA256'],'8dbf8b7e3852d02504ba92317f79593051d689f1357263ac0891a3a24084ed8c')
  for rel,sha in provenance['input_file_SHA256'].items():
   self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),sha,rel)

 def test_rows_and_keys(self):
  r=self.read(self.res/'R38_SPECTRAL_R37_H2_BRANCH_Q_19200.csv')
  s=self.read(self.res/'R38_SPECTRAL_R37_FIRST_EXIT_Q_1920.csv')
  c=self.read(self.res/'BO_FD_SPECTRAL_CHANNEL_CROSSCHECK_190.csv')
  self.assertEqual((len(r),len(s),len(c)),(19200,1920,190))
  self.assertEqual(len({(z['Tgas_K'],z['n_Hplus_cm_minus3'],z['z_boundary'],z['spin_policy'],z['initial_v0_J'],z['H2_final_J']) for z in r}),19200)

 def test_no_negative_probability_and_mass(self):
  r=self.read(self.res/'R38_SPECTRAL_R37_H2_BRANCH_Q_19200.csv')
  s=self.read(self.res/'R38_SPECTRAL_R37_FIRST_EXIT_Q_1920.csv')
  acc=defaultdict(float)
  for z in r:
   p=float(z['P_H2_J_before_first_exit'])
   self.assertGreaterEqual(p,0)
   key=tuple(z[v] for v in ('Tgas_K','n_Hplus_cm_minus3','z_boundary','spin_policy','initial_v0_J'))
   acc[key]+=p
  for z in s:
   key=tuple(z[v] for v in ('Tgas_K','n_Hplus_cm_minus3','z_boundary','spin_policy','initial_v0_J'))
   p=float(z['P_H2_before_first_exit'])
   self.assertLessEqual(p,1+1e-13)
   self.assertAlmostEqual(acc[key],p,delta=3e-13)
   self.assertAlmostEqual(float(z['P_exo_branch_per_initial_HD'])+float(z['P_endo_branch_per_initial_HD']),p,delta=3e-13)

 def test_energy_per_source_channel(self):
  r=self.read(self.res/'R38_SPECTRAL_R37_H2_BRANCH_Q_19200.csv')
  t=self.read(self.sp/'BO_ISOTOPE_THRESHOLDS_247.csv')
  lookup={(z['HD_v'],z['HD_J'],z['H2_v'],z['H2_J']):float(z['delta_E_hartree']) for z in t}
  for z in r:
   delta=lookup[('0',z['initial_v0_J'],'0',z['H2_final_J'])]
   self.assertAlmostEqual(float(z['Q_spectral_J']),-delta*EH_J,delta=1e-30)
   self.assertAlmostEqual(float(z['weighted_Q_spectral_J_per_initial_HD']),float(z['P_H2_J_before_first_exit'])*float(z['Q_spectral_J']),delta=1e-30)

 def test_zero_ground_threshold_is_not_electronic_depth(self):
  s=self.summary
  self.assertAlmostEqual(s['original_r38_spectral_threshold_00_K'],416.23192143147423,delta=3e-7)
  self.assertAlmostEqual(s['original_r38_FD_threshold_00_K'],416.2319911103885,delta=3e-7)
  self.assertEqual(s['exo_endothermic_channel_class_changes'],0)

 def test_reference_case_chemistry_not_modified(self):
  z=self.summary['reference_T105_n1000_z300_J2']
  self.assertAlmostEqual(float(z['P_H2_before_first_exit']),0.1938681645474435,delta=1e-14)
  self.assertAlmostEqual(float(z['conditional_Q_spectral_K']),-229.87936644715194,delta=1e-8)

 def test_output_manifest(self):
  manifest=json.loads((ROOT/'evidence/OUTPUT_SHA256.json').read_text())
  for name,sha in manifest.items():
   self.assertEqual(hashlib.sha256((self.res/name).read_bytes()).hexdigest(),sha)

if __name__=='__main__':unittest.main()
