import unittest, tempfile, shutil, hashlib, sys, json, math, csv
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import build_inverse_dd_atlas as b

class OriginalInverseDataTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=b.checked_sources(ROOT)
  cls.rows=b.records(ROOT)
  cls.cross=b.lowE_forward_map(cls.raw)

 def test_all_original_source_immutable_sha_git(self):
  self.assertEqual(set(self.raw),{'C0122','A1256','M0011','M0826'})
  self.assertEqual(b.SOURCE['C0122'][1],'ac638ddbea7795b281ab8494d3e75a62606b3f6d')
 def test_tamper_stops_both_by_sha_and_git_blob(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'sources').mkdir()
   for k in b.SOURCE: shutil.copy(ROOT/'sources'/f'{k}.x4',p/'sources'/f'{k}.x4')
   f=p/'sources/C0122.x4';f.write_bytes(f.read_bytes().replace(b' 30.',b' 31.',1))
   with self.assertRaises(AssertionError): b.checked_sources(p)
 def test_exact_independent_original_record_count_and_subentries(self):
  self.assertEqual(len(self.rows),41)
  self.assertEqual({sub:sum(x['EXFOR_subentry']==sub for x in self.rows) for sub in b.REGISTRY},
  {'C0122002':6,'C0122003':8,'C0122004':11,'C0122005':4,'A1256002':6,'A1256003':6})
 def test_no_double_count_as_independent(self):
  self.assertEqual(sum(x['EXFOR_entry']=='C0122' for x in self.rows),29)
  self.assertEqual(sum(x['EXFOR_entry']=='A1256' for x in self.rows),12)
 def test_relative_cross_sections_are_not_absolute(self):
  rel=[x for x in self.rows if x['observable_source_type']=='capture_REL_DA']
  self.assertEqual(len(rel),14)
  self.assertTrue(all(x['source_data_unit']=='NO-DIM' and x['source_absolute_capture_sigma'] is False for x in rel))
  self.assertTrue(all(x['source_norm']=='REL only' for x in rel))
 def test_partial_measured_cross_section_has_correct_units(self):
  a=[x for x in self.rows if x['observable_source_type']=='capture_PAR_DA']
  self.assertEqual(len(a),6)
  self.assertEqual(Decimal(a[0]['value']),Decimal('1.405E-05'))
  self.assertEqual(Decimal(a[0]['value_nb_per_sr']),Decimal('14.05'))
  self.assertEqual(Decimal(a[0]['err_nb_per_sr']),Decimal('.7176'))
  self.assertTrue(all(x['source_absolute_capture_sigma'] is False and x['source_measured_capture_partial_DA'] for x in a))
 def test_original_polarized_components_unchanged(self):
  pol=[x for x in self.rows if x['observable_source_type']=='capture_POL_ANA_two_components']
  tensor=[x for x in self.rows if x['observable_source_type']=='capture_TAP_polarization']
  self.assertEqual((len(pol),len(tensor)),(15,6))
  self.assertEqual([Decimal(x['value']) for x in pol[:2]],[Decimal('-0.08'),Decimal('-0.03')])
  self.assertEqual([Decimal(x['value_component2']) for x in pol[:2]],[Decimal('0.22'),Decimal('0.33')])
  self.assertEqual(Decimal(tensor[0]['value']),Decimal('-.2118'))
 def test_input_deuteron_lab_energy_maps_to_corresponding_alpha_rest_photon(self):
  ref=[('9.7',28.803787555005634),('20',33.986735465363569),('30',39.01872372784700),('50',49.082700252813866)]
  for val,target in ref:
   d=b.energies(Decimal(val));self.assertAlmostEqual(float(d['equivalent_Egamma_He_rest_MeV']),target,places=11)
 def test_kinematic_s_and_q(self):
  for E in ['9.7','20','30','50']:
   d=b.energies(Decimal(E));s=Decimal(d['s_MeV2']);q=Decimal(d['capture_CM_D_momentum_MeV_over_c']);k=Decimal(d['capture_CM_photon_momentum_MeV_over_c']);eg=Decimal(d['equivalent_Egamma_He_rest_MeV'])
   self.assertLess(abs(q*q - (s/4 - b.M_D**2)),Decimal('1e-27'))
   self.assertLess(abs(eg-(s-b.M_ALPHA**2)/(2*b.M_ALPHA)),Decimal('1e-27'))
   self.assertTrue(k>0)
 def test_distinct_photon_axes_not_assigned_to_raw_measured_capture_points(self):
  self.assertTrue(all(x['mapped_Egamma_is_derived'] and x['reaction_direction']=='D + D -> He4 + gamma' for x in self.rows))
 def test_measured_near90_relative_suppression_and_box(self):
  x=b.near_ninety_suppression(self.rows)
  self.assertEqual(len(x),2)
  self.assertAlmostEqual(float(x[0]['dimensionless_near90_to_shoulder']),.049/1.88,places=14)
  self.assertAlmostEqual(float(x[1]['dimensionless_near90_to_shoulder']),.06/1.60,places=14)
  self.assertLess(Decimal(x[0]['source_cartesian_1sigma_box_upper']),Decimal('.05'))
  self.assertLess(Decimal(x[1]['source_cartesian_1sigma_box_upper']),Decimal('.05'))
  self.assertTrue(all(not y['claimed_joint_confidence_interval'] for y in x))
 def test_source_relative_mirror_pair_witnesses_not_independent(self):
  r=b.symmetry_witnesses(self.rows)
  self.assertEqual(len(r),7)
  self.assertTrue(all(abs(Decimal(x['angle_sum_deg'])-180)<Decimal('.5') for x in r))
  self.assertTrue(all(x['mirror_rows_independent_measurements']=='NOT_ESTABLISHED' for x in r))
 def test_mirror_odd_contrast_small_but_not_proof(self):
  r=b.symmetry_witnesses(self.rows)
  self.assertTrue(all(abs(Decimal(x['odd_contrast_fraction'])) < Decimal('0.02') for x in r))
 def test_forward_source_overlap_only_not_numeric_sigma_substitution(self):
  c=self.cross
  self.assertEqual(len(c),4)
  self.assertEqual(c[0]['M0011002_bracketing_measured_SIG_energies_MeV'],['28','30'])
  self.assertEqual(c[2]['M0011002_bracketing_measured_SIG_energies_MeV'],['38','40'])
  self.assertEqual(len(c[2]['M0826002_reported_original_SIG_bins_containing_energy']),1)
  self.assertEqual(c[3]['M0011002_bracketing_measured_SIG_energies_MeV'],['47.5','52.5'])
 def test_result_reproducibility_and_safe_claims(self):
  r=b.write_result(ROOT)
  self.assertEqual(len(r['original_records']),41)
  self.assertIsNone(r['assertions']['photo_disintegration_absolute_sigma'])
  self.assertIsNone(r['assertions']['event_rate'])
  self.assertIsNone(r['assertions']['heat_rate'])
  self.assertFalse(r['assertions']['L4'])
 def test_csv_is_41_source_records(self):
  b.write_result(ROOT)
  with (ROOT/'results/INVERSE_DD_EXFOR_REAL_MEASUREMENTS_41.csv').open() as f:
   x=list(csv.DictReader(f))
  self.assertEqual(len(x),41)
  self.assertEqual(len([z for z in x if z['source_data_unit']=='MB/SR']),6)
 def test_1993_error_semantics_are_not_pure_statistical(self):
  self.assertIn('background',self.raw['C0122'])
  self.assertIn('beam polarization',self.raw['C0122'])
 def test_1984_partial_is_curve_not_tabular_primary_raw_instrument_counts(self):
  self.assertIn('STATUS     (CURVE',self.raw['A1256'])
  self.assertIn('MONITOR    (1-H-2(D,G)2-HE-4,,DA)',self.raw['A1256'])
 def test_no_fake_absolute_from_1993_and_1984(self):
  self.assertEqual(sum(z['source_absolute_capture_sigma'] for z in self.rows),0)
  self.assertTrue(all(z['source_absolute_breakup_sigma']==False for z in self.rows))

if __name__=='__main__': unittest.main()
