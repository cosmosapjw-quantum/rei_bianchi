from pathlib import Path
import importlib, os, sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))

def api(): return importlib.import_module('subspace_witness')

def test_subspace_fail_lifts_to_ambient_fail():
    O=np.eye(3); R=np.diag([-2.,.5,3.]); Q=np.array([[1.,0.],[0.,0.],[0.,1.]])
    d=api().analyze_pencil(O,R,Q)
    assert d['eta_reduced_point']==pytest.approx(3)
    assert d['eta_full_point']==pytest.approx(3)
    assert d['eta_reduced_le_eta_full'] is True
    assert d['witnesses']['positive']['ambient_rayleigh_real']==pytest.approx(3)

def test_reduced_pass_does_not_lift_to_ambient_pass():
    O=np.eye(2); R=np.diag([1.,-1.]); Q=np.ones((2,1))/np.sqrt(2)
    d=api().analyze_pencil(O,R,Q)
    assert d['eta_reduced_point']<1e-14
    assert d['eta_full_point']==pytest.approx(1)

def test_nonorthogonal_full_rank_Q_interlaces():
    rng=np.random.default_rng(310030)
    for _ in range(20):
        a=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6)); O=a.conj().T@a+np.eye(6)
        b=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6)); R=b+b.conj().T
        Q=rng.normal(size=(6,3))+1j*rng.normal(size=(6,3))
        d=api().analyze_pencil(O,R,Q)
        assert d['interlacing_pass'] is True
        assert d['eta_reduced_point'] <= d['eta_full_point']+1e-10

def test_lower_bound_on_minimum_connection_correction():
    O=np.eye(3);R=np.diag([-4.,1.,2.]);Q=np.eye(3)[:,:2]
    d=api().analyze_pencil(O,R,Q)
    assert d['minimum_whitened_connection_correction_full_point']==pytest.approx(2)
    assert d['minimum_whitened_connection_correction_lower_bound_from_reduced']==pytest.approx(2)

def test_bad_inputs_rejected():
    with pytest.raises(ValueError): api().analyze_pencil(np.diag([1.,-1.]),np.eye(2),np.ones((2,1)))
    with pytest.raises(ValueError): api().analyze_pencil(np.eye(2),np.array([[1,2],[0,1]]),np.ones((2,1)))
    with pytest.raises(ValueError): api().analyze_pencil(np.eye(2),np.eye(2),np.ones((2,2)))
