import importlib.util
from pathlib import Path
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("m",HERE/"refinement_gain.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_exact_propagation_against_hermite_restriction():
    rng=np.random.default_rng(3175);H=2.2358772390338113
    o0,o1,d0,d1,k0,k1=[rng.normal(size=(4,2))+1j*rng.normal(size=(4,2)) for _ in range(6)]
    om=(o0+o1)/2+H*(d0-d1)/8;dm=3*(o1-o0)/(2*H)-(d0+d1)/4;km=(k0+k1)/2
    cO,cD,cK=[rng.normal(size=(4,2))+1j*rng.normal(size=(4,2)) for _ in range(3)]
    om2,dm2,km2=om+cO,dm+cD,km+cK
    u=.75
    h00=2*u**3-3*u**2+1;h10=u**3-2*u**2+u;h01=-2*u**3+3*u**2;h11=u**3-u**2
    dh00=6*u*u-6*u;dh10=3*u*u-4*u+1;dh01=-6*u*u+6*u;dh11=3*u*u-2*u
    Oco=h00*o0+H*h10*d0+h01*o1+H*h11*d1
    dco=(dh00*o0+H*dh10*d0+dh01*o1+H*dh11*d1)/H
    Kco=(1-u)*k0+u*k1
    h=H/2;v=.5
    h00=2*v**3-3*v**2+1;h10=v**3-2*v**2+v;h01=-2*v**3+3*v**2;h11=v**3-v**2
    dh00=6*v*v-6*v;dh10=3*v*v-4*v+1;dh01=-6*v*v+6*v;dh11=3*v*v-2*v
    Ore=h00*om2+h*h10*dm2+h01*o1+h*h11*d1
    dre=(dh00*om2+h*dh10*dm2+dh01*o1+h*dh11*d1)/h
    Kre=.5*km2+.5*k1
    p=m.propagated_midpoint_correction(cO,cD,cK,H)
    assert np.allclose(Ore-Oco,p[0],rtol=0,atol=2e-14)
    assert np.allclose(dre-dco,p[1],rtol=0,atol=2e-14)
    assert np.allclose(Kre-Kco,p[4],rtol=0,atol=2e-14)

def test_z05_norm_bounds():
    b=m.norm_bounds_from_z05_errors(.0875296210906087,.06210196649428255,.15030919260543524,2.2358772390338113)
    assert b["O_lower"]==pytest.approx(.03508653720881643)
    assert b["O_upper"]==pytest.approx(.05244308388179227)
    assert b["dotO_lower"]==pytest.approx(.1019178360724072)
    assert b["dotO_upper"]==pytest.approx(.1329688193195485)
    assert b["K_exact"]==pytest.approx(.07515459630271762)

def test_secondary_pareto_rule():
    assert m.pareto_verdict([.1,.2],[.3,.4])=="REFINED_PARETO_SUPPORTED_AT_Z075"
    assert m.pareto_verdict([.3,.4],[.1,.2])=="COARSE_PARETO_SUPPORTED_AT_Z075"
    assert m.pareto_verdict([.1,.4],[.2,.3])=="REFINEMENT_TRADEOFF_UNRESOLVED"

def test_tolerance_boundary():
    assert m.pareto_verdict([0.,0.],[1e-10,1e-10])=="REFINEMENT_TRADEOFF_UNRESOLVED"
    assert m.pareto_verdict([0.,0.],[2e-10,1e-10])=="REFINED_PARETO_SUPPORTED_AT_Z075"

def test_primary_information():
    x=m.primary_information()
    assert x["S_design_only_per_ta"]==pytest.approx(.4895514808965761)
    assert x["K_half_gap_per_ta"]==pytest.approx(.17092315293092586)
    assert x["Dmax_half_gap_per_ta"]==pytest.approx(.17521540715404854)
    assert x["winner_prediction"] is False

def test_invalid():
    with pytest.raises(ValueError):m.norm_bounds_from_z05_errors(.1,.2,.3,0)
    with pytest.raises(ValueError):m.pareto_verdict([-.1,.2],[.3,.4])
