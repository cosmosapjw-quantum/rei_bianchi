"""Matrix and uncertainty-envelope tests; no native kernels."""
import importlib
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
def api():
    assert (Path(__file__).parent/'metric_controls.py').exists(), 'metric controls absent'
    return importlib.import_module('metric_controls')

def test_scalar_minimum_correction():
    c=api();d=c.diagnose(np.array([[2.]]),np.array([[6.]]))
    assert d['eta']==pytest.approx(3) and d['minimum_connection_correction']==pytest.approx(1.5)

def test_noncommuting_congruence_invariance():
    c=api();rng=np.random.default_rng(804)
    for _ in range(30):
        a=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));o=a.conj().T@a+np.eye(4)
        b=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));r=b+b.conj().T
        t=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));t+=3*np.eye(4)
        assert c.diagnose(t.conj().T@o@t,t.conj().T@r@t)['eta']==pytest.approx(c.diagnose(o,r)['eta'],rel=2e-11)

def test_projection_distance_is_attained():
    c=api();rng=np.random.default_rng(900)
    for _ in range(30):
        a=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3));o=a.conj().T@a+np.eye(3)
        b=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3));r=b+b.conj().T
        w=c.whiten(o,r);g=.5*w+1j*np.eye(3)
        assert np.linalg.norm(g-1j*np.eye(3),2)==pytest.approx(c.diagnose(o,r)['minimum_connection_correction'])

@pytest.mark.parametrize('o,r',[(np.array([[-1.]]),np.array([[1.]])),(np.eye(2),np.array([[0.,1.],[0.,0.]])),(np.eye(2),np.eye(3)),(np.array([[np.nan]]),np.ones((1,1)))])
def test_bad_matrices(o,r):
    with pytest.raises(ValueError):api().diagnose(o,r)

def test_conditional_envelope():
    c=api();lo,hi=c.uncertainty_envelope(3,.2,.5)
    assert lo==pytest.approx(2.5/1.2) and hi==pytest.approx(3.5/.8)

@pytest.mark.parametrize('args',[(1,1,.1),(1,-.1,.1),(-1,0,0),(1,0,-1),(float('nan'),0,0)])
def test_bad_envelopes(args):
    with pytest.raises(ValueError):api().uncertainty_envelope(*args)

def test_zero_limit():
    assert api().uncertainty_envelope(0,0,0)==(0,0)
