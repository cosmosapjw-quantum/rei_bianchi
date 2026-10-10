import importlib.util
from pathlib import Path
import math
import pytest

def module():
    path=Path(__file__).parents[1]/'model.py'
    assert path.exists(), 'Broad-history reaction/history implementation is missing'
    spec=importlib.util.spec_from_file_location('acc_model',path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_source_off_exponential_recombination():
    m=module(); o=m.advance_constant(.8,0.,3.,.4)
    assert o['q']==pytest.approx(.8*math.exp(-1.2),rel=2e-14)
    assert o['rec']==pytest.approx(.8-o['q'],abs=2e-15)
    assert o['excess']==0.

def test_overlap_is_budgeted_not_lost():
    m=module(); o=m.advance_constant(.2,2.,0.,1.)
    assert o['q']==1.
    assert o['excess']==pytest.approx(1.2,abs=1e-14)
    assert o['integral_q']==pytest.approx(.84,abs=1e-14)
    assert o['q']-.2+o['rec']+o['excess']==pytest.approx(o['emitted'],abs=1e-14)

def test_recombination_and_overlap_analytic():
    m=module(); o=m.advance_constant(0.,2.,1.,2.)
    hit=math.log(2); integral=2*hit-1+2-hit
    assert o['q']==1.
    assert o['integral_q']==pytest.approx(integral,rel=2e-14)
    assert o['excess']==pytest.approx(2-hit,rel=2e-14)
    assert o['q']+o['rec']+o['excess']==pytest.approx(4.,abs=1e-14)

def test_reaction_rejects_invalid_domain():
    m=module()
    for args in [(-.1,1,1,1),(1.1,1,1,1),(.5,-1,1,1),(.5,1,-1,1),(.5,1,1,-1),(.5,float('nan'),1,1)]:
        with pytest.raises(ValueError): m.advance_constant(*args)

def test_rate_and_geometry_domain():
    m=module()
    assert 1.3e-13 < m.alpha_b(20000.) < 1.6e-13
    with pytest.raises(ValueError):m.alpha_b(0.)
    c=m.default_config(); bg=m.make_background(c)
    p=bg.at(0)
    assert p['s']==0.
    assert p['z']==20.
    assert (p['nHe']/p['nH'])==pytest.approx(.2453/(4*(1-.2453)),rel=1e-14)
