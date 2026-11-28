import numpy as np
import pytest

from bass_he.eq54 import DeltaSurrogate
from bass_he.geometry import adaptive_seed_rhos


def test_local_cubic_surrogate_is_exact_for_cubic_in_u_rho2():
    rho=np.linspace(0.0,2.0,9)
    u=rho*rho
    delta=0.4+0.2*u-0.03*u*u+0.004*u*u*u
    s=DeltaSurrogate({'B':list(zip(rho,delta))})
    q=np.array([0.13,0.61,1.19,1.83])
    uq=q*q
    exact=0.4+0.2*uq-0.03*uq*uq+0.004*uq*uq*uq
    np.testing.assert_allclose(s.evaluate('B',q),exact,rtol=3e-13,atol=3e-13)


def test_surrogate_requires_endpoint_coverage_and_rejects_extrapolation():
    s=DeltaSurrogate({'B':[(0.0,0.5),(0.3,0.6),(0.7,0.9),(1.0,1.2)]})
    with pytest.raises(ValueError,match='coverage'):
        s.evaluate('B',[1.01])
    with pytest.raises(ValueError,match='rho'):
        s.evaluate('B',[-0.1])


def test_adaptive_seed_rhos_are_open_and_preserve_each_known_split():
    cuts=[0.0,1.0,2.0]
    r=adaptive_seed_rhos(cuts,rule='gk7')
    assert len(r)==14
    assert np.all((r>0)&(r<2))
    assert not np.any(np.isclose(r,1.0))
    assert np.count_nonzero(r<1.0)==7
    assert np.count_nonzero(r>1.0)==7


def test_surrogate_geometry_mapping_respects_branch_support_and_validation_report():
    from bass_he.eq54 import surrogate_geometry_mapping, validate_delta_surrogate
    # Use real branch names/supports but synthetic cubic-in-u anchors.
    from bass_he.eq54 import BRANCHES
    anchors={}
    for k,b in enumerate(BRANCHES):
        rho=np.linspace(0.0,b.support_cutoff,9)
        delta=0.2+0.01*k+0.03*rho*rho+0.001*rho**6
        anchors[b.name]=list(zip(rho,delta))
    s=DeltaSurrogate(anchors)
    rhos=np.array([0.1,2.0,8.0])
    g=surrogate_geometry_mapping(s,rhos)
    for rho in rhos:
        for b in BRANCHES:
            assert ((b.name,float(rho)) in g) == (rho<=b.support_cutoff)
    exact=[]
    for k,b in enumerate(BRANCHES):
        rho=0.37*b.support_cutoff
        d=0.2+0.01*k+0.03*rho*rho+0.001*rho**6
        exact.append(dict(branch=b.name,rho=rho,delta=d))
    report=validate_delta_surrogate(s,exact)
    assert report['count']==len(BRANCHES)
    assert report['max_relative_error']<1e-11
