"""Source-verifiable Verner fits and exact LRS angular-cut regressions."""
import hashlib
import math
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lrs_threshold_oracle import Ray
from verner_angular import (
    DONOR_PATH, Absorber, angular_verner, exact_angular_cutpoints,
    load_primary_fits, propagate_verner,
)

FITS=load_primary_fits()
ABSORBERS=tuple(Absorber(FITS[n], k) for n,k in
                (("HI",2.),("HeI",.7),("HeII",.3)))


def assert_ledger(r,tol=2e-10):
    assert r.photons_end >= 0
    assert 0 <= r.photons_end <= r.ray.photons0
    assert abs(r.photon_number_residual) <= tol*max(1.,r.ray.photons0)
    assert abs(r.energy_residual_ev) <= tol*max(1.,r.ray.photons0*r.ray.energy0_ev)
    assert r.redshift_work_ev >= 0
    for sp in ABSORBERS:
        name=sp.fit.symbol
        assert r.absorbed_counts[name] >= 0
        assert r.heat_ev[name] >= 0
        assert r.absorbed_energy_ev[name] >= r.heat_ev[name]


def test_primary_ascii_source_sha256_and_three_rows():
    data=DONOR_PATH.read_bytes()
    assert hashlib.sha256(data).hexdigest()=="a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389"
    assert len(data.splitlines())==185
    assert set(FITS)=={"HI","HeI","HeII"}
    assert (FITS["HI"].e0_ev,FITS["HeI"].y0,FITS["HeII"].sigma0_mb)==(.4298,.4434,13690.)


@pytest.mark.parametrize("name,threshold,threshold_mb,sigma100",[
    ("HI",13.6,6.346296358990503,0.019397922335679024),
    ("HeI",24.59,7.434698694110650,0.3938344374091019),
    ("HeII",54.42,1.5872802575386487,0.29608104987072614)
])
def test_wolfram_independent_verner_formula(name,threshold,threshold_mb,sigma100):
    f=FITS[name]
    assert f.threshold_ev==threshold
    assert math.isclose(f.threshold_sigma_mb,threshold_mb,rel_tol=2e-14)
    assert math.isclose(f.sigma_mb(100.),sigma100,rel_tol=2e-14)
    assert f.sigma_mb(threshold-1e-4)==0.


@pytest.mark.parametrize("s",[-.07,0.,.07])
@pytest.mark.parametrize("mu",[-.9,-.3,0.,.4,1.])
def test_full_atomic_rate_positive_h_he_ledger(s,mu):
    r=propagate_verner(Ray(100.,mu,1.,s),ABSORBERS,.75)
    assert_ledger(r)


def test_heii_threshold_cut_exactly_satisfies_energy_event():
    cuts=exact_angular_cutpoints(100.,.03,.61,[sp.fit.threshold_ev for sp in ABSORBERS])
    assert len(cuts)==4
    assert math.isclose(cuts[1],-cuts[2],rel_tol=1e-15)
    for mu in cuts[1:-1]:
        ray=Ray(100.,mu,1.,.03)
        assert abs(ray.geometry(.61)[0]-FITS["HeII"].threshold_ev)<1e-12


def test_no_artificial_cut_in_flrw_or_no_crossing():
    cuts=exact_angular_cutpoints(100.,0.,.61,[f.threshold_ev for f in FITS.values()])
    assert cuts==(-1.,1.)
    no=exact_angular_cutpoints(100.,.03,.3,[f.threshold_ev for f in FITS.values()])
    assert no==(-1.,1.)


def test_fixed_flrw_has_zero_anisotropic_pressure_and_number_balance():
    m=angular_verner(100.,0.,ABSORBERS,.7,rel_tol=1e-6)
    assert abs(m.pi_over_u)<2e-13
    assert abs(m.surviving+sum(m.absorbed.values())-1.)<2e-10
    assert len(m.boundaries)==2


def test_threshold_piecewise_adaptive_converges_without_deferred_gates():
    m=angular_verner(100.,.03,ABSORBERS,.61,rel_tol=1e-6,abs_tol=5e-10)
    assert len(m.boundaries)==4
    assert m.accepted_panels>=3
    assert m.evaluated_rays >= 3*24
    assert 0 < m.surviving < 1
    assert m.absorbed["HeII"]>0


def test_unphysical_donor_range_and_background_rejected():
    with pytest.raises(ValueError,match="Emax"):
        FITS["HI"].sigma_mb(100000.)
    with pytest.raises(ValueError,match="Emax"):
        propagate_verner(Ray(60000.,0.,1.,0.),ABSORBERS,.1)
    with pytest.raises(ValueError,match="positive"):
        propagate_verner(Ray(100.,0.,1.,0.),ABSORBERS,.1,
                         hubble_ratio=lambda x: -1.)
    with pytest.raises(ValueError,match="duplicate"):
        propagate_verner(Ray(100.,0.,1.,0.),[ABSORBERS[0],ABSORBERS[0]],.1)
