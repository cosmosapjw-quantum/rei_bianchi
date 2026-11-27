from pathlib import Path
import numpy as np
from wu088_hh.phys66_endpoint import solve_endpoint
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_extended_endpoint_preserves_nonzero_original_screen():
    x=solve_endpoint(SOURCE,ells=(20,21),outer=65.,join=39.,nodes=96)
    assert np.linalg.norm(x['coefficients'][0])>0.01

import pytest
from wu088_hh.phys64_born_hierarchy import solve_orders,coefficient_quadrature

@pytest.fixture(scope='module')
def twochannel():return solve_endpoint(SOURCE,ells=(20,21),outer=45.,join=35.,nodes=96)

def test_exact_join_carries_higher_coefficients(twochannel):
    n=2;mid=twochannel['join_state']
    assert np.linalg.norm(mid[2*n:].reshape(3,n,n)[1])>0
    assert np.array_equal(twochannel['solution'].sol(35.),mid)

def test_join_matches_old_single_interval(twochannel):
    old=solve_orders(SOURCE,ells=(20,21),outer=45.,nodes=96)
    for a,b in zip(old['coefficients'],twochannel['coefficients']):
        assert np.linalg.norm(a-b)<2e-8*np.linalg.norm(a)

def test_order_source_quadrature_control(twochannel):
    for n in (1,2,3):
        q=coefficient_quadrature(twochannel,n,96)
        assert np.linalg.norm(q-twochannel['coefficients'][n-1])<2e-7*np.linalg.norm(q)

def test_signed_m_preservation():
    a=solve_endpoint(SOURCE,ells=(20,21),m=1,outer=45.,nodes=64)
    b=solve_endpoint(SOURCE,ells=(20,21),m=-1,outer=45.,nodes=64)
    assert np.array_equal(a['coefficients'],b['coefficients'])

def test_analytic_and_numerical_statuses_distinct(twochannel):
    assert twochannel['analytic_radial_components']['total_numerical_error_certified'] is False
    assert twochannel['computed_coefficient_integration_error_bound'] is None
    assert twochannel['full_nonlinear_remainder_certified'] is False

@pytest.mark.parametrize('outer,join',[(81.,39.),(39.,39.),(65.,26.),(float('nan'),39.)])
def test_endpoint_outside_contract_rejected(outer,join):
    with pytest.raises(ValueError):solve_endpoint(SOURCE,outer=outer,join=join)

def test_bad_angular_inputs_and_source_fail(tmp_path):
    with pytest.raises(ValueError):solve_endpoint(SOURCE,ells=(20,65))
    p=tmp_path/'bad.npz';p.write_bytes(b'bad')
    with pytest.raises(ValueError):solve_endpoint(p)

def test_profile_outside_domain_is_not_extrapolated(twochannel):
    with pytest.raises(ValueError):twochannel['solution'].sol(90.)
