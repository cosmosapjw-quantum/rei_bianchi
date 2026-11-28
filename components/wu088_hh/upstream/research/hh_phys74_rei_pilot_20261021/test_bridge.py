"""Focused correctness checks, not performance or broad convergence testing."""
import math
import unittest
import numpy as np
from bridge import norms, PreparedFactory, mapped_case, make_grid

class BridgeTests(unittest.TestCase):
    def test_tensor_norms_and_work(self):
        got=norms(2., 0.3, [-0.02,0.01,0.04], kappa_time=7.)
        s=np.diag([-0.3,-0.3,0.6]); p=np.diag([-0.03,-0.03,0.06])
        self.assertAlmostEqual(got['Sigma_F'],np.linalg.norm(s)/2.)
        self.assertAlmostEqual(got['Pi_F'],7*np.linalg.norm(p)/4.)
        self.assertAlmostEqual(got['work'],7*np.sum(s*p)/8.)
    def test_stress_cancels_before_norm(self):
        got=norms(2.,0.3,[1.,-1.])
        self.assertEqual(got['Pi_F'],0.)
        self.assertIsNone(got['alignment'])
    def test_invalid_inputs(self):
        for H,s,ps in [(0.,1.,[1.]),(1.,float('nan'),[0.]),(1.,0.,[float('inf')])]:
            with self.assertRaises(ValueError):norms(H,s,ps)
    def test_legacy_factor(self):
        got=norms(3.,.2,[.1])
        self.assertAlmostEqual(got['Sigma_F']/got['Sigma_half'],math.sqrt(2))
    def test_grid(self):
        g=make_grid()
        self.assertEqual(len(g),63)
        self.assertEqual(len({(a,b) for a,b in g}),63)
    def test_initial_mapping_and_positive_domain(self):
        factory=PreparedFactory()
        for S,P in [(.004,.001),(-.004,-.001),(0.,0.),(.001,-.0005)]:
            obj,meta=mapped_case(factory,S,P)
            q=obj.fields(0.,obj.initial_state())
            got=norms(q['H'],q['s'],[q['Pi_gamma_J_m3'],q['Pi_nu_J_m3'],q['Pi_matter_J_m3']])
            self.assertAlmostEqual(got['Sigma_signed'],S,places=13)
            self.assertAlmostEqual(got['Pi_signed'],P,places=13)
            self.assertGreaterEqual(1-abs(meta['kappa_radiation']),.5)
        with self.assertRaises(ValueError): mapped_case(factory,.001,1.)
    def test_prepared_same_rhs_and_immutable_arrays(self):
        factory=PreparedFactory()
        a,_=mapped_case(factory,.002,-.0005)
        b=factory.fresh(a.Sigma_ref,a.orientation,a.k_gamma,a.k_nu)
        self.assertTrue(np.array_equal(a.initial_state(),b.initial_state()))
        y=a.initial_state()
        for x in [0.,.01]:
            self.assertTrue(np.array_equal(a.rhs(x,y),b.rhs(x,y)))
        with self.assertRaises(ValueError): a.energy_matrix[0,0]=1.
        c,_=mapped_case(factory,-.002,.0005)
        self.assertIs(a.momentum,c.momentum)
        self.assertIs(a.energy_matrix,c.energy_matrix)
        self.assertIsNot(a.initial_state(),c.initial_state())
    def test_history_parity(self):
        factory=PreparedFactory()
        a,_=mapped_case(factory,.001,.0005)
        b=factory.fresh(a.Sigma_ref,a.orientation,a.k_gamma,a.k_nu)
        sa,da,_=a.integrate(n=17,rtol=3e-11,atol=3e-13)
        sb,db,_=b.integrate(n=17,rtol=3e-11,atol=3e-13)
        self.assertTrue(np.array_equal(sa.y,sb.y))
        self.assertTrue(np.array_equal(sa.t,sb.t))

if __name__=='__main__': unittest.main()
