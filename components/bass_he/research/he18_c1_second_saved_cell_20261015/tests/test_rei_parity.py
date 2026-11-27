import importlib.util,json,sys,tempfile,unittest,os
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'rei_supplier'))
from signed_parity import evaluate
DATA=ROOT/'rei_supplier/source'
class FivePartialParity(unittest.TestCase):
  @classmethod
  def setUpClass(cls):cls.result=evaluate(DATA)
  def test_actual_five_partial_cases_same_scale_and_charges(self):
    r=self.result
    self.assertEqual(r['equal_scale_factor'],'0.08873654701704167')
    self.assertEqual(len(r['sample_sha256']),5)
    self.assertEqual(len(r['observables']),5)
    self.assertTrue(r['owner_code_or_run_changed'] is False)
    self.assertEqual(r['comparison_coordinate'],'FIXED_STORED_SCALE_FACTOR_NOT_PROPER_TIME')
  def test_even_quadratic_ratio_is_diagnostic_not_detection(self):
    r=self.result
    for k in ['x_HII','x_HeII','electron','T']:
       ratio=Decimal(r['observables'][k]['even_full_over_even_half'])
       self.assertLess(abs(ratio-Decimal(4)),Decimal('.0002'))
       self.assertIsNone(r['observables'][k]['true_IVP_error'])
    self.assertEqual(r['scientific_admission'],'EXPLORATORY_ONLY')
    self.assertLess(abs(Decimal(r['observables']['x_HII']['odd_full_q'])),Decimal('1e-14'))
  def test_live_manifest_wrong_source_rejected(self):
    original=json.loads((DATA/'SAMPLE_MANIFEST.json').read_text())
    original['cases']['SHEAR_PLUS']['source_identity_sha256']='0'*64
    with tempfile.TemporaryDirectory() as d:
       dst=Path(d)
       for n in ('ZERO','SHEAR_PLUS','SHEAR_MINUS','SHEAR_HALF_PLUS','SHEAR_HALF_MINUS'):
          (dst/(n+'_display_samples.csv')).symlink_to((DATA/(n+'_display_samples.csv')).resolve())
       (dst/'SAMPLE_MANIFEST.json').write_text(json.dumps(original))
       with self.assertRaisesRegex(ValueError,'SOURCE_MISMATCH'):evaluate(dst)
if __name__=='__main__': unittest.main()
