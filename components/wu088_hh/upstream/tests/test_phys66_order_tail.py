from pathlib import Path
from fractions import Fraction as F
from wu088_hh.phys66_order_tail import cutoff_bounds
SOURCE=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
def test_actual_source_orderwise_cutoff_bounds_are_provided():
    r=cutoff_bounds(SOURCE,max_ell=64,outer=65,orders=3)
    assert len(r['order_cutoff_bounds'])==3
    assert r['order_cutoff_bounds'][1]<F(1,10**65)
    assert r['order_cutoff_bounds'][2]<F(1,10**78)
    assert r['total_error_certified'] is False
import pytest
import mpmath as mp
from wu088_hh.phys66_order_tail import (sensitivity_numbers,exponential_decay_upper,
 A,BILINEAR,CHI,json_safe,decode_fraction,minimum_cutoff)

def test_noncommutative_majorant_factors():
    assert sensitivity_numbers(6)==(1,4,20,104,548,2904)

def test_order2_order3_have_closed_forms():
    x=cutoff_bounds(SOURCE,outer=55)
    t=exponential_decay_upper(F(56))
    assert x['order_cutoff_bounds']==[A*t,A*CHI*t,F(5,4)*A*CHI**2*t]

@pytest.mark.parametrize('t',[27,39,43,55,65,80,100])
def test_decay_upper_uses_outward_exact_fraction(t):
    upper=exponential_decay_upper(F(2*(t-27)))
    with mp.workdps(600):
        v=mp.mpf(upper.numerator)/upper.denominator
        assert v>=mp.exp(-2*(t-27))
    assert decode_fraction(json_safe(upper))==upper

def test_large_fraction_does_not_change_process_digit_limit():
    import sys,json
    before=sys.get_int_max_str_digits()
    f=F(10**10000+7,10**9999+9)
    assert decode_fraction(json.loads(json.dumps(json_safe(f))))==f
    assert sys.get_int_max_str_digits()==before

@pytest.mark.parametrize('l',[-1,65,True,1.5])
def test_unproved_angular_range_refused(l):
    with pytest.raises(ValueError):cutoff_bounds(SOURCE,max_ell=l)

@pytest.mark.parametrize('t',[26,101,39.0,True])
def test_invalid_or_inexact_cutoff_refused(t):
    with pytest.raises(ValueError):cutoff_bounds(SOURCE,outer=t)

def test_source_tamper(tmp_path):
    f=tmp_path/'fake.npz';f.write_bytes(b'not the original')
    with pytest.raises(ValueError,match='immutable'):cutoff_bounds(f)

def test_minimum_cutoff_is_actual_exact_budget_solution():
    t=minimum_cutoff(SOURCE,2,F(1,10**52))
    assert cutoff_bounds(SOURCE,outer=t)['order_cutoff_bounds'][1]<F(1,10**52)
    assert cutoff_bounds(SOURCE,outer=t-1)['order_cutoff_bounds'][1]>=F(1,10**52)

def test_no_fake_total_numerical_error_bound():
    x=cutoff_bounds(SOURCE,outer=65)
    assert x['exact_series_analytic_subtotal']>0
    assert x['numerical_error_bound'] is None
    assert x['unused_angular_modes_bound'] is None
    assert x['total_error_bound'] is None and not x['total_error_certified']
