from pathlib import Path
import sys,unittest,copy,math
from fractions import Fraction as Q
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from paired_contrast import contrast,refinement,assert_matched

def bindings():
    on={'mode':'LCS','research_model':'HH_ON04_COHORT_S0_LCS','geometry':'FLRW','dt_s':5e9,'end_s':8e11,'parent_sha256':'pinned','H':[1e-14]*3}
    off=copy.deepcopy(on);off['mode']='OFF';off['research_model']='HH_ON04_COHORT_S0_OFF'
    return on,off

class ContrastTests(unittest.TestCase):
    def test_exact_large_common_term_not_rounded_before_contrast_difference(self):
        self.assertEqual(refinement(1e16,0.,1e16,1.)['difference'],Q(-1))
    def test_actual_sign_is_on_minus_off(self):
        self.assertEqual(contrast(.25,.5),Q(-1,4))
    def test_shared_refinement_increment_cancels(self):
        r=refinement(1.25,1.,1.75,1.5)
        self.assertEqual(r['difference'],Q(0));self.assertEqual(r['on_increment'],Q(1,2))
    def test_zero_contrast_has_no_relative_accuracy_number(self):
        self.assertIsNone(refinement(.5,.5,.25,.25)['relative_change'])
    def test_nonfinite_not_an_accuracy_result(self):
        with self.assertRaises(ValueError):contrast(math.nan,0.)
    def test_bool_not_a_scientific_observable(self):
        with self.assertRaises(ValueError):contrast(True,0.)
    def test_changed_physical_grid_rejected(self):
        a,b=bindings();b['dt_s']=1e10
        with self.assertRaisesRegex(ValueError,'MATCHED_INPUT'):assert_matched(a,b)
    def test_two_on_runs_cannot_be_called_on_off(self):
        a,b=bindings();b['mode']='KS'
        with self.assertRaisesRegex(ValueError,'MATCHED_MODE'):assert_matched(a,b)
    def test_only_selector_and_model_name_may_differ(self):
        a,b=bindings();self.assertEqual(assert_matched(a,b),'MATCHED_INPUTS')
if __name__=='__main__':unittest.main()
