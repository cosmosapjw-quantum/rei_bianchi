from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

MODULE=Path(__file__).parents[1]/'analysis/pds_decomposition.py'

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_pds',MODULE)
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module


def test_decomposition_reconstructs_hydrogen_and_helium_rhs():
    m=load()
    rhs=np.array([
        [-2.0,2.0,-3.0,1.0,2.0],
        [ 4.0,-4.0,2.0,-5.0,3.0],
        [ 0.0,0.0,-1.0,0.25,0.75],
    ])
    flux=m.decompose_conservative_rhs(rhs)
    reconstructed=m.flux_rhs(flux)
    np.testing.assert_allclose(reconstructed,rhs,rtol=0.0,atol=2e-15)
    assert np.all(flux>=0.0)
    assert np.all(np.diagonal(flux,axis1=1,axis2=2)==0.0)


def test_hydrogen_and_helium_do_not_cross_blocks():
    m=load()
    rhs=np.array([[-1.0,1.0,-2.0,0.5,1.5]])
    flux=m.decompose_conservative_rhs(rhs)
    assert np.count_nonzero(flux[:,0:2,2:5])==0
    assert np.count_nonzero(flux[:,2:5,0:2])==0


def test_helium_deterministic_priority_is_stable():
    m=load()
    rhs=np.array([[0.0,0.0,3.0,-1.0,-2.0]])
    a=m.decompose_conservative_rhs(rhs)
    b=m.decompose_conservative_rhs(rhs.copy())
    assert a.tobytes()==b.tobytes()
    # donors HeII then HeIII feed receiver HeI in ascending donor order
    assert a[0,2,3]==pytest.approx(1.0)
    assert a[0,2,4]==pytest.approx(2.0)


def test_nonconservative_rhs_fails_closed():
    m=load()
    with pytest.raises(m.NonConservativeRHS):
        m.decompose_conservative_rhs(np.array([[1.0,0.0,0.0,0.0,0.0]]))


def test_nonfinite_rhs_fails_closed():
    m=load()
    with pytest.raises(ValueError):
        m.decompose_conservative_rhs(np.array([[np.nan,0.0,0.0,0.0,0.0]]))


def test_zero_rhs_has_exact_zero_flux():
    m=load()
    flux=m.decompose_conservative_rhs(np.zeros((4,5)))
    assert np.count_nonzero(flux)==0
