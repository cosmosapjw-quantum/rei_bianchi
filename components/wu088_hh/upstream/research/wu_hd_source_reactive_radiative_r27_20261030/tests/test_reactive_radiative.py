import unittest
import sys
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.reactive_radiative import *
GL=ROOT/'sources/GL2022_700_SOURCE.json'
A=ROOT/'sources/REC161_LAMDA_A_TRANSCRIPTION_REF.json'
class TestScientificR27(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.result=compute(GL,A);cls.rows=cls.result['source_rows']
 def test_source_hash(self):self.assertEqual(self.result['sources']['GL2022_700_token_tensor_sha256'],R26_BLOB_SHA256)
 def test_60_rows(self):self.assertEqual(len(self.rows),60)
 def test_10_nodes(self):self.assertEqual(len({r['T_K'] for r in self.rows}),10)
 def test_raw_spin_physical(self):
  a=next(r for r in self.rows if (r['T_K'],r['HD_initial_J'])==(105,2))
  self.assertEqual(a['status'],'SOURCE_POSITIVE_TRANSCRIBED_A')
  self.assertLess(abs(Decimal(a['Eq6_7_spin_effective_K_source_partial_cm3_s'])-Decimal('1.30461670021e-10')),Decimal('1e-19'))
 def test_ncrit(self):
  a=next(r for r in self.rows if (r['T_K'],r['HD_initial_J'])==(105,2))
  self.assertLess(abs(Decimal(a['critical_Hplus_density_spin_cm_neg3'])-Decimal('3954.4')),Decimal('0.5'))
 def test_a_units(self):
  a=next(r for r in self.rows if (r['T_K'],r['HD_initial_J'])==(105,1))
  self.assertEqual(Decimal(a['A_J_to_Jminus1_s_inv']),Decimal('5.442e-8'))
 def test_J5_suspect(self):
  for row in self.rows:
   if row['HD_initial_J']==5:
    self.assertFalse(row['critical_Hplus_density_spin_cm_neg3'])
    self.assertTrue(row['status'].startswith('SOURCE_SUSPECT') or row['status']=='PRINTED_ZERO_CENSORED')
 def test_2505_flag(self):
  a=next(r for r in self.rows if (r['T_K'],r['HD_initial_J'])==(2505,3))
  self.assertEqual(a['status'],'SOURCE_SUSPECT_EXPONENT');self.assertEqual(a['critical_Hplus_density_spin_cm_neg3'],'')
 def test_15_printed_zero_gate(self):
  self.assertTrue(any(r['status']=='PRINTED_ZERO_CENSORED' for r in self.rows))
  self.assertTrue(all(not r['critical_Hplus_density_spin_cm_neg3'] for r in self.rows if r['status']=='PRINTED_ZERO_CENSORED'))
 def test_no_incorrect_interpolation(self):
  self.assertTrue(self.result['physics']['no_thermal_interpolation'])
 def test_laplace_upper(self):
  t=Decimal(self.result['threshold_consistency']['theta_laplace_upper_meV'])
  self.assertLess(abs(t-Decimal('15.186303821758897273688')),Decimal('1e-14'))
 def test_ratio_physical_candidates(self):
  c=self.result['threshold_consistency']['candidate_cases']
  self.assertEqual(len(c),2)
  self.assertGreater(Decimal(c[0]['observed_over_allowed']),5)
  self.assertGreater(Decimal(c[1]['observed_over_allowed']),25)
 def test_null_gates(self):
  q=self.result['scope'];self.assertIsNone(q['physical_Q']);self.assertIsNone(q['owner_ACK']);self.assertIsNone(q['native_PES_threshold'])
 def test_wrong_source_fails(self):
  import tempfile, json
  j=json.loads(GL.read_text());j['tokens_jprime_j_T'][1][2][0]='4.00(14)'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.json';p.write_text(json.dumps(j))
   with self.assertRaises(SourceProblem):source_import(p,A)
 def test_rec_source_tamper_fails(self):
  import tempfile, json
  j=json.loads(A.read_text());j['radiative_j_to_j_minus_1_A_per_second']['2']='5.160E-07'
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad_rec.json';p.write_text(json.dumps(j))
   with self.assertRaises(SourceProblem):source_import(GL,p)
 def test_printed_zero_unqualified(self):self.assertIsNone(token_value('0.00(00)'))
if __name__=='__main__':unittest.main()
