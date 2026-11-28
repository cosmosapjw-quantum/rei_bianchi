import importlib
import numpy as np
import pytest
from arseny_reimpl.term_real import solve_real_term
from arseny_reimpl.term_complex import _branch_system, complex_term_residuals


def api():
    assert importlib.util.find_spec('bass_he.spectral') is not None, 'new spectral certification missing'
    return importlib.import_module('bass_he.spectral')


def test_duplicate_ground_state_is_not_a_branch():
    mod=api(); p=solve_real_term(1,0,0,1.,depth=96,tol=1e-12)
    z=np.array([p.p,p.separation_lambda,p.p,p.separation_lambda,1],complex)
    old=_branch_system(z,(1,0,0),(2,1,0),Z1=1.,Z2=2.,depth=96)
    assert max(abs(old))<1e-12  # demonstrated weakness in legacy criterion
    cert=mod.spectral_certificate((1,0,0),1.,p.p,p.separation_lambda,depth=96)
    assert not cert['singular']
    assert cert['sigma_min_over_max']>0.1


@pytest.mark.parametrize('state,R,p,lam', [((1,0,0),1.2+.6j,.8+.2j,-.3+.1j),((3,1,0),.7+.9j,.4+.2j,1.6+.5j),((3,2,1),3.+2j,1.+.7j,4.+2j)])
def test_analytic_jacobian_against_real_and_imaginary_differences(state,R,p,lam):
    mod=api(); F,J=mod.spectral_system(state,R,p,lam,depth=64)
    np.testing.assert_allclose(F,complex_term_residuals(state,R,p,lam,depth=64),rtol=2e-13,atol=2e-13)
    z=np.array([p,lam,R],complex)
    for direction in [1,1j]:
        for k in range(3):
            h=2e-6; e=np.zeros(3,complex); e[k]=direction*h
            zp=z+e; zm=z-e
            fp=mod.spectral_system(state,zp[2],zp[0],zp[1],depth=64)[0]
            fm=mod.spectral_system(state,zm[2],zm[0],zm[1],depth=64)[0]
            np.testing.assert_allclose(J[:,k],(fp-fm)/(2*h*direction),rtol=2e-7,atol=2e-7)


def test_branch_rank_and_monodromy_not_only_reference_closeness():
    mod=api(); ep=mod.find_exceptional_point((1,0,0),(2,1,0),1.212587527786+1.363819821336j,depth=96)
    assert abs(ep['R']-(1.212587527786+1.363819821336j))<6e-5
    assert ep['certificate']['singular']
    assert ep['certificate']['residual']<1e-8
    mon=mod.monodromy(ep,radius=.01,steps=96)
    assert mon['one_loop_swap_relative_error']<2e-6
    assert mon['two_loop_return_relative_error']<2e-6
    assert mon['minimum_distinct_sheet_gap']>1e-5
