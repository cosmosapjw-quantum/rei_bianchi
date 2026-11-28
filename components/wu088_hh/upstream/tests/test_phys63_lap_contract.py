from fractions import Fraction as F
from pathlib import Path
import pytest
from wu088_hh.phys63_lap_contract import applicability, conditional_neumann, exp_lower, source_guard, weighted_screen_bound_s1
SRC=Path(__file__).resolve().parents[1]/'research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'

def test_source_specific_literature_contract_is_not_numerical_certificate():
    d=applicability(SRC)
    assert d['energy_Hartree']=='49/200'
    assert d['radial_spectral_parameter']=='49/100'
    assert d['numerical_LAP_norm'] is None
    assert d['quantitative_Neumann_smallness']=='NOT_CERTIFIED'
    assert d['threshold_set']==[0] and d['HH_R10']=='OFF'

def test_exact_screen_weight_and_long_range_conditions():
    assert weighted_screen_bound_s1()==F(219,10**22)
    assert F(applicability(SRC)['long_range_weighted_gradient_bound'])==F(730,729)

def test_exp_enclosure_independent_high_precision():
    import mpmath as mp
    with mp.workdps(100):
        v=exp_lower(F(263,5))
        assert mp.mpf(v.numerator)/v.denominator < mp.exp(mp.mpf(263)/5)

def test_radial_unitary_and_weight_monotonicity_symbolically():
    import sympy as sp
    r,l=sp.symbols('r l', positive=True)
    u=sp.Function('u')(r)
    spatial=r*(-(sp.diff(u/r,r,2)+2/r*sp.diff(u/r,r)-l*(l+1)*u/r**3)/2-u/r**2)
    radial=-sp.diff(u,r,2)/2+l*(l+1)*u/(2*r**2)-u/r
    assert sp.simplify(spatial-radial)==0
    assert sp.simplify(sp.diff((1+r*r)*sp.exp(-2*(r-27)),r)/sp.exp(-2*(r-27))+2*((r-sp.Rational(1,2))**2+sp.Rational(3,4)))==0

def test_unknown_resolvent_bound_cannot_pass_neumann_gate():
    assert conditional_neumann(SRC,None)['q'] is None
    assert conditional_neumann(SRC,F(1))['status']=='CONDITIONAL_NEUMANN_LT_ONE'
    assert conditional_neumann(SRC,F(10**30))['status']=='NEUMANN_SMALLNESS_NOT_ESTABLISHED'

def test_tampered_original_not_accepted(tmp_path):
    p=tmp_path/'bad.npz';p.write_bytes(b'bad')
    with pytest.raises(ValueError,match='SHA256'): applicability(p)

def test_invalid_exact_contract_inputs():
    with pytest.raises(ValueError): exp_lower(F(-1))
    with pytest.raises(ValueError): conditional_neumann(SRC,1.0)

def test_resolvent_inverse_identity_without_neumann_smallness():
    # Manufactured finite linear algebra. Not a physical resolvent estimate.
    import numpy as np
    A=np.array([[1,0],[0,2]],dtype=complex)-.3j*np.eye(2)
    V=np.array([[4,.2],[.2,3]])
    GC=np.linalg.inv(A); GS=np.linalg.inv(A-V)
    assert np.linalg.norm(GC@V,2)>1
    inverse=np.eye(2)+GS@V
    assert np.linalg.norm((np.eye(2)-GC@V)@inverse-np.eye(2))<2e-14
