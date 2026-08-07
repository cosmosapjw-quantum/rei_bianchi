from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).parents[1]
WT = ROOT.parents[1]
INITIAL_SCRIPT = ROOT / "analysis" / "initial_material_state.py"
LAW_SCRIPT = ROOT / "analysis" / "state_derived_owner_law.py"
R1 = WT / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"
R2A = WT / "Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT"


def load(path: Path, name: str):
    assert path.exists(), f"{path.name} implementation missing"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixtures():
    initial_mod = load(INITIAL_SCRIPT, "r2b_r1_initial_for_law")
    law_mod = load(LAW_SCRIPT, "r2b_r1_owner_law")
    state = initial_mod.build_initial_material_state(r1_root=R1, r2a_root=R2A)
    model = law_mod.StateDerivedOwnerLaw(r1_root=R1, r2a_root=R2A, initial_state=state)
    forcing = model.forcing.iloc[0].to_dict()
    return law_mod, state, model, forcing


def test_owner_law_closes_total_opacity_current_and_common_flux():
    _, state, model, forcing = fixtures()
    result = model.evaluate(forcing_row=forcing, state_frame=state.frame)
    owner = result.owner_table
    for group, sub in owner.groupby("group"):
        assert sub.conditioned_kappa_cMpc_inv.sum() == pytest.approx(sub.authoritative_kappa_cMpc_inv.iloc[0], rel=1e-13)
        assert sub.owner_current_s_inv_cMpc3.sum() == pytest.approx(sub.authoritative_current_s_inv_cMpc3.iloc[0], rel=1e-13)
        positive = sub.conditioned_kappa_cMpc_inv > 0.0
        if positive.any():
            flux = sub.loc[positive, "owner_current_s_inv_cMpc3"] / sub.loc[positive, "conditioned_kappa_cMpc_inv"]
            assert np.max(np.abs(flux - flux.iloc[0]) / max(abs(float(flux.iloc[0])), 1.0)) < 2e-14


def test_structural_support_and_subgrid_resolved_sources_are_exact():
    law_mod, state, model, forcing = fixtures()
    result = model.evaluate(forcing_row=forcing, state_frame=state.frame)
    owner = result.owner_table.set_index(["group", "component"])
    assert owner.loc[("G1", "EFFECTIVE_HI_SUBGRID"), "conditioned_kappa_cMpc_inv"] > 0.0
    assert owner.loc[("G1", "EXPLICIT_HI_ATOMIC"), "conditioned_kappa_cMpc_inv"] == 0.0
    assert owner.loc[("G1", "EXPLICIT_HEI_ATOMIC"), "conditioned_kappa_cMpc_inv"] == 0.0
    assert owner.loc[("G1", "EXPLICIT_HEII_ATOMIC"), "conditioned_kappa_cMpc_inv"] == 0.0
    assert law_mod.RESOLVED_SOURCE["EFFECTIVE_HI_SUBGRID"] == (0, 0, 0)


def test_owner_and_node_law_is_state_sensitive_not_frozen():
    _, state, model, forcing = fixtures()
    base = model.evaluate(forcing_row=forcing, state_frame=state.frame)
    perturbed = state.frame.copy()
    transfer = 0.02 * perturbed.N_HeII.to_numpy()
    perturbed["N_HeII"] -= transfer
    perturbed["N_HeI"] += transfer
    changed = model.evaluate(forcing_row=forcing, state_frame=perturbed)
    base_frac = float(base.owner_table.query("group == 'G2a' and component == 'EXPLICIT_HEI_ATOMIC'").conditioned_fraction.iloc[0])
    changed_frac = float(changed.owner_table.query("group == 'G2a' and component == 'EXPLICIT_HEI_ATOMIC'").conditioned_fraction.iloc[0])
    assert changed_frac > base_frac
    assert changed.node_hashes[("G2a", "EXPLICIT_HEI_ATOMIC")] != base.node_hashes[("G2a", "EXPLICIT_HEI_ATOMIC")]


def test_primary_subgrid_law_is_predeclared_and_auditors_are_not_promoted():
    _, state, model, forcing = fixtures()
    result = model.evaluate(forcing_row=forcing, state_frame=state.frame)
    assert result.metadata["primary_subgrid_lane"] == "LOCAL_NEUTRAL_HAZARD_PRIMARY"
    assert result.metadata["auditor_lanes"] == ["RECOMBINATION_WEIGHTED_AUDITOR", "SCRIPT_SELF_SHIELDING_AUDITOR"]
    assert result.metadata["post_hoc_lane_selection_used"] is False


def test_node_allocations_are_nonnegative_conservative_and_zero_support_safe():
    _, state, model, forcing = fixtures()
    result = model.evaluate(forcing_row=forcing, state_frame=state.frame)
    for key, allocation in result.node_allocations.items():
        row = result.owner_table.query("group == @key[0] and component == @key[1]").iloc[0]
        assert np.isfinite(allocation).all()
        assert (allocation >= 0.0).all()
        assert allocation.sum() == pytest.approx(row.owner_current_s_inv_cMpc3, rel=1e-13, abs=1e-30)
        support = result.node_support[key]
        assert np.count_nonzero((~support) & (allocation != 0.0)) == 0


def test_explicit_heii_global_response_uses_helium_fraction_not_hydrogen_denominator():
    law_mod, state, model, forcing = fixtures()
    raw = model._global_raw(forcing, state.frame, "G3")
    n_he = float((state.frame.N_HeI + state.frame.N_HeII + state.frame.N_HeIII).sum())
    x_heii = float(state.frame.N_HeII.sum()) / n_he
    z = float(forcing["z_mid"])
    a = 1.0 / (1.0 + z)
    n_he_phys = law_mod.YHE * law_mod.NH0_CM3 * (1.0 + z) ** 3
    expected = (
        a
        * n_he_phys
        * x_heii
        * model.sigma[("HeII", "G3")]
        * law_mod.MPC_CM
    )
    assert raw["EXPLICIT_HEII_ATOMIC"] == pytest.approx(expected, rel=2e-15)
