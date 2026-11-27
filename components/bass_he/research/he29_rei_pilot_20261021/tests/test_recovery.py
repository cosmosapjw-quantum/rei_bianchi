"""Bounded recovery fixtures; never invokes the numerical integrator."""
import unittest,tempfile,sys,json,shutil,hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import pilot
class Recovery(unittest.TestCase):
 def test_failed_json_preserved(self):
  c=pilot.case_grid()[0]
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/(c['case_id']+'.json');old=b'{"status":"failed","error":"fixture"}\n';p.write_bytes(old)
   with patch.object(pilot,'run_case',return_value={'status':'failed','error':'new fixture'}) as run:pilot.write_case(c,t);run.assert_called_once()
   self.assertEqual((Path(t)/'attempts'/(c['case_id']+'.attempt_0001.json')).read_bytes(),old)
 def test_source_edit_blocks_reuse_and_compute(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);manifest=json.loads((ROOT/'data/reviewed_source_manifest.json').read_text())
   for name in list(manifest['sha256'])+['data/reviewed_source_manifest.json']:
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
   with (root/'src/coordinates.py').open('a') as f:f.write('\n# accidental fixture edit\n')
   with patch.object(pilot,'ROOT',root),patch.object(pilot.CanonicalFVSpecies,'integrate',side_effect=AssertionError('must not compute')):
    with self.assertRaises(pilot.SourceBindingError):pilot.completed_result(pilot.case_grid()[0],ROOT/'data/results/cases/s00_p00_zero.json')
    with self.assertRaises(pilot.SourceBindingError):pilot.run_case(pilot.case_grid()[0])
 def test_all_existing_cases_valid_without_compute(self):
  with patch.object(pilot.CanonicalFVSpecies,'integrate',side_effect=AssertionError('must not compute')):
   for c in pilot.case_grid():self.assertTrue(pilot.completed_result(c,ROOT/'data/results/cases'/(c['case_id']+'.json')))
if __name__=='__main__':unittest.main()
