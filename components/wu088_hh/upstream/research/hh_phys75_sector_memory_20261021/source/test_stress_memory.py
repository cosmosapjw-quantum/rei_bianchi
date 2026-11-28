import unittest
import numpy as np
from scipy.integrate import simpson
from stress_memory import memory_budget, sector_observables, simpson_weights

class MemoryTests(unittest.TestCase):
    def setUp(self): self.x=np.linspace(0.,1.,65)
    def test_zero_stress_redshifts_exactly(self):
        x=self.x; H=np.exp(-1.5*x); S=.004*np.exp(-1.5*x)
        r=memory_budget(x,H,S,np.zeros_like(x),np.zeros_like(x))
        self.assertLess(abs(r['closure_defect']),1e-18)
        self.assertEqual(r['matter_memory'],0.)
        self.assertFalse(r['has_stress_memory'])
    def test_cubic_integrand_against_exact_polynomial(self):
        x=self.x; H=np.exp(-3*x); pm=x**3; pr=-x**2
        S=.1+x**4/4-x**3/3
        r=memory_budget(x,H,S,pm,pr)
        self.assertAlmostEqual(float(r['matter_memory']),.25,14)
        self.assertAlmostEqual(float(r['radiation_memory']),-1/3,14)
        self.assertLess(abs(r['closure_defect']),1e-15)
    def test_opposite_stresses_preserve_sectors(self):
        x=self.x; r=memory_budget(x,np.ones_like(x),np.zeros_like(x),x,-x)
        self.assertGreater(r['matter_memory'],0)
        self.assertEqual(r['matter_memory'],-r['radiation_memory'])
        self.assertEqual(r['stress_memory_cancellation'],1)
    def test_batch_matches_independent_scipy_quadrature(self):
        x=self.x; H=np.exp(-np.arange(1,4)[:,None]*x)
        pm=np.arange(1,4)[:,None]*np.sin(x); pr=np.cos(x)[None,:]*np.ones((3,1))
        S=np.zeros_like(H); r=memory_budget(x,H,S,pm,pr)
        for j in range(3):
            k=np.exp(3*(x-x[-1]))*H[j]/H[j,-1]
            for name,y in [('matter_memory',pm),('radiation_memory',pr)]:
                self.assertAlmostEqual(float(r[name][j]),float(simpson(k*y[j],x=x)),14)
    def test_shared_weights_readonly_and_inputs_preserved(self):
        w=simpson_weights(self.x); self.assertFalse(w.flags.writeable)
        self.assertIs(w,simpson_weights(self.x))
        H=np.ones_like(self.x); S=self.x.copy(); before=S.tobytes()
        memory_budget(self.x,H,S,S,-S)
        self.assertEqual(before,S.tobytes())
    def test_invalid_grids_rejected(self):
        for x in (np.array([0,1]),np.array([0.,.1,1.]),self.x[::-1],np.array([0,np.nan,1])):
            with self.assertRaises(ValueError):simpson_weights(x)
    def test_invalid_shapes_hubble_and_nonfinite_rejected(self):
        z=np.zeros_like(self.x); h=np.ones_like(z)
        for hh,ss in [(h[:-1],z),(-h,z),(h,np.full_like(z,np.nan))]:
            with self.assertRaises(ValueError):memory_budget(self.x,hh,ss,z,z)
    def test_norm_sum_work_and_cross(self):
        r=sector_observables(np.array([.3]),np.array([.2]),np.array([-.2]))
        self.assertEqual(r['Pi_total_F'][0],0)
        self.assertGreater(r['Pi_m_F'][0],0)
        self.assertAlmostEqual(r['work_loss_m_dimensionless'][0],-.12)
        self.assertAlmostEqual(r['work_loss_r_dimensionless'][0],.12)
        self.assertAlmostEqual(r['matter_radiation_cross_F_squared'][0],-.16)
    def test_complex_inputs_are_not_silently_truncated(self):
        with self.assertRaises(ValueError):sector_observables(np.array([1+1j]),[0.],[0.])

if __name__=='__main__': unittest.main(verbosity=2)
