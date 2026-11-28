from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from refined_source import GridSpec, RefinedSourceModel, build_grid
from sourcecut import SourceCutModel as OldSource
from physics import Model, X_END

@pytest.mark.parametrize('q',[-.005,0.,.005])
def test_legacy_grid_byte_identity(q):
    a=Model(None,m=4,angles=4,q=q)
    g=build_grid(GridSpec(m=4,angles=4,q=q,strips=1))
    for v,w in [(a.Eref,g.energy),(a.mu0,g.mu),(a.weights,g.weight)]:
        assert np.array_equal(v,w)

@pytest.mark.parametrize('r',[1,2,4,8])
def test_strip_refines_independently(r):
    s=GridSpec(m=4,angles=4,q=0.,strips=r);g=build_grid(s)
    assert len(g.energy)==4*4*(3*4+4*r)
    narrow=[b-a for _,_,_,panels in g.groups for a,b,n in panels if n]
    assert len(narrow)==4*4*r
    base=build_grid(GridSpec(m=4,angles=4,q=0.,strips=1))
    max0=max(b-a for _,_,_,ps in base.groups for a,b,n in ps if n)
    assert max(narrow)<=max0/r*(1+1e-4)

@pytest.mark.parametrize('kwargs',[{'strips':0},{'strips':True},{'strips':3},{'angles':0},{'q':float('nan')},{'m':3}])
def test_invalid_grid(kwargs):
    with pytest.raises(ValueError):GridSpec(**kwargs)

@pytest.mark.parametrize('q',[-.005,0.,.005])
def test_positive_actual_moments(q):
    a=RefinedSourceModel(None,spec=GridSpec(q=q,strips=2),tabulate=False)
    for f in [0.,.1,.37,.9,1.]:
        w,r=a.source_moments(f*a.t_end)
        assert w.shape==(a.K,) and np.all(w>=0)
        assert r['max_relative_moment_error']<=3e-13
        assert r['max_angle_band_relative_error']<=3e-13
        assert len(a.initial_state())==len(a.scale)==4+a.K+19
        assert np.all(a.scale>0)


def test_legacy_source_parity():
    old=OldSource(None,m=4,angles=4,q=0.)
    new=RefinedSourceModel(None,spec=GridSpec(strips=1),tabulate=False)
    t=.37*old.t_end
    assert np.array_equal(old.source_moments(t)[0],new.source_moments(t)[0])
    assert np.array_equal(old.k_perp,new.k_perp)
    assert np.array_equal(old.k_parallel,new.k_parallel)
    np.testing.assert_allclose(old.breakpoints,new.breakpoints,rtol=0,atol=0)


def test_resource_gate_before_tables():
    with pytest.raises(MemoryError,match='TABLE_BUDGET'):
        RefinedSourceModel(None,spec=GridSpec(strips=2),tabulate=True,max_table_bytes=1)


def test_exact_opacity_one_sided_support():
    m=RefinedSourceModel(None,spec=GridSpec(strips=2),tabulate=False)
    bounds=[0.,*m.breakpoints,m.t_end]
    for lo,hi in zip(bounds[:-1],bounds[1:]):
        m.set_interval(lo,hi)
        for t in (lo,(lo+hi)/2,hi):
            v,r=m.source_moments(t)
            assert np.all(v>=0) and r['max_relative_moment_error']<=3e-13
