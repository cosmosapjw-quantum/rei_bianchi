"""Fresh tests for the opt-in real spectral anchor, independent of CF root seeds."""
import importlib.util
import math
import numpy as np
import pytest


def api():
    assert importlib.util.find_spec('bass_he.sturm_anchor') is not None, 'DR11E indexed anchor is missing'
    from bass_he import sturm_anchor
    return sturm_anchor


def test_stagnant_real_coordinate_and_requested_anchor():
    a=api()
    r=a.bound_state((4,2,0),2.07353989985252)
    assert abs(r['energy_hartree']-(-.31265420357357476))<2e-10
    assert r['indices']=={'radial':1,'angular':2}
    assert r['basis_converged']
    z=a.bound_state((4,2,0),1.4822661233645524)
    assert abs(z['energy_hartree']-(-.2961234879859993))<2e-10


def test_q_pair_retains_two_different_angular_ordinals():
    a=api();r=a.bound_pair((3,1,0),(4,2,0),7.9283658479841215)
    assert r['distinct']
    assert r['a']['indices']=={'radial':1,'angular':1}
    assert r['b']['indices']=={'radial':1,'angular':2}
    assert abs(r['a']['energy_hartree']+.3448813037297498)<2e-10
    assert abs(r['b']['energy_hartree']+.3073388107529941)<2e-10
    assert r['a']['tau']==r['b']['tau']


def test_r3_guard_reference_continues_as_3d_not_another_root():
    a=api()
    for R,ref in [(11.,-.6052531402700655),(14.,-.5798945940004903)]:
        r=a.bound_state((3,2,0),R)
        assert abs(r['energy_hartree']-ref)<2e-10
        assert r['indices']=={'radial':0,'angular':2}


def test_finite_pencil_is_strictly_monotone_with_fixed_basis():
    a=api();p=a.pencils(R=8.,m=1,tau=3.,size=28,Z1=1.,Z2=2.)
    assert np.linalg.eigvalsh(p['radial_slope'])[0]>0
    assert np.linalg.eigvalsh(p['angular_slope'])[0]>0
    vals=[a.match_value(p,1,1,w) for w in [.1,.25,.5,1.,2.,4.]]
    assert np.all(np.diff(vals)>0)


def test_angular_projection_preserves_the_top_edge_term():
    a=api();p=a.pencils(R=2.,m=0,tau=1.,size=8,Z1=1.,Z2=2.)
    # Integral P_l^2 eta^2 = c_{l-1}^2+c_l^2, including the missing external mode.
    l=7.;expected=1-l*l/((2*l-1)*(2*l+1))-(l+1)**2/((2*l+1)*(2*l+3))
    assert p['angular_slope'][-1,-1]==pytest.approx(expected,abs=2e-15)


def test_galerkin_minimax_refinement_is_not_an_arbitrary_root_choice():
    a=api();rs=[a.solve_indexed((4,2,1),8.,size=s,tau=3.) for s in [12,20,32,48]]
    es=np.array([r['energy_hartree'] for r in rs])
    assert np.all(np.diff(es)<2e-11) # allows documented float64 roundoff
    assert abs(es[-1]+.23359966931345516)<2e-10


def test_common_charge_scaling_and_united_atom_limit():
    a=api()
    r=a.bound_state((3,2,1),3.)
    t=a.bound_state((3,2,1),1.5,Z1=2.,Z2=4.)
    assert abs(r['p']-t['p'])<1e-10
    assert abs(t['energy_hartree']-4*r['energy_hartree'])<2e-10
    u=a.bound_state((4,2,0),.01)
    assert abs(u['energy_hartree']+.28125)<6e-7


def test_special_function_basis_oracle():
    a=api();from scipy.special import lpmv
    # Exact terminating 2F1 from requested 80-digit external oracle.
    h=.0004825890064239501953125
    val=-(1-.25**2)**1.5*math.factorial(15)/(8*math.factorial(3)*math.factorial(9))*h
    assert abs(val-lpmv(3,12,.25))<1e-12
    assert abs(val-(-32.8874105413069800072))<1e-12


@pytest.mark.parametrize('state,R', [((0,0,0),1.),((3,3,0),1.),((3,2,-1),1.),((3,2,0),0.),((3,2,0),float('nan')),((True,0,0),1.),((3,2.,0),1.)])
def test_invalid_input_rejected(state,R):
    with pytest.raises(ValueError):api().bound_state(state,R)


def test_budget_and_refinement_fail_closed():
    a=api()
    with pytest.raises(a.BranchUnresolved):a.solve_indexed((4,2,0),8.,maxiter=1)
    with pytest.raises(ValueError):a.bound_pair((3,1,0),(3,1,0),2.)
    with pytest.raises(a.BranchUnresolved):a.bound_state((4,2,1),8.,sizes=(8,9),energy_tol=1e-15,lambda_tol=1e-15)
