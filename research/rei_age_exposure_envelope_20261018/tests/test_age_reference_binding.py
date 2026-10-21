import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from compare_age_references import validate_pair
from reference_diagnostics import COMPUTATIONAL_BASE_SHA
from run_refinement import DEFAULT_CASES, NATIVE_SHA, plan


class AgeReferenceBindingTests(unittest.TestCase):
    def test_new_axis_keeps_explicit_historical_default(self):
        cases=plan()
        self.assertEqual(cases['age32'],dict(cases['age64'],name='age32',birth_panels=32))
        self.assertEqual(DEFAULT_CASES,'age64,time8,time16,time32,spectral128')

    def test_binding_accepts_passive_copy_and_rejects_binary_or_axis_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            paths=[]
            for births in (32,64):
                path=root/str(births);(path/'data').mkdir(parents=True)
                data=b'{"fixture":true}\n';(path/'data/endpoint.json').write_bytes(data)
                config=dict(plan()[f'age{births}'],tight=False,rpc_mode='binary64',error_norm='block-max')
                identity=dict(native_sha=NATIVE_SHA,binary_sha='fixture_same_binary',python='fixture_py',
                              numpy='fixture_numpy',scipy='fixture_scipy',transport_threads=48,rpc_mode='binary64',
                              solver_sha=COMPUTATIONAL_BASE_SHA)
                if births==32:
                    config['reference_diagnostics']=True
                    identity.update(computational_base_solver_sha=COMPUTATIONAL_BASE_SHA,
                                    solver_sha='fixture_passive_copy',diagnostic_transform_sha='fixture_transform')
                receipt=dict(status='COMPLETE',config=config,identity=identity,
                             outputs={'data/endpoint.json':hashlib.sha256(data).hexdigest()})
                (path/'RECEIPT.json').write_text(json.dumps(receipt));paths.append(path)
            self.assertEqual(validate_pair(*paths)['status'],'SAME_COMPUTATIONAL_SOURCE_BOUND')
            target=paths[0]/'RECEIPT.json';original=json.loads(target.read_text())
            for key,value in [('binary_sha','different'),('computational_base_solver_sha','different')]:
                changed=copy.deepcopy(original);changed['identity'][key]=value;target.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):validate_pair(*paths)
            changed=copy.deepcopy(original);changed['config']['source_subdivisions']=16;target.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):validate_pair(*paths)
            target.write_text(json.dumps(original));(paths[0]/'data/endpoint.json').write_text('changed')
            with self.assertRaises(ValueError):validate_pair(*paths)


if __name__ == '__main__':
    unittest.main()
