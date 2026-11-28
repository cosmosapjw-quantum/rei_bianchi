"""Tests exercise research probes only, never the live cloud service."""
import importlib.util
import math
import numpy as np
import pytest

def api():
    assert importlib.util.find_spec('research_kernels') is not None, 'shared-contour/resource probe not implemented'
    import research_kernels as r
    return r

def test_common_contour_constant_gap_has_analytic_primitive():
    r=api();n=512;s=np.linspace(0,1,n+1);Rc=3+2j
    R=3+2j*(2*s-s*s);dR=4j*(1-s)
    for rho in [0,.75,1.5,2.25]:
        got=r.action_from_trace(R,np.ones(n+1),dR,rho)
        expected=np.sqrt(Rc*Rc-rho*rho)-math.sqrt(9-rho*rho)
        assert abs(got-expected)<1e-9

def test_support_violation_not_silently_reweighted():
    r=api();s=np.linspace(0,1,17);R=1+1j*(2*s-s*s)
    for rho in [-1,1,1.01,float('nan')]:
        with pytest.raises(ValueError):r.action_from_trace(R,np.ones(17),2j*(1-s),rho)

def test_discrete_moment_bound_covers_actual_difference():
    r=api();s=np.linspace(0,1,65);R=2+3j*(2*s-s*s);dR=6j*(1-s)
    g=np.sqrt(R-(2+3j))*np.sqrt(R-(2-3j))
    for m in [4,12,32]:
        exact=r.action_from_trace(R,g,dR,1.5)
        value,bound=r.moment_action(R,g,dR,1.5,m)
        assert abs(value-exact)<=bound+1e-13

def test_equal_single_thread_jobs_fit_48_slots():
    r=api();got=r.fair_slots([32,32,32],[1,1,1],[1,1,1],48,1000)
    assert got==[16,16,16]

def test_dominant_memory_job_cannot_overcommit():
    r=api();a=r.fair_slots([32,32,32],[1,1,1],[1,12,1],48,96)
    assert sum(a)<=48 and sum(x*m for x,m in zip(a,[1,12,1]))<=96
    assert a[1]<a[0]

def test_idle_capacity_is_borrowed_without_starvation():
    r=api();a=r.fair_slots([8,32,32],[1,1,1],[1,1,1],48,1000)
    assert a==[8,20,20]

def test_active_memory_accounted_once_and_pending_reserved():
    r=api()
    assert r.can_admit_memory(70,10,5,100,5)
    assert not r.can_admit_memory(70,10,20,100,5)

def test_two_state_operator_difference_has_l1_norm_twice_dp():
    r=api();rng=np.random.default_rng(20260928)
    for sink in [False,True]:
        for _ in range(50):
            p,q=rng.random(2)
            assert np.linalg.norm(r.event_matrix(p,sink)-r.event_matrix(q,sink),1)==pytest.approx(2*abs(p-q))
