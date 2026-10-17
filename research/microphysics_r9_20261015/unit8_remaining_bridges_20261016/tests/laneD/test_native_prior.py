"""Meaningful postprocessing and portable-provider checks, without BBN solves."""
import importlib.util,json,pathlib,tarfile,tempfile,unittest
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'code/laneD'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
run=module('run_native_prior');analysis=module('analyze_native_prior')
class NativePriorTest(unittest.TestCase):
    def test_ddof_one_against_hand_calculation(self):
        np.testing.assert_allclose(analysis.covariance(np.array([[1.,2.],[3.,4.],[5.,8.]])),[[4.,6.],[6.,28/3]],rtol=1e-15)
    def test_portable_archive_reconstructs_all_517_pinned_inputs(self):
        manifest=json.loads((ROOT/'inputs/laneD/PRIMAT_DOWNLOAD_MANIFEST.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            with tarfile.open(ROOT/'inputs/laneD/primat_source_4bf97d5082ee.tar.gz') as tf:tf.extractall(temp,filter='data')
            self.assertEqual(len(run.verify(pathlib.Path(temp),manifest)),517)
            self.assertTrue((pathlib.Path(temp)/'COPYING').is_file())
    def test_raw_native_sample_census_and_repeatability(self):
        names,x=analysis.load_samples(ROOT/'evidence/laneD_raw/production_samples.tsv');pn,px=analysis.load_samples(ROOT/'evidence/laneD_raw/pilot_samples.tsv')
        self.assertEqual(names,pn);self.assertEqual(len(x),64)
        self.assertTrue(all(n in names for n in analysis.NUCLIDES))
        np.testing.assert_array_equal(x[:8],px)
    def test_actual_budget_and_native_execution(self):
        rec=json.loads((ROOT/'evidence/laneD_raw/execution_receipt.json').read_text())
        self.assertEqual([r['label'] for r in rec['records']],['build','nominal','tight','pilot','production'])
        self.assertTrue(all(r['returncode']==0 for r in rec['records']))
        self.assertLessEqual(rec['numerical_wall_s'],30)
        self.assertLessEqual(rec['records'][0]['wall_s'],30)
    def test_covariance_positive_and_preserves_mass7_linear_identity(self):
        names,x=analysis.load_samples(ROOT/'evidence/laneD_raw/production_samples.tsv');selected=x[:,[names.index(k) for k in analysis.SELECTED]]
        c=analysis.covariance(selected);std=np.sqrt(np.diag(c));r=c/np.outer(std,std)
        self.assertGreaterEqual(np.linalg.eigvalsh(r).min(),-1e-10)
        augmented=np.column_stack([selected,selected[:,4]+selected[:,5]])
        t=np.vstack([np.eye(6),[0,0,0,0,1,1]]);ac=analysis.covariance(augmented);scale=np.sqrt(np.outer(np.diag(ac),np.diag(ac)))
        self.assertLessEqual(np.max(abs(ac-t@c@t.T)/scale),1e-12)
if __name__=='__main__':unittest.main()
