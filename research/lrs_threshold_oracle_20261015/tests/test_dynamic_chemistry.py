"""Source-free photoionization/energy benchmarks against independent Radau ODE."""
import math
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import solve_ivp
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dynamic_chemistry import (Gas,evolve,pair_exact,threshold_events,TARGET,PRODUCT,CHANNELS)
from lrs_threshold_oracle import GAUSS8,Ray
from verner_angular import load_primary_fits
FITS=load_primary_fits()
GAS=Gas(.37,.03,.085,.012,.003)

def rays(s=.03):
    return tuple(Ray(e,mu,.5*w*num,s) for e,num in ((110.,.12),(72.,.08),(43.,.06)) for mu,w in GAUSS8)

def check(r,tol=6e-12):
    assert abs(r.photon_electron_residual)<tol
    assert abs(r.energy_residual_ev)<tol*max(1.,r.photon_energy_initial_ev)
    assert abs(r.hydrogen_residual)<tol
    assert abs(r.helium_residual)<tol
    assert all(x>=0 for x in r.photon_final)
    assert all(x>=0 for x in r.final.as_tuple())
    assert all(x>=0 for x in r.absorbed.values())
    assert r.binding_ev>=0 and r.heat_ev>=0 and r.expansion_work_ev>=0
    assert math.isclose(sum(r.absorbed.values()),r.final.electrons-r.initial.electrons,rel_tol=2e-12,abs_tol=tol)

def independent_ivp(ray_set,initial,end,rate):
    n=len(ray_set)
    y0=np.zeros(n+8)
    y0[:n]=[ray.photons0 for ray in ray_set]
    y0[n:n+5]=initial.as_tuple()
    thresholds=np.array([FITS[name].threshold_ev for name in CHANNELS])
    def rhs(x,y):
        photons=y[:n]
        stocks=y[n:n+5]
        energy=np.array([ray.geometry(x)[0] for ray in ray_set])
        sigma=np.array([[FITS[name].sigma_mb(float(e)) for name in CHANNELS] for e in energy])
        rates=rate*np.exp(-3*x)*sigma*stocks[np.array(TARGET)][None,:]*photons[:,None]
        sums=np.sum(rates,axis=0)
        out=np.zeros_like(y)
        out[:n]=-np.sum(rates,axis=1)
        for j in range(3):
            out[n+TARGET[j]]-=sums[j]
            out[n+PRODUCT[j]]+=sums[j]
        out[n+5]=float(np.dot(sums,thresholds))
        out[n+6]=float(np.sum(rates*np.maximum(energy[:,None]-thresholds[None,:],0.)))
        out[n+7]=sum(float(ph*ray.geometry(x)[0]*ray.drift_positive(x)) for ph,ray in zip(photons,ray_set))
        return out
    y=y0.copy()
    for a,b in zip(threshold_events(ray_set,FITS,end)[:-1],threshold_events(ray_set,FITS,end)[1:]):
        sol=solve_ivp(rhs,(a,b),y,method='Radau',rtol=2e-11,atol=2e-13)
        assert sol.success,sol.message
        y=sol.y[:,-1]
    return y

def test_exact_pair_scalar_logistic():
    assert pair_exact(0,1,10)==0
    assert pair_exact(4,0,10)==0
    for n,m,h in ((.5,.7,.03),(.2,.2,1.3),(.1,.4,1000.),(1e-5,.3,.001),(.3,.30000000000005,.4)):
        a=pair_exact(n,m,h)
        assert 0<=a<=min(n,m)
        d=abs(n-m);B=min(n,m)
        expected=B/(1+B*h) if d==0 else B*d*math.exp(-d*h)/(d+B*(-math.expm1(-d*h)))
        assert math.isclose(B-a,expected,rel_tol=1e-9,abs_tol=2e-14)

def test_identity_zero_rate_vacuum_energy():
    r=evolve(rays(),GAS,.65,rate_per_mb=0,step_max=.1)
    assert r.final==GAS
    assert r.photon_final==r.photon_initial
    assert abs(r.expansion_work_ev-(r.photon_energy_initial_ev-r.photon_energy_final_ev))<3e-13
    check(r)

@pytest.mark.parametrize('s',[-.05,0,.05])
@pytest.mark.parametrize('step',[.1,.04,.02])
def test_evolving_nuclei_and_electron_ledgers(s,step):
    r=evolve(rays(s),GAS,.65,rate_per_mb=2.,step_max=step)
    check(r)
    assert r.final.HI<GAS.HI
    assert r.final.HeIII>GAS.HeIII
    assert r.final.electrons>GAS.electrons
    assert all(x>0 for x in r.absorbed.values())

def test_independent_continuous_radau_agreement():
    y=independent_ivp(rays(),GAS,.65,2.)
    r=evolve(rays(),GAS,.65,rate_per_mb=2.,step_max=.00625)
    vector=np.array([*r.photon_final,*r.final.as_tuple(),r.binding_ev,r.heat_ev,r.expansion_work_ev])
    assert np.max(abs(vector-y))<1e-5
    check(r)

def test_strang_second_order_refinement():
    y=independent_ivp(rays(),GAS,.65,2.)
    errors=[]
    for step in (.08,.04,.02):
        r=evolve(rays(),GAS,.65,rate_per_mb=2.,step_max=step)
        vec=np.array([*r.photon_final,*r.final.as_tuple(),r.binding_ev,r.heat_ev,r.expansion_work_ev])
        errors.append(float(np.max(abs(vec-y))))
    assert errors[0]>errors[1]>errors[2],errors
    assert errors[0]/errors[1]>2.3,errors
    assert errors[1]/errors[2]>2.3,errors

def test_stiff_species_limited():
    r=evolve(rays(.02),Gas(.3,0,.09,0,0),.5,rate_per_mb=200.,step_max=.01)
    check(r)
    assert r.final.electrons<=sum(r.photon_initial)+1e-10

def test_transparent_all_ionized():
    g=Gas(0.,1.,0.,0.,.2)
    r=evolve(rays(0.),g,.3,rate_per_mb=100)
    assert r.final==g and r.photon_final==r.photon_initial
    check(r)

def test_invalid_input():
    with pytest.raises(ValueError,match='share'):
        evolve((Ray(90,.1,1,.03),Ray(90,.1,1,-.03)),GAS,.2)
    with pytest.raises(ValueError,match='nonnegative'):
        evolve(rays(),GAS,.2,rate_per_mb=-1)
    with pytest.raises(ValueError,match='budget'):
        evolve(rays(),GAS,.7,step_max=.001,step_budget=10)

@pytest.mark.parametrize('step',[.08,.02,.005])
def test_flrw_isotropy_exact_at_all_step_sizes(step):
    rr=rays(0.)
    r=evolve(rr,GAS,.65,rate_per_mb=2.,step_max=step)
    uv=sum(N*ray.geometry(.65)[0] for N,ray in zip(r.photon_final,rr))
    pv=sum(N*ray.geometry(.65)[0]*ray.geometry(.65)[1]**2
           for N,ray in zip(r.photon_final,rr))
    assert abs((3*pv-uv)/(2*uv))<2e-14

@pytest.mark.parametrize('s',[-.04,.04])
def test_lrs_reflection_symmetry_stays_exact(s):
    rr=rays(s)
    r=evolve(rr,GAS,.65,rate_per_mb=2.,step_max=.04)
    for block in range(3):
        start=block*8
        for j in range(4):
            assert r.photon_final[start+j]==pytest.approx(
                r.photon_final[start+7-j],abs=2e-16,rel=1e-13)
