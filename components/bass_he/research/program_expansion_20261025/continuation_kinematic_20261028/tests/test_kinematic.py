"""Single-run tests; saved numerical payload is accumulated in this process."""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kinematic08",ROOT/"src/kinematic.py")
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)
SAVED = {"native_rows":[],"map_curves":[],"controls":[],"benchmarks":[],"manufactured_density":["0","3/2","0"]}


def decimal_value(x):
    return Decimal(x.numerator)/Decimal(x.denominator)


def boost_cosine(model,mu):
    """Independent CM energy/momentum followed by a laboratory Lorentz boost."""
    with localcontext() as ctx:
        ctx.prec = 80
        A,M,e,u = map(decimal_value,(model.A,model.M,model.e,Q(mu)))
        s = A*A+2*A*e
        root_s = s.sqrt()
        cm_energy = root_s/2
        cm_momentum = (s-4*M*M).sqrt()/2
        beta = e/(A+e)
        gamma = (A+e)/root_s
        pz = gamma*(cm_momentum*u+beta*cm_energy)
        pt = cm_momentum*(1-u*u).sqrt()
        return +(pz/(pz*pz+pt*pt).sqrt())


def interval_record(value):
    return {"lower":str(value.lower),"upper":str(value.upper),"width":str(value.width),"width_bound":str(value.width_bound),"uncertainty_length":str(value.uncertainty_length)}


class KinematicTests(unittest.TestCase):
    def test_01_surds(self):
        cases = [(0,0,0,0),(3,-2,Q(9,4),0),(-3,2,Q(9,4),0),
                 (2,-1,3,1),(1,-2,3,-1),(-2,1,3,-1),(-1,2,3,1),
                 (0,-2,3,-1),(1,2,3,1),(-1,-2,3,-1),(2,-9,0,1)]
        for p,q,r,expected in cases:
            self.assertEqual(m.sign_surds(p,q,r),expected)
        with self.assertRaises(m.ContractError):m.sign_surds(1,1,-1)

    def test_02_scalar_and_domain_guards(self):
        for args in [(True,2,2),(3,float("nan"),2),(3,2,float("inf")),(0,2,2),(4,2,2),(3,0,2),(3,2,0),(3,2,1)]:
            with self.assertRaises(m.ContractError):m.PhysicalAngularMap(*args)
        with self.assertRaises(m.UnsupportedMeasureError):m.PhysicalAngularMap(3,2,Q(7,6))
        for kwargs in [{"measure_kind":"ATOMIC"},{"kappa":0}]:
            with self.assertRaises(m.UnsupportedMeasureError):m.PhysicalAngularMap(3,2,2,**kwargs)
        model = m.PhysicalAngularMap(3,2,2)
        for u,n in [(2,0),(0,2),(False,0),(0,float("nan"))]:
            with self.assertRaises(m.ContractError):model.compare(u,n)

    def test_03_stopped(self):
        model = m.PhysicalAngularMap(3,2,Q(3,2))
        self.assertEqual((model.K,model.topology),(0,"stopped"))
        with self.assertRaises(m.StoppedDirectionError):model.compare(-1,0)
        self.assertEqual(model._compare(-1,Q(1,2),auxiliary_stopped_limit=True),-1)
        self.assertEqual(model.preimage((-1,0),Q(1,1024)).inner,())

    def test_04_exact_increasing_and_sign_control(self):
        model = m.PhysicalAngularMap(3,2,2)
        self.assertEqual(model.topology,"increasing")
        self.assertEqual(model.compare(0,Q(2,3)),0)
        self.assertEqual(model.compare(-1,Q(-1,2)),-1)
        self.assertEqual(model.compare(1,1),0)
        # A squared-only comparison would lose this negative longitudinal sign.
        self.assertNotEqual(model.compare(-1,Q(1,2)),1)
        SAVED["controls"].append({"name":"lost_longitudinal_sign","correct":-1,"squared_only_mutant":1,"detected":True})

    def test_05_rational_fold(self):
        model = m.PhysicalAngularMap(3,2,Q(6,5))
        self.assertEqual(model.R,Q(1,81))
        self.assertEqual(model.topology,"fold")
        p = model.preimage((0,1),Q(1,2**20))
        self.assertLessEqual(p.fold_bracket[0],Q(-7,18))
        self.assertGreaterEqual(p.fold_bracket[1],Q(-7,18))
        self.assertEqual(m.sign_surds(Q(-7,18),model.G/model.e,model.R),0)

    def test_06_irrational_fold_strip_control(self):
        model = m.PhysicalAngularMap(3,2,Q(5,4))
        p = model.preimage((0,1),Q(1,2**20))
        lo,hi = p.fold_bracket
        self.assertLess(lo,hi)
        self.assertEqual(p.outer,m.FULL)
        self.assertNotEqual(p.inner,m.FULL)
        self.assertLessEqual(hi-lo,p.delta)
        self.assertLessEqual(p.uncertainty_length,5*p.delta)
        self.assertEqual(m.sign_surds(lo,model.G/model.e,model.R),-1)
        self.assertEqual(m.sign_surds(hi,model.G/model.e,model.R),1)
        SAVED["controls"].append({"name":"missing_fold_strip","correct_outer_length":str(m._API.length(p.outer)),"mutant_outer_length":str(m._API.length(p.inner)),"detected":True})

    def test_07_independent_decimal80_boost(self):
        for energy in [Q(6,5),Q(5,4),Q(3,2),Q(2)]:
            model = m.PhysicalAngularMap(3,2,energy)
            curve = {"A":"3","M":"2","e":str(energy),"topology":model.topology,"points":[]}
            for j in range(-20,21):
                u = Q(j,20)
                if model.K == 0 and u == -1:continue
                f = boost_cosine(model,u)
                curve["points"].append([str(u),str(f)])
                # Offset by 1e-50, much larger than 80-digit oracle rounding.
                with localcontext() as ctx:
                    ctx.prec=80
                    below,above=Q(f-Decimal("1e-50")),Q(f+Decimal("1e-50"))
                if below >= -1:self.assertEqual(model.compare(u,below),1)
                if above <= 1:self.assertEqual(model.compare(u,above),-1)
            SAVED["map_curves"].append(curve)

    def test_08_common_energy_scale(self):
        a,b = m.PhysicalAngularMap(3,2,Q(5,4)),m.PhysicalAngularMap(21,14,Q(35,4))
        for u in [Q(-1),Q(-2,3),Q(0),Q(1,3),Q(1)]:
            for n in [Q(-1,2),Q(0),Q(3,4)]:self.assertEqual(a.compare(u,n),b.compare(u,n))
        self.assertEqual(a.preimage((Q(1,2),1),Q(1,4096)),b.preimage((Q(1,2),1),Q(1,4096)))

    def test_09_full_singleton_backward(self):
        for e in [Q(6,5),Q(3,2),Q(2)]:
            model=m.PhysicalAngularMap(3,2,e)
            self.assertEqual(model.preimage((-1,1),Q(1,1024)).sets,m.SetBounds(m.FULL,m.FULL))
            self.assertEqual(model.preimage((Q(1,2),Q(1,2)),Q(1,1024)).outer,())
        p=m.PhysicalAngularMap(3,2,Q(5,4)).preimage((-1,0),Q(1,1024))
        self.assertEqual(p.inner,())
        self.assertLessEqual(p.uncertainty_length,p.delta)
        with self.assertRaises(m.ContractError):model.preimage((1,0),Q(1,1024))

    def test_10_normalization_and_signed_moment(self):
        density=m.BernsteinDensity([0,Q(3,2),0])
        self.assertEqual(density.sigma,1)
        full=m.physical_aperture_integral(m.PhysicalAngularMap(3,2,2),density,(-1,1))["integral"]
        self.assertEqual((full.lower,full.upper),(1,1))
        odd=m.BernsteinDensity([0,1])
        signed=m.physical_aperture_integral(m.PhysicalAngularMap(3,2,2),odd,(-1,1),w0=0,w1=1)["integral"]
        self.assertEqual((signed.lower,signed.upper),(Q(1,3),Q(1,3)))
        p=m.SetBounds((),((Q(-1,2),Q(-1,4)),(Q(1,4),Q(1,2))))
        bounded=m.BernsteinDensity([Q(1,2)]).bounds(p,0,1)
        self.assertEqual((bounded.lower,bounded.upper),(Q(-3,64),Q(3,64)))
        SAVED["controls"].append({"name":"normalization_factor_two","correct":str(full.lower),"mutant":str(full.lower/2),"detected":True})

    def test_11_pair_guards_and_zero(self):
        model=m.PhysicalAngularMap(3,2,2)
        with self.assertRaises(m.ContractError):m.physical_pair_response(model,m.BernsteinDensity([0,1]),(-1,0),(0,1))
        with self.assertRaises(m.ContractError):m.physical_pair_response(model,m.BernsteinDensity([1]),(-1,Q(1,2)),(0,1))
        zero=m.physical_pair_response(model,m.BernsteinDensity([0]),(-1,0),(0,1))
        self.assertEqual(zero["coincidence"].width,0)
        self.assertIsNone(zero["preimage_a"])
        self.assertEqual(m.physical_aperture_integral(model,m.BernsteinDensity([0]),(-1,1))["integral"].upper,0)
        for d in [Q(1,2**81),2]:
            with self.assertRaises(m.ContractError):m.physical_pair_response(model,m.BernsteinDensity([1]),(-1,0),(0,1),d)

    def test_12_shared_event_and_physical_energy_controls(self):
        model=m.PhysicalAngularMap(3,2,2)
        density=m.BernsteinDensity([Q(1,2)])
        r=m.physical_pair_response(model,density,(-1,Q(-9,10)),(Q(9,10),1))
        y=r["coincidence"]
        product_upper=r["hit_a"].upper*r["hit_b"].upper/density.sigma
        self.assertGreater(y.lower,product_upper)
        self.assertEqual(r["pair_energy_MeV"],y.scaled(5))
        self.assertEqual(r["coincidence_daughters"],y.scaled(2))
        self.assertEqual(r["selected_plus_energy_MeV"].added(r["selected_minus_energy_MeV"]).lower,r["pair_energy_MeV"].lower)
        self.assertGreater(r["pair_energy_MeV"].lower,y.scaled(2).upper)
        for key in ["hit_a","hit_b"]:self.assertGreaterEqual(r[key].upper,y.lower)
        SAVED["controls"].extend([
            {"name":"independent_marginal_coincidence","correct":interval_record(y),"mutant_upper":str(product_upper),"detected":True},
            {"name":"incorrect_physical_energy0","correct":interval_record(r["pair_energy_MeV"]),"mutant":interval_record(y.scaled(2)),"detected":True}])

    def test_13_default_and_manual_actual_bounds(self):
        density=m.BernsteinDensity([0,1,2,3,4,3,2,1,0])
        model=m.PhysicalAngularMap(3,2,Q(5,4))
        default=m.physical_pair_response(model,density,(0,Q(9,10)),(Q(9,10),1))
        coarse=m.physical_pair_response(model,density,(0,Q(9,10)),(Q(9,10),1),Q(1,16))
        for key in ["coincidence","hit_a","hit_b"]:
            self.assertLessEqual(default[key].width,density.sigma/Q(2**40))
            self.assertLessEqual(coarse[key].width,coarse[key].width_bound)
        self.assertGreater(coarse["hit_a"].width,density.sigma/Q(2**40))
        SAVED["bound_comparison"]={"default_delta":str(default["delta"]),"manual_delta":str(coarse["delta"]),"sigma":str(density.sigma),"default":interval_record(default["hit_a"]),"manual":interval_record(coarse["hit_a"])}
        # <=48 iterations per boundary follows from width <=2 and this default.
        self.assertLessEqual((2/default["delta"]).numerator.bit_length(),49)

    def test_14_native_nist_manufactured_density(self):
        source=ROOT.parent/"continuation_photon_20261027/sources/NIST_CODATA_2022_allascii.txt"
        raw=source.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),"77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67")
        lines=raw.decode().splitlines()
        def field(label):
            line=next(x for x in lines if x.startswith(label))
            return Q(line[60:85].replace(" ",""))
        A=field("alpha particle mass energy equivalent in MeV")
        M=field("deuteron mass energy equivalent in MeV")
        self.assertEqual((A,M),(Q("3727.3794118"),Q("1875.61294500")))
        SAVED["nist_source"]={"path":str(source.relative_to(ROOT.parent.parent.parent)),"sha256":hashlib.sha256(raw).hexdigest(),"A":str(A),"M":str(M),"measurement_uncertainty_certified":False}
        density=m.BernsteinDensity([0,Q(3,2),0])
        for energy in [213,258,330]:
            model=m.PhysicalAngularMap(A,M,energy)
            r=m.physical_pair_response(model,density,(-1,Q(-1,2)),(Q(1,2),1))
            for mu in [Q(-3,4),Q(0),Q(3,4)]:
                f=boost_cosine(model,mu)
                self.assertEqual(model.compare(mu,Q(f)+Q(1,10**45)),-1)
            y=r["coincidence"]
            self.assertEqual(r["pair_energy_MeV"],y.scaled(model.G))
            self.assertEqual(r["coincidence_daughters"],y.scaled(2))
            self.assertLessEqual(y.width,density.sigma/Q(2**40))
            SAVED["native_rows"].append({"e":energy,"G":str(model.G),"topology":model.topology,"delta":str(r["delta"]),"coincidence":interval_record(y),"hit_a":interval_record(r["hit_a"]),"hit_b":interval_record(r["hit_b"]),"pair_energy_MeV":interval_record(r["pair_energy_MeV"]),"operations":dict(model.operations)})


if __name__ == "__main__":
    unittest.main()
