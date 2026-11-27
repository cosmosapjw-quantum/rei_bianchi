"""Scoped new math/code controls only; not the historic BASS_HE science suite."""
import sys,unittest,random
from fractions import Fraction as F
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import lipschitz_lp_certificate as m

class TestConditionalCertificate(unittest.TestCase):
    def test_source_pinned(self):
        self.assertEqual(m.PARENT_PR,109)
        self.assertEqual(m.PARENT_HEAD,'11b3cfdb987137323d8ebd220e74063b0ed6db22')
        self.assertEqual(m.SOURCE[3],(87,F('0.14'),F('0.24')))
    def test_invalid_input_types(self):
        for x in (0.01,True,False,None,object()):
            with self.assertRaises(TypeError):m.exact(x)
    def test_min_l_rejection(self):
        with self.assertRaises(ValueError):m.make_grid('1/701',2)
    def test_pi_bound_exact(self):
        a,b=m.pi_bounds()
        self.assertLess(a,b)
        self.assertLess(max(abs(m.PI0-a),abs(m.PI0-b)),F(1,10**27))
    def test_taylor_remainder_domination(self):
        from math import factorial
        self.assertLess(6*(F(24,5)**32/factorial(32)+F(24,5)**33/factorial(33)+F(3,2)*F(1,10**27)),m.TRIG_EPS)
    def test_trig_symmetry_against_mpmath(self):
        import mpmath as mp
        with mp.workdps(60):
            for subdiv in (1,5):
                for j in (0,46*subdiv,70*subdiv,90*subdiv-1):
                    th=mp.mpf(2*j+1)/(2*subdiv);z=mp.pi*th/180
                    for t in ('0','0.3','1'):
                        g,gp=m.trig_mid(t,j,subdiv)
                        tt=mp.mpf(t)
                        refg=(mp.mpf('0.25')-tt)*mp.sin(z)+mp.sin(3*z)/4
                        refgp=mp.pi/180*((mp.mpf('0.25')-tt)*mp.cos(z)+mp.mpf('0.75')*mp.cos(3*z))
                        self.assertLess(abs(mp.mpf(g.numerator)/g.denominator-refg),mp.mpf('1e-8'))
                        self.assertLess(abs(mp.mpf(gp.numerator)/gp.denominator-refgp),mp.mpf('1e-8'))
    def test_source_cones_exact(self):
        for L in ('1/700','1/200','1/100'):
            for th,lo,hi in m.SOURCE:
                self.assertGreaterEqual(m.envelope(th,L),lo)
                self.assertLessEqual(m.envelope(th,L,True),hi)
            for i in range(91):self.assertLessEqual(m.envelope(i,L),m.envelope(i,L,True))
    def test_Dlower_vs_independent_quadrature(self):
        import scipy.integrate as si
        import math
        for L in ('1/700','1/200','1/100'):
            R=float(m.Dmin_rational(L))
            vals=[float(v[0]) for v in m.lower_segments(L)] +[90.0]
            actual=sum(si.quad(lambda th:float(m.envelope(str(th),L)) *math.sin(math.pi*th/180),a,b,epsabs=1e-12)[0] for a,b in zip(vals[:-1],vals[1:]))
            self.assertGreaterEqual(actual,R-1e-9)
    def test_all_observation_nodes(self):
        for n in (1,2,10):
            g=m.make_grid('1/200',n)
            self.assertEqual(g.n,90*n+1)
            self.assertGreater(g.Dmin,0)
            self.assertEqual(g.B,F('0.4'))
    def test_lp_positive_dual_bound(self):
        g=m.make_grid('1/700',2)
        for t in ('0.2','0.4'):
            for sign in (-1,1):
                r=m.solve_lp(t,g,sign)
                self.assertGreaterEqual(float(r['dual_upper'])+1e-8,r['numeric_opt'])
                self.assertGreaterEqual(r['penalty'],0)
    def test_primal_projection_is_valid(self):
        g=m.make_grid('1/200',3)
        bad=np.linspace(-0.5,2,g.n)
        good=m.feasible_projection(bad,g)
        self.assertTrue(all(0<=v<=g.B for v in good))
        self.assertTrue(all(abs(good[j+1]-good[j])<=g.L*g.h for j in range(g.n-1)))
    def test_feasible_witness_interval(self):
        g=m.make_grid('1/700',2)
        r=m.solve_lp('0.3',g,-1)
        w=m.witness_bounds(r['raw'],g)
        self.assertTrue(0<w['b_lower']<=w['b_upper']<1)
        self.assertTrue(w['lipschitz_feasible_exact'])
    def test_extrema_outer_inner_enclosure(self):
        for L in ('1/700','1/200'):
            x=m.full_extrema_certificate(L,2,9)
            lo,mi,ma,hi=[F(x[k]) for k in ('min_b_outer_low','min_b_inner_high','max_b_inner_low','max_b_outer_high')]
            self.assertLessEqual(lo,mi)
            self.assertLessEqual(ma,hi)
            self.assertLessEqual(lo,hi)
    def test_error_order_monotonicity(self):
        e1=m.errors(m.make_grid('1/200',2))
        e2=m.errors(m.make_grid('1/200',5))
        self.assertGreater(e1['total'],e2['total'])
    def test_t_outside_unit_rejected(self):
        for t in ('-0.1','1.1'):
            with self.assertRaises(ValueError):m.weights(t,2)
            with self.assertRaises(ValueError):m.certified_outer(t,m.make_grid('1/200',2),'upper')
    def test_gate_hold_no_event(self):
        self.assertIsNone(m.GATES['kappa'])
        self.assertIsNone(m.GATES['R_event'])
        self.assertFalse(m.GATES['physical_activation'])
        self.assertFalse(m.GATES['L4'])
        self.assertEqual(m.GATES['production'],'HOLD')
    def test_adversarial_dual_perturbation_still_bound(self):
        # Even unreliable floating LP marginals cannot turn exact postdual into false feasibility.
        g=m.make_grid('1/200',2)
        r=m.solve_lp('0.45',g,1)
        good=m.feasible_projection(r['raw'],g)
        obj=sum((v*w for v,w in zip(m.weights('0.45',2),good)),F())
        self.assertLessEqual(obj,r['dual_upper'])

if __name__=='__main__':unittest.main()
