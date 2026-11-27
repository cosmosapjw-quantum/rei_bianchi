"""Research-only tests: small synthetic matrices, no HH native evaluation."""
import importlib
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))

def api():
    return importlib.import_module('metric_cell')

def triple():
    o=np.array([[2, 1j],[-1j,3]],complex)
    d=np.array([[1j,.3+.1j],[-.2j,.4]],complex)
    od=np.array([[.2,.5j],[-.5j,-.1]],complex)
    return o,d,od

def test_scalar_witness_and_signed_bounds():
    d=api().diagnose(np.array([[2.]]),np.array([[-6.]]))
    assert d['eta_svd']==pytest.approx(3)
    assert d['witness_rate']==pytest.approx(-3)
    assert d['witness_norm']==pytest.approx(1)
    assert d['certified'] is False

def test_noncommuting_time_dependent_covariance():
    o,d,od=triple(); t=.37
    q=np.array([[1,t],[1j*t,1+1j*t*t]])
    qd=np.array([[0,1],[1j,2j*t]])
    x=api().pullback(o,d,od,q,qd)
    assert np.allclose(x['R'],q.conj().T@(od-d-d.conj().T)@q,rtol=1e-13,atol=1e-13)
    assert api().diagnose(o,od-d-d.conj().T)['eta_svd']==pytest.approx(api().diagnose(x['O'],x['R'])['eta_svd'],rel=1e-12)

def test_missing_connection_is_not_covariant():
    o,d,od=triple();t=.37
    q=np.array([[1,t],[1j*t,1+1j*t*t]]);qd=np.array([[0,1],[1j,2j*t]])
    x=api().pullback(o,d,od,q,qd)
    wrong_d=q.conj().T@d@q
    assert np.linalg.norm(x['dotO']-wrong_d-wrong_d.conj().T-x['R'])>1

def test_rectangular_projection_can_hide_defect():
    o=np.eye(2);r=np.diag([1.,-1.]);q=np.ones((2,1))/np.sqrt(2)
    out=api().pullback(o,-r/2,np.zeros((2,2)),q,np.zeros_like(q))
    assert api().diagnose(o,r)['eta_svd']==pytest.approx(1)
    assert api().diagnose(out['O'],out['R'])['eta_svd']<1e-14

def test_moving_rectangular_projection_cancels_connection():
    o,d,od=triple();q=np.array([[1],[.4j]]);qd=np.array([[0],[1j]])
    out=api().pullback(o,d,od,q,qd)
    assert np.allclose(out['R'],q.conj().T@(od-d-d.conj().T)@q)

def test_scalar_affine_endpoint_theorem():
    o0=np.array([[1.]]);o1=np.array([[2.]]);d0=np.array([[0.]]);d1=np.array([[-1.]])
    a=api().affine_endpoint_diagnostic(o0,o1,d0,d1,1.)
    assert a['lower_log_norm_rate']==pytest.approx(1.)
    assert a['upper_log_norm_rate']==pytest.approx(1.5)
    assert a['uniform_eta_numeric']==pytest.approx(1.5)
    assert a['certified'] is False

def test_noncommuting_affine_endcaps_on_dense_synthetic_grid():
    rng=np.random.default_rng(310029)
    for _ in range(24):
        a=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));o0=a.conj().T@a+np.eye(4)
        a=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));o1=a.conj().T@a+np.eye(4)
        d0=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));d1=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4))
        dt=.7; a=api().affine_endpoint_diagnostic(o0,o1,d0,d1,dt)
        for s in np.linspace(0,1,13):
            o=(1-s)*o0+s*o1;d=(1-s)*d0+s*d1;r=(o1-o0)/dt-d-d.conj().T
            f=api().diagnose(o,r)
            assert f['eta_svd']<=a['uniform_eta_numeric']+1e-11
            assert f['lambda_min_real']>=a['lower_log_norm_rate']-1e-11
            assert f['lambda_max_real']<=a['upper_log_norm_rate']+1e-11

def test_nonaffine_residual_refutes_unqualified_endcap_claim():
    # O=1, D(s)=-2*s*(1-s), R(s)=4*s*(1-s): zero endpoints, unit midpoint.
    end=api().affine_endpoint_diagnostic(np.eye(1),np.eye(1),np.zeros((1,1)),np.zeros((1,1)),1)
    assert end['uniform_eta_numeric']==0
    assert api().diagnose(np.eye(1),np.ones((1,1)))['eta_svd']==pytest.approx(1)

def test_time_unit_rescaling():
    o0=np.eye(2);o1=2*np.eye(2);d0=np.diag([.3,.4]);d1=2*d0
    a=api().affine_endpoint_diagnostic(o0,o1,d0,d1,2)
    b=api().affine_endpoint_diagnostic(o0,o1,5*d0,5*d1,2/5)
    assert b['uniform_eta_numeric']==pytest.approx(5*a['uniform_eta_numeric'])
    assert b['upper_log_norm_change']==pytest.approx(a['upper_log_norm_change'])

@pytest.mark.parametrize('dt',[0,-1,True,np.nan,np.inf])
def test_bad_time_intervals_rejected(dt):
    with pytest.raises(ValueError):api().affine_endpoint_diagnostic(np.eye(1),np.eye(1),np.eye(1),np.eye(1),dt)

@pytest.mark.parametrize('which',['nonfinite','nonhermitian','indefinite','empty','shape'])
def test_bad_metrics_rejected(which):
    o=np.eye(2,dtype=complex);r=o.copy()
    if which=='nonfinite':o[0,0]=np.nan
    elif which=='nonhermitian':r[0,1]=1
    elif which=='indefinite':o[0,0]=-1
    elif which=='empty':o=r=np.empty((0,0))
    elif which=='shape':r=np.eye(3)
    with pytest.raises(ValueError):api().diagnose(o,r)

def test_no_input_repair_or_mutation():
    o,d,od=triple();r=od-d-d.conj().T;ob=o.tobytes();rb=r.tobytes()
    api().diagnose(o,r)
    assert ob==o.tobytes() and rb==r.tobytes()

def test_witness_source_error_bound():
    f=api().conditional_witness_lower_bound
    assert f(3,.2,.5)==pytest.approx(2.5/1.2)
    assert f(.1,.1,.2)==0

@pytest.mark.parametrize('a,b,c',[(1,1,0),(1,-.1,0),(-1,0,0),(1,0,-1),(np.nan,0,0),(True,0,0)])
def test_bad_uncertainty_inputs(a,b,c):
    with pytest.raises(ValueError):api().conditional_witness_lower_bound(a,b,c)

def test_ill_shaped_frame_rejected():
    o,d,od=triple()
    with pytest.raises(ValueError):api().pullback(o,d,od,np.ones((3,1)),np.zeros((3,1)))

def test_singular_square_frame_rejected():
    o,d,od=triple()
    with pytest.raises(ValueError):api().pullback(o,d,od,np.ones((2,2)),np.zeros((2,2)))
