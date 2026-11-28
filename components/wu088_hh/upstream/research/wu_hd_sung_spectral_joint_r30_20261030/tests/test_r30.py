import copy, csv, hashlib, json, math, tempfile, unittest, zipfile
from pathlib import Path
import numpy as np
from src import spectral as s

class R30SourcePhysics(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.n,cls.rows,cls.lines,cls.products=s.build_atlas();cls.old=cls.n.load_grid();cls.new=s.get_grid(cls.old)
 def test_01_parent_original_sha_and_restore(self):
  p=s.ROOT/'archive'/s.R29_NAME
  self.assertEqual(s.sha_file(p),s.R29_SHA)
  with zipfile.ZipFile(p) as z:
   self.assertIsNone(z.testzip())
   self.assertEqual(len(z.namelist()),78)
 def test_02_source_and_primary_provenance(self):
  v=s.get_sung();self.assertEqual(s.sha_file(s.ROOT/'sources'/s.SUNG_SOURCE),s.SUNG_SOURCE_SHA)
  self.assertEqual(v['source_git_blob'],'23626dd9a77aa4e6214f6f9c792ea18270b3940c')
  self.assertEqual(v['reference_doi'],'10.1016/j.jqsrt.2022.108412')
  self.assertIs(True,v['fit_uncertainty_not_total_uncertainty'])
 def test_03_tamper_guard(self):
  before=s.SUNG_SOURCE_SHA
  s.SUNG_SOURCE_SHA='0'*64
  try:
   with self.assertRaises(s.SourceIntegrityError):s.get_sung()
  finally:s.SUNG_SOURCE_SHA=before
 def test_04_2011_and_sung_ladder_diff(self):
  self.assertEqual(self.new.energies_cm1[0],0)
  for j in range(1,5):self.assertAlmostEqual(self.new.energies_cm1[j]-self.new.energies_cm1[j-1],s.SOURCE_LINE_VALUES[j-1],12)
  self.assertAlmostEqual(self.new.energies_cm1[4]-self.old.energies_cm1[4],sum(s.SOURCE_LINE_VALUES)-self.old.energies_cm1[4],12)
 def test_05_unchanged_source_chemistry_collisions_A(self):
  self.assertIs(self.new.q,self.old.q)
  self.assertIs(self.new.down,self.old.down)
  self.assertIs(self.new.A,self.old.A)
  self.assertEqual(len(self.old.q),350)
  self.assertEqual(len(self.old.down),70)
 def test_06_case_count(self):
  self.assertEqual(len(self.rows),210)
  self.assertEqual(len(self.lines),840)
  self.assertEqual(len(self.products),2100)
 def test_07_qualified_exact_temperature_grid(self):
  self.assertEqual(set(q['T_K'] for q in self.rows),set(s.load_r29().TEMPS))
  self.assertEqual(set(q['policy'] for q in self.rows),set(self.n.POLICIES))
 def test_08_first_photon_probability_partition(self):
  for q in self.rows:
   self.assertAlmostEqual(q['photons_at_least_one_probability']+q['no_photon_exchange_probability'],1,places=10)
   self.assertTrue(0<=q['photons_at_least_one_probability']<=1)
 def test_09_line_counts_and_positive_energy(self):
  for q in self.rows:
   ls=[l for l in self.lines if (l['T_K'],l['policy'],l['n_over_ncrit_J2'],l['initial_J'])==(q['T_K'],q['policy'],q['n_over_ncrit_J2'],q['initial_J'])]
   self.assertEqual(len(ls),4)
   self.assertAlmostEqual(sum(r['expected_photons_this_line'] for r in ls),q['expected_photons'],places=10)
   self.assertAlmostEqual(sum(r['probability_this_is_first_photon'] for r in ls),q['photons_at_least_one_probability'],places=10)
   self.assertAlmostEqual(sum(r['integrated_line_radiation_energy_J'] for r in ls),q['integrated_photon_energy_J_per_initial_HD'],places=28)
   for l in ls:
    self.assertGreater(l['fit_line_photon_frequency_Hz'],0)
    self.assertGreater(l['fit_line_wavelength_um'],0)
    self.assertGreater(l['expected_photons_this_line'],0)
 def test_10_photon_product_joint_partition(self):
  for q in self.rows:
   pr=[p for p in self.products if (p['T_K'],p['policy'],p['n_over_ncrit_J2'],p['initial_J'])==(q['T_K'],q['policy'],q['n_over_ncrit_J2'],q['initial_J'])]
   self.assertEqual(len(pr),10)
   self.assertAlmostEqual(sum(p['probability_restricted_product_Jprime'] for p in pr),1,places=9)
   self.assertAlmostEqual(sum(p['joint_probability_no_photon_and_product'] for p in pr),q['no_photon_exchange_probability'],places=9)
   self.assertAlmostEqual(sum(p['joint_probability_at_least_one_photon_and_product'] for p in pr),q['photons_at_least_one_probability'],places=9)
   for p in pr:
    self.assertGreaterEqual(p['joint_probability_at_least_one_photon_and_product'],-1e-12)
    self.assertAlmostEqual(p['joint_probability_at_least_one_photon_and_product']+p['joint_probability_no_photon_and_product'],p['probability_restricted_product_Jprime'],places=9)
 def test_11_first_event_photon_and_reaction_equivalence(self):
  T=105;P='Eq6-7_spin_effective';nH=self.n.reference_density(self.old,T,P)
  G,GC,G0,_=self.n.assemble(self.new,T,P,nH)
  e=np.zeros(5);e[2]=1
  m0=np.linalg.solve(-G0,e)
  prod=np.column_stack([nH*self.n.reaction_vector(self.new,T,j,P) for j in range(5)])@m0
  self.assertAlmostEqual(float(prod.sum()+sum(self.new.A[j]*m0[j] for j in range(1,5))),1,places=11)
 def test_12_reference_105K_spin(self):
  q=next(q for q in self.rows if q['T_K']==105 and q['policy']=='Eq6-7_spin_effective' and q['n_over_ncrit_J2']==1. and q['initial_J']==2)
  self.assertAlmostEqual(q['nHplus_cm3'],3954.41818210718,places=5)
  self.assertAlmostEqual(q['photons_at_least_one_probability'],0.47362861731084116,places=12)
  self.assertAlmostEqual(q['expected_photons'],0.8880279503111301,places=12)
  self.assertAlmostEqual(q['integrated_photon_energy_J_per_initial_HD'],2.580602925218754e-21,places=29)
 def test_13_original_2011_source_restored_not_mutated(self):
  self.assertAlmostEqual(self.old.energies_cm1[4],883.163755,places=6)
  self.assertAlmostEqual(self.new.energies_cm1[4],sum(s.SOURCE_LINE_VALUES),places=6)
 def test_14_no_raw_EMAA_or_physical_Q_claim(self):
  data=json.loads((s.ROOT/'results'/'SUMMARY.json').read_text())
  self.assertFalse(data['EMAA_original_ASCII_bytes_acquired'])
  self.assertIsNone(data['physical_Q'])
  self.assertIsNone(data['PES_native_threshold'])
  self.assertIsNone(data['owner_ACK'])
  self.assertEqual(data['central_DAG'],{'done':34,'total':49})
 def test_15_reported_fit_not_full_uncertainty(self):
  doc=s.get_sung()
  self.assertTrue(doc['fit_uncertainty_not_total_uncertainty'])
  self.assertFalse('covariance' in doc and isinstance(doc['covariance'],list))
 def test_16_model_full_markov_energy_is_not_gas_cooling(self):
  for q in self.rows:
   self.assertFalse(q['is_full_cosmological_cooling'])
   self.assertGreater(q['integrated_photon_energy_J_per_initial_HD'],0)
 def test_17_consistent_before_and_after_source_grid(self):
  for T in self.n.TEMPS:
   for pol in self.n.POLICIES:
    self.assertEqual(self.n.reference_density(self.new,T,pol),self.n.reference_density(self.old,T,pol))
 def test_18_csv_json_byte_rebuild(self):
  with tempfile.TemporaryDirectory() as d:
   s.main if False else None
   s.write_csv(Path(d)/'lines.csv',self.lines)
   s.write_csv(Path(d)/'joint.csv',self.products)
   self.assertEqual((Path(d)/'lines.csv').read_bytes(),(s.ROOT/'results'/'R30_PHOTON_ATLAS_840.csv').read_bytes())
   self.assertEqual((Path(d)/'joint.csv').read_bytes(),(s.ROOT/'results'/'R30_RESTRICTED_H2_JOINT_2100.csv').read_bytes())
 def test_19_positive_m_matrix(self):
  for T in self.n.TEMPS:
   for pol in self.n.POLICIES:
    nH=self.n.reference_density(self.new,T,pol)
    G,_,G0,_=self.n.assemble(self.new,T,pol,nH)
    self.assertLess(np.max(G.sum(axis=0)),0)
    self.assertLess(np.max(G0.sum(axis=0)),0)
    self.assertTrue(np.all(np.linalg.eigvals(G).real<0))
    self.assertTrue(np.all(np.linalg.eigvals(G0).real<0))
 def test_20_no_1950_or_2505_or_1505_temperature_included(self):
  self.assertEqual(tuple(self.n.TEMPS),(55,105,255,505,1005,2005,3005))

if __name__=='__main__':unittest.main()
