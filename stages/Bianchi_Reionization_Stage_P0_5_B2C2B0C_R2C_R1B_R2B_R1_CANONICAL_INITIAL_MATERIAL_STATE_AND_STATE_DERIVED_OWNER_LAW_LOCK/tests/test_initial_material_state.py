from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "analysis" / "initial_material_state.py"
WT = ROOT.parents[1]
R1 = WT / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"
R2A = WT / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT"


def load_module():
    assert SCRIPT.exists(), "initial material-state implementation missing"
    spec = importlib.util.spec_from_file_location("r2b_r1_initial_material_state", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build():
    return load_module().build_initial_material_state(r1_root=R1, r2a_root=R2A)


def test_initial_state_uses_exact_direct_history_z6_row():
    state = build()
    assert state.metadata["source_redshift"] == pytest.approx(6.0, abs=0.0)
    assert state.metadata["source_history_kind"] == "CANONICAL_DIRECT_REEVOLVED"
    assert state.metadata["node_count"] == 46080


def test_initial_state_closes_h_and_he_nuclei_and_species_moments():
    state = build()
    f = state.frame
    h_total = float((f.N_HI + f.N_HII).sum())
    he_total = float((f.N_HeI + f.N_HeII + f.N_HeIII).sum())
    assert h_total == pytest.approx(state.metadata["global_H_nuclei_cMpc-3"], rel=1e-13)
    assert he_total == pytest.approx(state.metadata["global_He_nuclei_cMpc-3"], rel=1e-13)
    assert float(f.N_HII.sum() / h_total) == pytest.approx(state.metadata["global_xHII"], rel=1e-13)
    assert float(f.N_HeI.sum() / he_total) == pytest.approx(state.metadata["global_xHeI"], rel=1e-13)
    assert float(f.N_HeII.sum() / he_total) == pytest.approx(state.metadata["global_xHeII"], rel=1e-13)
    assert float(f.N_HeIII.sum() / he_total) == pytest.approx(state.metadata["global_xHeIII"], rel=1e-13)


def test_initial_state_closes_canonical_internal_energy_without_clipping():
    state = build()
    f = state.frame
    assert np.isfinite(f[["N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved", "T_K"]].to_numpy()).all()
    assert (f[["N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved"]].to_numpy() >= 0.0).all()
    assert (f.T_K.to_numpy() > 0.0).all()
    assert float(f.U_resolved.sum()) == pytest.approx(state.metadata["global_U_resolved_erg_cMpc-3"], rel=1e-13)
    assert state.metadata["thermal_normalization_factor"] > 0.0
    assert state.metadata["clipping_used"] is False


def test_temperature_is_recovered_from_u_and_particle_counts():
    state = build()
    f = state.frame
    k_b = state.metadata["k_B_erg_K-1"]
    particles = f.N_HI + f.N_HII + f.N_HeI + f.N_HeII + f.N_HeIII + f.N_HII + f.N_HeII + 2.0 * f.N_HeIII
    recovered = 2.0 * f.U_resolved.to_numpy() / (3.0 * k_b * particles.to_numpy())
    assert np.max(np.abs(recovered - f.T_K.to_numpy()) / f.T_K.to_numpy()) < 2e-14


def test_initial_state_is_byte_deterministic_at_array_level():
    a = build()
    b = build()
    assert a.array_hashes == b.array_hashes
    assert set(a.array_hashes) >= {"N_HI", "N_HII", "N_HeI", "N_HeII", "N_HeIII", "U_resolved", "T_K"}
