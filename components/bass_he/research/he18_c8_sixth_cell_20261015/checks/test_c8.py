"""Public-only sixth-cell source-clock, Bernstein and error-carry regressions."""
import importlib.util
import hashlib
import json
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(m)
    return m
class SixthCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=module(ROOT/"src/stage_sixth.py","stage_c8_test")
        cls.bern=module(ROOT/"src/optimize_cached_bernstein.py","bern_c8_test")
        cls.prop=module(ROOT/"checks/propagate_sixth.py","prop_c8_test")
        cls.env={"Q":Q}
        exec(cls.bern.NEW_KERNEL,cls.env)
    def test_global_clock(self):
        s="""return self.global_volume(z+4)
xq=lo(x)+4
if xq<4 or hi(x)+4>5:
raise ValueError('FIFTH_CELL_SHEAR_DOMAIN')
return bound(0,5*self.h*self.si)
"""
        out=self.stage.patch_source(s)
        for k in ("global_volume(z+5)","xq=lo(x)+5",
                  "hi(x)+5>6","SIXTH_CELL_SHEAR_DOMAIN",
                  "bound(0,6*self.h*self.si)"):
            self.assertIn(k,out)
        with self.assertRaisesRegex(ValueError,"PATCH_BASELINE_CHANGED"):
            self.stage.patch_source(out)
    def test_adjacent_saved_indices(self):
        s="""old=archived_state['states'][:s.n,4]
new=archived_state['states'][:s.n,5]
n1=rows[4]['ne_cm3']
n2=rows[5]['ne_cm3']
err='FIFTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'
stage='HE18_C7'
clock=[str(4*h),str(5*h)]
lab='fifth-cell FIXED_REFERENCE.npz exact dyadic coefficients'
"""
        out=self.stage.patch_assembler(s)
        for k in (
          "old=archived_state['states'][:s.n,5]",
          "new=archived_state['states'][:s.n,6]",
          "n1=rows[5]['ne_cm3']",
          "n2=rows[6]['ne_cm3']",
          "clock=[str(5*h),str(6*h)]",
          "SIXTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH"):
            self.assertIn(k,out)
    def test_shared_basis_reused(self):
        b=self.env["_panel_weights"]
        self.assertIs(b(16),b(16))
        self.assertEqual(len(b(16)),16)
        with self.assertRaisesRegex(ValueError,"NONPOSITIVE_PANEL_COUNT"):
            b(0)
    def test_exact_quadratic_Bernstein_identity(self):
        for c0,c1,c2 in ((Q(2,3),Q(-1,5),Q(7,11)),
                         (Q(-3,5),Q(4,7),Q(-5,13))):
            for a,b in ((Q(-1,2),Q(-3,8)),(Q(0),Q(1,2))):
                controls=(c0+c1*a+c2*a*a,
                          c0+c1*(a+b)/2+c2*a*b,
                          c0+c1*b+c2*b*b)
                for u in (Q(0),Q(1,7),Q(1,2),Q(3,4),Q(1)):
                    z=a+(b-a)*u
                    p=c0+c1*z+c2*z*z
                    out=controls[0]*(1-u)**2+2*controls[1]*u*(1-u)+controls[2]*u*u
                    self.assertEqual(p,out)
    def test_all_signs_and_strict_interval_validation(self):
        f=self.env["residual_bounds"]
        mid=[["-2/5","1/3"],["-4/7","7/13"],
             ["-3/11","5/17"],["0","0"]]
        whole=[["0","0"],["0","0"],["0","0"],["1/19","1/19"]]
        a=f(mid,whole,16)
        self.assertEqual(a,f(mid,whole,16))
        self.assertGreater(a["sup"],0)
        for z in (Q(k,64) for k in range(-32,33)):
            for c0 in (Q(-2,5),Q(1,3)):
                for c1 in (Q(-4,7),Q(7,13)):
                    for c2 in (Q(-3,11),Q(5,17)):
                        val=c0+c1*z+c2*z*z+Q(1,19)*z**3
                        self.assertLessEqual(abs(val),a["sup"])
        with self.assertRaisesRegex(ValueError,"REVERSED_TAYLOR_COEFFICIENT"):
            f([["2","1"],["0","0"],["0","0"],["0","0"]],whole)
    def test_no_overwrite_of_existing_runtime(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            with self.assertRaisesRegex(ValueError,"REFUSE_OVERWRITE"):
                self.stage.stage(p,p)
    def test_actual_error_consumer_rejects_negative(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td)
            (t/"results").mkdir()
            (t/"inputs").mkdir()
            c={"photon_error_end_raw_exact":["0"]*2904,
               "gas_error_end_scaled":["0"]*4}
            c["photon_error_end_raw_exact"][0]="-1/100"
            raw=(json.dumps(c)+"\n").encode()
            (t/"inputs/ENDPOINT_MEMORY_R7.json").write_bytes(raw)
            (t/"inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps({
                "adapted_incoming_sha256":hashlib.sha256(raw).hexdigest(),
                "prev_photon_error_sha256":"testpin",
                "source_commit":"test"}))
            (t/"results/CERTIFICATE.json").write_text(json.dumps({
                "gas_error_components":[{"rational":"0"}]*4}))
            (t/"results/RESIDUAL_COUPLING.json").write_text(json.dumps({
                "C_scaled":[["0"]*4 for _ in range(2904)],
                "photon":[{"integral":"0"}]*2904}))
            original=self.prop.ROOT
            try:
                self.prop.ROOT=t
                with self.assertRaisesRegex(ValueError,"NEGATIVE_PHOTON_RADIUS"):
                    self.prop.compute()
            finally:self.prop.ROOT=original
if __name__=="__main__":
    unittest.main()
