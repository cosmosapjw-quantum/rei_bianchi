"""Local-only V8 RR/DR+cooling reference, NOT actual PR150 Rust tests."""
from __future__ import annotations
from math import exp, isclose
import numpy as np
import pytest

from rrdr_sourcefree_v8 import (
    CHI_ERG, CHANNELS, KB, T_DOMAIN, Y_HE, binding_energy, compare, evolve,
    native, nuclei_and_electrons, pair_exact, radau_reference, result_vector,
    rhs_independent, stock_vector, symmetric_reactions, rates_at,
)


def test_original_129_rate_table_exact_parity():
    match = native.table_parity()
    assert match["points"] == 129
    assert match["max_relative_error"] == 0.


@pytest.mark.parametrize("ion,electron,exposure",[
    (0., 0.8, 100.), (.02, 0.4, 0.), (.5, .5, 4.),
    (1e-9, .4, 1e10), (.1, .21, 5.), (.25, .250000000001, .5),
])
def test_exact_pair_positive_conserves_1_to_1(ion,electron,exposure):
    a=pair_exact(ion,electron,exposure)
    assert 0 <= a <= min(ion,electron)
    assert ion-a>=-1e-16 and electron-a>=-1e-16
    if ion==electron and ion>0:
        assert isclose(ion-a,ion/(1+ion*exposure),rel_tol=1e-13)


def test_rejected_negative_pair_and_bad_composition():
    with pytest.raises(ValueError,match="nonnegative"):
        pair_exact(-1.,1.,1.)
    with pytest.raises(ValueError,match="simplex"):
        stock_vector((0.3,0.9,0.3))


def test_four_channel_binding_costs_HeII_RR_and_DR_share_HeI_threshold():
    assert CHI_ERG[1]==CHI_ERG[3]
    assert CHI_ERG[2]>CHI_ERG[1]>CHI_ERG[0]
    t=23000.
    a,q=rates_at(t)
    assert len(CHANNELS)==4
    assert a[3] >0 and q[3]>0
    assert (q[3]/a[3])/native.EV_ERG>39.


def test_native_v7_continuous_RHS_equivalence_at_original_density():
    y0=native.initial_state()
    now=rhs_independent(0.,np.r_[y0[:4],np.zeros(13)])
    old=native.rhs(0.,np.r_[y0[:4],0.,0.])
    assert np.allclose(now[:4],old[:4],rtol=1e-12,atol=1e-29)
    assert isclose(sum(now[8:16]),old[4],rel_tol=5e-15)
    assert now[16]==old[5]


def test_no_absorbers_adiabatic_exact_work():
    r=evolve(13,density_factor=0,x_end=.004)
    assert abs(r.temperature - native.T0_K*exp(-.008))<1e-8
    assert np.count_nonzero(r.events)==0
    assert np.count_nonzero(r.cooling)==0
    assert abs(r.energy_residual)<1e-25
    assert np.min(r.stocks)>=0


def test_independent_unchanged_v7_Radau_endpoint():
    sol=radau_reference()
    old=native.integrate(2e-12)
    assert old.success
    assert np.max(np.abs(sol.y[:4,-1]-old.y[:4,-1]))<2e-14
    assert abs(sol.y[16,-1]-old.y[5,-1])<1e-25
    assert abs(sum(sol.y[8:16,-1])-old.y[4,-1])<1e-25


@pytest.mark.parametrize("density,span",[(1.,1e-5),(100.,.002),(1000.,.002),(10000.,.0003)])
def test_four_channel_population_and_thermal_energy_ledgers(density,span):
    r=evolve(24,x_end=span,density_factor=density)
    nh,nhe,ne=nuclei_and_electrons(r.stocks)
    assert abs(nh-1)<1e-13 and abs(nhe-Y_HE)<1e-13
    assert np.all(r.stocks>=0)
    assert np.all(r.events>=0) and np.all(r.cooling>=0)
    assert np.all(r.binding_escape>=0)
    assert abs(r.energy_residual)<1e-24
    start_e=native.INITIAL_FRACTIONS[0]+Y_HE*(native.INITIAL_FRACTIONS[1]+2*native.INITIAL_FRACTIONS[2])
    assert abs(ne-start_e+sum(r.events))<3e-14
    # This is an independently computed *stored* binding decrement, not an
    # energy column constructed by subtraction from the residual.
    old=stock_vector(native.INITIAL_FRACTIONS)
    assert abs(binding_energy(old)-binding_energy(r.stocks)-sum(r.binding_escape))<1e-24
    assert r.max_Tmid_residual<5e-8
    assert 10000 <= r.min_temperature <= r.max_temperature <= 24000


def test_four_channel_continuous_energy_rhs_identity():
    y=native.initial_state()
    ext=np.r_[y[:4],np.zeros(13)]
    f=rhs_independent(0.,ext,200.)
    de_binding=-(f[12]+f[13]+f[14]+f[15])
    direct=f[3] + de_binding + sum(f[8:16]) + f[16]
    assert abs(direct)<1e-25


def test_thermal_work_channel_split_matches_Radau():
    kwargs={'density_factor':1000.,'x_end':.002}
    direct=radau_reference(**kwargs)
    r=evolve(128,**kwargs)
    d=compare(r,direct)
    assert d['T_error_K']<4e-5
    assert d['ne_abs_error']<2e-9
    assert all(np.isfinite(list(d['cooling_error_by_channel_erg_per_H'].values())))
    assert d['max_rr_exposure']<0.05
    assert sum(r.cooling)>0 and r.cooling[3]>0


def test_explicit_provider_out_of_domain_rejected():
    with pytest.raises(ValueError,match="validated"):
        evolve(10,T0=24001.)
    with pytest.raises(ValueError,match="density"):
        evolve(10,density_factor=-1.)


def test_direct_radua_refinement_is_second_order_when_observable_above_roundoff():
    ref=radau_reference(x_end=.002,density_factor=1000.)
    h_errors=[]
    for n in (8,16,32,64):
        r=evolve(n,x_end=.002,density_factor=1000.)
        h_errors.append(compare(r,ref)['T_error_K'])
    p=np.log2(np.asarray(h_errors[:-1])/np.asarray(h_errors[1:]))
    assert np.min(p)>1.95 and np.max(p)<2.12, (h_errors,p.tolist())


def test_dense_helium_fraction_and_separate_DR_event_converge():
    kw={'x_end':.002,'density_factor':1000.,'T0':22000.}
    ref=radau_reference(**kw)
    r=evolve(64,**kw)
    err=abs(r.events[3]-ref.y[7,-1])
    assert r.events[3]>1e-10
    assert err<7e-14
    assert abs(r.energy_residual)<1e-24
