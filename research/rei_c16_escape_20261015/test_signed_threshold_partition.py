#!/usr/bin/env python3
"""Independent Bianchi signed-threshold positive-cell tests, not old 62."""
import math
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import signed_threshold_partition as s

class ExactGeometryTests(unittest.TestCase):
    def test_flrw_identity(self):
        for mu in [-1.,-.4,0.,.35,1.]:
            self.assertAlmostEqual(s.photon_ratio(0.,mu),1.)
            self.assertAlmostEqual(s.threshold_q(.2,54.42,0.,mu),10.884)
            self.assertAlmostEqual(s.threshold_velocity(0.,mu,0.),1.)
    def test_signed_axis(self):
        for d in [-.25,0.,.21]:
            self.assertAlmostEqual(s.photon_ratio(d,0.),math.exp(d))
            self.assertAlmostEqual(s.photon_ratio(d,1.),math.exp(-2*d))
            for v in [-.15,.10]:
                self.assertAlmostEqual(s.threshold_velocity(d,0.,v),1-v)
                self.assertAlmostEqual(s.threshold_velocity(d,1.,v),1+2*v)
    def test_characteristic_metric_inverse(self):
        for d in [-.14,.07,.21]:
            for mu in [-1.,-.65,.0,.55,1.]:
                inv_perp=math.exp(d)
                inv_axial=math.exp(-2*d)
                r2=(1-mu*mu)*inv_perp**2+mu*mu*inv_axial**2
                self.assertAlmostEqual(r2,s.photon_ratio(d,mu)**2)
    def test_dlogthreshold_high_precision_independent(self):
        import mpmath as mp
        mp.mp.dps=65
        for mu in [-1.,-.48,0.,.66,1.]:
            for v in [-.6,-.04,0.,.32,1.04]:
                x=mp.mpf("0.1")
                d=mp.mpf("0.023")
                m=mp.mpf(str(mu))
                sh=mp.mpf(str(v))
                def independent_logq(xx):
                    dd=d+sh*(xx-x)
                    r=mp.sqrt((1-m*m)*mp.exp(2*dd)+m*m*mp.exp(-4*dd))
                    return xx+mp.log(mp.mpf("24.59"))-mp.log(r)
                high_precision=float(mp.diff(independent_logq,x))
                calculated=s.threshold_velocity(float(d),mu,v)
                self.assertAlmostEqual(calculated,high_precision,delta=3e-14)
    def test_can_reverse_when_anisotropic(self):
        self.assertLess(s.threshold_velocity(0.,0.,1.1),0.)
        self.assertLess(s.threshold_velocity(0.,1.,-.6),0.)
        for v in [-.49,0.,.2,.9]:
            self.assertGreater(min(s.threshold_velocity(.06,mu,v) for mu in [-1.,0.,1.]),0.)

class PositiveClosureTests(unittest.TestCase):
    def test_inversion_exponential_moments(self):
        for t in [-200.,-20.,-4.,-.002,0.,.002,.2,2.,20.,150.]:
            mean=s.unit_mean(t)
            fit=s.fit_slope(mean)
            self.assertAlmostEqual(s.unit_mean(fit),mean,delta=2e-14)
    def test_symmetry(self):
        for t in [0.,.001,.23,1.,9.,99.]:
            self.assertAlmostEqual(s.unit_mean(t)+s.unit_mean(-t),1.,delta=2e-15)
    def test_uniform_cell_exact(self):
        out=s.split_parent(1.5,4.5,2.,4.,3.)
        self.assertAlmostEqual(out.active_n,.75)
        self.assertAlmostEqual(out.passive_n,.75)
        self.assertAlmostEqual(out.active_u,2.625)
        self.assertAlmostEqual(out.passive_u,1.875)
        self.assertEqual(out.slope,0.)
    def test_positive_conservation_random(self):
        rng=random.Random(20261015)
        for _ in range(1000):
            lo=rng.uniform(.1,7.)
            hi=lo+rng.uniform(.1,10.)
            n=10**rng.uniform(-7,2)
            t=rng.uniform(-25,25)
            m=s.unit_mean(t)
            u=n*(lo+(hi-lo)*m)
            cut=rng.uniform(lo-.01*(hi-lo),hi+.01*(hi-lo))
            out=s.split_parent(n,u,lo,hi,cut,slope=t)
            self.assertGreaterEqual(out.active_n,0.)
            self.assertGreaterEqual(out.passive_n,0.)
            self.assertGreaterEqual(out.active_u,0.)
            self.assertGreaterEqual(out.passive_u,0.)
            self.assertAlmostEqual(out.active_n+out.passive_n,n,delta=2e-15*max(1.,n))
            self.assertAlmostEqual(out.active_u+out.passive_u,u,delta=2e-15*max(1.,u))
            self.assertLessEqual(out.active_u,hi*out.active_n+1e-11)
            self.assertLessEqual(out.passive_u,hi*out.passive_n+1e-11)
    def test_reversible_moving_cut(self):
        original=(.42,1.26,2.,4.)
        cuts=[1.,3.8,2.6,3.99,2.,3.3,4.5,1.1,2.6]
        results=[s.split_parent(*original,cut) for cut in cuts]
        self.assertAlmostEqual(results[2].active_n,results[-1].active_n)
        self.assertAlmostEqual(results[2].active_u,results[-1].active_u)
    def test_tiny_passive_positive_regression(self):
        # Preserved Rust 4M-case NCP failure: cancellation produced negative
        # ~3e-14 eV when active dominated (t about +29.47).
        cases=[
            (.24971307045505534,35.443966638684465,29.470397434767253,
             4.400581512699786,.2870781925288911),
            (16.781308148654286,54.18056496851821,27.439255780059316,
             3.5871413173518847,16.781335534074863),
            (19.71164657794233,75.16307059938998,29.743456225027277,
             2.9689902221871147,19.71585220012639)]
        for lo,hi,t,n,cut in cases:
            u=n*(lo+(hi-lo)*s.unit_mean(t))
            out=s.split_parent(n,u,lo,hi,cut,slope=t)
            self.assertGreaterEqual(out.passive_u,0.)
            self.assertGreaterEqual(out.active_u,0.)
            self.assertLessEqual(out.passive_u,cut*out.passive_n+1e-15)
            self.assertAlmostEqual(out.active_u+out.passive_u,u,delta=5e-14)
    def test_endpoint_delta(self):
        low=s.split_parent(1.0,2.0,2.,4.,2.)
        self.assertEqual(low.active_n,1.)
        high=s.split_parent(1.0,4.0,2.,4.,4.)
        self.assertEqual(high.active_n,1.)
        high2=s.split_parent(1.0,4.0,2.,4.,4.0001)
        self.assertEqual(high2.active_n,0.)
    def test_nested_species_active_number(self):
        parent=(1.,55.,10.,70.)
        for d in [-.1,0.,.2]:
            cuts=[s.threshold_q(.7,e,d,.29) for e in [13.6,24.59,54.42]]
            n=[s.split_parent(*parent,c).active_n for c in cuts]
            self.assertGreaterEqual(n[0]+1e-15,n[1])
            self.assertGreaterEqual(n[1]+1e-15,n[2])
    def test_reverse_flux_sign(self):
        self.assertGreater(s.flux_on_cut(.6,2.,4.,3.,0.,1.2)[0],0.)
        self.assertLess(s.flux_on_cut(.6,2.,4.,3.,0.,-1.2)[0],0.)
    def test_flux_cut_derivative_both_moments(self):
        for t in [-10.,0.,.1,9.]:
            n=3.0;lo=10.;hi=40.;r=.34
            cut=lo+(hi-lo)*r
            u=n*(lo+(hi-lo)*s.unit_mean(t))
            drift=-.04
            h=1e-5
            hi_cut=cut*math.exp(h*drift)
            lo_cut=cut*math.exp(-h*drift)
            before=s.split_parent(n,u,lo,hi,lo_cut,slope=t)
            after=s.split_parent(n,u,lo,hi,hi_cut,slope=t)
            fn,fu=s.flux_on_cut(n,lo,hi,cut,t,drift)
            self.assertAlmostEqual((after.active_n-before.active_n)/(2*h),-fn,delta=3e-10)
            self.assertAlmostEqual((after.active_u-before.active_u)/(2*h),-fu,delta=2e-8)
    def test_invalid_moments_rejected(self):
        for fields in [(1.,5.,2.,4.,3.),(-1.,3.,2.,4.,3.),
                       (0.,1.,2.,4.,3.),(1.,3.,4.,2.,3.)]:
            with self.assertRaises(ValueError):
                s.split_parent(*fields)
    def test_outside_cut_no_flux(self):
        for c in [1.0,2.,4.0001,7.]:
            out=s.split_parent(.1,.3,2.,4.,c)
            self.assertAlmostEqual(out.active_n+out.passive_n,.1)

class IndependentQuadrature(unittest.TestCase):
    def test_high_precision_direct_integral(self):
        import mpmath as mp
        mp.mp.dps=55
        for t in [-14.,-2.,0.,1.,9.]:
            n=1.7;lo=2.;hi=5.;cut=3.4
            mean=s.unit_mean(t)
            out=s.split_parent(n,n*(lo+(hi-lo)*mean),lo,hi,cut,slope=t)
            tt=mp.mpf(str(t))
            rr=mp.mpf(str((cut-lo)/(hi-lo)))
            z=mp.quad(lambda y: mp.exp(tt*y),[0,1])
            exact_n=float(n*mp.quad(lambda y: mp.exp(tt*y),[rr,1])/z)
            exact_u=float(n*mp.quad(lambda y: (mp.mpf("2")+3*y)*mp.exp(tt*y),[rr,1])/z)
            self.assertAlmostEqual(out.active_n,exact_n,delta=3e-13)
            self.assertAlmostEqual(out.active_u,exact_u,delta=5e-12)

if __name__=="__main__":
    unittest.main(verbosity=2)
