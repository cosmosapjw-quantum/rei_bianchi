from pathlib import Path
import numpy as np
from wu088_hh.phys63_scaled_riccati import solve_response
SRC=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_physical_scaled_response_not_lost_to_zero():
    out=solve_response(SRC)
    ref=2.7660422460123427e-24+4.500676730155306e-25j
    assert abs(out['delta'][1,0]-ref)/abs(ref)<2e-7

import pytest
from wu088_hh.phys63_scaled_riccati import AngularScreen, central_impedance, born_from_central_path, direct_fundamental_control

@pytest.fixture(scope='module')
def full28():
    return solve_response(SRC,ells=tuple(range(29)))

def test_full_block_keeps_cross_partition_and_reciprocity(full28):
    D=full28['delta']
    assert D.shape==(29,29)
    assert abs(D[21,20])>2e-24
    assert np.max(np.abs(D-D.T))<1e-36
    assert full28['status']=='FINITE_ANGULAR_RADIAL_NONCERTIFYING'
    assert full28['physical_nonlinear_remainder_resolved'] is False

def test_original_boundary_matches_independent_coulomb(full28):
    z=full28['central_z']
    for ell in (0,20,21,28):
        assert abs(z[ell]-central_impedance(ell,27.0))<2e-10

def test_separate_born_quadrature_consistency(full28):
    D=born_from_central_path(full28)
    assert np.linalg.norm(D-full28['delta'])/np.linalg.norm(D)<2e-9
    # These agree at physical strength because nonlinear corrections are far
    # below double relative precision; this is NOT a resolved Born remainder.

@pytest.mark.parametrize('m',[0,1,2])
def test_signed_m_and_direct_source_psd(m):
    A=AngularScreen((20,21,22),m,128).scaled(27)
    B=AngularScreen((20,21,22),-m,128).scaled(27)
    assert np.array_equal(A,B)
    assert np.linalg.eigvalsh(A).min()>0
    assert np.linalg.norm(A,2)<1

def test_zero_screen_exact_delta():
    r=solve_response(SRC,ells=(0,1),strength=0)
    assert np.array_equal(r['delta'],np.zeros((2,2)))

def test_amplified_nonlinear_path_against_second_order_fundamental():
    r=solve_response(SRC,ells=(0,1),outer=33,strength=1e20)
    d=direct_fundamental_control(SRC)
    Z=np.diag(r['central_z'])+r['delta']
    assert np.max(np.abs(Z-d['Z']))<2e-10
    assert d['flux_error']<2e-10
    first=solve_response(SRC,ells=(0,1),outer=33,strength=1e20,nonlinear=False)
    assert np.linalg.norm(r['delta']-first['delta'])/np.linalg.norm(r['delta'])>1e-5

def test_numeric_radial_and_angular_refinement(full28):
    refined=solve_response(SRC,ells=tuple(range(29)),outer=43,nodes=192,rtol=2e-12)
    assert abs(refined['delta'][21,20]-full28['delta'][21,20])/abs(refined['delta'][21,20])<3e-8

@pytest.mark.parametrize('kwargs',[{'ells':(1,1)},{'ells':(0,1),'m':2},{'outer':27},{'rtol':1e-16},{'strength':-1}])
def test_invalid_inputs_rejected(kwargs):
    with pytest.raises(ValueError): solve_response(SRC,**kwargs)

def test_source_corruption_rejected(tmp_path):
    p=tmp_path/'fake.npz';p.write_bytes(b'not-original')
    with pytest.raises(ValueError,match='SHA256'): solve_response(p)
