"""PHYS60 C5-C8 source-locked finite radial real-energy complex Born tests."""
from pathlib import Path
import numpy as np
import mpmath as mp
import pytest
from wu088_hh.phys60_positive_born import *
from wu088_hh.phys60_finite_jost import angular_real_block, hplus, hplus_derivative
SRC=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
def val(q):return complex(float(q['real_Born']),float(q['imag_Born']))
def test_original_source():assert source_sha_guard(SRC)==FROZEN_SHA
@pytest.mark.parametrize('m',[0,1,2])
def test_real_original_angular_at_boundary(m):
    v=angular_real_block(27,(20,21),m,192)
    assert 0<v[0,1]<1e-22
    assert abs(v[1,0]-v[0,1])<1e-36
@pytest.mark.parametrize('m',[0,1,2])
def test_original_plusminus_m_parity(m):
    q=first_born_raw(21,20,m,18,128,39,48)
    rev=first_born_raw(21,20,-m,18,128,39,48)
    assert abs(val(q)-val(rev))<1e-37
@pytest.mark.parametrize('m',[0,1,2])
def test_reciprocal_complex_symmetric_born(m):
    q=first_born_raw(21,20,m,18,128,39,48)
    rev=first_born_raw(20,21,m,18,128,39,48)
    assert abs(val(q)-val(rev))<1e-37
@pytest.mark.parametrize('n,a',[(10,96),(18,128),(26,192),(34,256)])
def test_complex_born_physical_nonzero(n,a):
    q=first_born_raw(21,20,0,n,a,39,55)
    v=val(q)
    assert v.real>2.7e-24 and v.imag>4.4e-25
    assert abs(v)<3.0e-24

def test_independent_incoming_is_complex_conjugate():
    out=first_born_raw(21,20,0,18,128,39,55)
    incoming=first_born_raw(21,20,0,18,128,39,55,incoming=True)
    assert abs(val(incoming)-val(out).conjugate())<1e-37
    assert abs(val(out)-val(incoming))>8e-25

def test_radial_quadrature_refinement_observed():
    a=val(first_born_raw(21,20,0,26,192,39,55))
    b=val(first_born_raw(21,20,0,34,256,39,55))
    assert abs(a-b)/abs(b)<1e-10 # numerical, not interval enclosure

def test_positive_E_differs_from_negative_offshell():
    v=val(first_born_raw(21,20,0,26,192,39,55))
    assert abs(v.imag)>0 # negative-energy Whittaker first Born would be real
@pytest.mark.parametrize('bad',[(21,20,22,18,128,39,55),(21,20,0,2,128,39,55),(21,20,0,18,32,39,55)])
def test_input_rejections(bad):
    with pytest.raises(ValueError):first_born_raw(*bad)

@pytest.mark.parametrize('ell',[0,20,21,28])
def test_independent_coulomb_cf_real_and_phase(ell):
    with mp.workdps(65):
        ref=hplus_derivative(ell,27.,65)/hplus(ell,27.,65)
    got=outgoing_dtn_cf(ell,27.,768)
    assert abs(got.real-float(mp.re(ref)))<4e-12
    if ell<=21:assert abs(got.imag-float(mp.im(ref)))<3e-12

def test_exact_source_screen_tail_not_born_tail():
    from fractions import Fraction as F
    tail=exact_exterior_screen_tail_L1(39,160)
    assert 0<tail<F(1,10**33)
    assert exact_exterior_screen_tail_L1(43)<tail

@pytest.mark.parametrize('bad',[-1,4097])
def test_cf_depth_invalid(bad):
    with pytest.raises(ValueError):outgoing_dtn_cf(21,27.,bad)
