"""Scientific regressions and deliberately negative contract tests."""
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from rice_covariance import (A_P2,BIN_SPECS,M_ALPHA,M_D,Q,delta,daughters,angular_density,
                             daughter_pdf,tail_probability,bound_for_bin,monotonic_split_upper,
                             covariance_from_discrete,build_results)

def simpson(f,a,b,n=6000):
    h=(b-a)/n
    return h/3*(f(a)+f(b)+4*math.fsum(f(a+i*h) for i in range(1,n,2))+2*math.fsum(f(a+i*h) for i in range(2,n,2)))

class RiceP2Source(unittest.TestCase):
    def test_threshold_masses(self):
        self.assertAlmostEqual(Q,23.84647820,places=7)
    def test_source_reported_fit_totals(self):
        self.assertAlmostEqual(2*math.pi*1.32,8.29,delta=0.015)
        self.assertAlmostEqual(2*math.pi*.69,4.34,delta=0.015)
    def test_normalized_angular_density(self):
        self.assertAlmostEqual(simpson(angular_density,-1,1),1.,places=11)
        self.assertAlmostEqual(simpson(lambda x:x*x*angular_density(x),-1,1),.2,places=11)
        self.assertAlmostEqual(simpson(lambda x:x*angular_density(x),-1,1),0.,places=11)
    def test_energy_sum_identity(self):
        for e in [150,180,190,213,220,250]:
            for mu in [-1,-.85,-.4,0,.5,1]:
                kp,km=daughters(e,mu)
                self.assertAlmostEqual(kp+km,e-Q,places=11)
                other=daughters(e,-mu)
                self.assertAlmostEqual(kp,other[1],places=11)
    def test_pdf_normalization_and_variance(self):
        for e in [150,190,220,250]:
            ctr=(e-Q)/2;d=delta(e)
            self.assertAlmostEqual(simpson(lambda k:daughter_pdf(e,k),ctr-d,ctr+d),1.,places=10)
            v=simpson(lambda k:(k-ctr)**2*daughter_pdf(e,k),ctr-d,ctr+d)
            self.assertAlmostEqual(v,d*d/5,delta=2e-8)
    def test_tail_limits_and_monotonicity(self):
        for a,b,*_ in BIN_SPECS:
            for threshold in [60,80,100,120,140]:
                values=[tail_probability(a+i*(b-a)/200,threshold) for i in range(201)]
                self.assertTrue(all(-1e-12<=x<=1+1e-12 for x in values))
                self.assertTrue(all(values[i]<=values[i+1]+1e-12 for i in range(200)))
    def test_monotone_delta_certificate(self):
        self.assertLess(monotonic_split_upper(150,250),.5)
    def test_covariance_upper_model(self):
        for a,b,*_ in BIN_SPECS:
            x=bound_for_bin(a,b)
            self.assertLess(x['max_covariance_upper_MeV2'],0)
            self.assertLess(x['a_critical_for_forced_negative_pair_covariance'], A_P2)
            self.assertTrue(0<=x['sharp_extremizer_probability_at_Emax']<=1)
    def test_bound_is_sharp_endpoint_distribution(self):
        for a,b,*_ in BIN_SPECS:
            x=bound_for_bin(a,b)
            p=x['sharp_extremizer_probability_at_Emax']
            actual=covariance_from_discrete([a,b],[1-p,p])
            self.assertAlmostEqual(actual,x['max_covariance_upper_MeV2'],places=9)
    def test_no_other_E_distribution_exceeds_bound(self):
        g=random.Random(20261030)
        for a,b,*_ in BIN_SPECS:
            upper=bound_for_bin(a,b)['max_covariance_upper_MeV2']
            for _ in range(500):
                e=[g.uniform(a,b) for j in range(8)]
                w=[g.random() for j in range(8)]
                self.assertLessEqual(covariance_from_discrete(e,w),upper+2e-10)
    def test_model_not_observed_history(self):
        x=build_results()
        self.assertIsNone(x['target_epoch_He_rest_photon_history'])
        self.assertIsNone(x['reaction_event_rate'])
        self.assertIsNone(x['heat_rate'])
        self.assertEqual(x['central_DAG'],'28/88')
        self.assertEqual(x['HE_physical_DAG'],'14/18')
        self.assertEqual(len(x['tails']),10)
    def test_invalid_inputs_fail_closed(self):
        for e in [0,Q,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):delta(e)
        for mu in [-2,2]:
            with self.assertRaises(ValueError):daughters(220,mu)
        with self.assertRaises(ValueError):covariance_from_discrete([190],[0])
        with self.assertRaises(ValueError):bound_for_bin(250,190)
    def test_angular_assumption_sensitive(self):
        x=bound_for_bin(190,250,a2moment=.19)
        self.assertGreater(x['max_covariance_upper_MeV2'],0)
        self.assertLess(x['a_critical_for_forced_negative_pair_covariance'],.2)

if __name__=='__main__':unittest.main()
