import math
import pytest

from bass_he.model_gates import (
    source_headon_rmin_a0, rotation_access_ratio,
    semiclassical_action_probability, paper_eq52_probability,
    source_coupling_regime, critical_energy_for_matching_radius_eVu,
)


def test_source_headon_rmin_recovers_published_100_evu_anchors_and_inverse_energy_scaling():
    assert source_headon_rmin_a0(100.0,'H') == pytest.approx(0.65)
    assert source_headon_rmin_a0(100.0,'D') == pytest.approx(0.40)
    assert source_headon_rmin_a0(100.0,'T') == pytest.approx(0.30)
    assert source_headon_rmin_a0(500.0,'H') == pytest.approx(0.13)
    assert source_headon_rmin_a0(50.0,'H') == pytest.approx(1.30)


def test_rotation_access_ratio_is_diagnostic_not_boolean_gate():
    assert rotation_access_ratio(100.0,'H',1) == pytest.approx(0.65/(7/12))
    assert rotation_access_ratio(500.0,'H',1) == pytest.approx(0.13/(7/12))


def test_source_coupling_regime_uses_published_boundaries_without_inventing_precision():
    assert source_coupling_regime(1000.0) == 'RADIAL_DOMINANT_ABOVE_500_EVU_SOURCE_DISCUSSION'
    assert source_coupling_regime(500.0) == 'ROTATIONAL_RISING_40_TO_500_EVU_SOURCE_DISCUSSION'
    assert source_coupling_regime(100.0) == 'ROTATIONAL_RISING_40_TO_500_EVU_SOURCE_DISCUSSION'
    assert source_coupling_regime(30.0) == 'BELOW_40_EVU_RADIAL_REGAINS_SOURCE_DISCUSSION'


def test_action_probability_carries_factor_two_from_amplitude_modulus_square():
    delta=0.37; v=0.21
    p52=paper_eq52_probability(delta,v)
    p_action=semiclassical_action_probability(delta,v)
    assert p_action == pytest.approx(p52*p52, rel=2e-15)
    assert p_action == pytest.approx(math.exp(-2*delta/v))


def test_model_gate_inputs_are_strict():
    with pytest.raises(ValueError): source_headon_rmin_a0(0,'H')
    with pytest.raises(ValueError): source_headon_rmin_a0(100,'X')
    with pytest.raises(ValueError): rotation_access_ratio(100,'H',0)
    with pytest.raises(ValueError): semiclassical_action_probability(-1,1)
    with pytest.raises(ValueError): paper_eq52_probability(1,0)


def test_upper_shell_absorbing_diagnostic_exposes_bound_separated_correlation():
    from bass_he.model_gates import upper_shell_absorbing_diagnostics
    rows={x['branch']:x for x in upper_shell_absorbing_diagnostics(3)}
    assert rows['Q23']['absorbing_upper_shell'] is True
    assert rows['Q23']['separated_center'] == 'Z2'
    assert rows['Q23']['separated_n'] == 2
    assert rows['Q12']['absorbing_upper_shell'] is False
    assert rows['Q12']['separated_center'] == 'Z1'
    assert rows['Q12']['separated_n'] == 1


def test_source_anchor_implies_energy_threshold_for_inherited_matching_radius():
    assert critical_energy_for_matching_radius_eVu('H',1) == pytest.approx(111.42857142857143)
    assert critical_energy_for_matching_radius_eVu('D',1) == pytest.approx(68.57142857142857)
    assert critical_energy_for_matching_radius_eVu('T',1) == pytest.approx(51.42857142857143)
    assert critical_energy_for_matching_radius_eVu('H',2) == pytest.approx(33.91304347826087)



def test_rutherford_proxy_turning_point_recovers_headon_source_anchor():
    from bass_he.model_gates import rutherford_proxy_rmin_a0
    for E in (50.0,100.0,250.0,500.0,5000.0):
        assert rutherford_proxy_rmin_a0(E,'H',0.0) == pytest.approx(source_headon_rmin_a0(E,'H'))


def test_rutherford_proxy_bmax_solves_turning_point_equal_matching_radius():
    from bass_he.model_gates import rutherford_proxy_bmax_for_radius, rutherford_proxy_rmin_a0
    Rcut=7/12
    for E in (250.0,500.0,5000.0):
        bmax=rutherford_proxy_bmax_for_radius(E,'H',Rcut)
        assert bmax > 0
        assert rutherford_proxy_rmin_a0(E,'H',bmax) == pytest.approx(Rcut, rel=2e-14, abs=2e-14)
    assert rutherford_proxy_bmax_for_radius(100.0,'H',Rcut) == 0.0


def test_rutherford_proxy_accessible_area_fraction_is_one_minus_r0_over_radius():
    from bass_he.model_gates import rutherford_proxy_accessible_area_fraction
    Rcut=7/12
    expected={100.0:0.0,250.0:1-(0.65*100/250)/Rcut,500.0:1-.13/Rcut,5000.0:1-.013/Rcut}
    for E,want in expected.items():
        assert rutherford_proxy_accessible_area_fraction(E,'H',Rcut) == pytest.approx(want, rel=2e-14, abs=2e-14)


def test_rutherford_proxy_rejects_being_used_as_negative_or_invalid_geometry():
    from bass_he.model_gates import rutherford_proxy_rmin_a0, rutherford_proxy_bmax_for_radius
    with pytest.raises(ValueError): rutherford_proxy_rmin_a0(100,'H',-0.1)
    with pytest.raises(ValueError): rutherford_proxy_bmax_for_radius(100,'H',0.0)



def test_trajectory_observable_gate_distinguishes_total_from_state_and_isotope_sensitive_claims():
    from bass_he.model_gates import trajectory_observable_gate
    assert trajectory_observable_gate('total_capture_H') == 'RECENT_COUPLED_TRAJECTORY_STUDY_SUPPORTS_APPROXIMATE_TRAJECTORY_ROBUSTNESS'
    assert trajectory_observable_gate('state_resolved_capture') == 'LOW_ENERGY_TRAJECTORY_SENSITIVITY_REMAINS_OPEN'
    assert trajectory_observable_gate('isotope_resolved_capture') == 'LOW_ENERGY_TRAJECTORY_SENSITIVITY_ESTABLISHED_IN_SOURCE'
    assert trajectory_observable_gate('projectile_energy_loss') == 'TRAJECTORY_SENSITIVITY_ESTABLISHED'
    with pytest.raises(ValueError): trajectory_observable_gate('everything')


def test_two_pass_markov_is_phase_average_of_coherent_interference():
    import numpy as np
    from bass_he.model_gates import markov_double_pass_probability, coherent_double_pass_probability
    x,w=np.polynomial.legendre.leggauss(32)
    phases=(x+1)*math.pi/2
    for p in (1e-6,0.01,0.2,0.5,0.9,1-1e-6):
        avg=sum(wi*coherent_double_pass_probability(p,phi) for wi,phi in zip(w,phases))/2
        assert avg == pytest.approx(markov_double_pass_probability(p), rel=2e-14, abs=2e-14)


def test_coherent_two_pass_envelope_contains_markov_average_and_reaches_twice_it():
    from bass_he.model_gates import markov_double_pass_probability, coherent_double_pass_envelope
    for p in (0.01,0.2,0.5,0.8,0.99):
        lo,hi=coherent_double_pass_envelope(p)
        pm=markov_double_pass_probability(p)
        assert lo == 0.0
        assert hi == pytest.approx(2*pm)
        assert lo <= pm <= hi <= 1.0


def test_coherent_probability_input_validation():
    from bass_he.model_gates import coherent_double_pass_probability, markov_double_pass_probability
    with pytest.raises(ValueError): markov_double_pass_probability(-0.1)
    with pytest.raises(ValueError): coherent_double_pass_probability(1.1,0.0)
    with pytest.raises(ValueError): coherent_double_pass_probability(0.5,float('nan'))
