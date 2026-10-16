"""V11 scope-specific reproducible suite, frozen PR150 native-source microphysics."""
from __future__ import annotations
import sys
from pathlib import Path
import hashlib
import math
import numpy as np
import pytest
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'src'))
import ci_thermal_clock as m

REPO=HERE.parents[2] if (HERE.parents[2]/'rust'/'rei_microphysics').exists() else HERE
RUST=REPO/'rust'/'rei_microphysics'/'src'
TABLE=REPO/'rust'/'rei_microphysics'/'tests'/'data'/'igm_grackle'/'grackle_literal_reference.csv'


def check_energy(y,initial,delta=8e-12):
    assert np.all(np.isfinite(y)),y
    assert np.all(y[4:15]>=-2e-13)
    assert abs(m.energy_ledger(y,initial))<=delta
    assert m.valid_state(y)
    assert y[0]>=0 and 0<=y[1]+y[2]<=1


def test_exact_owner_byte_hashes():
    expected={'igm_rates.rs':'310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf',
              'igm_thermal.rs':'30515d96270ec73a37829ba298513a42112991168479d3cb40f33b67fd469ab2',
              'igm_state.rs':'1651b00a517d67aaa71b38d3c69af6413570adfc38b591a3ed25284f039e0ae0'}
    for filename,sha in expected.items():
        assert hashlib.sha256((RUST/filename).read_bytes()).hexdigest()==sha


def test_original_literal_c_donor_all_rows():
    parity=m.grackle_literal_table_parity(TABLE)
    assert parity['rows']==96
    assert parity['columns']==17
    assert parity['max_relative_difference']<4e-13


@pytest.mark.parametrize('temperature',[100.0,2000.0,5000.0,9000.0,10000.0,15000.0,22000.0,100000.0,1000000.0])
def test_source_grackle_rate_domains(temperature):
    rates=m.native_rates(temperature)
    assert len(rates.ci)==len(rates.rr)==len(rates.ce)==3
    if temperature/11605<=.8:
        assert rates.ci[1:]==(1e-20,1e-20)
        assert rates.dr==rates.dr_cool==0
    assert rates.ff>0


@pytest.mark.parametrize('bad',[-1.0,float('nan'),0.,1000001.0])
def test_fail_native_temperature_domain(bad):
    with pytest.raises(ValueError,match='IGM_TEMPERATURE_DOMAIN'):
        m.native_rates(bad)


def test_initial_total_H_nuclei_and_EOS():
    y=m.initial_state()
    assert m.temperature(y)==pytest.approx(15000,abs=2e-11)
    assert m.Y==pytest.approx(0.2454/(4*(1-0.2454)),rel=1e-14)
    assert m.binding(y)>0


def test_helium_metastable_CE_uses_ne_squared_not_neutral_he():
    q=m.initial_state()
    rates=m.native_rates(m.temperature(q))
    vals,_=m.analytic_components(0,q)
    nh=m.v7.density(m.v7.A0)[0]
    ne=nh*(q[0]+m.Y*(q[1]+2*q[2]))
    predicted=ne**2*m.Y*q[1]*rates.ce[1]/(m.v7.hubble(m.v7.A0)*m.EV)
    assert vals[8]==pytest.approx(predicted,rel=3e-14)


def test_cmb_owner_signs_and_physical_recovery():
    q=m.initial_state()
    v,_=m.analytic_components(0,q)
    assert v[11]<0 # gas at 15000 K > TCMB ~ 57 K
    assert v[7]>10.0 # HI collisional excitation is the largest non-RR thermal term
    q2=m.initial_state(T0=50.)
    v2,_=m.analytic_components(0,q2)
    assert v2[11]>0


@pytest.mark.parametrize('mode',list(m.CLOCKS))
@pytest.mark.parametrize('steps',[8,32])
def test_positive_nuclei_and_conservative_energy(mode,steps):
    y0=np.zeros(21);y0[:4]=m.initial_state()
    y,res=m.integrate_clock(m.CLOCKS[mode],steps)
    check_energy(y,y0)
    assert res<3e-11
    assert np.all(y[4:15]>=0)
    assert y[20]>0 # adiabatic cooling work


def test_continuous_radau_reference_energy_and_tolerance():
    a=m.reference(rtol=2e-12);b=m.reference(rtol=2e-13)
    assert a.success and b.success
    assert abs(m.energy_ledger(a.y[:,-1],a.y[:,0]))<3e-12
    assert abs(m.temperature(a.y[:4,-1])-m.temperature(b.y[:4,-1]))<3e-8


def test_frozen_native_v10_no_radiation_be_parity():
    y,res=m.integrate_clock(m.CLOCKS['owner_like_be'],128)
    # Historical native printed endpoint, not a fabricated Rust call in this session.
    native_T=14988.7611352303
    assert abs(m.temperature(y[:4])-native_T)<2e-8


def test_full_midpoint_second_order_against_independent_continuous_radau():
    s=m.reference(rtol=2e-12);truth=m.temperature(s.y[:4,-1])
    errors=[]
    for n in [8,16,32,64]:
        y,_=m.integrate_clock(m.CLOCKS['all_mid'],n)
        errors.append(abs(m.temperature(y[:4])-truth))
    ratios=[a/b for a,b in zip(errors[:-1],errors[1:])]
    assert all(3.5<r<4.5 for r in ratios),ratios


def test_be_and_partial_clocks_first_order():
    s=m.reference(rtol=2e-12);truth=m.temperature(s.y[:4,-1])
    for name in ['owner_like_be','ce_mid','chemical_mid','thermal_mid']:
        errors=[abs(m.temperature(m.integrate_clock(m.CLOCKS[name],n)[0][:4])-truth)
                for n in [8,16,32]]
        assert all(1.6<a/b<2.5 for a,b in zip(errors[:-1],errors[1:])),(name,errors)


def test_ce_midpoint_is_dominant_measured_clock_at_native_density():
    s=m.reference(rtol=2e-12);truth=m.temperature(s.y[:4,-1])
    e_be=abs(m.temperature(m.integrate_clock(m.CLOCKS['owner_like_be'],16)[0][:4])-truth)
    e_ce=abs(m.temperature(m.integrate_clock(m.CLOCKS['ce_mid'],16)[0][:4])-truth)
    e_ci=abs(m.temperature(m.integrate_clock(m.CLOCKS['ci_mid'],16)[0][:4])-truth)
    assert e_ce<0.04*e_be
    assert e_ci>0.90*e_be


def test_partial_BE_cooling_signed_CMB_ledger():
    for mode in ('owner_like_be','all_mid'):
        y,_=m.integrate_clock(m.CLOCKS[mode],8)
        assert y[15]<0 # CMB energy leaves gas
        assert y[7]>0 and y[11]>0 # RR and CE channel events/cooling
        initial=np.zeros(21);initial[:4]=m.initial_state()
        assert abs(m.energy_ledger(y,initial))<2e-12


def test_fail_bad_clock_and_root_dimension():
    with pytest.raises(ValueError,match='CLOCK_PHASE_INVALID'):
        m.Clock(ce='backward_reverse')
    with pytest.raises(ValueError,match='NONPOSITIVE_STEP'):
        m.piecewise_advance(m.initial_state(),0.,0.,m.CLOCKS['all_mid'])
    with pytest.raises(ValueError,match='STEP_BUDGET'):
        m.integrate_clock(m.CLOCKS['all_mid'],0)
