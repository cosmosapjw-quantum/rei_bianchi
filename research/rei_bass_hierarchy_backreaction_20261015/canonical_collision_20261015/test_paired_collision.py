"""Scientific gate for positive angular Markov collision, gas recoil ledger.

The optical depth is explicitly conditioned input. Tests do NOT assume a
physically sourced cross section, gas bulk Euler, thermal equilibrium or
validity of the new operator in production photoionization.
"""
from __future__ import annotations
import math
import numpy as np
import pytest

from canonical_fv import CanonicalMomentumFV
from paired_collision import PositiveCanonicalAngularCollision,C_SI
from run_hierarchy import source_lock


@pytest.fixture(scope="module")
def angular_jump():
    lock=source_lock()
    kinetic_ref=lock.rhocrit_j_m3 *lock.omega_m*.1/lock.aref**3
    original=CanonicalMomentumFV(30.,.5,32,16,gauss_order=3)
    return PositiveCanonicalAngularCollision(original,kinetic_ref)


def test_canonical_shell_numbers_and_positive_source(angular_jump):
    C=angular_jump
    pop=C.populations()
    assert np.all(pop>=0)
    assert pop.shape==(96,48)
    # Compactification extends to q=infinity: the far FD tail can
    # underflow to *zero* in f64, but may never become negative.
    assert np.all(pop.sum(axis=1)>=0)
    assert np.any(pop.sum(axis=1)>0)
    assert abs(C.wmu.sum()-1)<1e-14
    assert not C.initial.flags.writeable
    assert C.source_rhs(pop).shape==pop.shape
    assert abs(C.source_rhs(pop).sum())<1e-13
    expected=C.source.moments(.2,.015)
    measured=C.moments(.2,.015,pop)
    assert measured.energy_norm==pytest.approx(expected.rho,rel=1e-14)
    assert measured.delta_pressure_norm==pytest.approx(
        3*expected.pi_s,rel=1e-14)
    assert abs(measured.moment_z_norm)<2e-15


def test_zero_optical_depth_is_exact_identity(angular_jump):
    C=angular_jump
    before=C.populations()
    after,event=C.event(.2,.015,0.,before,5e-12)
    np.testing.assert_array_equal(after,before)
    assert event.massive_delta_energy_J_m3==0
    assert event.gas_delta_energy_J_m3==0
    assert event.gas_energy_after_J_m3==5e-12
    assert event.count_before==event.count_after
    assert not after.flags.writeable


@pytest.mark.parametrize("tau", [.001,.1,.7,3.,30.,1000.])
def test_exact_semigroup_positivity_and_cell_number(angular_jump,tau):
    C=angular_jump
    old=C.populations()
    after,event=C.event(.2,.015,tau,old,1e-7)
    assert np.all(after>=0)
    assert not after.flags.writeable
    assert event.max_radial_shell_count_abs_error<2e-14
    assert abs(event.count_before-event.count_after)<3e-14
    assert event.relative_entropy_after<=event.relative_entropy_before+2e-15
    assert event.status=="SCOPED_CONDITIONAL_PAIR_4MOMENTUM_CONSISTENCY"
    assert event.massive_delta_energy_J_m3+event.gas_delta_energy_J_m3==0
    assert event.massive_delta_zmomentum_J_m3_over_c+event.gas_delta_zmomentum_J_m3_over_c==0
    if tau>=30:
        ideal=C.isotropic_target(old)
        assert np.max(abs(after-ideal))<2e-12*float(np.max(old))


def test_collision_time_semigroup_and_ledger_composition(angular_jump):
    C=angular_jump
    begin=C.populations()
    middle,a=C.event(.2,.015,.2,begin,1e-7)
    final,b=C.event(.2,.015,.6,middle,a.gas_energy_after_J_m3)
    direct,c=C.event(.2,.015,.8,begin,1e-7)
    np.testing.assert_allclose(final,direct,rtol=2e-14,atol=1e-15)
    assert b.gas_energy_after_J_m3==pytest.approx(
        c.gas_energy_after_J_m3,rel=4e-12,abs=1e-20)
    assert b.relative_entropy_after<=a.relative_entropy_after
    assert abs((a.massive_delta_energy_J_m3+b.massive_delta_energy_J_m3)
               -c.massive_delta_energy_J_m3)<3e-19


def test_initial_source_P2_damping_exact_at_isotropic_geometry():
    c=PositiveCanonicalAngularCollision(
        CanonicalMomentumFV(30.,.5,32,16,gauss_order=3),
        source_lock().rhocrit_j_m3*.1*source_lock().omega_m/
        source_lock().aref**3)
    before=c.populations()
    for tau in [.01,.1,1.,10.]:
        after,e=c.event(0.,0.,tau,before,3.1885e-19)
        initial=c.moments(0.,0.,before)
        final=c.moments(0.,0.,after)
        assert final.delta_pressure_norm==pytest.approx(
            math.exp(-tau)*initial.delta_pressure_norm,rel=3e-13,abs=1e-15)
        assert e.massive_delta_energy_J_m3==0.
        assert e.gas_energy_after_J_m3==3.1885e-19


def test_energy_partner_recoil_and_boundary_gas_fail_closed(angular_jump):
    C=angular_jump
    before=C.populations()
    after,event=C.event(.1,.01,.7,before,1e-7)
    assert event.massive_delta_energy_J_m3>0
    assert event.gas_delta_energy_J_m3<0
    assert event.Pi_m_after_J_m3<event.Pi_m_before_J_m3
    # Proper physical energy is separately recomputed from the resulting
    # phase-space populations, not merely re-used from the ledger.
    b=C.moments(.1,.01,before)
    a=C.moments(.1,.01,after)
    independently=(a.energy_norm-b.energy_norm)*C.ref_energy
    assert abs(independently-event.massive_delta_energy_J_m3) < 1e-20
    assert abs(event.gas_delta_energy_J_m3+
               event.massive_delta_energy_J_m3)<1e-32
    # Source REI thermal u_g is 10^6-10^7 below the conditioned required
    # recoil reserve. Never borrow cosmological rest mass silently.
    with pytest.raises(ValueError,match="insufficient"):
        C.event(.1,.01,.7,before,3.1885009560495904e-19)


def test_conditional_negative_b_can_heat_gas(angular_jump):
    C=angular_jump
    _,e=C.event(.8,-.01,.7,C.populations(),1e-15)
    assert e.massive_delta_energy_J_m3<0
    assert e.gas_delta_energy_J_m3>0
    assert e.gas_energy_after_J_m3>e.gas_energy_before_J_m3


def test_markov_canonical_detailed_balance_not_physical_thermal_equilibrium(angular_jump):
    C=angular_jump
    i=1;j=12
    # For homogeneous angular redistribution K_{i->j}=lambda*wj;
    # equilibrium w_i K_ij = w_j K_ji exactly.
    direct=C.wmu[i]*C.wmu[j]
    reversed=C.wmu[j]*C.wmu[i]
    assert direct==reversed
    target=C.isotropic_target(C.populations())
    assert abs(C.relative_entropy(target))<1e-12
    assert C.relative_entropy(C.populations())>0


def test_fail_closed_invalid_negative_and_odd_source(angular_jump):
    C=angular_jump
    initial=C.populations()
    for invalid in [-1.,float("nan"),float("inf"),1001.]:
        with pytest.raises(ValueError):
            C.event(0.,0.,invalid,initial,1.)
    corrupted=initial.copy()
    corrupted[1,1]=-1e-3
    with pytest.raises(ValueError):
        C.event(0.,0.,.1,corrupted,1.)
    odd=initial.copy()
    odd[1,1]*=1.15
    with pytest.raises(ValueError,match="Euler"):
        C.event(0.,0.,.1,odd,1.)
    with pytest.raises(ValueError,match="nonnegative"):
        C.event(0.,0.,.1,initial,-1.)


def test_declared_source_is_not_a_physical_ionization_rate(angular_jump):
    C=angular_jump
    fixed=C.populations()
    a=C.source_rhs(fixed)
    # The generator conserves every radial shell independently and is
    # incapable of creating or destroying H/He species: no claim that
    # tau is an actual MD14/Case-A collision optical depth.
    np.testing.assert_allclose(a.sum(axis=1),np.zeros(a.shape[0]),
                               atol=8e-17)


def test_relative_entropy_data_processing_bound_stronger_than_monotonicity(angular_jump):
    C=angular_jump
    p=C.populations()
    h0=C.relative_entropy(p)
    for tau in (.02,.3,1.,4.,10.):
        next_p,rec=C.event(.1,0.,tau,p,1e-7)
        assert rec.relative_entropy_after<=math.exp(-tau)*h0+2e-14


def test_strong_generator_limit_matches_finite_event_at_small_dtau(angular_jump):
    C=angular_jump
    state=C.populations()
    dt=1e-6
    new,_=C.event(0.,0.,dt,state,1e-7)
    derivative=(new-state)/dt
    exact=C.source_rhs(state)
    assert np.max(abs(derivative-exact))<2e-6*float(np.max(exact))
