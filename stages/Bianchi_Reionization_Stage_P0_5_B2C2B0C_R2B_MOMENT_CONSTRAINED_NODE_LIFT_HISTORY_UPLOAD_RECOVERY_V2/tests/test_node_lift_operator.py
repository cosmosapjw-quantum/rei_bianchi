from __future__ import annotations
import math
import sys
from pathlib import Path
import unittest
import numpy as np

SRC=Path(__file__).resolve().parents[1]/'src'
sys.path.insert(0,str(SRC))

from node_lift_operator import (  # noqa: E402
    bernoulli_kl_mean_projection,
    positive_mass_projection,
    capacity_constrained_group_projection,
    signed_transfer_lift,
)

class ScalarProjectionTests(unittest.TestCase):
    def test_positive_projection_closes_total_and_preserves_shape(self):
        prior=np.array([1.0,2.0,7.0])
        x=positive_mass_projection(prior,5.0)
        self.assertTrue(np.all(x>=0.0))
        self.assertAlmostEqual(float(x.sum()),5.0,places=14)
        np.testing.assert_allclose(x/x.sum(),prior/prior.sum(),rtol=0,atol=1e-15)

    def test_positive_projection_exact_zero_total(self):
        x=positive_mass_projection(np.array([1.0,2.0]),0.0)
        np.testing.assert_array_equal(x,np.zeros(2))

    def test_bernoulli_projection_identity_has_zero_kl(self):
        w=np.array([0.2,0.3,0.5])
        p=np.array([0.1,0.4,0.8])
        target=float(w@p/w.sum())
        x,cert=bernoulli_kl_mean_projection(p,w,target)
        np.testing.assert_allclose(x,p,rtol=0,atol=2e-14)
        self.assertLessEqual(abs(cert['mean_residual']),1e-14)
        self.assertLessEqual(abs(cert['kl']),1e-14)

    def test_bernoulli_projection_hits_nontrivial_target(self):
        w=np.array([1.0,2.0,3.0,4.0])
        p=np.array([0.02,0.2,0.6,0.95])
        x,cert=bernoulli_kl_mean_projection(p,w,0.73)
        self.assertTrue(np.all((x>0.0)&(x<1.0)))
        self.assertLess(abs(float(w@x/w.sum())-0.73),2e-13)
        self.assertLess(abs(cert['mean_residual']),2e-13)
        self.assertGreaterEqual(cert['kl'],-1e-14)

    def test_signed_transfer_preserves_sign_and_net(self):
        p=np.array([1.0,3.0,6.0])
        pos,neg,net=signed_transfer_lift(-7.5,p)
        self.assertAlmostEqual(float(pos.sum()),0.0,places=15)
        self.assertAlmostEqual(float(neg.sum()),7.5,places=14)
        self.assertAlmostEqual(float(net.sum()),-7.5,places=14)
        np.testing.assert_allclose(net,-7.5*p/p.sum(),rtol=0,atol=1e-15)

class CapacityProjectionTests(unittest.TestCase):
    def test_capacity_projection_closes_columns_and_kkt(self):
        prior=np.array([[8.0,2.0],[1.0,4.0],[1.0,4.0]],dtype=float)
        totals=np.array([6.0,5.0])
        caps=np.array([3.0,4.0,5.0])
        x,cert=capacity_constrained_group_projection(prior,totals,caps,tol=1e-12)
        np.testing.assert_allclose(x.sum(axis=0),totals,rtol=1e-11,atol=1e-11)
        self.assertTrue(np.all(x.sum(axis=1)<=caps+1e-11))
        self.assertGreater(cert['active_row_count'],0)
        self.assertLess(cert['max_column_relative_residual'],1e-11)
        self.assertLess(cert['max_capacity_violation'],1e-11)
        self.assertLess(cert['max_stationarity_residual'],2e-10)
        self.assertLess(cert['max_complementarity_residual'],2e-10)
        lamb=np.asarray(cert['lambda'])
        slack=caps-x.sum(axis=1)
        self.assertTrue(np.all(lamb>=-1e-13))
        self.assertLess(float(np.max(np.abs(lamb*slack))),2e-10)

    def test_identity_projection_zero_kl_when_prior_scaled_columns_is_feasible(self):
        prior=np.array([[2.0,1.0],[1.0,3.0],[2.0,1.0]])
        totals=prior.sum(axis=0)
        caps=np.array([4.0,5.0,4.0])
        x,cert=capacity_constrained_group_projection(prior,totals,caps)
        np.testing.assert_allclose(x,prior,rtol=2e-12,atol=2e-12)
        self.assertLess(abs(cert['generalized_kl']),2e-12)

    def test_infeasible_total_capacity_returns_certificate(self):
        prior=np.ones((3,2))
        with self.assertRaisesRegex(ValueError,'INFEASIBLE_TOTAL_CAPACITY') as ctx:
            capacity_constrained_group_projection(prior,np.array([4.0,3.0]),np.array([1.0,1.0,1.0]))
        self.assertIn('INFEASIBLE_TOTAL_CAPACITY',str(ctx.exception))

if __name__=='__main__':
    unittest.main()
