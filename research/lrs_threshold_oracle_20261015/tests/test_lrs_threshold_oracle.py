"""Physics and analytic controls for a conditional LRS Bianchi I reference."""
import math
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lrs_threshold_oracle import GAUSS8, Ray, Species, propagate, angular_moments

HI=Species("HI",13.5984,2.)
HEI=Species("HeI",24.5874,.7)
HEII=Species("HeII",54.4178,.3)

def check(r,tol=4e-11):
    scale=max(1.,r.ray.photons0*r.ray.energy0_ev)
    assert abs(r.photon_number_residual)<tol*max(1.,r.ray.photons0)
    assert abs(r.energy_residual_ev)<tol*scale
    assert r.photons_end>=0 and r.redshift_work_ev>=0
    assert all(x>=0 for x in r.absorbed_counts.values())
    assert all(x>=0 for x in r.heat_ev.values())
    assert all(r.absorbed_energy_ev[k]>=r.heat_ev[k] for k in r.heat_ev)

def test_exact_null_characteristic_finite_difference():
    r=Ray(100,.47,1,.03)
    x,h=.3,1.e-4
    fd=(math.log(r.geometry(x+h)[0])-math.log(r.geometry(x-h)[0]))/(2*h)
    assert abs(fd+r.drift_positive(x))<2e-11
    mu=r.geometry(x)[1]
    mudot=(r.geometry(x+h)[1]-r.geometry(x-h)[1])/(2*h)
    assert abs(mudot+3*r.s_over_h*mu*(1-mu*mu))<2e-11

def test_vacuum_count_energy_work():
    ray=Ray(80.,.41,3.,.07)
    r=propagate(ray,[],1.2)
    assert r.photons_end==ray.photons0
    assert abs(r.redshift_work_ev-ray.photons0*(ray.energy0_ev-r.energy_end_ev))<3e-12
    check(r)

def test_flrw_closed_form_count_heating_and_work():
    ray=Ray(15.,.37,2.1,0.)
    sp=Species("HI",10.,.9)
    L=.2
    r=propagate(ray,[sp],L)
    eta=.9*(10./15.)**3
    absorption=ray.photons0*(-math.expm1(-eta*L))
    qabs=(ray.photons0*eta*ray.energy0_ev*(-math.expm1(-(eta+1)*L))/(eta+1))
    w=(ray.photons0*ray.energy0_ev*(-math.expm1(-(eta+1)*L))/(eta+1))
    assert math.isclose(r.absorbed_counts["HI"],absorption,rel_tol=3e-13)
    assert math.isclose(r.absorbed_energy_ev["HI"],qabs,rel_tol=4e-12)
    assert math.isclose(r.redshift_work_ev,w,rel_tol=4e-12)
    check(r)

def test_three_threshold_events_are_exactly_split():
    ray=Ray(80.,-.8,1.5,0.)
    r=propagate(ray,[HI,HEI,HEII],2.0)
    for sp in (HI,HEI,HEII):
        assert math.isclose(r.threshold_events[sp.name],math.log(80./sp.threshold_ev),rel_tol=5e-14)
        assert r.absorbed_counts[sp.name]>0.
    check(r)

@pytest.mark.parametrize("s_over_h",[-.08,-.03,0.,.03,.08])
@pytest.mark.parametrize("mu0",[-.91,-.15,0.,.3,1.])
def test_signed_shear_competing_h_he_absorption(s_over_h,mu0):
    r=propagate(Ray(100.,mu0,4.,s_over_h),[HI,HEI,HEII],.8)
    check(r)

def test_inactive_channels_do_not_steal_photons():
    ray=Ray(18.,.7,2.,.03)
    r=propagate(ray,[HEI,HEII],.6)
    assert r.photons_end==ray.photons0
    assert r.absorbed_counts=={"HeI":0.,"HeII":0.}
    check(r)

def test_hubble_ratio_changes_attenuation_as_expected():
    ray=Ray(95,.2,1.,0.)
    r=propagate(ray,[HI],.7,hubble_ratio=lambda x:2.)
    eta=HI.opacity_at_threshold*(HI.threshold_ev/ray.energy0_ev)**3
    assert math.isclose(r.photons_end,math.exp(-eta*.7/2.),rel_tol=4e-13)
    check(r)

def test_flrw_pressure_is_isotropic():
    results=[propagate(Ray(90.,mu,.5*w,0.),[],.3) for mu,w in GAUSS8]
    p=angular_moments(results)
    assert abs(p.pi_ev/p.energy_ev)<2e-15
    assert math.isclose(p.p_parallel_ev+2*p.p_transverse_ev,p.energy_ev,rel_tol=2e-15)

def test_collisionless_linear_response_pi_over_u_minus_eight_fifths():
    def stress_ratio(s):
        results=(propagate(Ray(100.,mu,.5*w,s),[],.4) for mu,w in GAUSS8)
        m=angular_moments(results)
        return m.pi_ev/m.energy_ev
    eps=1e-4
    slope=(stress_ratio(eps)-stress_ratio(-eps))/(2*eps)
    assert abs(slope-(-8./5.*.4))<3e-8

def test_stiff_optical_depth_is_substepped_and_positive():
    r=propagate(Ray(100.,.4,1.,.01),[Species("HI",20.,5000.)],.5,max_substeps=5000)
    assert r.substeps>1
    check(r)

def test_input_domains():
    with pytest.raises(ValueError,match="monotone-redshift"):
        Ray(20,.1,1,-.6)
    with pytest.raises(ValueError,match="unique"):
        propagate(Ray(80,0,1,0),[HI,HI],.2)
    with pytest.raises(ValueError,match="positive"):
        propagate(Ray(80,0,1,0),[HI],.2,hubble_ratio=lambda x:-1.)
