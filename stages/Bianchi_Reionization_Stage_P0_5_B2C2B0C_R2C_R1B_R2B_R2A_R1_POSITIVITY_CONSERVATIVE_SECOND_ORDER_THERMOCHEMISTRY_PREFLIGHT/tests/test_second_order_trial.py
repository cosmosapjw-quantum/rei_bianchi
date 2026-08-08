from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np
import pytest

MODULE=Path(__file__).parents[1]/'analysis/second_order_trial.py'
REPO=Path(__file__).resolve().parents[3]

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_trial2',MODULE)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m


def test_conditioned_owner_fraction_closes_exactly():
    m=load()
    p=m.condition_owner_fractions(np.array([[0.1,0.2],[0.2,0.3],[0.7,0.5],[0.0,0.0]]))
    np.testing.assert_allclose(np.sum(p,axis=0),1.0,rtol=0.0,atol=0.0)
    assert np.all(p>=0.0)


def test_subgrid_routes_only_to_unresolved_ledgers():
    m=load()
    led=m.empty_ledgers()
    m.post_owner_counts(led,np.array([10.0,2.0,3.0,4.0]),np.array([100.0,20.0,30.0,40.0]))
    assert led['effective_subgrid_absorption']==10.0
    assert led['unresolved_absorbed_energy']==100.0
    assert led['resolved_photoheating']==90.0
    assert led['resolved_HI_absorption']==2.0


def test_small_physical_step_is_positive_conservative_and_owner_closed():
    m=load(); solver=m.SecondOrderPhysicalTrial.from_repo(repo_root=REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY')
    state=solver.inputs.state0.mutable_copy(); duration=solver.forcing.duration_seconds(0)
    result=solver.solve(state=state,t0=0.0,t1=duration/4096.0,partition=4096,trial_kind='TEST')
    assert result.converged, result.certificate
    assert np.min(result.state.values[:5])>0.0
    assert result.hydrogen_residual<1e-11
    assert result.helium_residual<1e-11
    assert result.photon_residual<1e-8
    assert result.thermal_residual<1e-10
    assert result.pds_reconstruction_residual<1e-11
    assert result.ledger_delta['effective_subgrid_absorption']>0.0
    assert result.ledger_delta['unresolved_absorbed_energy']>=0.0


def test_trial_does_not_mutate_parent_state():
    m=load(); solver=m.SecondOrderPhysicalTrial.from_repo(repo_root=REPO,lane='RECOMBINATION_WEIGHTED_AUDITOR')
    state=solver.inputs.state0.mutable_copy(); before=(state.values.tobytes(),state.temperature_K.tobytes())
    duration=solver.forcing.duration_seconds(0)
    solver.solve(state=state,t0=0.0,t1=duration/4096.0,partition=4096,trial_kind='TEST')
    assert before==(state.values.tobytes(),state.temperature_K.tobytes())


def test_unknown_lane_fails_closed():
    m=load()
    with pytest.raises(KeyError):
        m.SecondOrderPhysicalTrial.from_repo(repo_root=REPO,lane='POST_HOC_BEST')
