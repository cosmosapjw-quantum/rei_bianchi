from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import numpy as np

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parents[1]


def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def test_physical_map_closes_on_small_internal_step_without_subgrid_leakage():
    p=_load('r2b_r2a_physical_trial',STAGE/'analysis/physical_trial.py')
    solver=p.PhysicalTrialSolver.from_repo(repo_root=REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY')
    duration=solver.forcing.duration_seconds(0)
    trial=solver.solve_trial(
        solver.inputs.state0,0.0,duration/1024,1024,'FULL'
    )
    assert trial.result.converged
    assert trial.result.max_hydrogen_residual < 1e-11
    assert trial.result.max_helium_residual < 1e-11
    assert trial.result.max_photon_residual < 1e-8
    assert trial.ledger_delta['effective_subgrid_absorption'] > 0.0
    assert trial.ledger_delta['resolved_photoheating'] >= 0.0
    assert trial.ledger_delta['unresolved_absorbed_energy'] >= 0.0
    assert trial.result.state.values[0].shape == (46080,)


def test_rejected_physical_trial_keeps_parent_bytes():
    p=_load('r2b_r2a_physical_trial_parent',STAGE/'analysis/physical_trial.py')
    t=_load('r2b_r2a_tensorized_parent',STAGE/'analysis/tensorized_inputs.py')
    solver=p.PhysicalTrialSolver.from_repo(repo_root=REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY')
    parent=solver.inputs.state0.mutable_copy()
    before=t.accepted_bytes(parent,{})
    duration=solver.forcing.duration_seconds(0)
    _=solver.solve_trial(parent,0.0,duration/8,8,'FULL')
    assert t.accepted_bytes(parent,{}) == before


def test_physical_solver_keeps_stable_numpy_oracle_after_jax_sequence_failure():
    p=_load('r2b_r2a_physical_trial_backend',STAGE/'analysis/physical_trial.py')
    solver=p.PhysicalTrialSolver.from_repo(
        repo_root=REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY'
    )
    assert solver.backend.thermal.name == 'NUMPY_ARRAY_ORACLE'


def test_physical_solver_records_compact_scalar_trial_audit():
    p=_load('r2b_r2a_physical_trial_audit',STAGE/'analysis/physical_trial.py')
    solver=p.PhysicalTrialSolver.from_repo(
        repo_root=REPO,lane='LOCAL_NEUTRAL_HAZARD_PRIMARY'
    )
    duration=solver.forcing.duration_seconds(0)
    solver.solve_trial(solver.inputs.state0,0.0,duration/1024,1024,'FULL')
    assert len(solver.trial_records) == 1
    record=solver.trial_records[0]
    assert record['partition'] == 1024
    assert record['trial_kind'] == 'FULL'
    assert isinstance(record['residual'],float)
    assert isinstance(record['map_calls'],int)
    assert 'state' not in record
    assert 'node_current' not in record
