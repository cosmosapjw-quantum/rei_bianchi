import csv,sys,unittest
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from independent_decimal import check_decimal, check_stage_summary

class TestIndependentDecimal(unittest.TestCase):
 def test_crosscheck_60_selected_residuals(self):
  result=check_decimal(ROOT/'parent'/'full')
  self.assertEqual(result['decimal_residual_components_checked'],60)
  self.assertLess(result['max_normalized_abs_difference'],1e-65)
 def test_stage_sentinel_then_accepted(self):
  v=check_stage_summary(ROOT/'parent'/'full')
  self.assertEqual(v['step0_sentinel_rows'],9)
  self.assertEqual(v['accepted_stage_rows'],3456)
  self.assertEqual(v['positive_stage2_count_range'],[2440,2444])
  self.assertFalse(v['independent_rhs_certified'])

if __name__=='__main__':unittest.main()
