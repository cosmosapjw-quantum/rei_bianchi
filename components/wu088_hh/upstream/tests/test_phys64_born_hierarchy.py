from pathlib import Path
import numpy as np
from wu088_hh.phys64_born_hierarchy import solve_orders
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_second_order_is_computed_in_its_own_scale():
    result=solve_orders(SRC,ells=(20,21),orders=3)
    y=result['coefficients']
    assert np.linalg.norm(y[1])>1e-8, 'second-order response must not be lost as total minus Born'

import pytest
from wu088_hh.phys64_born_hierarchy import ordered_sources, coefficient_quadrature, series_delta, summary
from wu088_hh.phys63_scaled_riccati import solve_response, direct_fundamental_control

@pytest.fixture(scope='module')
def physical():
    return solve_orders(SRC,ells=tuple(range(29)),orders=3)

def test_ordered_matrix_source_cannot_commute():
    a=np.array([[1,2],[2,3]],complex);b=np.array([[2,1],[1,4]],complex)
    c=np.array([a,b,a-b]);w=np.eye(2)
    s=ordered_sources(c,w)
    assert np.array_equal(s[1],a@a)
    assert np.array_equal(s[2],a@b+b@a)
    assert not np.array_equal(s[2],2*a@b)

@pytest.mark.parametrize('order',[1,2,3])
def test_coefficient_integral_independent_discretization(physical,order):
    q=coefficient_quadrature(physical,order,80)
    assert np.linalg.norm(q-physical['coefficients'][order-1])/np.linalg.norm(q)<2e-8

def test_first_order_matches_inherited_mpmath_born(physical):
    oracle=2.7660422460142386e-24+4.5006767301594555e-25j
    assert abs(physical['contributions'][0,21,20]-oracle)/abs(oracle)<2e-9

def test_higher_contributions_not_subtracted_or_called_total_error(physical):
    a=physical['contributions']
    assert 1e-49<abs(a[1,21,20])<1e-46
    assert 1e-73<abs(a[2,21,20])<1e-69
    assert physical['full_nonlinear_remainder_certified'] is False
    assert np.array_equal(a[0]+a[1],a[0]) # addition hides it, stored coefficient does not

@pytest.mark.parametrize('order',[0,1,2])
def test_complex_transpose_reciprocity(physical,order):
    c=physical['coefficients'][order]
    assert np.linalg.norm(c-c.T)/np.linalg.norm(c)<1e-12

def test_signed_m_parity_of_each_coefficient():
    plus=solve_orders(SRC,ells=(20,21),m=1,orders=3)
    minus=solve_orders(SRC,ells=(20,21),m=-1,orders=3)
    assert np.array_equal(plus['coefficients'],minus['coefficients'])

def test_amplified_nonphysical_fundamental_validation():
    result=solve_orders(SRC,ells=(0,1),outer=33.,orders=4,rtol=1e-12)
    independent=direct_fundamental_control(SRC,ells=(0,1),outer=33.,strength=1e20,rtol=1e-12)
    errs=[np.linalg.norm(np.diag(result['central_z'])+series_delta(result,1e20,j)-independent['Z']) for j in (1,2,3)]
    assert errs[1]<errs[0]*.001
    assert errs[2]<errs[1]*.01
    assert independent['flux_error']<1e-12

def test_zero_strength_reconstructs_zero(physical):
    assert not np.any(series_delta(physical,0))

def test_source_tamper_rejected(tmp_path):
    p=tmp_path/'wrong';p.write_bytes(b'wrong input')
    with pytest.raises(ValueError,match='SHA256'):solve_orders(p)

@pytest.mark.parametrize('kwargs',[{'orders':0},{'orders':6},{'outer':27},{'rtol':1e-16},{'max_step':float('nan')},{'ells':(21,21)},{'nodes':20}])
def test_invalid_contract_rejected(kwargs):
    with pytest.raises(ValueError):solve_orders(SRC,**kwargs)

def test_summary_preserves_all_scope_flags(physical):
    import json
    d=summary(physical)
    json.dumps(d,allow_nan=False)
    assert len(d['terms'])==3
    assert d['spatial_and_roundoff_error_certified'] is False
