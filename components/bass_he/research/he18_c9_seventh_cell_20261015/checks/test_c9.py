"""Public regression for exact source-scoped HE18 C9 seventh-cell continuation."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(path,tag):
    spec=importlib.util.spec_from_file_location(tag,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

class SeventhCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=load(ROOT/"src/stage_seventh.py","stage_C9")
        cls.memo=load(ROOT/"src/optimize_memoized_residuals.py","memo_C9")
        cls.long=load(ROOT/"src/prepare_long_fraction.py","long_C9")
        cls.carry=load(ROOT/"checks/propagate_seventh.py","carry_C9")

    def test_seventh_global_shear_clock(self):
        text="""return self.global_volume(z+5)
xq=lo(x)+5
if xq<5 or hi(x)+5>6:raise ValueError('SIXTH_CELL_SHEAR_DOMAIN')
return bound(0,6*self.h*self.si)
"""
        out=self.stage.patch_source(text)
        for term in ("global_volume(z+6)","xq=lo(x)+6","hi(x)+6>7",
                     "SEVENTH_CELL_SHEAR_DOMAIN","bound(0,7*self.h*self.si)"):
            self.assertIn(term,out)
        with self.assertRaisesRegex(ValueError,"PATCH_BASELINE_CHANGED"):
            self.stage.patch_source(out)

    def test_saved_state_row_shifts_simultaneously(self):
        text="""left=archived_state['states'][:s.n,5]
right=archived_state['states'][:s.n,6]
ne0=rows[5]['ne_cm3']
ne1=rows[6]['ne_cm3']
err='SIXTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'
stage='HE18_C8'
clock=[str(5*h),str(6*h)]
label='sixth-cell FIXED_REFERENCE.npz exact dyadic coefficients'
"""
        out=self.stage.patch_assembler(text)
        for wanted in ("left=archived_state['states'][:s.n,6]",
                       "right=archived_state['states'][:s.n,7]",
                       "ne0=rows[6]['ne_cm3']","ne1=rows[7]['ne_cm3']",
                       "stage='HE18_C9'","clock=[str(6*h),str(7*h)]"):
            self.assertIn(wanted,out)

    def test_pure_memo_duplicate_cases_do_not_drop_rays(self):
        namespace={"Q":Q}
        computed=[]
        def mock(mid,whole):
            computed.append(1)
            return {"sup":Q(mid[0][0])+Q(whole[3][1])+Q(1)}
        namespace["residual_bounds"]=mock
        exec(self.memo.HOOK,namespace)
        values=[]
        for i in range(1452):
            mid=[[str(i),str(i)]]+[["0","0"]]*3
            whole=[["0","0"]]*3+[["0","1/3"]]
            values.extend([(mid,whole),(mid,whole)])
        mid=[a for a,b in values]
        whole=[b for a,b in values]
        res=namespace["_memoized_photon_residuals"](mid,whole)
        self.assertEqual(len(computed),1452)
        self.assertEqual(len(res),2904)
        self.assertTrue(all(res[2*i]==res[2*i+1] for i in range(1452)))
        self.assertEqual(res[-1]["sup"],Q(1451)+Q(4,3))
        with self.assertRaisesRegex(ValueError,"PHOTON_RESIDUAL_DIMENSION_NOT_2904"):
            namespace["_memoized_photon_residuals"](mid[:-1],whole)

    def test_long_fraction_patch_only_targeted_files(self):
        self.assertEqual(self.long.LIMIT,50000)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"src").mkdir()
            (root/"checks").mkdir()
            for rel,needle in (("src/assemble_certificate.py","from warm_interval import *"),
                ("checks/propagate_seventh.py","from fractions import Fraction as Q"),
                ("checks/verify_seventh.py","from fractions import Fraction as Q")):
                (root/rel).write_text(needle+"\n")
            self.long.patch(root)
            for rel in ("src/assemble_certificate.py","checks/propagate_seventh.py",
                         "checks/verify_seventh.py"):
                self.assertIn("set_int_max_str_digits(50000)",(root/rel).read_text())
            with self.assertRaisesRegex(ValueError,"REFUSE_REPEAT"):
                self.long.patch(root)

    def test_actual_negative_radius_consumer(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"results").mkdir();(root/"inputs").mkdir()
            packet={"photon_error_end_raw_exact":["0"]*2904,
                    "gas_error_end_scaled":["0"]*4}
            packet["photon_error_end_raw_exact"][-1]="-1/12"
            raw=(json.dumps(packet)+"\n").encode()
            (root/"inputs/ENDPOINT_MEMORY_R7.json").write_bytes(raw)
            (root/"inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps({
                "adapted_incoming_sha256":hashlib.sha256(raw).hexdigest(),
                "prev_photon_error_sha256":"testsha","source_commit":"test"}))
            (root/"results/CERTIFICATE.json").write_text(json.dumps({
                "gas_error_components":[{"rational":"0"}]*4}))
            (root/"results/RESIDUAL_COUPLING.json").write_text(json.dumps({
                "C_scaled":[["0"]*4 for _ in range(2904)],
                "photon":[{"integral":"0"} for _ in range(2904)]}))
            prev=self.carry.ROOT
            try:
                self.carry.ROOT=root
                with self.assertRaisesRegex(ValueError,"NEGATIVE_PHOTON_RADIUS"):
                    self.carry.compute()
            finally:
                self.carry.ROOT=prev

    def test_no_overwrite_source_staging(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            with self.assertRaisesRegex(ValueError,"REFUSE_OVERWRITE"):
                self.stage.stage(p,p)

    def test_exact_quadratic_bernstein_identity(self):
        for c0,c1,c2 in ((Q(1,2),Q(-3,7),Q(7,11)),
                         (Q(-2,5),Q(3,11),Q(-5,13))):
            for a,b in ((Q(-1,2),Q(0)),(Q(0),Q(1,2))):
                B0=c0+c1*a+c2*a*a
                B1=c0+c1*(a+b)/2+c2*a*b
                B2=c0+c1*b+c2*b*b
                for t in (Q(0),Q(1,7),Q(1,2),Q(6,7),Q(1)):
                    z=a+(b-a)*t
                    self.assertEqual(c0+c1*z+c2*z*z,
                        B0*(1-t)**2+2*B1*t*(1-t)+B2*t*t)
if __name__=="__main__":
    unittest.main()
