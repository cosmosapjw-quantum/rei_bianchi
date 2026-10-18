import math
import pytest
from paired_response_bound import paired_bound

def env(k):
    return dict(response_abs_max=1.,smooth_lipschitz=k)

def test_identical_age_measure_but_distinct_opacity_has_nonzero_bound():
    delta=math.exp(-1)-math.exp(-2)
    result=paired_bound([1.],[2.],[1.],[2.],left_envelope=env(1.),
        right_envelope=env(2.),response_sup_difference=delta)
    assert result['absolute_bound']==pytest.approx(2*delta,rel=2e-15)

@pytest.mark.parametrize('delta',[-1.,float('nan'),float('inf')])
def test_invalid_response_difference_is_rejected(delta):
    with pytest.raises(ValueError):
        paired_bound([0.],[1.],[0.],[1.],left_envelope=env(0.),
            right_envelope=env(0.),response_sup_difference=delta)

def test_unequal_mass_constant_responses_is_sharp():
    a=dict(response_abs_max=1.,smooth_lipschitz=0.)
    b=dict(response_abs_max=.2,smooth_lipschitz=0.)
    result=paired_bound([0.],[10.],[0.],[1.],left_envelope=a,
        right_envelope=b,response_sup_difference=.8)
    assert result['absolute_bound']==pytest.approx(9.8)

def test_one_empty_measure_needs_no_normalized_age():
    result=paired_bound([],[],[1.],[2.],left_envelope=env(1.),
        right_envelope=env(1.),response_sup_difference=0.)
    assert result['absolute_bound']==2.

def test_same_response_reduces_to_common_bound():
    result=paired_bound([0.],[1.],[1.],[1.],left_envelope=env(1.),
        right_envelope=env(1.),response_sup_difference=0.)
    assert result['absolute_bound']==1.

def test_both_triangle_decompositions_bound_independent_discrete_responses():
    import random
    rng=random.Random(20261018)
    for _ in range(100):
        xa=[rng.random() for i in range(5)];xb=[rng.random() for i in range(7)]
        wa=[rng.random() for x in xa];wb=[rng.random() for x in xb]
        ga=lambda x:.1+.2*x
        gb=lambda x:.3+.1*x
        delta=.2
        result=paired_bound(xa,wa,xb,wb,
            left_envelope=dict(response_abs_max=.3,smooth_lipschitz=.2),
            right_envelope=dict(response_abs_max=.4,smooth_lipschitz=.1),
            response_sup_difference=delta)
        truth=abs(math.fsum(w*ga(x) for x,w in zip(xa,wa))-
                  math.fsum(w*gb(x) for x,w in zip(xb,wb)))
        assert all(truth<=v+2e-15 for v in result['candidates'])
        assert truth<=result['absolute_bound']+2e-15
