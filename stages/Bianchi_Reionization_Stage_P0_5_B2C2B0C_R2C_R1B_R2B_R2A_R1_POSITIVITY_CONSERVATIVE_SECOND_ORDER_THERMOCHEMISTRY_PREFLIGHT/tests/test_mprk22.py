from __future__ import annotations
import importlib.util, sys
from pathlib import Path
import numpy as np
import pytest

MODULE=Path(__file__).parents[1]/'analysis/mprk22.py'

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_mprk22',MODULE)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m


def two_state_flux(t,y):
    k=1.0+0.5*t
    out=np.zeros((y.shape[0],2,2),float)
    out[:,1,0]=k*y[:,0]
    return out


def exact_two_state(t,y0):
    surv=np.exp(-t-0.25*t*t)
    out=np.empty_like(y0)
    out[:,0]=y0[:,0]*surv
    out[:,1]=np.sum(y0,axis=1)-out[:,0]
    return out


def test_mprk22_is_positive_and_conservative_for_large_step():
    m=load(); y0=np.array([[0.9,0.1],[2.0,3.0]])
    result=m.mprk22_step(y0=y0,t0=0.0,dt=20.0,flux_function=two_state_flux)
    assert np.all(result.corrector>0.0)
    np.testing.assert_allclose(np.sum(result.corrector,axis=1),np.sum(y0,axis=1),rtol=2e-15,atol=0.0)


def test_mprk22_observed_order_is_second_for_nonautonomous_transfer():
    m=load(); y0=np.array([[0.9,0.1]])
    errors=[]
    for n in (4,8,16,32):
        y=y0.copy(); dt=1.0/n; t=0.0
        for _ in range(n):
            y=m.mprk22_step(y0=y,t0=t,dt=dt,flux_function=two_state_flux).corrector
            t+=dt
        errors.append(np.max(np.abs(y-exact_two_state(1.0,y0))))
    orders=[np.log(errors[i]/errors[i+1])/np.log(2.0) for i in range(len(errors)-1)]
    assert min(orders[-2:])>1.8, (errors,orders)


def test_zero_flux_is_exact_identity():
    m=load(); y0=np.array([[1.0,2.0,3.0]])
    def zero(t,y): return np.zeros((y.shape[0],3,3))
    result=m.mprk22_step(y0=y0,t0=2.0,dt=9.0,flux_function=zero)
    np.testing.assert_array_equal(result.predictor,y0)
    np.testing.assert_array_equal(result.corrector,y0)


def test_pairwise_structural_zero_remains_zero():
    m=load(); y0=np.array([[1.0,2.0,3.0]])
    def flux(t,y):
        out=np.zeros((1,3,3)); out[:,1,0]=0.2*y[:,0]
        return out
    result=m.mprk22_step(y0=y0,t0=0.0,dt=1.0,flux_function=flux)
    assert result.stage_flux[0,2,0]==0.0
    assert result.final_flux[0,2,0]==0.0
    assert result.corrector[0,2]==y0[0,2]


def test_negative_flux_fails_closed():
    m=load(); y0=np.array([[1.0,1.0]])
    def bad(t,y):
        out=np.zeros((1,2,2)); out[:,1,0]=-1.0; return out
    with pytest.raises(ValueError):
        m.mprk22_step(y0=y0,t0=0.0,dt=1.0,flux_function=bad)


def test_nonpositive_parent_fails_closed():
    m=load()
    with pytest.raises(ValueError):
        m.mprk22_step(y0=np.array([[1.0,0.0]]),t0=0.0,dt=1.0,flux_function=two_state_flux)

def test_public_corrector_matches_combined_step():
    m=load(); y0=np.array([[0.9,0.1]]); dt=0.2
    flux0=two_state_flux(0.0,y0)
    pred=m.patankar_euler(y0=y0,flux=flux0,dt=dt)
    flux1=two_state_flux(dt,pred)
    direct=m.mprk22_corrector(y0=y0,predictor=pred,stage_flux=flux0,final_flux=flux1,dt=dt)
    combined=m.mprk22_step(y0=y0,t0=0.0,dt=dt,flux_function=two_state_flux).corrector
    np.testing.assert_allclose(direct,combined,rtol=0.0,atol=0.0)
