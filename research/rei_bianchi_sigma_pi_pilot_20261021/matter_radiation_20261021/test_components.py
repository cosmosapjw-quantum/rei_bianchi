"""Small extension checks: actual inversion, rejection and reference provenance."""
import hashlib,json,unittest
from pathlib import Path
from component_pilot import ComponentReduced,HERE,PARENT,case_grid
class ComponentChecks(unittest.TestCase):
    def test_inverse_and_positive_source(self):
        model=ComponentReduced()
        for s,m,r in [(0.,.0004,-.0004),(.004,-.0004,0.),(-.004,.0004,0.)]:
            _,i=model.initial(s,m,r)
            self.assertLessEqual(i['axis_error'],1e-12);self.assertGreaterEqual(i['A_m'],-1);self.assertLessEqual(i['A_m'],2)
            self.assertGreaterEqual(model.momentum.cell_numbers.min(),0)
        with self.assertRaisesRegex(ValueError,'UNREALIZABLE_MATTER_TARGET'):model.initial(0.,.001,0.)
    def test_case_scope(self):
        cases=case_grid();self.assertEqual(len(cases),606);self.assertEqual(len({c['id'] for c in cases}),606)
        self.assertEqual(sum(c['lane']=='MATTER_SLICE' for c in cases),600)
        self.assertEqual(sum(c['lane']=='MIXED_CANCELLATION' for c in cases),6)
    def test_reference_provenance(self):
        controls=json.loads((HERE/'reference_controls.json').read_text());self.assertEqual(controls['new_trajectory_count'],0);self.assertEqual(len(controls['references']),25)
        for ref in controls['references']:
            self.assertEqual(ref['provenance'],'REFERENCE_REUSE')
            oldpath=PARENT/'results/pilot/cases'/(ref['old_case_id']+'.json');old=json.loads(oldpath.read_text())
            self.assertEqual(ref['old_initial'],old['initial']);self.assertEqual(ref['old_case_identity'],old['identity']);self.assertEqual(ref['old_case'],old['case'])
            self.assertEqual(ref['old_json_sha256'],hashlib.sha256(oldpath.read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
