"""BASS source-conditioned massless and massive quadrupole REI research tests.

The production R3c source is untouched; this tests the independent
collisionless momentum hierarchy extension to the source Einstein IVP.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
import pytest

from bass_hierarchy_transport import (
    BASSQuadrupoleTransport,bass_hierarchy_scalar_shear_coefficient,
    check_initial_quadrupole,
)
from sigma_pi_coupled import SigmaPiScenario,historical_axis_ratio_to_sigma

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SCENARIO=ROOT/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json"
DONOR=HERE/"REI_DONOR_CANDIDATE_OPTIN_ONLY.json"
SHA="07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"


@pytest.fixture(scope="module")
def model():
    assert hashlib.sha256(SCENARIO.read_bytes()).hexdigest()==SHA
    return SigmaPiScenario.from_locked_json(SCENARIO,
                         gas_case="donor",donor_path=DONOR)


def test_angular_seed_positive_normalized_and_distinct_from_shear(model):
    for ar,am in [(0,0),(.2,.4),(-.2,.1),(-1.,2.),(2.,-1.)]:
        d=BASSQuadrupoleTransport(model,sigma_ref=0,orientation=0,
                        source_rad_amplitude=ar,source_matter_amplitude=am)
        er,pi,_,(par,perp)=d.moments(0,0)
        u,pim,pbar=d.matter(0,0)
        assert er==model.radiation_energy_ref
        assert pi/er==pytest.approx(ar/5,abs=2e-16)
        assert (par+2*perp-er)/er==pytest.approx(0,abs=2e-15)
        assert pim/model.gas_pressure_ref==pytest.approx(3*am/5,abs=5e-16)
        assert u==pytest.approx(1.5*model.gas_pressure_ref,rel=5e-16)
        assert d.inspect(0,0,0).Sigma==0
        assert d.source_identity()["BASS_massive_J2_pi"].startswith("pi_ab")
    for ar in (-1.1,2.01,float("nan")):
        with pytest.raises(ValueError):
            check_initial_quadrupole(ar)


def test_stf_source_pi_normalization_bass_I2(model):
    d=BASSQuadrupoleTransport(model,sigma_ref=0,orientation=0,
                    source_rad_amplitude=.2,source_matter_amplitude=.3)
    for eta,b in [(.0,.0),(.2,.04),(.9,-.028)]:
        er,pi,_,_ = d.moments(eta,b)
        m,pim,pbar=d.matter(eta,b)
        pi_tensor=np.diag([-pi/3,-pi/3,2*pi/3])
        assert abs(np.trace(pi_tensor))<1e-15*max(abs(pi),1e-40)
        assert 1.5*pi_tensor[2,2]==pytest.approx(pi,rel=1e-14)
        assert abs(pi)<1.5*er
        assert m>0 and pbar>0


def test_source_l2_hierarchy_massless_and_massive_limits():
    assert bass_hierarchy_scalar_shear_coefficient(1.,1.)==pytest.approx(-8/15)
    for p in (.01,.5,10.):
        assert bass_hierarchy_scalar_shear_coefficient(3*p,0.)==pytest.approx(-2*p)
    for invalid in ((-1.,1.),(1.,-1.),(float("nan"),1.)):
        with pytest.raises(ValueError):
            bass_hierarchy_scalar_shear_coefficient(*invalid)


@pytest.mark.parametrize("ar,am",[(0,0),(.2,0),(0,.5),(-.2,.5)])
def test_exact_particle_energy_conservation_both_sectors(model,ar,am):
    d=BASSQuadrupoleTransport(model,sigma_ref=0,orientation=0,
                     source_rad_amplitude=ar,source_matter_amplitude=am)
    for eta,b in [(.05,.015),(.3,-.027),(.9,.004)]:
        h=1e-5
        er,pi,_,_=d.moments(eta,b)
        u,pim,_=d.matter(eta,b)
        dr=(d.moments(eta,b+h)[0]-d.moments(eta,b-h)[0])/(2*h)
        dm=(d.matter(eta,b+h)[0]-d.matter(eta,b-h)[0])/(2*h)
        assert abs(dr+2*pi)<2e-8*er
        assert abs(dm+2*pim)<2e-8*u


@pytest.mark.parametrize("ar,am",[(0,0),(.2,0),(-.2,.4)])
def test_bass_reduced_rank2_matches_exact_first_order_for_small_b(model,ar,am):
    d=BASSQuadrupoleTransport(model,sigma_ref=0,orientation=0,
                     source_rad_amplitude=ar,source_matter_amplitude=am)
    for b in (-.0001,.0001):
        exact_r=d.moments(0,b)[1]
        exact_m=d.matter(0,b)[1]
        approx_r,approx_m=d.hierarchy_linearized_pi(0,b)
        assert abs(exact_r-approx_r)<3e-4*model.radiation_energy_ref
        assert abs(exact_m-approx_m)<3e-4*model.gas_pressure_ref
    a,b=d.hierarchy_linearized_pi(0,0)
    assert a==pytest.approx(ar/5*model.radiation_energy_ref,abs=1e-27)
    assert b==pytest.approx(3*am/5*model.gas_pressure_ref,abs=1e-27)


def test_zero_geometry_with_rad_quadrupole_generates_real_shear(model):
    d=BASSQuadrupoleTransport(model,sigma_ref=0.,orientation=0,
                     source_rad_amplitude=.2,source_matter_amplitude=0.)
    sol=d.evolution(rtol=2e-11,atol=1e-14)
    end=d.inspect(sol.t[-1],*sol.y[:2,-1])
    assert sol.success
    assert end.orientation==1
    assert end.Sigma>0
    # Independent native BASS PR159 exact source experiment same
    # h=.674, omega_b=.0224, Omega_r=.000092 and positive seed A=.2.
    assert end.b==pytest.approx(8.41189e-5,rel=4e-6)
    assert end.shear_s_inv/end.H_s_inv==pytest.approx(5.89303e-5,rel=4e-6)


def test_independent_cold_matter_quadrupole_generates_tiny_shear(model):
    d=BASSQuadrupoleTransport(model,sigma_ref=0.,orientation=0,
                     source_rad_amplitude=0.,source_matter_amplitude=.5)
    state=d.inspect(0,0,0.)
    assert state.rad_Pi_J_m3==0
    assert state.matter_Pi_J_m3>0
    dx=d.rhs(0,[0.,0.,0.])
    assert dx[1]>0 and dx[0]==0.
    sol=d.evolution(rtol=2e-11,atol=1e-15)
    end=d.inspect(sol.t[-1],*sol.y[:2,-1])
    assert end.Sigma>1e-15 and end.orientation==1
    assert end.rad_Pi_J_m3<0  # dynamically generated radiation opposite shear


def test_zero_P2_source_reproduces_parent_PR135_both_signed_branches(model):
    for sign in (-1,1):
        mag=historical_axis_ratio_to_sigma(.01)[0]
        first=BASSQuadrupoleTransport(model,sigma_ref=mag,orientation=sign)
        from sigma_pi_coupled import SigmaPiDynamics
        second=SigmaPiDynamics(model,sigma_ref=mag,orientation=sign)
        x=first.evolution();y=second.evolution()
        assert abs(x.y[0,-1]-y.y[0,-1])<3e-12
        assert abs(x.y[1,-1]-y.y[1,-1])<3e-12


def test_batched_moments_match_independent_scalar_and_no_extrapolation(model):
    d=BASSQuadrupoleTransport(model,sigma_ref=0.,orientation=0,
                     source_rad_amplitude=.2,source_matter_amplitude=.3)
    xs=np.linspace(-.05,.05,2049)
    batch=d.angular_batch(xs)
    scalar=np.array([d.radiation_normalized(float(b))[:2] for b in xs])
    np.testing.assert_allclose(batch,scalar,atol=2e-13,rtol=2e-12)
    with pytest.raises(ValueError):
        d.angular_batch(np.array([float("inf")]))


def test_independent_source_bass_direct_receipt_if_available():
    path=HERE/"BASS_DIRECT_HIERARCHY_RECEIPT.json"
    if not path.exists():
        pytest.skip("original BASS source oracle has not been executed")
    r=json.loads(path.read_text())
    assert r["status"]=="PASS_BASS_DIRECT_MASSLESS_AND_MASSIVE_L2_SOURCE_LIOUVILLE"
    for case in r["actual_original_source_anisotropic_l2_RHS_vs_full_direct_momentum_oracle"]:
        assert case["normalized_full_tensor_RHS_difference"]<2e-8
