import math
import unittest
from shear_attribution import decompose

class AttributionTests(unittest.TestCase):
    def test_free_shear(self):
        n=[i/32 for i in range(33)];h=[math.exp(-1.5*x) for x in n]
        s=[0.01*math.exp(-1.5*x) for x in n]
        r=decompose(n,h,s,[0]*33,[0]*33,norm='half')
        self.assertLess(r['max_abs_sampled_closure_defect'],1e-17)
    def test_opposite_stress_cancellation(self):
        n=[0.,.2,.4];h=[1.]*3;s=[0.]*3;p=[.1,.2,.4]
        r=decompose(n,h,s,p,[-x for x in p],norm='half')
        self.assertEqual(r['max_abs_sampled_closure_defect'],0.)
        self.assertTrue(all(x['cancellation_fraction']==1. for x in r['rows']))
    def test_exact_affine_integrand(self):
        n=[0.,.1,.35,1.];h=[math.exp(-3*x) for x in n]
        pm=[2*x for x in n];pr=[-x for x in n];s=[.5*x*x for x in n]
        r=decompose(n,h,s,pm,pr,norm='half')
        self.assertLess(r['max_abs_sampled_closure_defect'],2e-16)
        self.assertAlmostEqual(r['endpoint']['matter_impulse'],1.)
        self.assertAlmostEqual(r['endpoint']['radiation_impulse'],-.5)
    def test_norm_conversion_and_work(self):
        n=[0.,.2,.4];h=[1.,.9,.8];s=[.2,-.1,.05];m=[.3,.2,-.1];r=[-.1,.1,.04]
        a=decompose(n,h,s,m,r,norm='half')
        b=decompose(n,h,*[[math.sqrt(2)*x for x in v] for v in (s,m,r)],norm='frobenius')
        for ar,br in zip(a['rows'],b['rows']):
            self.assertAlmostEqual(ar['normalized_work_m'],br['normalized_work_m'])
            self.assertAlmostEqual(ar['normalized_work_r'],br['normalized_work_r'])
            self.assertAlmostEqual(math.sqrt(2)*ar['predicted_shear'],br['predicted_shear'])
    def test_bad_grid(self):
        with self.assertRaises(ValueError):decompose([0,0],[1,1],[0,0],[0,0],[0,0],norm='half')
    def test_nonfinite(self):
        with self.assertRaises(ValueError):decompose([0,1],[1,1],[0,float('nan')],[0,0],[0,0],norm='half')
    def test_zero_hubble(self):
        with self.assertRaises(ValueError):decompose([0,1],[1,0],[0,0],[0,0],[0,0],norm='half')
    def test_norm_required(self):
        with self.assertRaises(ValueError):decompose([0,1],[1,1],[0,0],[0,0],[0,0],norm='unknown')

if __name__=='__main__':unittest.main()
