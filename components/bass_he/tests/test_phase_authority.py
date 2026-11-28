import math
import pytest

from bass_he.phase_authority import (
    nuclear_momentum,
    exact_nuclear_momentum_difference,
    common_trajectory_linearized_difference,
    phase_authority_inventory,
    path_phase,
)


def test_exact_nuclear_momentum_difference_identity():
    M=1467.0; A=2.4; Ua=0.13; Ub=0.17
    pa=nuclear_momentum(M,A,Ua); pb=nuclear_momentum(M,A,Ub)
    exact=pb-pa
    rationalized=-2*M*(Ub-Ua)/(pb+pa)
    assert exact == pytest.approx(rationalized, rel=2e-14, abs=2e-14)
    assert exact_nuclear_momentum_difference(M,A,Ua,Ub) == pytest.approx(exact, rel=2e-14)


def test_common_trajectory_linearization_converges_for_small_surface_gap():
    M=1467.0; A=2.4; U=0.15
    p0=nuclear_momentum(M,A,U)
    for du,tol in ((1e-4,3e-5),(1e-6,3e-7),(1e-8,3e-9)):
        exact=exact_nuclear_momentum_difference(M,A,U,U+du)
        approx=common_trajectory_linearized_difference(M,p0,du)
        assert abs(exact/approx-1) < tol


def test_phase_authority_forbids_local_real_branch_action_as_full_path_phase():
    a=phase_authority_inventory()
    assert a['local_branch_action_imaginary_part']['single_pass_probability_authorized'] is True
    assert a['local_branch_action_real_part']['full_interference_phase_authorized'] is False
    assert a['full_reaction_path_real_action']['required_for_coherent_phase'] is True
    assert a['topological_phase']['square_root_adiabatic_value'] == pytest.approx(math.pi/2)


def test_full_path_phase_combines_real_action_and_encircling_phase_explicitly():
    assert path_phase(1.2,0) == pytest.approx(1.2)
    assert path_phase(1.2,1) == pytest.approx(1.2+math.pi/2)
    assert path_phase(1.2,-2) == pytest.approx(1.2-math.pi)


def test_phase_authority_inputs_are_strict():
    with pytest.raises(ValueError): nuclear_momentum(0,1,0)
    with pytest.raises(ValueError): nuclear_momentum(1,0,1)
    with pytest.raises(ValueError): common_trajectory_linearized_difference(1,0,0.1)
    with pytest.raises(ValueError): path_phase(float('nan'),0)
    with pytest.raises(ValueError): path_phase(1.0,1.2)
