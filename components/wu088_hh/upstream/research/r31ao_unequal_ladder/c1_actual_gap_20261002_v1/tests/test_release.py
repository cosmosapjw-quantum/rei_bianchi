from pathlib import Path
from fractions import Fraction as Q
import copy, json, os, subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import exact_gap_binding as b
from machine_predicate_bridge import E,LIMITS,rounding_bracket

class ReleaseTests(unittest.TestCase):
    def test_independent_polynomial_certificate(self):
        a=[[(Q(3),Q(0)),(Q(0),Q(0))],[(Q(0),Q(0)),(Q(4),Q(0))]]
        self.assertTrue(b.verify_norm_bracket(a,{'lo':'4','hi':'4'}))
    def test_independent_certificate_detects_bad_upper(self):
        a=[[(Q(3),Q(0)),(Q(0),Q(0))],[(Q(0),Q(0)),(Q(4),Q(0))]]
        self.assertFalse(b.verify_norm_bracket(a,{'lo':'3','hi':'7/2'}))
        self.assertFalse(b.verify_norm_bracket(a,{'lo':'9/2','hi':'5'}))
    def test_cli_emits_result_and_nine_checked_norms(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'new'
            p=subprocess.run([sys.executable,'-B',str(ROOT/'exact_gap_binding.py'),'--output',str(out)],capture_output=True,timeout=30)
            self.assertEqual(p.returncode,0,p.stderr.decode())
            self.assertTrue((out/'RESULT.json').exists(),'CLI must emit source-bound result')
            r=json.loads((out/'RESULT.json').read_text())
            self.assertEqual(r['polynomial_certificate']['checked_norms'],9)
            self.assertTrue(r['polynomial_certificate']['all_pass'])
    def test_cli_cannot_claim_continuous_target(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'new'
            p=subprocess.run([sys.executable,'-B',str(ROOT/'exact_gap_binding.py'),'--output',str(out),'--require-continuous'],capture_output=True,timeout=30)
            self.assertEqual(p.returncode,3)
            self.assertEqual(json.loads((out/'RETURN.json').read_text())['status'],'UNRESOLVED_INPUTS')
    def test_cli_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);(out/'sentinel').write_bytes(b'KEEP')
            p=subprocess.run([sys.executable,'-B',str(ROOT/'exact_gap_binding.py'),'--output',str(out)],capture_output=True,timeout=30)
            self.assertEqual(p.returncode,4)
            self.assertEqual((out/'sentinel').read_bytes(),b'KEEP')

class ExistingEngineRegression(unittest.TestCase):
    def test_work_cap_rejection(self):
        with self.assertRaises(ValueError):
            E.spectral_norm([[(Q(1),Q(0))]*2]*2,precision=128,limits=E.Limits(max_operations=1))
    def test_rne_midpoint_even(self):
        midpoint=Q(1)+Q(1,2**53)
        self.assertEqual(E.round_binary64(midpoint),0x3ff0000000000000)
    def test_negative_directed_bracket(self):
        q=-Q(1,10);lo,hi=rounding_bracket(q)
        self.assertLessEqual(lo,q);self.assertGreaterEqual(hi,q);self.assertLess(lo,hi)
    def test_exact_field_decoder_against_numpy_as_ratio(self):
        import io,zipfile,numpy as np
        inp=b.load_inputs(ROOT)
        for spec in inp['bindings']['prediction_members']:
            with zipfile.ZipFile(ROOT/'inputs'/spec['archive']) as z:
                a=np.load(io.BytesIO(z.read(spec['member'])),allow_pickle=False)
            expected=inp['models'][spec['model']][spec['field']]
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    self.assertEqual(expected[i][j],(Q(*float(a[i,j].real).as_integer_ratio()),Q(*float(a[i,j].imag).as_integer_ratio())))

if __name__=='__main__':unittest.main()
