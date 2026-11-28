"""Manufactured overlap/geometry checks. No molecular eigensolve or archive read."""
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
import numpy as np
from numpy.polynomial import Polynomial
from scipy.interpolate import BSpline
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from overlap_integral import (Values,charge_center_positions,common_o_to_prolate,
                              geometry,patches,pair_overlap,refinement_audit)


def manufactured(m=0,R=2.,charges=(1.,2.)):
    degree=3
    def axis(edges,radial):
        edges=np.asarray(edges,float)
        knots=np.r_[np.repeat(edges[0],degree),edges,np.repeat(edges[-1],degree)]
        n=len(knots)-degree-1
        basis=BSpline(knots,np.eye(n)[:,:n-int(radial)],degree,extrapolate=False)
        greville=np.array([np.mean(knots[i+1:i+degree+1]) for i in range(n)])
        coefficients=(edges[-1]-greville)[:-1] if radial else np.ones(n)
        return SimpleNamespace(edges=edges,basis=basis),coefficients
    radial,cr=axis([1,1.5,2,3],True);angular,ca=axis([-1,-.2,.7,1],False)
    x=Polynomial([0,1]);f=(3-x)**2*(x*x-1)**m;g=(1-x*x)**m
    def integ(p,lo,hi):
        a=p.integ();return a(hi)-a(lo)
    norm2=R**3/8*(integ(f*x*x,1,3)*integ(g,-1,1)-integ(f,1,3)*integ(g*x*x,-1,1))
    return SimpleNamespace(R=R,ZA=charges[0],ZB=charges[1],m=m,xi_max=3.,normalization=norm2**-.5,
                           radial_coefficients=cr,angular_coefficients=ca,_radial=radial,_angular=angular)


class OverlapTests(unittest.TestCase):
    def test_exact_manufactured_norms(self):
        for m in (0,1):
            state=manufactured(m)
            rec=pair_overlap(state,state,20,backend='python')
            self.assertLess(rec['max_self_norm_error_abs'],5e-14)
            self.assertLess(abs(rec['overlap']-1),5e-14)
            self.assertEqual(rec['directional_difference_abs'],0)
    def test_landmarks_are_target_nuclei(self):
        for targetR in (1.,2.,3.):
            source=manufactured(R=2.);target=manufactured(R=targetR)
            _,meta=geometry(source,target)
            mid=charge_center_positions(source.R,source.ZA,source.ZB)[2]
            calculated=[]
            for s,theta,xi in meta['target_nuclei_stheta']:
                calculated.append(source.R/2*np.sqrt(1+s*s)*np.cos(theta)+mid)
                self.assertLess(abs(source.R/2*s*np.sin(theta)),2e-15)
            np.testing.assert_allclose(calculated,charge_center_positions(target.R,target.ZA,target.ZB)[:2],rtol=0,atol=2e-15)
    def test_duffy_tiles_source_domain(self):
        source=manufactured(R=2.);target=manufactured(R=3.)
        measure=sum(float(np.sum(w)) for s,t,w in patches(source,target,12))
        self.assertAlmostEqual(measure,np.sqrt(8)*np.pi,places=13)
        for s,t,w in patches(source,target,12):
            self.assertTrue(np.all(s>0));self.assertTrue(np.all(t>0));self.assertTrue(np.all(t<np.pi));self.assertTrue(np.all(w>0))
    def test_geometry_metric_balance(self):
        source=manufactured(R=11.);target=manufactured(R=12.)
        cells,_=geometry(source,target)
        for sl,sh,tl,th,p in cells:
            if p is None:continue
            hs=(sh-sl)/p[2] if p[0]>0 else sh-sl
            self.assertLessEqual(max(hs,th-tl)/min(hs,th-tl),2.+1e-14)
    def test_zero_extension_and_common_origin(self):
        state=manufactured();value=Values(state)
        xi,eta=common_o_to_prolate(np.array([100.]),np.array([100.]),state)
        self.assertEqual(value(xi,eta)[0],0.)
        za,zb,mid=charge_center_positions(3.,1.,2.)
        self.assertEqual((za,zb,mid),(-2.,1.,-.5))
    def test_negative_phase_and_three_order_gate(self):
        a=manufactured(m=1);b=copy.deepcopy(a);b.radial_coefficients*=-1
        records=[pair_overlap(a,b,q,'python') for q in (12,16,20)]
        audit=refinement_audit(records)
        self.assertTrue(audit['transport_pass']);self.assertEqual(audit['phase_factor'],-1)
        bad=copy.deepcopy(records);bad[-2]['directional_difference_abs']=2e-7
        self.assertFalse(refinement_audit(bad)['transport_pass'])
        with self.assertRaises(ValueError):refinement_audit(records[:2])
    def test_native_python_parity(self):
        for m in (0,1):
            a=manufactured(m=m,R=2.);b=manufactured(m=m,R=3.)
            native=pair_overlap(a,b,20,'native');reference=pair_overlap(a,b,20,'python')
            for key in ('left_domain_overlap','right_domain_overlap','self_norm_left','self_norm_right','normalized_overlap'):
                self.assertLess(abs(native[key]-reference[key]),2e-14)
    def test_native_invalid_inputs_rejected(self):
        from integration_native import sum_products
        for counts in (np.array([0]),np.array([3]),np.array([1.,1.])):
            with self.assertRaises(ValueError):sum_products(np.ones(2),np.ones(2),np.ones(2),counts)
        with self.assertRaises(ValueError):sum_products(np.ones(2),np.array([1.,np.nan]),np.ones(2),np.array([2]))
    def test_input_rejection(self):
        with self.assertRaises(ValueError):pair_overlap(manufactured(0),manufactured(1),16,'python')
        with self.assertRaises(ValueError):pair_overlap(manufactured(),manufactured(),True,'python')
        with self.assertRaises(ValueError):pair_overlap(manufactured(),manufactured(),16,'fallback')

if __name__=='__main__':unittest.main()
