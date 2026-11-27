"""Scoped photo-only numerical and physics tests; no native Case-A admission."""
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from he21_photo import (
    sigma_cm2, FIT_CUTS, cells, simpson, KBT_EV, Y_HE, SOURCE_N_PER_H,
    redshift_factor, neutral, electrons, binding, temperature, run,
)

def test_verner_source_thresholds():
    exact=np.array([6.34629636e-18,7.43469869e-18,1.58728026e-18])
    got=np.diag(sigma_cm2(FIT_CUTS))
    np.testing.assert_allclose(got,exact,rtol=2e-9)
    assert np.all(sigma_cm2(np.array([13.599,24.589,54.419]))[np.arange(3),np.arange(3)]==0.)
    with pytest.raises(ValueError):sigma_cm2(np.array([50001.]))


def test_original_spectral_moments_positive():
    for m in (4,8,16,64):
        cc=cells(m)
        assert len(cc)==3*m
        assert all(c[0]<=c[3]/c[2]<=c[1] and c[2]>0 for c in cc)
        avg=math.fsum(c[3] for c in cc)/math.fsum(c[2] for c in cc)
        assert abs(avg-20.2765954)<3e-7


def test_signed_kinematics_limits():
    for mu in (-1.,-.7,0.,.7,1.):
        assert redshift_factor(0.,mu,0.)==1.
        x=.002
        assert math.isclose(redshift_factor(x,mu,0.),math.exp(-x),rel_tol=3e-16)
        p=redshift_factor(x,mu,1e-3)
        expected=math.exp(-x)*(1-1e-3*x*(1-3*mu*mu))
        assert abs(p-expected)<1e-11
    with pytest.raises(ValueError):redshift_factor(-0.1,0.,0.)


def test_zero_photon_redshift_and_gas_work():
    result=run(4,4,0.,photons=False)
    assert result.source_count==0.
    assert result.absorbed==(0.,0.,0.)
    assert result.photon_final_ev==0.
    assert abs(result.number_defect)<1e-20
    assert abs(result.energy_defect)<1e-13
    assert result.gas_u_final_ev<result.initial_gas_u_ev


def test_photo_only_photon_energy_charge_and_support():
    for q in (-.005,0.,.005):
        v=run(4,8,q)
        assert abs(v.source_count-SOURCE_N_PER_H)<1e-18
        assert all(x>=0 for x in v.absorbed)
        assert v.absorbed[0]+v.absorbed[1]+v.absorbed[2]<=v.source_count
        assert v.max_support_crossing==0
        assert abs(v.number_defect)<2e-18
        assert abs(v.energy_defect)<2e-15
        assert abs(v.electron_defect)<2e-12
        assert v.work_photon_ev>=0 and v.work_gas_ev>=0
        assert v.heat_ev>0 and temperature(v.gas_final)>0
        assert v.max_newton_error<2.1e-13
        assert v.source_shape_energy_defect<1e-12


def test_both_ionizations_separate_he_binding():
    v=run(4,4,0.)
    x,y,z,u=v.gas_final
    assert 0<=x<=1 and 0<=y and 0<=z and y+z<=1
    assert y>0 and z>0
    # total gas binding delta is equal to summed physical photoevent thresholds
    from he21_photo import BIND_EV
    assert math.isclose(v.binding_delta_ev,sum(a*b for a,b in zip(v.absorbed,BIND_EV)),rel_tol=2e-9)


def test_no_absorbers_throws_no_photoevent():
    fully=(1.,0.,1.,None)
    r=run(4,4,0.,initial=fully)
    assert r.absorbed==(0.,0.,0.)
    assert r.heat_ev==0.
    assert r.photon_final_ev>0
    assert r.work_photon_ev>0
    assert abs(r.energy_defect)<1e-15


def test_split_vs_unsplit_negative_control():
    yes=run(4,8,0.,threshold_split=True)
    no=run(4,8,0.,threshold_split=False)
    assert yes.max_support_crossing==0
    assert no.max_support_crossing>0
    assert abs(yes.energy_defect)<1e-14
    assert abs(no.energy_defect)<1e-14


def test_convergent_spectral_photo_ionization():
    r4=run(4,8,0.)
    r8=run(8,8,0.)
    r16=run(16,8,0.)
    e4=abs(r4.absorbed[0]-r16.absorbed[0]);e8=abs(r8.absorbed[0]-r16.absorbed[0])
    assert e8 < e4
    assert e8 < 5e-12


def test_invalid_domain():
    with pytest.raises(ValueError):run(0,2)
    with pytest.raises(ValueError):run(2,0)
    with pytest.raises(ValueError):run(4,2,source_count=-1)
    with pytest.raises(ValueError):run(4,2,q=1.)
