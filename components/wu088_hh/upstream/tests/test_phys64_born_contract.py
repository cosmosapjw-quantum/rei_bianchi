from fractions import Fraction as F
from wu088_hh.phys64_born_contract import majorant

def test_catalan_quadratic_majorant_keeps_coupling_strength():
    a=majorant(F(2),F(1),F(1,100),2)
    assert a['q']==F(4,25)
    assert a['tail_upper']==F(8,13125)

import pytest
from wu088_hh.phys64_born_contract import catalan, low_mode_certificate, EPSILON

@pytest.mark.parametrize('n,expected',[(0,1),(1,1),(2,2),(3,5),(4,14),(5,42)])
def test_catalan_exact_noncommuting_tree_count(n,expected):
    assert catalan(n)==expected

def test_original_low_channel_continuum_bound_is_not_high_channel_claim():
    d=low_mode_certificate(F(39),2)
    assert d['screen_upper']<EPSILON
    assert d['q']<F(4,10**19)
    assert d['tail_upper']<F(3,10**58)
    assert d['high_angular_or_P20_Q21_certificate'] is False
    assert d['validates_ode_roundoff_or_spatial_truncation'] is False

def test_divergent_sufficient_condition_rejected():
    with pytest.raises(ValueError,match='q<1'):
        majorant(F(2),F(1),F(1),2)

def test_float_pretending_exact_rejected():
    with pytest.raises(TypeError):majorant(2.,F(1),F(1,100),2)

def test_zero_potential_exact_zero_remainder():
    assert majorant(F(10),F(0),F(1),3)['tail_upper']==0

def test_conditional_scope_survives_small_numerical_q():
    assert 'CONDITIONAL' in majorant(F(12),F(1),EPSILON,3)['scope']
