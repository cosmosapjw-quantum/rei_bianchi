from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
MODULE = STAGE / "analysis" / "tensorized_inputs.py"
R1 = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK"
R1B1 = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"


def _load():
    spec = importlib.util.spec_from_file_location("r2b_r2a_tensorized", MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_tensorized_inputs_are_contiguous_immutable_and_locked_shape():
    m = _load()
    data = m.load_tensorized_inputs(repo_root=REPO)
    assert data.absorption.shape == (5, 17, 4)
    assert data.kappa.shape == (5, 17, 4)
    assert data.external_subgrid.shape == (5, 17, 4)
    assert data.time_s.shape == (5, 17)
    assert data.state0.values.shape == (6, 46080)
    assert data.state0.temperature_K.shape == (46080,)
    for array in (data.absorption, data.kappa, data.external_subgrid, data.state0.values):
        assert array.flags.c_contiguous
        assert not array.flags.writeable


def test_tensorized_roundtrip_matches_canonical_tables():
    m = _load()
    data = m.load_tensorized_inputs(repo_root=REPO)
    forcing = pd.read_csv(
        R1B1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv"
    ).sort_values(["interval_index", "node_index"])
    expected_abs = np.stack(
        [forcing[f"absorption_{g}_s-1_cMpc-3"].to_numpy(float) for g in m.GROUPS], axis=1
    ).reshape(5, 17, 4)
    expected_kappa = np.stack(
        [forcing[f"kappa_{g}_cMpc-1"].to_numpy(float) for g in m.GROUPS], axis=1
    ).reshape(5, 17, 4)
    assert np.array_equal(data.absorption, expected_abs)
    assert np.array_equal(data.kappa, expected_kappa)


def test_state_byte_image_is_deterministic_and_one_ulp_sensitive():
    m = _load()
    data = m.load_tensorized_inputs(repo_root=REPO)
    ledgers = {"photon": 1.0, "energy": 2.0}
    a = m.accepted_bytes(data.state0, ledgers)
    b = m.accepted_bytes(data.state0, dict(reversed(list(ledgers.items()))))
    assert a == b
    changed = data.state0.mutable_copy()
    changed.values[0, 0] = np.nextafter(changed.values[0, 0], np.inf)
    assert m.accepted_bytes(changed, ledgers) != a
