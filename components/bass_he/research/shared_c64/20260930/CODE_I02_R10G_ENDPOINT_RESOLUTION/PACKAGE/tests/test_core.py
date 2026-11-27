import numpy as np
import pytest
from eta_rotation import eta_rotation_batch,eta_dop853
from endpoint_quadrature import integrate_endpoint


def test_headon_limit_and_nonentered_block():
    a=eta_rotation_batch(2,1,[.5,.5],[0.,2.],R_cut=.75,steps=128)
    np.testing.assert_allclose(a['P_abs'],np.broadcast_to(np.eye(2),(2,2,2)),atol=5e-13)
    assert a['entered'].tolist()==[True,False]


def test_small_rho_independent_integrator_and_step_gate():
    r=np.array([.00067675,.00338375,.033412, .1])
    a=eta_rotation_batch(3,2,5.,r,R_cut=25/12,steps=128)
    b=eta_rotation_batch(3,2,5.,r,R_cut=25/12,steps=256)
    assert np.max(abs(a['P_abs']-b['P_abs']))<1e-7
    q=eta_dop853(3,2,5.,r[1],R_cut=25/12)
    assert np.max(abs(b['P_abs'][1]-q['P_abs']))<1e-8
    assert np.max(abs(b['U_z'].conj().swapaxes(-1,-2)@b['U_z']-np.eye(5)))<5e-13
    assert np.max(abs(b['P_abs'].sum(1)-1))<5e-13


@pytest.mark.parametrize('r',[-1.,np.nan,np.inf])
def test_invalid_rho_rejected(r):
    with pytest.raises(ValueError):eta_rotation_batch(2,1,.5,r,R_cut=.75)


@pytest.mark.parametrize('steps',[True,3,1.5])
def test_steps_contract(steps):
    with pytest.raises(ValueError):eta_rotation_batch(2,1,.5,.05,R_cut=.75,steps=steps)


def test_vector_integral_cylindrical_jacobian_and_confirmation():
    calls=[]
    def f(r):
        calls.extend(r.tolist())
        return np.column_stack([np.ones(len(r)),r*r])
    result=integrate_endpoint(f,B=.5,scale=.0067675,tail=[2.,3.],tail_error=[0.,0.],max_leaves=8)
    assert result['converged'] and result['stable_confirmation']
    np.testing.assert_allclose(result['integral'],[2+np.pi*.25,3+np.pi*.5**4/2],rtol=3e-10)
    assert all(0<x<.5 for x in calls)
    assert result['evaluations']<=210
    assert result['leaf_count']>=3


def test_componentwise_not_total_only_and_budget_stop():
    def f(r):return np.column_stack([1e5*np.ones(len(r)),.1+np.sin(800*r)**2])
    result=integrate_endpoint(f,B=.5,scale=.01,tail=[0.,0.],tail_error=[0.,0.],max_leaves=2)
    assert not result['converged']
    assert result['status']=='ENDPOINT_BUDGET_UNRESOLVED'
    assert result['evaluations']==30


def test_no_relaxation_when_tail_error_already_exhausts_budget():
    def f(r):return np.ones((len(r),1))
    result=integrate_endpoint(f,B=.5,scale=.01,tail=[1.],tail_error=[10.],max_leaves=3)
    assert not result['converged']
    assert result['evaluations']==60


def test_invalid_integrand_fails_closed():
    with pytest.raises(ValueError):
        integrate_endpoint(lambda r:np.full((len(r),1),np.nan),B=.5,scale=.01,tail=[0.],tail_error=[0.])


def test_transport_identity_and_absorbing_probability_structure():
    from audit_support import propagate
    y=propagate(np.zeros((2,5)),np.broadcast_to(np.eye(10),(2,10,10)))
    assert np.all(y[:,2]==1) and np.all(y.sum(1)==1)
    p=np.zeros((2,5));p[:,0]=1  # S23 sink turns initial state2 into state5
    y=propagate(p,np.broadcast_to(np.eye(10),(2,10,10)))
    assert np.all(y[:,5]==1) and np.all(y.sum(1)==1)


def test_rotation_lane_contract_names():
    import ast
    from pathlib import Path
    tree=ast.parse(Path('execute_endpoint.py').read_text())
    # Guard a literal-index integration wiring error without scientific execution.
    source=Path('execute_endpoint.py').read_text()
    assert "mats['SL_CPC' if kind=='CPC' else 'SL_AUTHORCUT']" in source


def test_archive_wrong_hash_fails_before_extraction(tmp_path):
    from execute_endpoint import restore
    path=tmp_path/'bad.zip';path.write_bytes(b'not a zip')
    with pytest.raises(ValueError,match='IDENTITY_MISMATCH'):restore(path,tmp_path/'extracted')
    assert not (tmp_path/'extracted').exists()


def test_frozen_components_probabilities_and_shape():
    from audit_support import frozen_components
    y=frozen_components([.001,.03,.25])
    assert y.shape==(3,18) and np.min(y)>=0 and np.max(y)<=1
