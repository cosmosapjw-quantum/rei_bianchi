"""HE22 local interface verification; uses constructed owner, NOT native Grackle."""
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from he21_photo import BIND_EV, Y_HE, binding, electrons, EV_ERG, temperature
from he22_contract import photomap,solve_midpoint,PhotoOnlyTestDouble,NativePoint,evaluate


def gas():
    x,y,z=1e-5,1e-5,1e-8
    n=x+Y_HE*(y+2*z)
    u=1.5*1.380649e-16*8.098143045064857*(1+Y_HE+n)/EV_ERG
    return np.array([x,y,z,u],dtype=float)


def input_photons():
    # Distinct physical photo-binding thresholds versus Verner support cutoffs.
    return np.array([13.60,24.59,54.42,76.4]), np.array([1.9e-6,0.6e-6,0.2e-6,0.1e-6])


def test_photo_map_positive_and_competing_species():
    energies,n=input_photons()
    m=photomap(gas(),n,energies,0.00175757,1e10)
    assert np.all(m.events_per_H>=0) and np.all(m.heat_per_H>=0)
    assert np.all(m.new_counts>=0)
    assert abs(m.photon_number_residual)<1e-20
    assert abs(m.photon_energy_residual_eV_per_H)<1e-18
    assert m.events_per_H[0]>0 and m.events_per_H[1]>0 and m.events_per_H[2]>0
    assert m.gamma_s.shape==(3,) and m.heat_erg_per_absorber_s.shape==(3,)


def test_case_a_mock_energy_charge_implicit():
    g0=gas();E,N=input_photons();nh=0.00175757
    step=solve_midpoint(g0,N,E,nh,1e10,PhotoOnlyTestDouble(nh))
    assert step.scaled_implicit_residual<3e-12
    assert all(step.gas[:3]>=0)
    assert abs(step.photons_number_residual)<1e-19
    assert abs(step.photons_energy_residual)<1e-17
    assert abs(step.total_energy_residual_ev_per_H)<1e-14
    assert np.min(step.photons)>=0
    expected=float(step.events_per_H.sum())
    assert abs(electrons(step.gas)-electrons(g0)-expected)<1e-11
    assert abs(binding(step.gas)-binding(g0)-np.dot(step.events_per_H,BIND_EV))<1e-10
    assert temperature(step.gas)>temperature(g0)


def test_zero_photon_native_rates_zero():
    g0=gas();nh=.00175757
    z=solve_midpoint(g0,np.zeros(2),np.array([19.,79.]),nh,1e10,PhotoOnlyTestDouble(nh))
    assert np.array_equal(z.gas,g0)
    assert np.all(z.events_per_H==0)
    assert z.total_energy_residual_ev_per_H==0


def test_fully_ionized_has_no_photoevents():
    g=gas();g[:3]=[1.,0.,1.]
    e,n=input_photons();p=photomap(g,n,e,0.00175757,1e10)
    assert np.all(p.events_per_H==0)
    assert np.array_equal(p.new_counts,n)


def test_external_native_wrong_photo_event_is_refused():
    g=gas();e,n=input_photons();nh=0.00175757
    def corrupted(gv, gamma,power):
        good=PhotoOnlyTestDouble(nh)(gv,gamma,power)
        return NativePoint(good.fraction_dt,good.w_dt_ev_per_h_s,good.temperature_K,
                           good.photo_events_cm3_s+1e-10,good.thermal_micro_erg_cm3_s,
                           good.binding_micro_erg_cm3_s,good.escape_erg_cm3_s,
                           good.cmb_to_gas_erg_cm3_s,good.photo_input_erg_cm3_s)
    with pytest.raises(AssertionError,match='EVENT_OWNER'):
        evaluate(g,g,n,e,nh,1e10,corrupted)


def test_external_native_wrong_energy_balance_is_refused():
    g=gas();e,n=input_photons();nh=.00175757
    def corrupted(gv,gamma,power):
        good=PhotoOnlyTestDouble(nh)(gv,gamma,power)
        return NativePoint(good.fraction_dt,good.w_dt_ev_per_h_s,good.temperature_K,
                           good.photo_events_cm3_s,good.thermal_micro_erg_cm3_s,
                           good.binding_micro_erg_cm3_s,good.escape_erg_cm3_s+1e-8,
                           good.cmb_to_gas_erg_cm3_s,good.photo_input_erg_cm3_s)
    with pytest.raises(AssertionError,match='MICRO_ENERGY'):
        evaluate(g,g,n,e,nh,1e10,corrupted)


def test_invalid_gamma_inputs_fail():
    g=gas();e,n=input_photons()
    with pytest.raises(ValueError):photomap(g,n,e,0.,1e10)
    with pytest.raises(ValueError):photomap(g,-n,e,.00175757,1e10)
    with pytest.raises(ValueError):photomap(g,n,e,.00175757,-1.)
    with pytest.raises(ValueError):photomap(g,n,np.array([12.,24.,30.]),.00175757,1e10)


def test_energy_moment_not_same_as_cutoff_support():
    e,n=input_photons();g=gas()
    # Cross section at exact Verner cutoff may be nonzero, while physical
    # binding threshold remains distinct (photoelectron retains E-I).
    p=photomap(g,n,e,.00175757,1e10)
    assert e[0]>BIND_EV[0] and e[1]>BIND_EV[1] and e[2]>BIND_EV[2]
    assert p.heat_per_H.sum()>0


def test_manufactured_casea_rr_escape_energy_conservation():
    from he22_contract import ConstructedCaseAEscapeTestDouble
    g0=gas();e,n=input_photons();nh=.00175757
    s=solve_midpoint(g0,n,e,nh,1e10,ConstructedCaseAEscapeTestDouble(nh))
    assert s.escaped_ev_per_H>0
    assert abs(s.total_energy_residual_ev_per_H)<1e-12
    assert abs(s.photons_number_residual)<1e-17
    # Photo photons remain separate from recombination escaped radiation.
    assert float(s.events_per_H.sum())>0
