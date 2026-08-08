from __future__ import annotations
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent
REPO=STAGE.parents[1]


def load_module():
    spec=importlib.util.spec_from_file_location('uncertainty_trial',STAGE/'analysis/uncertainty_trial.py')
    assert spec and spec.loader
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def solver():
    m=load_module()
    return m.UncertaintySecondOrderTrial.from_repo(
        repo_root=REPO,
        lane='LOCAL_NEUTRAL_HAZARD_PRIMARY',
        v_policy='CELL_LOWER_STRICT',
        f_value=0.1,
    )


def test_branch_trial_never_calls_legacy_summed_rhs():
    s=solver()
    def forbidden(*args,**kwargs):
        raise AssertionError('legacy summed RHS must not be called')
    s.backend.micro._batch_rhs=forbidden
    parent=s.inputs.state0.mutable_copy(); before=(parent.values.tobytes(),parent.temperature_K.tobytes())
    duration=s.forcing.duration_seconds(0); dt=duration/2048
    result=s.solve(state=parent,t0=0.0,t1=dt,partition=2048,trial_kind='FULL')
    assert result.converged, result.certificate
    assert before==(parent.values.tobytes(),parent.temperature_K.tobytes())


def test_branch_trial_closes_population_and_augmented_energy_ledgers():
    s=solver(); parent=s.inputs.state0.mutable_copy(); duration=s.forcing.duration_seconds(0); dt=duration/2048
    result=s.solve(state=parent,t0=0.0,t1=dt,partition=2048,trial_kind='FULL')
    assert result.converged, result.certificate
    assert result.hydrogen_residual <= 1e-11
    assert result.helium_residual <= 1e-11
    assert result.owner_residual <= 1e-11
    assert result.photon_residual <= 1e-8
    assert result.thermal_residual <= 1e-10
    assert result.pds_reconstruction_residual <= 1e-11
    assert result.minimum_species > 0
    for name in ('ots_resolved_heating','ots_unresolved_energy','ots_escaped_energy','ots_chemical_energy'):
        assert name in result.ledger_delta
    assert result.certificate['max_augmented_energy_residual'] <= 1e-10
    assert result.certificate['branch_domain_failure_count'] == 0
    assert result.certificate['legacy_rhs_calls'] == 0
    assert result.certificate['thermal_event_outer_residual'] <= 1e-10
    assert result.certificate['thermal_event_outer_iterations'] >= 1
