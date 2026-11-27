import importlib
import numpy as np
import pytest
from arseny_reimpl.rotational import angular_momentum_operators, rotational_block


def api():
    assert importlib.util.find_spec('bass_he.rotation') is not None,'gauge-regularized rotation missing'
    return importlib.import_module('bass_he.rotation')


@pytest.mark.parametrize('rho',[0.,.001,.2,.58,.7])
def test_rotation_probability_bounds_and_unitarity(rho):
    r=api().rotation_batch(2,1,[.5],[rho],steps=32)
    U=r['U_z'][0]; P=r['P_abs'][0]
    np.testing.assert_allclose(U.conj().T@U,np.eye(3),atol=5e-13)
    np.testing.assert_allclose(P.sum(0),1,atol=5e-13)
    assert P.min()>=0
    if rho==0 or rho>=.5833333333333:
        np.testing.assert_allclose(P,np.eye(2),atol=5e-13)


def test_gauge_hamiltonian_identity():
    mod=api(); _,lx,lz=angular_momentum_operators(2); ly=mod.angular_operators(2)[1]
    x=-.7; rho=.2; theta=np.arctan2(rho,x); G=np.diag(np.exp(-1j*theta*np.diag(lz)))
    transformed=G.conj().T@((x*x+rho*rho)*(lx@lx))@G
    np.testing.assert_allclose(transformed,(x*lx-rho*ly)@(x*lx-rho*ly),atol=2e-15)


def test_new_rotator_matches_old_well_resolved_but_not_by_using_its_ode():
    r=api().rotation_batch(2,1,[.5],[.2],steps=32)['P_abs'][0]
    legacy=rotational_block(2,1,.5,.2,steps=2048).probability_abs_mx
    np.testing.assert_allclose(r,legacy,atol=1e-7,rtol=0)


def test_fourth_order_and_batch_vs_scalar():
    mod=api(); ps=[mod.rotation_batch(3,2,[.5],[.5],steps=n)['P_abs'][0] for n in [8,16,32]]
    e1=np.max(abs(ps[0]-ps[1]));e2=np.max(abs(ps[1]-ps[2]))
    assert 3.7 < np.log2(e1/e2)<4.3
    batch=mod.rotation_batch(2,1,[.5,5],[.1,.3],steps=32)
    for i in range(2):
        scalar=mod.rotation_batch(2,1,[[.5,5][i]],[[.1,.3][i]],steps=32)
        np.testing.assert_allclose(batch['P_abs'][i],scalar['P_abs'][0],atol=5e-14)


@pytest.mark.parametrize('E,rho',[(0,.1),(-1,.1),(np.nan,.1),(.5,np.nan),(.5,-1)])
def test_invalid_inputs(E,rho):
    with pytest.raises(ValueError): api().rotation_batch(2,1,[E],[rho])
