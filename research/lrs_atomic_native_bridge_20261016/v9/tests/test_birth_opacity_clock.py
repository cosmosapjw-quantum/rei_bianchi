"""Source-on factor-isolation proof-of-concept; no native PR150 claim."""
import math
import pytest
from birth_opacity_clock import (Experiment,MODES,evolve,ledgers,pair_exact,
    pair_be,radau,independent_exact_photon,linear_frozen_midpoint,slope)

@pytest.mark.parametrize('n,m,z',[(0,1,4),(1,0,4),(1,1,0),(.1,.1,100),(.7,.35,.2),(.9,.6,30),(.9,.9000000000001,.4)])
def test_exact_mass_action_pair(n,m,z):
    a=pair_exact(n,m,z)
    assert 0<=a<=min(n,m)
    if z and n and m:
        small=min(n,m);diff=abs(n-m)
        future=(small/(1+small*z) if not diff else
            small*diff*math.exp(-diff*z)/(diff+small*(-math.expm1(-diff*z))))
        assert a==pytest.approx(small-future,abs=3e-14)

@pytest.mark.parametrize('n,m,z',[(.6,.4,.1),(.4,.4,12),(1,1,1000)])
def test_be_positive_and_implicit(n,m,z):
    a=pair_be(n,m,z)
    assert 0<=a<=min(n,m)
    assert a==pytest.approx(z*(n-a)*(m-a),rel=1e-9,abs=1e-14)

@pytest.mark.parametrize('mode',MODES)
@pytest.mark.parametrize('steps',[4,8,32,128])
def test_positive_both_ledgers_at_all_placement_modes(mode,steps):
    p=Experiment()
    o=evolve(p,steps,mode)
    ls=ledgers(o,p)
    assert min(o.photons,o.neutral,o.ionized,o.absorptions,o.births)>=0
    assert o.ionized==pytest.approx(o.absorptions,abs=3e-14)
    assert max(abs(ls[k]) for k in ('photons','neutral_atoms','ion_reactions'))<2e-13
    assert abs(ls['energy_ev'])<3e-11

@pytest.mark.parametrize('mode',MODES)
def test_zero_opacity_source_integral(mode):
    p=Experiment(opacity0=0,source_slope=0)
    o=evolve(p,8,mode)
    assert o.photons==pytest.approx(p.n0+p.source0*p.t_end,abs=1e-14)
    assert o.neutral==p.neutral0

@pytest.mark.parametrize('mode',MODES)
def test_zero_source_reduction(mode):
    p=Experiment(source0=0)
    o=evolve(p,8,mode)
    assert o.births==0
    assert o.neutral<p.neutral0
    assert o.photons<p.n0

@pytest.mark.parametrize('source_slope,opacity_slope',[(.9,0), (0,.9),(.9,.9)])
def test_factorial_smooth_order_for_linear_prescribed_opacity(source_slope,opacity_slope):
    p=Experiment(source_slope=source_slope,opacity_slope=opacity_slope)
    exact=independent_exact_photon(p)
    errs=[abs(linear_frozen_midpoint(p,n,'mid_mid')[0]-exact[0]) for n in (16,32,64,128)]
    if source_slope == opacity_slope and source_slope != 0:
        # Exact manufactured subcase: S(x)/k(x) constant, k linear.
        # Midpoint exactly integrates total optical depth, so the entire
        # affine source solution is exactly propagated to roundoff.
        assert max(errs)<2e-14
    else:
        assert all(a>b>0 for a,b in zip(errs,errs[1:]))
        assert 1.85<slope(errs[-2],errs[-1])<2.15
    if source_slope:
        e=[abs(linear_frozen_midpoint(p,n,'source_left')[0]-exact[0]) for n in (32,64,128)]
        assert .85<slope(e[-2],e[-1])<1.15
    if opacity_slope:
        e=[abs(linear_frozen_midpoint(p,n,'opacity_left')[0]-exact[0]) for n in (32,64,128)]
        assert .85<slope(e[-2],e[-1])<1.15

@pytest.mark.parametrize('mode,lower,upper',[('mid_mid',1.85,2.15),('source_left',.85,1.15),('opacity_left',.85,1.15),('both_left',.85,1.15),('birth_start',.85,1.15),('chem_be',.85,1.15)])
def test_coupled_dynamic_opacity_radau_convergence(mode,lower,upper):
    p=Experiment()
    exact=radau(p)[0]
    e=[abs(evolve(p,n,mode).photons-exact) for n in (32,64,128,256)]
    assert all(a>b>0 for a,b in zip(e,e[1:]))
    assert lower<slope(e[-2],e[-1])<upper


def test_birth_and_opacity_timing_cancellation_counterexample():
    p=Experiment()
    exact=radau(p)[0]
    e_mid=abs(evolve(p,64,'mid_mid').photons-exact)
    e_double=abs(evolve(p,64,'both_left').photons-exact)
    e_source=abs(evolve(p,64,'source_left').photons-exact)
    e_opacity=abs(evolve(p,64,'opacity_left').photons-exact)
    # Both lagged factors can partially cancel at a *single resolution*.
    assert e_double<min(e_source,e_opacity)
    assert e_mid<e_double


def test_input_rejection():
    for kwargs in [dict(n0=-.1),dict(neutral0=1.1),dict(source_slope=-5),
                   dict(opacity_slope=-5),dict(energy_ev=5),dict(t_end=0)]:
        with pytest.raises(ValueError):Experiment(**kwargs)
    with pytest.raises(ValueError):evolve(Experiment(),0)
    with pytest.raises(ValueError):evolve(Experiment(),4,'not-a-mode')
    with pytest.raises(ValueError):pair_exact(1,-1,3)

@pytest.mark.parametrize('mode,coefficient',[
    ('source_left',lambda p: -p.source0*p.source_slope/2.),
    ('opacity_left',lambda p: p.opacity0*p.opacity_slope*p.n0/2.),
    ('birth_start',lambda p: -p.opacity0*p.source0/2.),
])
def test_one_step_wolfram_local_defect_coefficient(mode,coefficient):
    p=Experiment(t_end=1e-3)
    exact=independent_exact_photon(p)[0]
    delta=linear_frozen_midpoint(p,1,mode)[0]-exact
    assert delta/p.t_end**2 == pytest.approx(coefficient(p),rel=0.012)


def test_proportional_s_and_k_yield_exact_frozen_linear_update():
    p=Experiment(source_slope=.91,opacity_slope=.91)
    ref=independent_exact_photon(p)[0]
    for n in (1,2,4,8,16,32,64):
        assert linear_frozen_midpoint(p,n,'mid_mid')[0] == pytest.approx(ref,abs=3e-14)
