from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pytest

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
OLD = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2_OWNER_CORRECT_PHOTON_CONSERVING_NONAUTONOMOUS_FIXED_POINT_HISTORY_RERUN"
R1 = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK"
R1B1 = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"
R2A = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _mods():
    tensor = _load("r2b_r2a_tensorized", STAGE / "analysis/tensorized_inputs.py")
    array = _load("r2b_r2a_array_owner", STAGE / "analysis/array_owner_kernel.py")
    forcing = _load("r2b_r2_legacy_forcing_parity", OLD / "analysis/forcing.py")
    owner = _load("r2b_r2_legacy_owner_parity", OLD / "analysis/owner_kernel.py")
    return tensor, array, forcing, owner


def _legacy(tensor, forcing, owner):
    data = tensor.load_tensorized_inputs(repo_root=REPO)
    npz = np.load(R1 / "data/initial_material_state_z6.npz")
    state = {name: np.asarray(npz[name]) for name in npz.files}
    f = forcing.CanonicalForcing.from_stage_inputs(
        forcing_csv=R1B1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv",
        owner_csv=R2A / "data/time_resolved_owner_split.csv",
    )
    k = owner.DynamicOwnerKernel.from_stage_inputs(
        initial_state=state,
        atomic_moments_csv=R1B1 / "data/atomic_moments/verner_gray_and_limit_moments.csv",
        r1b_r1_stage=R1B1,
        r2a_stage=R2A,
    )
    row = f.evaluate(0, 0.0)
    ext = {g: f.external_subgrid_raw(0, g, 0.0) for g in tensor.GROUPS}
    return data, state, row, ext, k


def _relative_l1(a, b):
    return float(np.sum(np.abs(a-b), dtype=np.float64) / max(np.sum(np.abs(b), dtype=np.float64), 1.0))


@pytest.mark.parametrize("lane", [
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
])
def test_array_owner_kernel_matches_legacy_on_locked_state(lane):
    tensor, array, forcing, owner = _mods()
    data, state, row, ext, legacy_kernel = _legacy(tensor, forcing, owner)
    new = array.ArrayOwnerKernel.from_repo(repo_root=REPO, inputs=data)
    got = new.evaluate(interval=0, node=0, state=data.state0, lane=lane)
    ref = legacy_kernel.evaluate(
        forcing_row=row, state=state, external_subgrid_raw=ext, subgrid_lane=lane
    )
    ref_fraction = np.array([[ref.owner_fraction[(g,c)] for g in tensor.GROUPS] for c in tensor.OWNERS])
    assert np.max(np.abs(got.owner_fraction-ref_fraction)) < 1e-11
    for ci,c in enumerate(tensor.OWNERS):
        for gi,g in enumerate(tensor.GROUPS):
            reference = ref.node_current[(g,c)]
            assert _relative_l1(got.node_current[ci,gi], reference) < 1e-11
            if not data.owner_support[ci,gi]:
                assert np.count_nonzero(got.node_current[ci,gi]) == 0


def test_node_permutation_is_invariant_after_inverse_permutation():
    tensor, array, _forcing, _owner = _mods()
    data = tensor.load_tensorized_inputs(repo_root=REPO)
    kernel = array.ArrayOwnerKernel.from_repo(repo_root=REPO, inputs=data)
    ref = kernel.evaluate(interval=0, node=0, state=data.state0, lane="LOCAL_NEUTRAL_HAZARD_PRIMARY")
    rng = np.random.default_rng(314159)
    perm = rng.permutation(data.state0.node_count)
    perm_state = tensor.ArrayState(data.state0.values[:,perm].copy(), data.state0.temperature_K[perm].copy())
    got = kernel.permuted(perm).evaluate(interval=0, node=0, state=perm_state, lane="LOCAL_NEUTRAL_HAZARD_PRIMARY")
    inv = np.argsort(perm)
    assert _relative_l1(got.node_current[...,inv], ref.node_current) < 1e-11


def test_unsupported_owner_group_support_is_exact_zero():
    tensor, array, _forcing, _owner = _mods()
    data = tensor.load_tensorized_inputs(repo_root=REPO)
    got = array.ArrayOwnerKernel.from_repo(repo_root=REPO, inputs=data).evaluate(
        interval=0,node=0,state=data.state0,lane="LOCAL_NEUTRAL_HAZARD_PRIMARY"
    )
    assert np.count_nonzero(got.node_current[~data.owner_support.astype(bool)]) == 0


def test_roundoff_closure_is_assigned_to_largest_support_not_tiny_tail():
    owner = _load('r2b_r2a_array_owner_roundoff', STAGE/'analysis/array_owner_kernel.py')
    h=np.array([3769531.2919941754,0.019905772835280652,1.5733767554744014e-154])
    total=7.0
    q,current=owner._allocate(total,h)
    uncorrected=total*(h/np.sum(h,dtype=np.float64))
    changed=np.flatnonzero(current != uncorrected)
    assert changed.tolist() == [int(np.argmax(h))]
    assert np.sum(current,dtype=np.float64) == total
    assert current[-1] == uncorrected[-1]
