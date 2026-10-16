"""Unit and scientific falsification controls for conditional positive age oracle."""
import json
import math
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from positive_reference import (phi1_negative,birth_loss_fraction,frozen_slab,
    midpoint_impulses,midpoint_ratio_exact,source_time_history,positive_node_step)
from native_age_audit import parse_cohorts,summarize
from scipy.integrate import quad,solve_ivp

class PositiveReferenceTests(unittest.TestCase):
    def test_phi1_zero_and_small(self):
        self.assertEqual(phi1_negative(0),1.)
        self.assertEqual(birth_loss_fraction(0),0.)
        for t in (1.e-14,1e-9,1e-7,1e-4,1e-2,1.,20.,1e4):
            a=phi1_negative(t);b=birth_loss_fraction(t)
            self.assertGreaterEqual(a,0);self.assertLessEqual(a,1)
            self.assertGreaterEqual(b,0);self.assertLessEqual(b,1)
            self.assertAlmostEqual(a+b,1.,places=14)

    def test_scalar_source_only(self):
        r=frozen_slab(0.,.7,(0.,0.,0.),.001,60.)
        self.assertAlmostEqual(r.survived,.7,places=14)
        self.assertEqual(sum(r.absorbed),0.)

    def test_initial_plus_newborn(self):
        r=frozen_slab(.3,.8,(300.,0.,0.),.002,60.)
        tau=.6
        self.assertAlmostEqual(r.survived,.3*math.exp(-tau)+.8*phi1_negative(tau),places=14)
        self.assertAlmostEqual(sum(r.absorbed),.3+.8-r.survived,places=14)
        self.assertLess(abs(r.number_residual),2e-15)
        self.assertLess(abs(r.energy_residual_ev),1e-13)

    def test_competing_he_species_and_energy(self):
        r=frozen_slab(.5,.1,(400.,200.,100.),.001,80.)
        self.assertGreater(min(r.absorbed),0)
        self.assertAlmostEqual(r.absorbed[0]/r.absorbed[2],4.,places=13)
        self.assertLess(abs(r.energy_residual_ev),1e-13)
        self.assertGreater(r.photoheat_ev,0)
        self.assertGreater(r.binding_ev,0)

    def test_invalid_below_fit(self):
        with self.assertRaises(ValueError):frozen_slab(1.,0.,(0.,0.,1.),.01,54.419)
        with self.assertRaises(ValueError):frozen_slab(1.,0.,(0.,0.,1.),.01,20.)

    def test_invalid_domain(self):
        for opts in [(-1.,1.,(1.,0.,0.),.001,20.),(1.,-1.,(1.,0.,0.),.001,20.),
                     (1.,1.,(-1.,0.,0.),.001,20.),(1.,1.,(1.,0.,0.),-1.,20.),
                     (1.,1.,(1.,0.,0.),.001,float('nan'))]:
            with self.subTest(opts=opts),self.assertRaises(ValueError):frozen_slab(*opts)

    def test_midpoint_ratio(self):
        for tau in (.00001,.1,1.,15.,80.,200.,350.):
            true=phi1_negative(tau)
            for n in (4,8,16,32,128):
                m=midpoint_impulses(1.,tau,n)
                self.assertAlmostEqual(m/true,midpoint_ratio_exact(tau,n),delta=2e-13)
                self.assertLessEqual(m,true*(1+1e-12))

    def test_midpoint_growth_from_doubling(self):
        tau=200.
        for n in (8,16,32,64):
            a=midpoint_impulses(1.,tau,n)
            b=midpoint_impulses(1.,tau,2*n)
            self.assertAlmostEqual(b/a,math.cosh(tau/(4*n)),delta=2e-12*math.cosh(tau/(4*n)))
            self.assertGreater(b,a)

    def test_phi1_erases_born_boundary_layer_without_mass_bias(self):
        emitted=7.29527e-5;tau=200.
        accurate=frozen_slab(0.,emitted,(tau/0.002,0.,0.),0.002,30.)
        self.assertAlmostEqual(accurate.survived,emitted*phi1_negative(tau),places=18)
        for n in (8,16,32):
            self.assertLess(midpoint_impulses(emitted,tau,n),accurate.survived)

    def test_native_archive_derived_signed_summary(self):
        d=json.loads((ROOT/'results/native_age_summary.json').read_text())
        for q in ('-0.1','0','0.1'):
            obj=d['by_signed_s_over_H'][q]
            self.assertLess(obj['total_emission_relative_span'],5e-8)
            self.assertGreater(obj['observed_ratio_16_over_8'],50.)
            self.assertGreater(obj['observed_ratio_32_over_16'],10.)
            for n in ('8','16','32'):
                self.assertGreater(obj[n]['last_cohort_share_of_survivors'],0.996)

    def test_native_archive_sensitivity_does_not_identify_fixed_kappa(self):
        d=json.loads((ROOT/'results/native_age_summary.json').read_text())
        for q,obj in d['by_signed_s_over_H'].items():
            first=obj['effective_constant_opacity_depth_from_first_ratio']
            second=obj['effective_constant_opacity_depth_from_second_ratio']
            self.assertGreater(second-first,40.,msg=q)

    def test_reconstructed_cohort_parser(self):
        text=('Accepted { cohorts: [Cohort { birth: Birth { lower_x: 0.0, upper_x: 0.2, '
              'x: 0.1, j_per_h_dln_a: 10.0, quadrature_weight_dln_a: 0.2, '
              'original: PhotonState { number: [1.0, 1.0], energy_ref: [40, 40] }, '
              'surviving: PhotonState { number: [0.2, 0.3], energy_ref: [4, 5] } } }] }')
        cohort=parse_cohorts(text)
        self.assertEqual(len(cohort),1)
        self.assertAlmostEqual(cohort[0]['original_n'],2.)
        self.assertAlmostEqual(summarize(cohort)['survived_n_per_H'],.5)

    def test_smooth_variable_opacity_independent_quad(self):
        L=.002;j0=.036
        def j(x):return j0*(1+.18*x/L)
        def k(x):return (8e4*(1+.25*x/L),0.,0.)
        def depth(x):return 8e4*((L-x)+.25*(L*L-x*x)/(2*L))
        ref=quad(lambda x:j(x)*math.exp(-depth(x)),0,L,epsabs=3e-16,epsrel=2e-12,limit=500)[0]
        errors=[]
        for n in (100,200,400,800):
            r=source_time_history(0,L,n,j,k,50.)
            errors.append(abs(r['survived']-ref))
            self.assertGreater(r['survived'],0)
            self.assertLess(abs(r['photon_ledger_residual']),1e-16)
            self.assertLess(abs(r['energy_ledger_residual_ev']),1e-14)
        self.assertGreater(errors[0]/errors[1],3.5)
        self.assertGreater(errors[1]/errors[2],3.5)
        self.assertGreater(errors[2]/errors[3],3.5)

    def test_event_split_he_threshold(self):
        # Prescribed abrupt ionization event; source continuous; split exactly there.
        event=.63;energy=80.
        def j(x):return .4
        def k(x):return (1.5,0.,8. if x>=event else 0.)
        exact1=frozen_slab(0.,j(0)*event,(1.5,0,0),event,energy)
        exact2=frozen_slab(exact1.survived,j(0)*(1-event),(1.5,0,8.),1-event,energy)
        expected=exact2.survived
        for n in (1,3,7):
            r=source_time_history(0,1,n,j,k,energy,split_at=(event,))
            self.assertAlmostEqual(r['survived'],expected,places=14)
        unsplit=source_time_history(0,1,1,j,k,energy)
        self.assertGreater(abs(unsplit['survived']-expected),0.02)

    def test_signed_three_channel_photon_nodes(self):
        q=[15.,30.,65.,90.];n=[.1,.2,.3,.4]
        rates=[(1.,0.,0.),(1.,2.,0.),(1.,2.,5.),(1.,2.,5.)]
        ans=positive_node_step(q,n,rates,.2,1.)
        self.assertGreater(ans['number'],0.)
        self.assertTrue(all(v>=0 for v in ans['events']))
        self.assertLess(abs(ans['number_residual']),4e-16)
        self.assertLess(abs(ans['q_energy_residual']),5e-14)
        self.assertLess(abs(ans['physical_energy_residual']),5e-14)
        self.assertGreaterEqual(ans['reference_energy']/ans['number'],min(q))
        self.assertLessEqual(ans['reference_energy']/ans['number'],max(q))

    def test_negative_dop853_internal_trial_manufactured(self):
        # SciPy 1.17, rtol2e-9, atol1e-15: positive ODE but internal RK trial <0.
        calls=[0];neg=[]
        def guarded(x,y):
            calls[0]+=1
            if y[0]<0:
                neg.append((x,float(y[0])))
                raise ValueError('physical nonnegative native-domain guard')
            return [-30000.*y[0]]
        with self.assertRaisesRegex(ValueError,'native-domain guard'):
            solve_ivp(guarded,(0,.002),[9e-6],method='DOP853',rtol=2e-9,atol=1e-15)
        self.assertGreater(calls[0],50)
        self.assertLess(neg[0][1],0.)
        # Nonnegative continuous exact update for identical scalar physics.
        val=9e-6
        for _ in range(100):
            val=frozen_slab(val,0.,(30000.,0.,0.),.002/100,30.).survived
        self.assertGreater(val,0.)
        self.assertAlmostEqual(val,9e-6*math.exp(-60),delta=1e-30)

    def test_zero_and_stiff_limit(self):
        z=frozen_slab(0.,0.,(0.,0.,0.),.01,0.)
        self.assertEqual(z.survived,0.)
        r=frozen_slab(1.,1.,(1e8,0.,0.),.1,50.)
        self.assertGreaterEqual(r.survived,0.)
        self.assertGreater(r.absorbed[0],1.9)
        self.assertLess(abs(r.number_residual),1e-10)

if __name__=='__main__':unittest.main()
