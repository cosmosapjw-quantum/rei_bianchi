from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import numpy as np

ANALYSIS=Path(__file__).resolve().parents[1]/'analysis'

def load():
    spec=importlib.util.spec_from_file_location('evalsite_implicit_certificates',ANALYSIS/'implicit_certificates.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module);return module

def test_implicit_tangent_matches_centered_difference():
    m=load()
    A=np.array([[[2.0,-0.2],[-0.1,1.5]]])
    b=np.array([[1.0,0.7]])
    dA=np.array([[[0.03,0.01],[-0.02,0.04]]])
    db=np.array([[0.02,-0.01]])
    z=np.linalg.solve(A,b[...,None])[...,0]
    dz=m.implicit_linear_tangent(A,z,dA,db)
    eps=1.0e-6
    zp=np.linalg.solve(A+eps*dA,(b+eps*db)[...,None])[...,0]
    zm=np.linalg.solve(A-eps*dA,(b-eps*db)[...,None])[...,0]
    oracle=(zp-zm)/(2*eps)
    assert np.max(np.abs(dz-oracle))<2.0e-10

def test_interval_krawczyk_certifies_small_matrix_box():
    m=load()
    A0=np.array([[[1.2,-0.1],[-0.2,1.4]]])
    rad=np.full_like(A0,1.0e-5)
    b0=np.array([[1.0,0.8]])
    brad=np.full_like(b0,1.0e-6)
    cert=m.linear_interval_krawczyk(A0-rad,A0+rad,b0-brad,b0+brad)
    assert bool(cert.certified[0])
    assert cert.row_sum_bound[0]<1.0
    assert np.all(cert.radius[0]>0.0)

def test_scalar_root_krawczyk_excludes_zero_denominator():
    m=load()
    cert=m.scalar_root_krawczyk(
        center=np.array([1.0]),
        residual=np.array([0.0]),
        derivative_lower=np.array([1.9]),
        derivative_upper=np.array([2.1]),
        initial_radius=np.array([1.0e-6]),
    )
    assert bool(cert.certified[0])
    assert not bool(cert.denominator_contains_zero[0])
