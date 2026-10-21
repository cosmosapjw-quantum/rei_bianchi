"""Targeted contract tests: unique signed grid, realized physical axes, exact inputs."""
import hashlib,json,unittest
import numpy as np
from pilot import HERE,Reduced,case_grid
class ContractTests(unittest.TestCase):
    def test_grid_and_axes(self):
        cases=case_grid();self.assertEqual(len(cases),625);self.assertEqual(len({r['id'] for r in cases}),625)
        self.assertEqual(len({(r['eps_sigma']*r['Sigma0'],r['eps_pi']*r['Pi0']) for r in cases}),625)
        model=Reduced()
        errors=[]
        for r in cases:
            _,initial=model.initial(r['Sigma0'],r['eps_pi']*r['Pi0'],r['eps_sigma'])
            errors.append(initial['axis_error']);self.assertLessEqual(abs(initial['k']),.5)
        self.assertLessEqual(max(errors),1e-12)
    def test_byte_exact_sources(self):
        record=json.loads((HERE/'SOURCE_ATTRIBUTION.json').read_text())
        for row in record['files']:
            self.assertEqual(hashlib.sha256((HERE/row['vendored_path']).read_bytes()).hexdigest(),row['sha256'])
    def test_unrealizable_target_rejected(self):
        with self.assertRaisesRegex(ValueError,'UNREALIZABLE_K'):Reduced().initial(0,.002,0)
if __name__=='__main__':unittest.main()
