"""Independent stiff ODE and physical limits for H/He ionization/recombination heat.

Scientific status: conditional benchmark, not full native EoR/Case-B provider.
"""
from __future__ import annotations
import sys
from pathlib import Path
from math import fsum, isclose
import numpy as np
import pytest
from scipy.integrate import solve_ivp

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lrs_threshold_oracle import Ray, GAUSS8
from dynamic_chemistry import Gas,CHANNELS,TARGET,PRODUCT,threshold_events
from recomb_thermal import (
    PhotoRecombRates,K_B_EV_PER_K,chemical_energy,particle_count,
    gas_temperature,evolve_thermal)
from verner_angular import load_primary_fits

FITS=load_primary_fits()
GAS=Gas(.37,.03,.085,.012,.003)
RATE=PhotoRecombRates(2.0,(.32,.15,.12),10000.0,(.7,.7,.7))


def rays(s=.03):
    return tuple(Ray(e,mu,.5*w*num,s) for e,num in
        ((110.,.12),(72.,.08),(43.,.06)) for mu,w in GAUSS8)


def independent_continuous(ray_set, gas, end, T0, settings=RATE):
    """Continuous ODE independently assembled; no split map or ledger closure."""
    n=len(ray_set)
    idx_u=n+5;idx_wp=n+6;idx_wg=n+7;idx_escape=n+8
    idx_ap=n+9;idx_ar=n+12
    y=np.zeros(n+15)
    y[:n]=[r.photons0 for r in ray_set]
    y[n:n+5]=gas.as_tuple()
    y[idx_u]=1.5*K_B_EV_PER_K*T0*particle_count(gas.as_tuple())
    thresholds=np.array([FITS[c].threshold_ev for c in CHANNELS])
    def rhs(x,z):
        photons=z[:n]
        stocks=z[n:n+5]
        thermal=z[idx_u]
        # Reference rates directly evaluate donor cross section and proper n=e^-3X.
        e=np.array([r.geometry(x)[0] for r in ray_set])
        cross=np.array([[FITS[c].sigma_mb(float(v)) for c in CHANNELS] for v in e])
        p=settings.photo_per_mb*np.exp(-3*x)*cross*photons[:,None]*stocks[np.array(TARGET)][None,:]
        pchan=p.sum(axis=0)
        electrons=stocks[1]+stocks[3]+2*stocks[4]
        temperature=thermal/(1.5*K_B_EV_PER_K*(sum(stocks)+electrons))
        rates=(np.array(settings.recomb_at_tref)*np.exp(-3*x)
               *(temperature/settings.temperature_ref_K)**(-np.array(settings.temperature_power)))
        rec=rates*stocks[np.array(PRODUCT)]*electrons
        out=np.zeros_like(z)
        out[:n]=-p.sum(axis=1)
        for j in range(3):
            out[n+TARGET[j]]+=-pchan[j]+rec[j]
            out[n+PRODUCT[j]]+=pchan[j]-rec[j]
        out[idx_u]=(-2*thermal+float(np.sum(p*(e[:,None]-thresholds[None,:])))
                    -float(np.sum(rec))*1.5*K_B_EV_PER_K*temperature)
        out[idx_wp]=sum(float(ph*r.geometry(x)[0]*r.drift_positive(x)) for ph,r in zip(photons,ray_set))
        out[idx_wg]=2*thermal
        out[idx_escape]=float(np.dot(rec,thresholds)+sum(rec)*1.5*K_B_EV_PER_K*temperature)
        out[idx_ap:idx_ap+3]=pchan
        out[idx_ar:idx_ar+3]=rec
        return out
    events=threshold_events(ray_set,FITS,end)
    for a,b in zip(events[:-1],events[1:]):
        sol=solve_ivp(rhs,(a,b),y,method='Radau',rtol=3e-11,atol=4e-13,
                      max_step=.025)
        assert sol.success,sol.message
        y=sol.y[:,-1]
    return y


def check(r,tol=4e-11):
    scale=max(1.,r.initial_photon_energy_ev+r.initial_thermal_ev+r.initial_chemical_ev)
    assert abs(r.photon_reaction_residual)<tol
    assert abs(r.electron_reaction_residual)<tol
    assert abs(r.hydrogen_residual)<tol
    assert abs(r.helium_residual)<tol
    assert abs(r.energy_residual_ev)<tol*scale
    assert all(v>=-1e-14 for v in r.final.as_tuple())
    assert all(v>=-1e-14 for v in r.photons_final)
    assert r.final_temperature_K>0
    assert r.final_thermal_ev>0
    assert r.escaped_recomb_energy_ev>=0
    assert r.photo_redshift_work_ev>=0
    assert r.gas_adiabatic_work_ev>=0
    assert all(v>=-1e-14 for v in r.photo_events+r.recomb_events)


def state_array(r):
    return np.array([*r.photons_final,*r.final.as_tuple(),r.final_thermal_ev,
                     r.photo_redshift_work_ev,r.gas_adiabatic_work_ev,
                     r.escaped_recomb_energy_ev,*r.photo_events,*r.recomb_events])


def test_thermal_temperature_inverse_and_electron_census():
    g=GAS.as_tuple()
    U=1.5*K_B_EV_PER_K*8000*particle_count(g)
    assert isclose(gas_temperature(U,g),8000,rel_tol=1e-15)
    assert particle_count(g)==pytest.approx(GAS.hydrogen+GAS.helium+GAS.electrons)
    assert chemical_energy(g,(13.6,24.59,54.42))>0


def test_recomb_only_counts_energy_and_temp_stability():
    rr=rays(0.0)
    zero_photons=tuple(Ray(ray.energy0_ev,ray.mu0,0.,0.) for ray in rr)
    st=PhotoRecombRates(photo_per_mb=0.,recomb_at_tref=(.7,.4,.3))
    r=evolve_thermal(zero_photons,GAS,.3,rates=st,max_step=.015)
    check(r)
    assert all(x==0 for x in r.photo_events)
    assert sum(r.recomb_events)>0
    assert r.final.electrons<GAS.electrons
    assert r.final_temperature_K < 8000  # adiabatic cooling; recombination alone preserves T


def test_no_photo_no_recomb_adiabatic_exact():
    rate=PhotoRecombRates(0.,(0.,0.,0.))
    r=evolve_thermal(rays(.04),GAS,.4,rates=rate,max_step=.08)
    check(r)
    assert r.final==GAS
    assert r.photons_final==r.photons_initial
    assert r.final_temperature_K==pytest.approx(8000*np.exp(-.8),rel=2e-14)
    assert r.final_thermal_ev==pytest.approx(r.initial_thermal_ev*np.exp(-.8),rel=2e-14)
    assert r.escaped_recomb_energy_ev==0


@pytest.mark.parametrize('s',[-.04,0.,.04])
@pytest.mark.parametrize('dt',[.08,.03,.008])
def test_positive_conservative(s,dt):
    r=evolve_thermal(rays(s),GAS,.65,rates=RATE,max_step=dt)
    check(r)
    assert r.final.electrons>0
    assert sum(r.photo_events)>0
    assert sum(r.recomb_events)>0


def test_flrw_angular_isotropy_with_recomb():
    r=evolve_thermal(rays(0.),GAS,.65,max_step=.025)
    check(r)
    E=[ray.geometry(.65)[0] for ray in rays(0.)]
    mu=[ray.geometry(.65)[1] for ray in rays(0.)]
    u=fsum(n*e for n,e in zip(r.photons_final,E))
    p=fsum(n*e*v*v for n,e,v in zip(r.photons_final,E,mu))
    assert abs((3*p-u)/(2*u))<3e-14


def test_independent_radau_and_second_order_refinement():
    rr=rays(.03)
    ref=independent_continuous(rr,GAS,.65,8000.,RATE)
    errors=[]
    for dt in (.08,.04,.02,.01):
        sol=evolve_thermal(rr,GAS,.65,max_step=dt,rates=RATE)
        check(sol)
        diff=abs(state_array(sol)-ref)
        errors.append(float(diff.max()))
    assert errors[0]>errors[1]>errors[2]>errors[3],errors
    assert errors[-1]<2e-4,errors
    assert errors[1]/errors[2]>2.0,errors
    assert errors[2]/errors[3]>2.0,errors


def test_extreme_absorption_positive_no_untracked_energy():
    p=PhotoRecombRates(150.,(3.,2.,1.))
    r=evolve_thermal(rays(.03),GAS,.5,rates=p,max_step=.004)
    check(r)


def test_recomb_excess_energy_sink_and_chemical_storage():
    r=evolve_thermal(rays(.05),GAS,.65,max_step=.0125)
    check(r)
    # Cumulative emitted-recombination energy must include binding release
    # as well as the thermal-electron energy removed from the gas.
    bound=sum(a*f for a,f in zip(r.recomb_events,(FITS[c].threshold_ev for c in CHANNELS)))
    assert r.escaped_recomb_energy_ev > bound
    assert r.final_chemical_ev != r.initial_chemical_ev


def test_mirrored_bianchi_rays():
    rr=rays(-.03)
    r=evolve_thermal(rr,GAS,.65,max_step=.05)
    for block in range(3):
        for i in range(4):
            assert r.photons_final[block*8+i]==pytest.approx(r.photons_final[block*8+7-i],abs=2e-16)


def test_domain_and_budget():
    with pytest.raises(ValueError,match='temperature'):
        evolve_thermal(rays(),GAS,.3,temperature_initial_K=-1)
    with pytest.raises(ValueError,match='timestep'):
        evolve_thermal(rays(),GAS,.6,max_step=.001,max_steps=4)
    with pytest.raises(ValueError,match='nonnegative'):
        PhotoRecombRates(-1.,(.1,.1,.1))
