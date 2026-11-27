import numpy as np
import pytest

from bass_he.geometry import adaptive_vector_quadrature, AdaptiveQuadratureError
from bass_he.rotation import full_rotation_batch


def test_adaptive_u_quadrature_integrates_vector_polynomial_across_known_split():
    def evaluate(rhos):
        r=np.asarray(rhos,float)
        return np.stack([np.ones_like(r),r*r],axis=1)
    out=adaptive_vector_quadrature(evaluate,[0.,1.,2.],rtol=1e-10,atol=1e-12,max_intervals=32)
    np.testing.assert_allclose(out['integral'],[4*np.pi,8*np.pi],rtol=2e-12,atol=2e-12)
    assert out['converged']
    assert out['known_splits_preserved']==[0.,1.,2.]


def test_known_support_jump_is_never_integrated_across():
    seen=[]
    def evaluate(rhos):
        r=np.asarray(rhos,float);seen.extend(r.tolist())
        return (r<1.)[:,None].astype(float)
    out=adaptive_vector_quadrature(evaluate,[0.,1.,2.],rtol=1e-11,atol=1e-12,max_intervals=32)
    np.testing.assert_allclose(out['integral'],[np.pi],rtol=2e-12,atol=2e-12)
    assert all(abs(x-1.)>1e-14 for x in seen)


def test_componentwise_error_catches_cancellation_hidden_in_total():
    c=4.0
    exact=np.array([np.e-1., c-(np.e-1.)])*np.pi
    def evaluate(rhos):
        u=np.asarray(rhos,float)**2
        a=np.exp(u)
        return np.stack([a,c-a],axis=1)
    out=adaptive_vector_quadrature(evaluate,[0.,1.],rtol=2e-10,atol=1e-12,max_intervals=128)
    np.testing.assert_allclose(out['integral'],exact,rtol=2e-10,atol=2e-12)
    assert np.all(out['component_error_estimate'] <= out['component_tolerance'])
    # The summed integrand is exactly constant, so a scalar-total-only gate would be blind.
    assert abs(out['integral'].sum()-c*np.pi)<1e-12


def test_adaptive_budget_exhaustion_is_explicit():
    def evaluate(rhos):
        r=np.asarray(rhos,float)
        return np.sin(150*r*r)[:,None]**2
    with pytest.raises(AdaptiveQuadratureError,match='budget'):
        adaptive_vector_quadrature(evaluate,[0.,1.],rtol=1e-13,atol=1e-15,max_intervals=1)


def test_rotation_matching_radius_scale_one_is_exactly_backward_compatible():
    E=np.array([.5,5.]);rho=np.array([.2,.4])
    a=full_rotation_batch(3,E,rho,steps=32)
    b=full_rotation_batch(3,E,rho,steps=32,R_cut_scale=1.0)
    np.testing.assert_array_equal(a,b)


def test_mandatory_subinterval_nodes_are_batched_in_one_evaluator_call():
    calls=[]
    def evaluate(rhos):
        calls.append(np.asarray(rhos).copy())
        r=np.asarray(rhos,float)
        return np.stack([np.ones_like(r),r*r],axis=1)
    out=adaptive_vector_quadrature(evaluate,[0.,1.,2.],rtol=1e-8,atol=1e-12,max_intervals=16)
    assert out['converged']
    assert len(calls)==1
    assert calls[0].shape==(30,)


def test_gk7_rule_is_available_for_lower_cost_adaptive_pilot():
    calls=[]
    def evaluate(rhos):
        calls.append(len(rhos));r=np.asarray(rhos,float)
        return np.stack([np.ones_like(r),r*r],axis=1)
    out=adaptive_vector_quadrature(evaluate,[0.,1.,2.],rtol=1e-8,atol=1e-12,max_intervals=16,rule='gk7')
    np.testing.assert_allclose(out['integral'],[4*np.pi,8*np.pi],rtol=2e-12,atol=2e-12)
    assert calls==[14]
    assert '3_7' in out['method']
