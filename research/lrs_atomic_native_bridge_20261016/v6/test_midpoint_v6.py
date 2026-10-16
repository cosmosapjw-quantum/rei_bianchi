"""Scoped independent regression of time-centered Case-A exact-pair composition."""
import math, os, sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import solve_ivp

from bootstrap_v6 import setup
setup()
from rate_table import CaseARates, ConstantRates
from midpoint_recomb_v6 import midpoint_casea_event
from recomb_thermal import K_B_EV_PER_K, EV_J, particle_count
from recomb_thermal_midpoint_v6 import evolve_thermal
from recomb_dominated_v5 import INITIAL, N_STAR, H0, END, T0, rays
from dynamic_chemistry import Gas, pair_exact


def thermal(g,t):
    return 1.5*K_B_EV_PER_K*t*particle_count(g)


def test_frozen_rate_exact_map_with_cooling_zero():
    rates=ConstantRates(rr=(3e-13,0.,0.),cooling=(0.,0.,0.))
    g=list(Gas(.2,.3,0.,0.,0.).as_tuple())
    U=thermal(g,13000.)
    h=0.01;scale=1e15
    expected=pair_exact(.3,.3,h*scale*3e-13)
    final,esc,e=midpoint_casea_event(g,U,0,h,scale,rates,13.598434599702)
    assert e.count==pytest.approx(expected,rel=2e-14)
    assert e.cooling_ev==0.
    assert final==U
    assert esc==pytest.approx(13.598434599702*expected,rel=1e-13)
    assert g[1]>=0 and g[0]>=0
    assert sum(g[:2])==pytest.approx(.5)


@pytest.mark.parametrize('species,ion',[(0,1),(1,3),(2,4)])
def test_real_casea_all_ions_positive_and_ledger(species,ion):
    g=list(Gas(.37,.03,.08,.017,.004).as_tuple())
    before=tuple(g)
    n0=particle_count(g)
    U=thermal(g,15000.)
    final,escaped,e=midpoint_casea_event(g,U,species,.0025,
                 .1/1e-16,CaseARates(),(13.598434599702,24.587389011,54.41776)[species])
    assert 0<=e.count<=before[ion]
    assert abs((before[ion]-g[ion])-e.count)<1e-15
    assert min(g)>=0
    assert e.cooling_ev>=0
    assert final>=0
    assert abs((U-final)-e.cooling_ev)<2e-15
    assert escaped==pytest.approx((13.598434599702,24.587389011,54.41776)[species]*e.count+e.cooling_ev)
    assert particle_count(g)==pytest.approx(n0-e.count,abs=1e-15)
    assert 10000<e.midpoint_temperature_K<24000


def test_provider_outside_domain_never_mutates():
    provider=CaseARates()
    g=list(Gas(.3,.1,0,0,0).as_tuple())
    orig=g[:]
    with pytest.raises(ValueError,match='provider'):
        midpoint_casea_event(g,thermal(g,29000.),0,.01,.1/1e-16,provider,13.6)
    assert g==orig


def test_negative_exposure_blocked():
    g=list(Gas(.3,.1,0,0,0).as_tuple());before=g[:]
    with pytest.raises(ValueError,match='nonphysical'):
        midpoint_casea_event(g,thermal(g,15000.),0,-.1,.1/1e-16,CaseARates(),13.6)
    assert g==before


def test_h_dense_regression_four_steps_and_order():
    from run_dense_v6 import run
    ans=run()
    rows=ans['rows']
    for r in rows:
        assert abs(r['v6_energy_residual_ev'])<1e-12
        assert abs(r['v6_nuclear_residual_H'])<1e-12
        assert r['v6_T_K']>10000
        assert r['v6_HII']>=0
    for p in ans['v6_temperature_error_K_orders'][:4]:
        assert 1.90<p<2.08
    for p in ans['legacy_temperature_error_K_orders'][:4]:
        assert .95<p<1.06
    assert rows[3]['v6_temperature_error_K'] < rows[3]['legacy_temperature_error_K']/1000


def test_multichannel_photon_positive_chemistry():
    from study_v5 import rays as make_rays, GAS
    v=evolve_thermal(make_rays(.04),GAS,.05,temperature_initial_K=15000.,
                     max_step=.00125,atomic_rates=CaseARates(),
                     n_star_cm3=1e-6,h0_s=1e-16)
    assert min(v.final.as_tuple())>=0
    assert min(v.photons_final)>=0
    assert v.final_temperature_K>10000.
    assert abs(v.energy_residual_ev)<1e-11
    assert abs(v.hydrogen_residual)<1e-12
    assert abs(v.helium_residual)<1e-12
    assert abs(v.electron_reaction_residual)<1e-12
    assert abs(v.photon_reaction_residual)<1e-12


def test_h_only_no_radiation_heating_energy_identity():
    v=evolve_thermal(rays(0.,0.),INITIAL,.01,temperature_initial_K=15000.,
                     max_step=.000625,atomic_rates=CaseARates(),
                     n_star_cm3=.1,h0_s=1e-16)
    assert abs(v.energy_residual_ev)<1e-12
    assert v.recomb_events[0]>0
    assert sum(v.photo_events)==0
    assert v.escaped_recomb_energy_ev>0
