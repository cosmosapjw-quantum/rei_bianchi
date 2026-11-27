"""Public regression suite for warm fourth cell and sparse/parallel orchestration."""
import importlib.util
import json,tempfile,unittest
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def get(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m
class TestC6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=get(ROOT/"src/stage_fourth.py","test_stage4")
        cls.sparse=get(ROOT/"src/optimize_sparse.py","test_sparse")
        cls.runner=get(ROOT/"src/run_parallel.py","test_parallel")
        cls.verify=get(ROOT/"checks/verify_fourth.py","test_verify")
    def test_cell_clock_transform(self):
        src="""return self.global_volume(z+2)
xq=lo(x)+2
if xq<2 or hi(x)+2>3:raise ValueError('THIRD_CELL_SHEAR_DOMAIN')
return bound(0,3*self.h*self.si)
"""
        out=self.stage.patch_source(src)
        self.assertIn("self.global_volume(z+3)",out)
        self.assertIn("hi(x)+3>4",out)
        self.assertIn("bound(0,4*self.h*self.si)",out)
        with self.assertRaisesRegex(ValueError,"PATCH_BASELINE_CHANGED"):
            self.stage.patch_source(out)
    def test_correct_simultaneous_endpoint_indices(self):
        src="""a=archived_state['states'][:s.n,2]
b=archived_state['states'][:s.n,3]
n=rows[2]['ne_cm3']+rows[3]['ne_cm3']
err='THIRD_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'
stage='HE18_C5'
cells=[str(2*h),str(3*h)]
label='third-cell FIXED_REFERENCE.npz exact dyadic coefficients'
"""
        out=self.stage.patch_assembler(src)
        self.assertIn("archived_state['states'][:s.n,3]",out)
        self.assertIn("archived_state['states'][:s.n,4]",out)
        self.assertIn("rows[3]['ne_cm3']+rows[4]['ne_cm3']",out)
        self.assertIn("[str(3*h),str(4*h)]",out)
    def test_sparse_zero_path_is_rigorous_only(self):
        self.assertIn("all(lo(z)==hi(z)==0",self.sparse.NEW2)
        self.assertNotIn("float(",self.sparse.NEW2)
        self.assertIn("rp.append(dy[4+j]-src*self.h)",self.sparse.NEW2)
        with self.assertRaisesRegex(ValueError,"SPARSE_SOURCE_ANCHOR_CHANGED"):
            self.sparse.optimize("missing mathematical source")
    def test_exact_small_thomson_bounds(self):
        for s in (Q(1,10**8),Q(1,10**5),Q(1,100)):
            lo=self.verify.probability_lower(s)
            hi=self.verify.probability_upper(s)
            self.assertTrue(0<lo<hi<s)
    def test_parallel_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            for folder in ("inputs","results","evidence"):
                (p/folder).mkdir()
            (p/"inputs/FIXED_REFERENCE.npz").write_bytes(b"stub")
            (p/"results/mid_jets.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"REFUSE_OVERWRITE_EXISTING_CERTIFICATE"):
                self.runner.run(p)
if __name__=="__main__":unittest.main()
