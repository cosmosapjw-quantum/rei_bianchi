import math
import random
import pytest
from age_response_bound import response_bound
from compare_results import w1

def bound(xa,wa,xb,wb,G=1.,L=0.,jumps=()):
    r=response_bound(xa,wa,xb,wb,response_abs_max=G,smooth_lipschitz=L,jumps=jumps)
    assert isinstance(r,dict), 'missing conditional response enclosure'
    return r

def test_same_shape_different_mass_not_invisible():
    r=bound([1.],[1.],[1.],[10.])
    assert r['age_W1']==0 and r['absolute_bound']==9.

def test_lipschitz_linear_response_is_sharp():
    r=bound([0.],[2.],[3.],[2.],G=3.,L=1.)
    assert r['absolute_bound']==6.

def test_small_age_distance_can_cross_a_unit_jump():
    eps=1.e-9
    r=bound([1-eps],[1.],[1+eps],[1.],jumps=[(1.,1.)])
    assert r['age_W1']<3e-9 and r['absolute_bound']==1.

def test_threshold_equality_is_right_closed():
    r=bound([1.],[1.],[1.0001],[1.],jumps=[(1.,1.)])
    assert r['absolute_bound']==0.

def test_zero_mass_has_no_fake_normalized_age():
    r=bound([],[],[3.],[2.],G=4.)
    assert r['age_W1'] is None and r['absolute_bound']==8.

def test_uniform_rescaling_is_homogeneous():
    a=bound([0.,2.],[.2,.8],[1.],[1.],G=2,L=.3,jumps=[(.5,.4)])
    b=bound([0.,2.],[2.,8.],[1.],[10.],G=2,L=.3,jumps=[(.5,.4)])
    assert b['absolute_bound']==pytest.approx(10*a['absolute_bound'],rel=2e-15)

@pytest.mark.parametrize('kwargs',[{'G':-1},{'L':float('nan')},{'jumps':[(float('inf'),1.)]}])
def test_invalid_bound_data_rejected(kwargs):
    with pytest.raises(ValueError):bound([0.],[1.],[0.],[1.],**kwargs)

def test_independent_scipy_W1_and_actual_responses():
    from scipy.stats import wasserstein_distance
    rng=random.Random(20261018)
    for i in range(200):
        xa=[rng.random()*2 for _ in range(5)];xb=[rng.random()*2 for _ in range(7)]
        wa=[rng.random() for _ in xa];wb=[rng.random() for _ in xb]
        slope=.3;cut=.7;jump=.4
        f=lambda t: .2+slope*t+jump*(t>=cut)
        r=bound(xa,wa,xb,wb,G=1.2,L=slope,jumps=[(cut,jump)])
        truth=abs(math.fsum(w*f(t) for t,w in zip(xa,wa))-math.fsum(w*f(t) for t,w in zip(xb,wb)))
        assert truth<=r['absolute_bound']+3e-15
        assert r['age_W1']==pytest.approx(wasserstein_distance(xa,xb,wa,wb),abs=5e-15)
