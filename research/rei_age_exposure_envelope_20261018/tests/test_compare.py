import pytest
import compare_results as c

def test_no_prepost_substitution_at_a_jump():
    left=[{'x':1.,'side':'pre','physical':{'N':2.}}]
    right=[{'x':1.,'side':'post','physical':{'N':5.}}]
    matched,missing=c.match_observations(left,right)
    assert matched==[] and len(missing)==1

def test_zero_reference_not_epsilon_regularized():
    assert c.relative(0.,0.)==0.
    assert c.relative(1e-30,0.) is None

def test_wasserstein_is_independent_of_histogram_edges():
    assert c.w1([0.],[1.],[2.],[1.])==2.
    assert c.w1([0.,2.],[.5,.5],[1.],[1.])==1.

def test_wasserstein_same_measure_split_atoms():
    assert c.w1([0.,1.],[1.,1.],[0.,0.,1.],[.5,.5,1.])==0.

def test_mismatched_clock_not_silently_compared():
    with pytest.raises(ValueError,match='PHYSICAL_CLOCK'):
        c.endpoint_metrics({'proper_time_s':1.},{'proper_time_s':2.})
