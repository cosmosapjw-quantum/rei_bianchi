import importlib.util,math,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("original_rei_f08_s0_sky",HERE/"observer_sky.py")
s=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=s;SPEC.loader.exec_module(s)

class OriginalBianchiThomson(unittest.TestCase):
    def setUp(self):
        self.Hbar=1e-14
        self.H=(1.01e-14,9.9e-15,1e-14)
        self.T=1e13
    def test_original_source_hashes(self):
        for name,value in s.SOURCE_SHA.items():
            self.assertEqual(s.sha(HERE/"source_inputs"/name),value)
    def test_exact_axial_bianchi_redshift(self):
        z=math.expm1(self.Hbar*.50*self.T)
        for i in range(3):
            n=tuple(float(j==i) for j in range(3))
            expect=math.log1p(z)/self.H[i]
            got=s.lookback(self.H,n,z,self.T)
            self.assertAlmostEqual(got/expect,1,places=13)
            self.assertLess(abs(s.log_redshift(self.H,n,got)-math.log1p(z)),3e-15)
    def test_exact_flrw_limit(self):
        z=math.expm1(.75*self.Hbar*self.T)
        for _,_,_,_,n in s.angular_grid(8,16):
            got=s.lookback((self.Hbar,)*3,n,z,self.T)
            self.assertLess(abs(got/.75/self.T-1),5e-13)
    def test_anisotropic_redshift_even_parity(self):
        z=math.expm1(self.Hbar*.5*self.T)
        for _,_,_,_,n in s.angular_grid(8,16):
            plus=s.lookback(self.H,n,z,self.T)
            minus=s.lookback(self.H,tuple(-q for q in n),z,self.T)
            self.assertLess(abs(plus-minus),.003)
    def test_positive_source_screen_and_partial_integral(self):
        a=s.ScreenIntegral([0,1,2,3,4],[5.]*5)
        self.assertEqual(a.value(1.25),5)
        self.assertAlmostEqual(a.integral(1.25),13.75,places=13)
        self.assertAlmostEqual(a.integral(0),20.,places=13)
        self.assertAlmostEqual(a.integral(4),0.,places=13)
    def test_linear_density_coarsening(self):
        a=s.ScreenIntegral(list(range(9)),[1.+2*t for t in range(9)])
        for t in (.75,2.5,5.125):
            self.assertAlmostEqual(a.integral(t),a.coarsened(2).integral(t),places=12)
            self.assertAlmostEqual(a.integral(t),a.coarsened(4).integral(t),places=12)
    def test_first_order_shear_sign_and_size(self):
        z=math.expm1(self.Hbar*.5*self.T)
        n=(1.,0.,0.)
        Delta=s.lookback(self.H,n,z,self.T)
        exact=s.C_CGS*s.SIGMA_T_CM2*.0001*(Delta-.5*self.T)
        shear=self.H[0]-self.Hbar
        linear=-s.C_CGS*s.SIGMA_T_CM2*.0001*(.5*self.T/self.Hbar)*shear
        self.assertLess(abs(exact-linear)/abs(linear),.02)
        self.assertLess(exact,0)
    def test_geometry_material_decomposition(self):
        t=[0,1,2,3,4]
        bi=s.ScreenIntegral(t,[1.,2.,3.,4.,5.])
        fl=s.ScreenIntegral(t,[1.,1.,1.,1.,1.])
        n=next(s.angular_grid(8,16))
        r=s.physics_row((.101,.099,.1),.1,bi,fl,.5,8,16,n,4.,.015)
        self.assertAlmostEqual(r["delta_tau_total"],
           r["delta_tau_material_fixed_time"]+r["delta_tau_geometry_fixed_relative_z"],places=14)
        self.assertGreater(r["tau_BI"],0)
    def test_uniform_geometry_isotropic_at_fixed_z(self):
        bi=s.ScreenIntegral([0,1,2,3,4],[2.]*5)
        fl=s.ScreenIntegral([0,1,2,3,4],[1.]*5)
        out=[]
        for n in s.angular_grid(8,16):
            r=s.physics_row((.1,.1,.1),.1,bi,fl,.5,8,16,n,4.,.04)
            out.append(r)
            self.assertLess(abs(r["delta_tau_geometry_fixed_relative_z"]),4e-14)
        self.assertLess(max(v["tau_BI"] for v in out)-min(v["tau_BI"] for v in out),4e-14)
    def test_exact_relative_z_visibility_derivative(self):
        t=[float(x) for x in range(101)]
        sbi=s.ScreenIntegral(t,[2.5]*101)
        sfl=s.ScreenIntegral(t,[3.5]*101)
        H=(.000101,.000099,.0001);Hbar=.0001
        n=(0.4,math.sqrt(1-.4**2),0.)
        frac=.5;T=100.
        z=math.expm1(frac*Hbar*T)
        D=s.lookback(H,n,z,T);te=T-D
        tau=.002*sbi.integral(te)
        Hdir=s.effective_H(H,n,D)
        g=(.002*sbi.value(te)*math.exp(-tau))/((1+z)*Hdir)
        def probability(zx):
            t_emit=T-s.lookback(H,n,zx,T)
            return -math.expm1(-.002*sbi.integral(t_emit))
        eps=2e-6
        num=(probability(z+eps)-probability(z-eps))/(2*eps)
        self.assertLess(abs(num/g-1),3e-6)
    def test_equal_area_weights(self):
        for m,p in s.ANGULAR_GRIDS:
            q=list(s.angular_grid(m,p))
            self.assertEqual(len(q),m*p)
            self.assertTrue(all(abs(sum(x*x for x in v[-1])-1)<5e-15 for v in q))
            self.assertAlmostEqual(sum(v[2] for v in q),0.,places=12)
    def test_frozen_science_rules(self):
        self.assertEqual((s.GATE,s.WIDTH),(2e-4,2e-3))
        self.assertEqual(s.CENTRAL,"28/88_REPORTED")
        self.assertEqual(sum(m*p for m,p in s.ANGULAR_GRIDS)*len(s.WINDOW_FRACTIONS),10752)

if __name__=="__main__":
    unittest.main(verbosity=2)
