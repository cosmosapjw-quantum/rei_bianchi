from pathlib import Path
import sys,math
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from survival_bounds import survival_envelope

def test_dirac_has_no_compression_uncertainty():
    b=survival_envelope([2.],[3.],.5)
    assert b.lower==pytest.approx(3/math.e,rel=2e-15)
    assert b.upper==pytest.approx(b.lower,rel=2e-15)

def test_two_endpoints_chord_is_sharp():
    b=survival_envelope([0.,2.],[.5,.5],1.)
    assert b.lower==pytest.approx(math.exp(-1.),rel=2e-15)
    assert b.upper==pytest.approx((1+math.exp(-2.))/2,rel=2e-15)

from survival_bounds import moment_bounds,distance_interval,difference_interval

@pytest.mark.parametrize('seed',range(6))
def test_nested_bounds_contain_direct_positive_measure(seed):
    rng=np.random.default_rng(seed);r=rng.uniform(0,10,1000);w=rng.uniform(0,1,1000);w/=w.sum()
    exact=float(w@np.exp(-r));last=None
    for depth in (0,1,2,3,4,6,8,10):
        b=survival_envelope(r,w,1.,depth)
        assert b.lower<=exact<=b.upper
        if last:
            assert b.lower>=last.lower-2e-15
            assert b.upper<=last.upper+2e-15
        last=b
    assert last.width<1e-6

@pytest.mark.parametrize('age',[0.,1e-15,1.,1e3])
def test_zero_mass_and_zero_opacity(age):
    assert survival_envelope([0.,1.],[0.,0.],age).width==0
    b=survival_envelope([0.,0.],[.3,.7],age)
    assert b.lower==b.upper==1.

@pytest.mark.parametrize('bad',[-1.,float('nan'),float('inf')])
def test_reject_invalid_rates_or_weights(bad):
    with pytest.raises(ValueError):survival_envelope([bad],[1.],1.)
    with pytest.raises(ValueError):survival_envelope([1.],[bad],1.)

@pytest.mark.parametrize('depth',[-1,17,True,1.5])
def test_reject_invalid_depth(depth):
    with pytest.raises(ValueError):survival_envelope([1.],[1.],1.,depth)


def test_mean_matching_does_not_determine_survival():
    r=np.array([0.,2.]);w=np.array([.5,.5])
    assert w@r==1.
    assert w@np.exp(-r)>math.exp(-1.)+.1


def test_mass_unit_scaling_and_diagnostic_distance():
    b=survival_envelope([0.,1.,3.],[.2,.3,.5],2.,2)
    c=survival_envelope([0.,1.,3.],[2e-6,3e-6,5e-6],2.,2)
    assert c.lower==pytest.approx(b.lower*1e-5,rel=2e-14)
    assert c.upper==pytest.approx(b.upper*1e-5,rel=2e-14)
    low,high=distance_interval(0.,b)
    assert low==b.lower and high==b.upper


def test_conditional_triangle_bounds_do_not_invent_error_estimates():
    assert difference_interval(1.,2.,.1,.2)==pytest.approx((.7,1.3))
    assert difference_interval(1.,1.01,.1,.2)[0]==0
    with pytest.raises(ValueError):difference_interval(1.,2.,-1.,1.)


def test_subnormal_small_tau_and_large_tau_are_finite():
    for t in (1e-300,1e3):
        b=survival_envelope([0.,1.,2.],[1.,1.,1.],t,3)
        assert all(math.isfinite(x) for x in (b.lower,b.upper))
        assert 0<=b.lower<=b.upper<=3.


def test_explicit_moment_domain():
    with pytest.raises(ValueError):moment_bounds(1.,3.,0.,2.,1.)
    with pytest.raises(ValueError):moment_bounds(1.,1.,0.,2.,-1.)
    with pytest.raises(ValueError):survival_envelope([],[],1.)
    with pytest.raises(ValueError):survival_envelope([1.],[1.,2.],1.)
