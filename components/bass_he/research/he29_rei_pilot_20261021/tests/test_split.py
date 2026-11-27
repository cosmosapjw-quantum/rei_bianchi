import sys,unittest,tempfile,types
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import split_pilot as p, pilot,shared_runner
class Split(unittest.TestCase):
 def test_original_references_valid(self):
  for si in ['00','02']:
   for suffix in ['p00_zero','p02_minus','p02_plus']:
    name=f's{si}_{suffix}';c=next(c for c in pilot.case_grid() if c['case_id']==name);self.assertTrue(pilot.completed_result(c,ROOT/'data/results/cases'/(name+'.json')))
 def test_explicit_fake_campaign(self):
  api=types.SimpleNamespace(completed_result=lambda c,path:c=={'fixture':1})
  with patch.dict(sys.modules,{'fixture_split_api':api}):self.assertTrue(shared_runner.reusable({'fixture':1},'/unused','fixture_split_api'))
if __name__=='__main__':unittest.main()
