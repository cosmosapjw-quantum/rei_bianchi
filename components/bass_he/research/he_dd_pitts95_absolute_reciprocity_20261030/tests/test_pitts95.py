import hashlib
import math
import sys
import tempfile
import unittest
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import build_pitts95 as a

class MeasuredPitts95(unittest.TestCase):
 def test_exact_source_identity(self):
  raw,data=a.source(ROOT/'sources/C0621.x4')
  self.assertEqual(len(raw),3269)
  self.assertEqual(hashlib.sha256(raw).hexdigest(),a.SOURCE_SHA256)
  self.assertEqual([len(data[k]) for k in ('DA','Ay','Ayy')],[8,8,8])
 def test_source_tamper_fail_closed(self):
  raw=(ROOT/'sources/C0621.x4').read_bytes()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x4';p.write_bytes(raw[:-1]+b'!')
   with self.assertRaisesRegex(ValueError,'SOURCE_IDENTITY_MISMATCH'):a.source(p)
 def test_input_numerical_absolute_DA(self):
  _,d=a.source(ROOT/'sources/C0621.x4')
  self.assertEqual(d['DA'][0]['value'],F('2.02'))
  self.assertEqual(d['DA'][2]['value'],F('0.21'))
  self.assertEqual(d['DA'][7]['data_err'],F('0.17'))
 def test_beam_energy_matching_exact(self):
  k=a.invariants();self.assertEqual(k['s'],a.M*a.M+2*a.M*k['Egamma'])
 def test_spin_factor_direction_corrected(self):
  k=a.invariants()
  self.assertEqual(k['ordered']*k['capture_over_photo_ordered'],1)
  self.assertGreater(k['ordered'],1)
  self.assertLess(k['capture_over_photo_ordered'],1)
 def test_identical_final_D_event_half(self):
  k=a.invariants();self.assertEqual(2*k['event'],k['ordered'])
 def test_threshold_satisfied(self):
  k=a.invariants();self.assertGreater(k['q2'],0);self.assertGreater(k['k2'],0)
 def test_ordered_to_event_pair_lab_conserved(self):
  d=a.generate(ROOT);kt=float(a.invariants()['Egamma']-a.invariants()['Q'])
  for x in d['data']:
   self.assertAlmostEqual(float(x['conditional_photo_Kplus_MeV'])+float(x['conditional_photo_Kminus_MeV']),kt,delta=2e-10)
 def test_abs_norm_source_does_not_change_central_dag(self):
  d=a.generate(ROOT);self.assertEqual(d['DAG']['central'],'28/88');self.assertEqual(d['DAG']['HE_physical'],'14/18')
 def test_photo_only_conditional_no_rate(self):
  for x in a.generate(ROOT)['data']:
   self.assertFalse(x['photo_measured']);self.assertIsNone(x['event_rate']);self.assertIsNone(x['heat_rate'])
 def test_measured_analyzing_not_exchanged_for_cross_sections(self):
  d=a.generate(ROOT)
  self.assertEqual(d['data'][3]['Ay_measured'], '-0.461')
  self.assertEqual(d['data'][3]['Ayy_measured'], '0.359')
 def test_common_normalization_rankone_factorization(self):
  d=a.generate(ROOT);c=d['source_normalization_covariance_component_nb2_per_sr2'];x=d['data']
  for i in range(8):
   for j in range(8):
    expected=(F(x[i]['measured_capture_DA_nb_per_sr'])*F(x[j]['measured_capture_DA_nb_per_sr'])/625)
    self.assertAlmostEqual(float(c[i][j]),float(expected),delta=1e-14)
 def test_per_angle_inversion(self):
  d=a.generate(ROOT);fac=a.invariants()['ordered'];fac2=a.invariants()['event']
  for row in d['data']:
   sig=F(row['measured_capture_DA_nb_per_sr'])
   self.assertAlmostEqual(float(row['conditional_ordered_photo_DA_nb_per_sr']),float(sig*fac),delta=1e-12)
   self.assertAlmostEqual(float(row['conditional_event_fullsphere_photo_DA_nb_per_sr']),float(sig*fac2),delta=1e-12)
 def test_zero_total_measured_photodata(self):
  d=a.generate(ROOT);self.assertEqual(d['original_source']['measured_photodisintegration_rows'],0)
 def test_source_polarized_metadata(self):
  raw,_=a.source(ROOT/'sources/C0621.x4');self.assertIn(b'vector polarization',raw)
 def test_idempotent_outputs(self):
  p=ROOT/'results/PITTS95_SOURCE_RECIPROCITY_ATLAS.json';a.generate(ROOT);first=p.read_bytes();a.generate(ROOT);self.assertEqual(first,p.read_bytes())

if __name__=='__main__': unittest.main()
