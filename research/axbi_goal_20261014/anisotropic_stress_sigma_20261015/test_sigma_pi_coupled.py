"""Executable scientific verification for selected Bianchi I Einstein stress pilot."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from sigma_pi_coupled import (
    SQRT3,KAPPA,RadiationKillingGL,SigmaPiScenario,SigmaPiDynamics,
    sigma_from_signed_axis,historical_axis_ratio_to_sigma,
)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SCENARIO=ROOT/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json"
DONOR=HERE/"REI_DONOR_CANDIDATE_OPTIN_ONLY.json"
EXPECTED_SCENARIO_SHA="07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696"
DONOR_GIT_BLOB="1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4"


@pytest.fixture(scope="module")
def reference():
    assert hashlib.sha256(SCENARIO.read_bytes()).hexdigest()==EXPECTED_SCENARIO_SHA
    assert hashlib.sha1(b"blob "+str(DONOR.stat().st_size).encode()+
           b"\0"+DONOR.read_bytes()).hexdigest()==DONOR_GIT_BLOB
    return SigmaPiScenario.from_locked_json(SCENARIO,gas_case="baseline")


@pytest.fixture(scope="module")
def donor():
    return SigmaPiScenario.from_locked_json(SCENARIO,gas_case="donor",donor_path=DONOR)


def test_shear_scalar_definition_and_signed_branch():
    for s,h in [(0,1),(.001,.1),(-.003,.7)]:
        mag,branch=sigma_from_signed_axis(s,h)
        assert mag==pytest.approx(math.sqrt(3)*abs(s)/h)
        assert branch==(1 if s>0 else -1 if s<0 else 0)
    with pytest.raises(ValueError):
        sigma_from_signed_axis(1,0)
    for old in (0.,.005,-.005,.01,-.01):
        sig,branch=historical_axis_ratio_to_sigma(old)
        assert 0<=sig<math.sqrt(3)
        assert sig==pytest.approx(math.sqrt(3)*abs(old)/math.hypot(1,old))
        assert branch==(1 if old>0 else -1 if old<0 else 0)


def test_original_REI_density_and_donor_source_contract(reference,donor):
    assert reference.x_e_ref==.0002
    assert donor.x_e_ref==.000210349192936
    assert donor.gas_T_ref_K==9.306042400380866
    assert reference.source_scenario_sha256==EXPECTED_SCENARIO_SHA
    assert reference.gas_owner.startswith("frozen_REI")
    assert reference.gas_pressure_ref>0
    assert donor.gas_pressure_ref>reference.gas_pressure_ref
    with pytest.raises(ValueError,match="orientation"):
        SigmaPiDynamics(reference,sigma_ref=.01,orientation=0)
    with pytest.raises(ValueError,match="Sigma"):
        SigmaPiDynamics(reference,sigma_ref=math.sqrt(3),orientation=1)
    with pytest.raises(ValueError,match="donor"):
        SigmaPiScenario.from_locked_json(SCENARIO,gas_case="donor",donor_path=None)


def test_exact_isotropic_radiation_and_small_shear_slope():
    angular=RadiationKillingGL(96)
    A,Pi,delta,press=angular.factors(0.)
    assert A==1 and Pi==0 and delta==0
    np.testing.assert_allclose(press,[1/3,1/3],rtol=0,atol=0)
    for b in (.00001,-.00001,.000003,-.000003):
        A,Pi,delta,press=angular.factors(b)
        assert Pi*b<0
        assert abs(Pi/b+1.6)<5e-5
        assert abs(delta/b**2-1.6)<1e-4
        assert abs(press[0]+2*press[1]-A)<4e-14
    # Angular order should converge without derivative approximation.
    for b in [-.07,-.025,.01,.07]:
        a=RadiationKillingGL(32).factors(b)
        c=RadiationKillingGL(128).factors(b)
        assert abs(a[0]-c[0])<2e-14
        assert abs(a[1]-c[1])<2e-14


@pytest.mark.parametrize("sigma,sign",[(0.,0),(.004,1),(.012,-1),(.017,1)])
def test_energy_and_hamiltonian_consistency(reference,sigma,sign):
    dyn=SigmaPiDynamics(reference,sigma_ref=sigma,orientation=sign)
    first=dyn.inspect(0,0,dyn.initial_shear_dimless)
    assert first.Sigma==pytest.approx(sigma,rel=3e-14,abs=3e-15)
    assert first.orientation==sign
    assert first.constraint_h2_s_inv2==pytest.approx(first.H_s_inv**2,rel=2e-15)
    for eta,b in [(.1,.01),(.6,-.02),(1.4,.015)]:
        residual=dyn.stress_conservation_identites(eta,b)
        assert residual["radiation_relative"]<2e-8
        assert residual["matter_relative"]<2e-8
        er,pr,_,_=dyn.moments(eta,b)
        um,pm,pbar=dyn.matter(eta,b)
        assert er>0 and um>0 and pbar==pytest.approx((2/3)*um,rel=1e-14)
        # Strict tensor contraction with eigenvalues (-s,-s,2s)
        q=first.shear_s_inv
        trace_sigma_pi=((-q)*(-pr/3))*2+(2*q)*(2*pr/3)
        assert trace_sigma_pi==pytest.approx(2*q*pr,rel=2e-15)


def test_isotropized_matter_is_own_closure_not_silent_zero(reference):
    sl=SigmaPiDynamics(reference,sigma_ref=.01,orientation=1,
                       closure="collisionless_matter")
    iso=SigmaPiDynamics(reference,sigma_ref=.01,orientation=1,
                        closure="isotropized_matter")
    for eta,b in [(.3,.02),(.8,-.03)]:
        u,p,pbar=sl.matter(eta,b)
        ui,pi,pbari=iso.matter(eta,b)
        assert pi==0
        assert abs(p)>0
        assert ui>0 and u>0
    assert sl.initial_shear_dimless==iso.initial_shear_dimless


def test_frozen_original_stress_free_geometry_has_exact_s_a3(reference):
    sigma=.01731964211523149
    drv=SigmaPiDynamics(reference,sigma_ref=sigma,orientation=-1,
                          geometry="prescribed_source")
    sol=drv.evolution(rtol=5e-12,atol=5e-13,max_step=.025)
    eta=np.linspace(0,sol.t[-1],35)
    samples=sol.sol(eta)
    np.testing.assert_allclose(samples[1],
       drv.initial_shear_dimless*np.exp(-3*eta),atol=1e-12,rtol=3e-10)
    assert samples[0,-1]<0


@pytest.mark.parametrize("orientation",[-1,1])
def test_full_Einstein_backreaction_both_signed_sigma_branches(reference,orientation):
    sigma=historical_axis_ratio_to_sigma(.01)[0]
    drv=SigmaPiDynamics(reference,sigma_ref=sigma,orientation=orientation)
    sol=drv.evolution()
    end=drv.inspect(sol.t[-1],*sol.y[:2,-1])
    assert sol.success and sol.nfev>15
    assert 0<end.Sigma<sigma
    assert end.orientation==orientation
    assert end.rad_Pi_J_m3*orientation<0
    assert end.matter_Pi_J_m3*orientation<0
    assert abs(end.rad_Pi_J_m3)>abs(end.matter_Pi_J_m3)*1e6
    # A second temporal method/step size and angular resolution at same IC
    refined=SigmaPiDynamics(reference,sigma_ref=sigma,orientation=orientation,n_mu=128)
    sol2=refined.evolution(rtol=5e-12,atol=5e-13,max_step=.0075)
    other=refined.inspect(sol2.t[-1],*sol2.y[:2,-1])
    assert abs(other.Sigma-end.Sigma)<5e-10
    assert abs(other.b-end.b)<5e-10


def test_exact_radiation_batch_matches_positive_half_scalar_for_1k_nodes():
    ang=RadiationKillingGL(64)
    x=np.linspace(-.04,.04,1103)
    batch=ang.factors_batch(x)
    separate=np.array([ang.factors(float(v))[:3] for v in x])
    np.testing.assert_allclose(batch,separate,rtol=6e-13,atol=1e-13)


def test_native_reference_rust_oracle_if_available(reference):
    csv=HERE/"NATIVE_RUST_RADIATION_ORACLE.csv"
    if not csv.is_file():
        pytest.skip("actual native Rust source has not been compiled yet")
    dat=np.loadtxt(csv,delimiter=",",skiprows=1)
    assert dat.shape==(9,4)
    angular=RadiationKillingGL(96)
    e0=reference.radiation_energy_ref*(reference.a_ref/(1/5))**4
    for b,Er,Pi,Delta in dat:
        A,p,d,_=angular.factors(float(b))
        np.testing.assert_allclose([Er,Pi,Delta],[e0*A,e0*p,e0*d],
                                   rtol=1e-10,atol=3e-22)


@pytest.mark.parametrize("orientation",[-1,1])
def test_independent_einstein_raychaudhuri_from_H_constraint(reference,orientation):
    mag=historical_axis_ratio_to_sigma(.01)[0]
    dyn=SigmaPiDynamics(reference,sigma_ref=mag,orientation=orientation,
                        closure="collisionless_matter")
    sol=dyn.evolution()
    for eta in (.01,.4,1.0,sol.t[-1]):
        b,u,_=sol.sol(eta)
        rel=dyn.raychaudhuri_relative_residual(float(eta),float(b),float(u))
        assert rel<2e-8, f"Einstein mean-curvature violation rel={rel}"


def test_exact_gas_pressure_source_linear_response(reference):
    d=SigmaPiDynamics(reference,sigma_ref=.009,orientation=-1)
    p0=reference.gas_pressure_ref
    for b in (-1e-5,1e-5):
        u,pi,pbar=d.matter(0,b)
        assert pi/b==pytest.approx(-6*p0,rel=8e-5)
        assert abs(u/(1.5*p0)-1)<4e-9


def test_actual_completed_native_rei_radiation_feedback_consistency():
    from verify_native_feedback import verify
    actual=verify()
    assert actual["status"]=="PASS_PERTURBATIVE_CROSS_MODEL"
    assert actual["original_native_history_rows"]==312238
    assert actual["new_Einstein_delta_s_over_H"]<0
    assert abs(actual["signed_native_ionizing_delta_s_over_H"])<(
        1e-7*abs(actual["original_source_perturbative_delta_s_over_H"])
    )


def test_proper_clock_is_integrated_locally_and_remains_monotone(reference):
    dyn=SigmaPiDynamics(reference,
         sigma_ref=historical_axis_ratio_to_sigma(.01)[0],orientation=1)
    sol=dyn.evolution()
    sampled=dyn.sampled(sol,count=121)
    t=np.array([r["elapsed_proper_t_s"] for r in sampled])
    assert t[0]==0
    assert np.all(np.diff(t)>0)
    assert 1e16<t[-1]<1e17
    # Source numerical clock is dt/dln(a)=1/H; independent short
    # increment from physical midpoint agrees to expected order.
    i=27
    dt=t[i+1]-t[i]
    delta=sampled[i+1]["eta"]-sampled[i]["eta"]
    m=sol.sol((sampled[i]["eta"]+sampled[i+1]["eta"])/2)
    H=dyn.inspect((sampled[i]["eta"]+sampled[i+1]["eta"])/2,
                   float(m[0]),float(m[1])).H_s_inv
    h0=sampled[i]["H_per_s"]
    h1=sampled[i+1]["H_per_s"]
    simpson=delta*(1/h0+4/H+1/h1)/6
    assert abs((dt-simpson)/dt)<2e-8
