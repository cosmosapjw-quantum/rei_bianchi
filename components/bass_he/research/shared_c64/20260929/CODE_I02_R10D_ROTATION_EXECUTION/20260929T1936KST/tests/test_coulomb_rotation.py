import numpy as np
import pytest
from bass_he.rotation import rotation_batch
from arseny_reimpl.rotational import s_sigma_boundary
from coulomb_rotation import author_cutoff,coulomb_rotation_batch


def test_author_cutoff_exact_values():
    assert author_cutoff(1)==0.75
    assert author_cutoff(2)==25/12


def test_coulomb_length_uses_atomic_mass_conversion():
    p=coulomb_rotation_batch(2,1,[.5,5.],[.2,.2],steps=64,R_cut=.75)
    np.testing.assert_allclose(p['coulomb_a'],[.067675,.0067675],rtol=2e-14)


def test_a_zero_limit_matches_straight_line_at_same_cutoff():
    for N,l,rho,cut in [(2,1,.2,.75),(3,2,.5,25/12)]:
        straight=rotation_batch(N,l,[.5],[rho],steps=256,R_cut=cut)['P_abs'][0]
        coulomb=coulomb_rotation_batch(N,l,[.5],[rho],steps=256,R_cut=cut,a_override=0.)['P_abs'][0]
        np.testing.assert_allclose(coulomb,straight,atol=1e-7,rtol=0)
        tiny=coulomb_rotation_batch(N,l,[.5],[rho],steps=256,R_cut=cut,a_override=1e-10)['P_abs'][0]
        np.testing.assert_allclose(tiny,straight,atol=1e-7,rtol=0)


def test_explicit_cpc_cutoff_recovers_current_straight_implementation():
    for N,l,rho in [(2,1,.2),(3,2,.5)]:
        baseline=rotation_batch(N,l,[.5],[rho],steps=32)['P_abs']
        reset=rotation_batch(N,l,[.5],[rho],steps=32,R_cut=s_sigma_boundary(l))['P_abs']
        np.testing.assert_array_equal(reset,baseline)


def test_closest_approach_gate_returns_identity():
    result=coulomb_rotation_batch(2,1,[.5],[.74],steps=64,R_cut=.75)
    assert result['entered'][0] == False
    np.testing.assert_allclose(result['P_abs'][0],np.eye(2),atol=1e-14)


def test_unitary_and_collapsed_stochastic():
    result=coulomb_rotation_batch(3,2,[.5],[.5],steps=128,R_cut=25/12)
    U=result['U_z'][0];P=result['P_abs'][0]
    assert np.max(abs(U.conj().T@U-np.eye(5)))<5e-13
    assert np.max(abs(P.sum(0)-1))<5e-13
    assert P.min()>=0


def test_step_doubling_reduces_probability_difference():
    p=[coulomb_rotation_batch(3,2,[.5],[.5],steps=n,R_cut=25/12)['P_abs'][0]
       for n in (64,128,256)]
    e1=np.max(abs(p[0]-p[1]));e2=np.max(abs(p[1]-p[2]))
    assert e2<e1 and e2<1e-7


def test_zero_rho_requires_separate_limit():
    with pytest.raises(ValueError,match='rho'):
        coulomb_rotation_batch(2,1,[.5],[0.],R_cut=.75)
