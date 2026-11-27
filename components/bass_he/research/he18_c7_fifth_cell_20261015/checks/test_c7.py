"""Public-only C7 tests. Private P01 arrays are not bundled."""
import importlib.util,json,tempfile,unittest
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj
class FifthCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=module(ROOT/"src/stage_fifth.py","test_stage")
        cls.bern=module(ROOT/"src/optimize_assembly.py","test_bern")
        cls.prop=module(ROOT/"checks/propagate_fifth.py","test_prop")
    def test_exact_global_shift(self):
        s='''return self.global_volume(z+3)
xq=lo(x)+3
if xq<3 or hi(x)+3>4:
raise ValueError('FOURTH_CELL_SHEAR_DOMAIN')
return bound(0,4*self.h*self.si)
'''
        changed=self.stage.patch_source(s)
        for t in ("global_volume(z+4)","xq=lo(x)+4",
                  "hi(x)+4>5","FIFTH_CELL_SHEAR_DOMAIN",
                  "bound(0,5*self.h*self.si)"):
            self.assertIn(t,changed)
        with self.assertRaises(ValueError):self.stage.patch_source(changed)
    def test_source_rows_simultaneously(self):
        s='''old=archived_state['states'][:s.n,3]
new=archived_state['states'][:s.n,4]
n1=rows[3]['ne_cm3']
n2=rows[4]['ne_cm3']
v='FOURTH_CELL_DYADIC_ENDPOINT_SOURCE_MISMATCH'
stage='HE18_C6'
clock=[str(3*h),str(4*h)]
label='fourth-cell FIXED_REFERENCE.npz exact dyadic coefficients'
'''
        res=self.stage.patch_assembler(s)
        self.assertIn("old=archived_state['states'][:s.n,4]",res)
        self.assertIn("new=archived_state['states'][:s.n,5]",res)
        self.assertIn("n1=rows[4]['ne_cm3']",res)
        self.assertIn("n2=rows[5]['ne_cm3']",res)
        self.assertIn("clock=[str(4*h),str(5*h)]",res)
    def test_Bernstein_controls_exact_identity(self):
        from math import factorial
        for c0,c1,c2 in ((Q(1,2),Q(-1,3),Q(7,11)),
                         (Q(-3,5),Q(4,7),Q(-5,13))):
            for a,b in ((Q(-1,2),Q(-3,8)),(Q(0),Q(1,2))):
                b0=c0+c1*a+c2*a*a
                b1=c0+c1*(a+b)/2+c2*a*b
                b2=c0+c1*b+c2*b*b
                for theta in (Q(0),Q(1,7),Q(1,2),Q(3,4),Q(1)):
                    value=c0+c1*(a+(b-a)*theta)+c2*(a+(b-a)*theta)**2
                    bern=b0*(1-theta)**2+2*b1*theta*(1-theta)+b2*theta**2
                    self.assertEqual(value,bern)
    def test_exact_fraction_bound_covers_manufacture(self):
        env={"Q":Q};exec(self.bern.NEW_KERNEL,env)
        f=env["residual_bounds"]
        mid=[["1/2","2/3"],["-1/3","-1/4"],["3/5","4/5"],["0","0"]]
        whole=[["0","0"],["0","0"],["0","0"],["1/7","1/7"]]
        c=f(mid,whole,16)
        self.assertGreater(c["sup"],0)
        self.assertGreater(c["integral"],0)
        self.assertGreater(c["weighted_integral"],0)
        for t in [Q(k,64) for k in range(-32,33)]:
            for c0 in [Q(1,2),Q(2,3)]:
                for c1 in [Q(-1,3),Q(-1,4)]:
                    for c2 in [Q(3,5),Q(4,5)]:
                        f0=c0+c1*t+c2*t*t+Q(1,7)*t**3
                        self.assertLessEqual(abs(f0),c["sup"])
        self.assertGreaterEqual(c["integral"],0)
    def test_no_overwrite_guard(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            with self.assertRaisesRegex(ValueError,"REFUSE_OVERWRITE"):
                self.stage.stage(p,p)
    def test_negative_photon_error_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/"results").mkdir();(p/"inputs").mkdir()
            c={"photon_error_end_raw_exact":["0"]*2904,
               "gas_error_end_scaled":["0"]*4}
            c["photon_error_end_raw_exact"][0]="-1"
            import hashlib
            raw=(json.dumps(c)+"\n").encode()
            (p/"inputs/ENDPOINT_MEMORY_R7.json").write_bytes(raw)
            (p/"inputs/STAGED_SOURCE_IDENTITY.json").write_text(json.dumps(
                dict(adapted_incoming_sha256=hashlib.sha256(raw).hexdigest(),
                     prev_photon_error_sha256="hash",source_commit="test")))
            (p/"results/CERTIFICATE.json").write_text(json.dumps(
                {"gas_error_components":[{"rational":"0"}]*4}))
            (p/"results/RESIDUAL_COUPLING.json").write_text(json.dumps(
                {"C_scaled":[["0"]*4 for _ in range(2904)],
                 "photon":[{"integral":"0"}]*2904}))
            orig=self.prop.ROOT
            try:
                self.prop.ROOT=p
                with self.assertRaisesRegex(ValueError,"NEGATIVE_PHOTON_RADIUS"):
                    self.prop.compute()
            finally:
                self.prop.ROOT=orig
if __name__=="__main__":unittest.main()
