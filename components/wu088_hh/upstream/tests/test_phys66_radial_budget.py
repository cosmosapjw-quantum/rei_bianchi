from fractions import Fraction as F
from wu088_hh.phys66_radial_budget import error_weights

def test_order_two_tail_is_not_silently_omitted():
    assert error_weights(3)==[F(1),F(1),F(5,4)]

from pathlib import Path
import hashlib,json,sys
import pytest
import mpmath as mp
from wu088_hh.phys66_radial_budget import (certificate,coefficient_bounds,plan_radius,
    to_jsonable,from_rational,UPSTREAM_BLOB,SOURCE_SHA)
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_source_guard_and_upstream_exact_code():
    d=certificate(SOURCE,64,'65',3)
    assert d['source_sha256']==SOURCE_SHA
    assert d['gamma']==32400
    assert d['chi']==F(19683,1250000000000000000)
    assert d['upstream_blob']==UPSTREAM_BLOB

def test_weights_match_independent_series():
    import sympy as s
    x=s.symbols('x')
    oracle=s.series(1/(2*s.sqrt(1-x)-1),x,0,5).removeO()
    assert error_weights(5)==[F(str(oracle.coeff(x,n))) for n in range(5)]

@pytest.mark.parametrize('T',[39,43,55,65,75])
def test_fraction_upper_encloses_transcendental(T):
    c=coefficient_bounds(64,T,3)
    with mp.workdps(500):
        def m(f):return mp.mpf(f.numerator)/f.denominator
        e=mp.exp(-2*(T-27))
        for n,row in enumerate(c['terms']):
            exact=m(c['a'])*m(c['chi'])**n*m(error_weights(3)[n])*e
            assert m(row['radial_cutoff_bound'])>=exact
            assert m(row['radial_cutoff_bound'])<exact*(1+mp.mpf('1e-12'))

def test_planner_minimal_radius_not_total_error():
    p=plan_radius(64,{1:'1e-30',2:'1e-54',3:'1e-78'})
    assert p['outer']==65
    assert coefficient_bounds(64,64)['terms'][2]['radial_cutoff_bound']>F('1e-78')
    assert p['certificate']['terms'][2]['radial_cutoff_bound']<F('1e-78')
    assert p['total_numerical_error_certified'] is False
    assert p['certificate']['continuum_born_remainder']>F('1e-61')
    assert p['certificate']['numerical_error_bound'] is None

def test_planner_fails_within_small_radius_budget():
    assert plan_radius(64,{3:'1e-78'},35,64)['status']=='NO_RADIUS_WITHIN_SEARCH'

def test_lossless_giant_fraction_serialization():
    before=sys.get_int_max_str_digits()
    q=F(2**24000+1,3**13000+7)
    encoded=to_jsonable({'q':q})
    restored=from_rational(json.loads(json.dumps(encoded))['q'])
    assert restored==q
    assert sys.get_int_max_str_digits()==before

@pytest.mark.parametrize('l',[-1,65,True,21.0])
def test_bad_angular_cutoff_rejected(l):
    with pytest.raises(ValueError):coefficient_bounds(l,'65')

@pytest.mark.parametrize('T',[F(26),F(101),65.0,True])
def test_bad_or_inexact_radius_rejected(T):
    with pytest.raises(ValueError):coefficient_bounds(64,T)

@pytest.mark.parametrize('n',[0,6,True,2.0])
def test_bad_order_rejected(n):
    with pytest.raises(ValueError):error_weights(n)

def test_missing_numerical_bounds_cannot_be_promoted():
    d=certificate(SOURCE,28,55,3)
    assert d['numerical_error_bound'] is None
    assert d['excluded_angular_error_bound'] is None
    assert d['HH_R10']=='OFF'
    assert d['scope']=='EXACT_CONTINUUM_FINITE_L_RADIAL_COMPONENT_ONLY'

def test_source_tamper_fails(tmp_path):
    p=tmp_path/'wrong.npz';p.write_bytes(b'wrong')
    with pytest.raises(ValueError,match='source SHA'):certificate(p)

def test_zero_radial_span_is_conservative_for_each_coefficient():
    c=coefficient_bounds(64,27,5)
    assert all(r['radial_cutoff_bound']>=r['weighted_coefficient_bound'] for r in c['terms'])

def test_late_upstream_pr115_normalization_is_exactly_equivalent():
    assert tuple(x*4**i for i,x in enumerate(error_weights(5)))==(1,4,20,104,548)
