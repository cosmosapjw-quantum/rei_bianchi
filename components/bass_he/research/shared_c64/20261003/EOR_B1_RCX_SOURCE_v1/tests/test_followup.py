"""Post-implementation independent invariants, not counted as test-first."""
import math
import json
import pytest
from bass_he_rcx import ContractError,NumericalFailure,solve_partial_wave,partial_sum,physical_scales

@pytest.mark.parametrize('ell',[0,1,4])
def test_free_outer_extension_changes_no_loss_or_phase(ell):
    a=solve_partial_wave(1.2,ell,[0.,1.5],[-1.],[[.07]])
    b=solve_partial_wave(1.2,ell,[0.,1.5,4.],[-1.,0.],[[.07],[0.]])
    assert abs(complex(*a['S'])-complex(*b['S']))<2e-9
    assert b['loss_probability']==pytest.approx(a['loss_probability'],rel=3e-9)

def test_budget_failure_is_execution_failure():
    with pytest.raises(NumericalFailure,match='BUDGET'):
        solve_partial_wave(1.,0,[0.,1.,2.],[-1.,2.],[[.01],[.01]],max_nfev=1)

def test_mixed_models_not_summed():
    a=solve_partial_wave(1.,0,[0.,1.],[0.],[[.1]])
    b=solve_partial_wave(1.1,1,[0.,1.],[0.],[[.1]])
    with pytest.raises(ContractError):partial_sum([a,b])

@pytest.mark.parametrize('scale',[(0.,1.,1.),(1.,-1.,1.),(1.,1.,True),(1.,1.,float('inf'))])
def test_bad_physical_scale_rejected(scale):
    with pytest.raises(ContractError):physical_scales(*scale)

def test_strict_tolerance_no_silent_relaxation():
    with pytest.raises(ContractError):solve_partial_wave(1.,0,[0.,1.],[0.],[[.1]],rtol=1e-17)

def test_reservoir_partition_not_photon_spectrum():
    a=solve_partial_wave(.8,1,[0.,1.2],[-1.],[[.02,.05]])
    b=solve_partial_wave(.8,1,[0.,1.2],[-1.],[[.07]])
    assert abs(complex(*a['S'])-complex(*b['S']))<1e-13
    assert a['loss_probability']==pytest.approx(b['loss_probability'],rel=1e-13)
    assert a['photon_energy_moment'] is None

def test_zero_width_channel_zero_exactly():
    a=solve_partial_wave(1.,0,[0.,1.],[0.],[[.1,0.]])
    assert a['component_loss_probabilities'][1]==0

def test_subtraction_cannot_be_relative_certificate():
    a=solve_partial_wave(1.,0,[0.,1.],[0.],[[1e-30]])
    assert a['loss_probability']>0
    assert a['loss_by_subtraction']==0 or abs(a['loss_by_subtraction'])/a['loss_probability']>1e8
    assert not a['rigorous_numerical_enclosure']
