#!/usr/bin/env python3
"""Same-author mathematical and numeric validation of source second derivative only."""
import importlib.util,itertools,math,unittest
from pathlib import Path
import numpy as np

SRC=Path(__file__).resolve().parents[1]/'photon_curvature.py'
spec=importlib.util.spec_from_file_location('local_source_curvature',SRC)
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

class SourceCurvatureTests(unittest.TestCase):
    def test_exact_zero_source(self):
        p,e,d=f.shares([4,0,6],2)
        J,H=f.jac_hess(p)
        self.assertEqual(p[1],0)
        self.assertTrue(np.all(J[1]==0))
        self.assertTrue(np.all(H[1]==0))
        self.assertAlmostEqual(sum(p)+e,1)

    def test_jacobian_and_hessian_finite_difference(self):
        a=np.array([.71,2.12,.49]);ext=.28;delta=np.zeros(3);eps=2e-5
        _,_,p,J,H,_=f.log_fraction_response(a,ext,delta)
        for u in range(3):
            plus=np.zeros(3);plus[u]=eps
            minus=-plus
            pp=f.log_fraction_response(a,ext,plus)[0]
            pm=f.log_fraction_response(a,ext,minus)[0]
            self.assertTrue(np.allclose((pp-pm)/(2*eps),J[:,u],rtol=1e-8,atol=2e-11))
            self.assertTrue(np.allclose((pp-2*p+pm)/(eps**2),H[:,u,u],rtol=4e-5,atol=5e-7))
        for u in range(3):
            for v in range(3):
                up=np.zeros(3);up[v]=eps
                dn=-up
                Jp=f.jac_hess(f.log_fraction_response(a,ext,up)[0])[0]
                Jm=f.jac_hess(f.log_fraction_response(a,ext,dn)[0])[0]
                self.assertTrue(np.allclose((Jp[:,u]-Jm[:,u])/(2*eps),H[:,u,v],rtol=2e-8,atol=2e-11))

    def test_hessian_symmetry(self):
        for p in (np.array([.1,.2,.3]),np.array([.8,.11,.01]),np.array([.0,.4,.6])):
            _,H=f.jac_hess(p)
            self.assertLess(np.max(abs(H-H.transpose(0,2,1))),3e-16)

    def test_abs_bound(self):
        a=np.array([1.,2.,.15]);ext=.25
        for d in itertools.product((-.2,0,.2),repeat=3):
            _,res,p,_,_,_=f.log_fraction_response(a,ext,np.array(d))
            self.assertTrue(np.all(abs(res)<=np.array([1.,1.,1.])*(sum(abs(t) for t in d)**2)+3e-16))

    def test_full_box_corner(self):
        r=f.finite_corner_report([.91,1.74,.07],[1.,2.,.1],[1.12,2.17,.14],[.2,.4,.1],.8,5e6)
        self.assertEqual(len(r['corners']),8)
        self.assertLessEqual(max(r['maxcorner']-r['rbound']),2e-14)
        self.assertTrue(np.all(r['H']==r['H'].transpose(0,2,1)))
        self.assertTrue(np.all(np.isfinite(r['quadratic_photon_event_remainder_bound'])))

    def test_zero_width_remainder(self):
        s=[1.,2.,3.]
        r=f.finite_corner_report(s,s,s,[.2,.1,.4],1,100)
        self.assertEqual(r['L'],0)
        self.assertTrue(np.all(r['rbound']==0))

    def test_zero_external_valid(self):
        r=f.finite_corner_report([1.,2.,3.],[2.,3.,4.],[3.,4.,5.],[1.,2.,.2],0,100)
        self.assertTrue(np.isfinite(r['J']).all())
        self.assertAlmostEqual(sum(r['p']),1)

    def test_zero_supported_species(self):
        r=f.finite_corner_report([1.,2.,3.],[2.,3.,4.],[3.,4.,5.],[0.,2.,.2],1,100)
        self.assertEqual(r['p'][0],0)
        self.assertEqual(r['rbound'][0],0)

    def test_input_reject(self):
        with self.assertRaises(ValueError):f.finite_corner_report([0,2,3],[2,3,4],[3,4,5],[1,1,1],1,100)
        with self.assertRaises(ValueError):f.finite_corner_report([1,2,3],[.9,3,4],[3,4,5],[1,1,1],1,100)
        with self.assertRaises(ValueError):f.shares([-1,0,2],1)
        with self.assertRaises(ValueError):f.log_fraction_response([1,2,3],1,[float('nan'),0,0])

    def test_exact_binary_sum_enclosure(self):
        from decimal import Decimal,localcontext
        a=np.array([1e-18,.1,1e-30,.2,1e-28,1e-18,10.],float)
        lo,hi=f.exact_sum_bounds(a)
        with localcontext() as c:
            c.prec=180
            exact=sum((Decimal.from_float(float(x)) for x in a),Decimal(0))
        self.assertLessEqual(Decimal.from_float(lo),exact)
        self.assertGreaterEqual(Decimal.from_float(hi),exact)

    def test_random_box_corners(self):
        rng=np.random.default_rng(811)
        for _ in range(320):
            s0=10**rng.uniform(-2,2,size=3)
            slo=s0*np.exp(-rng.uniform(0,.12,size=3))
            shi=s0*np.exp(rng.uniform(0,.12,size=3))
            c=np.where(rng.uniform(size=3)<.2,0.,rng.uniform(.1,10,size=3))
            r=f.finite_corner_report(slo,s0,shi,c,float(rng.uniform(0,5)),float(rng.uniform(1,1e8)))
            self.assertTrue(np.all(r['maxcorner']<=r['rbound']+2e-14))

if __name__=='__main__':unittest.main()
