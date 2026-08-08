from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np

ANALYSIS = Path(__file__).parents[1] / 'analysis'
REPO = Path(__file__).resolve().parents[3]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_fast_physical_trial_matches_reference_and_closes_gates():
    fastmod = load('r2b_fast_sdirk_trial', ANALYSIS / 'second_order_sdirk_fast_trial.py')
    refmod = load('r2b_reference_sdirk_trial', ANALYSIS / 'second_order_sdirk_trial.py')
    fast = fastmod.SecondOrderSDIRKFastTrial.from_repo(
        repo_root=REPO, lane='LOCAL_NEUTRAL_HAZARD_PRIMARY'
    )
    reference = refmod.SecondOrderSDIRKTrial.from_repo(
        repo_root=REPO, lane='LOCAL_NEUTRAL_HAZARD_PRIMARY'
    )
    parent = fast.inputs.state0.mutable_copy()
    duration = fast.forcing.duration_seconds(0)
    t1 = duration / 2048
    got = fast.solve(state=parent, t0=0.0, t1=t1, partition=2048, trial_kind='TEST')
    expected = reference.solve(
        state=parent, t0=0.0, t1=t1, partition=2048, trial_kind='REFERENCE'
    )
    assert got.converged, got.certificate
    assert expected.converged, expected.certificate
    assert got.minimum_species > 0.0
    assert got.hydrogen_residual < 1.0e-11
    assert got.helium_residual < 1.0e-11
    assert got.owner_residual < 1.0e-11
    assert got.photon_residual < 1.0e-8
    assert got.thermal_residual < 1.0e-10
    assert got.pds_reconstruction_residual < 1.0e-11
    assert np.max(np.abs(got.state.values / expected.state.values - 1.0)) < 1.0e-10
    assert np.max(np.abs(got.state.temperature_K / expected.state.temperature_K - 1.0)) < 1.0e-10
    assert got.certificate['thermal_root'] == 'ANALYTIC_NEWTON_BISECTION'
    assert got.certificate['thermal_predictor_root'] == 'ANALYTIC_NEWTON_BISECTION'
    assert got.certificate['thermal_predictor_iterations'] < 20
