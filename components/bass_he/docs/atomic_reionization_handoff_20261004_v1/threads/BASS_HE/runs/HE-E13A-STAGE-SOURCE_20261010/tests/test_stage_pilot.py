"""Stage-input pilot exactness, negative controls, and native shadow byte parity."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from stage_witness_reader import read_stage_rows, WitnessError, validate_stage_rows

class TestStageWitness(unittest.TestCase):
 def test_pilot_stage_rows(self):
  for mode in ('OFF','KF','GM'):
   base=ROOT/'evidence'/'pilot'/mode
   r=read_stage_rows(base/'OWNER_STAGE_INPUTS.csv')
   self.assertEqual(len(r),2)
   d=validate_stage_rows(r,base/'OWNER_SELECTED_RCT.csv',base/'OWNER_INTERNAL_5.csv')
   self.assertEqual(d['stage_records'],2)
   self.assertEqual(d['missing_stage_input_rows'],0)
   self.assertTrue(d['native_rerun_requested'])

 def test_missing_RHS_rejected(self):
  path=ROOT/'evidence'/'pilot'/'OFF'/'OWNER_STAGE_INPUTS.csv'
  rows=read_stage_rows(path)
  del rows[0]['rhs_w_dt']
  with self.assertRaises(WitnessError):
   validate_stage_rows(rows,ROOT/'evidence'/'pilot'/'OFF'/'OWNER_SELECTED_RCT.csv',ROOT/'evidence'/'pilot'/'OFF'/'OWNER_INTERNAL_5.csv')

 def test_false_lexical_clock_rejected(self):
  base=ROOT/'evidence'/'pilot'/'OFF'
  rows=read_stage_rows(base/'OWNER_STAGE_INPUTS.csv')
  rows[1]['s0']=rows[0]['s0']
  with self.assertRaises(WitnessError):validate_stage_rows(rows,base/'OWNER_SELECTED_RCT.csv',base/'OWNER_INTERNAL_5.csv')

if __name__=='__main__':unittest.main()
