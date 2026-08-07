from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

STAGE = Path(__file__).resolve().parents[1]
REPO = STAGE.parents[1]
R1B_R1 = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R1_CANONICAL_TIME_RESOLVED_GROUP_BOUNDARY_FLUX_DYNAMIC_OPACITY_AND_HEATING_MOMENT_EXTRACTION_LOCK_RERUN_V2"
R2A = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2A_PHOTON_SINK_MATERIAL_REACTION_OWNER_SPLIT_PREFLIGHT"
R2B_R1 = REPO / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R1_CANONICAL_INITIAL_MATERIAL_STATE_AND_STATE_DERIVED_OWNER_LAW_LOCK"


def _load(stem: str):
    name = f"r2b_r2_{stem}"
    spec = importlib.util.spec_from_file_location(name, STAGE / "analysis" / f"{stem}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _state_dict() -> dict[str, np.ndarray]:
    with np.load(R2B_R1 / "data/initial_material_state_z6.npz") as z:
        return {key: np.asarray(z[key]).copy() for key in z.files}


def test_forcing_reproduces_every_locked_endpoint_and_is_monotone():
    forcing = _load("forcing")
    model = forcing.CanonicalForcing.from_stage_inputs(
        forcing_csv=R1B_R1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv",
        owner_csv=R2A / "data/time_resolved_owner_split.csv",
    )
    raw = pd.read_csv(R1B_R1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv")

    assert model.interval_indices == (0, 1, 2, 3, 4)
    for interval, block in raw.groupby("interval_index"):
        times = block.sort_values("node_index")["time_s"].to_numpy(float)
        assert np.all(np.diff(times) > 0.0)
        for _, row in block.iterrows():
            got = model.evaluate(int(interval), float(row["time_s"]))
            assert got["fraction"] == pytest.approx(float(row["fraction"]), rel=0.0, abs=1e-15)
            assert got["xHII"] == pytest.approx(float(row["xHII"]), rel=3e-14, abs=1e-15)
            assert got["T_K"] == pytest.approx(float(row["T_K"]), rel=3e-14, abs=1e-10)
            for group in forcing.GROUPS:
                assert got[f"kappa_{group}_cMpc-1"] == pytest.approx(
                    float(row[f"kappa_{group}_cMpc-1"]), rel=3e-14, abs=1e-300
                )
                assert got[f"absorption_{group}_s-1_cMpc-3"] == pytest.approx(
                    float(row[f"absorption_{group}_s-1_cMpc-3"]), rel=3e-14, abs=1e-300
                )


def test_pchip_integral_is_additive_under_1_2_4_8_partition():
    forcing = _load("forcing")
    model = forcing.CanonicalForcing.from_stage_inputs(
        forcing_csv=R1B_R1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv",
        owner_csv=R2A / "data/time_resolved_owner_split.csv",
    )
    for interval in model.interval_indices:
        duration = model.duration_seconds(interval)
        for group in forcing.GROUPS:
            reference = model.integrate_group_absorption(interval, group, 0.0, duration)
            for n in (2, 4, 8):
                pieces = [
                    model.integrate_group_absorption(
                        interval, group, duration * k / n, duration * (k + 1) / n
                    )
                    for k in range(n)
                ]
                assert math.fsum(pieces) == pytest.approx(reference, rel=2e-15, abs=1e-250)


def test_external_subgrid_raw_is_interpolated_without_creating_support():
    forcing = _load("forcing")
    model = forcing.CanonicalForcing.from_stage_inputs(
        forcing_csv=R1B_R1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv",
        owner_csv=R2A / "data/time_resolved_owner_split.csv",
    )
    for interval in model.interval_indices:
        t = 0.437 * model.duration_seconds(interval)
        assert model.external_subgrid_raw(interval, "G1", t) > 0.0
        assert model.external_subgrid_raw(interval, "G2a", t) > 0.0
        assert model.external_subgrid_raw(interval, "G2b", t) == 0.0
        assert model.external_subgrid_raw(interval, "G3", t) == 0.0


def test_owner_kernel_closes_authoritative_totals_and_exact_structural_zeros():
    forcing = _load("forcing")
    owner = _load("owner_kernel")
    model = forcing.CanonicalForcing.from_stage_inputs(
        forcing_csv=R1B_R1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv",
        owner_csv=R2A / "data/time_resolved_owner_split.csv",
    )
    state = _state_dict()
    kernel = owner.DynamicOwnerKernel.from_stage_inputs(
        initial_state=state,
        atomic_moments_csv=R1B_R1 / "data/atomic_moments/verner_gray_and_limit_moments.csv",
        r1b_r1_stage=R1B_R1,
        r2a_stage=R2A,
    )
    interval = 0
    t = 0.5 * model.duration_seconds(interval)
    row = model.evaluate(interval, t)
    raw_subgrid = {g: model.external_subgrid_raw(interval, g, t) for g in forcing.GROUPS}
    result = kernel.evaluate(
        forcing_row=row,
        state=state,
        external_subgrid_raw=raw_subgrid,
        subgrid_lane="LOCAL_NEUTRAL_HAZARD_PRIMARY",
    )

    for group in forcing.GROUPS:
        assert math.fsum(result.owner_kappa[(group, c)] for c in owner.COMPONENTS) == pytest.approx(
            row[f"kappa_{group}_cMpc-1"], rel=2e-14, abs=1e-300
        )
        assert math.fsum(result.owner_current[(group, c)] for c in owner.COMPONENTS) == pytest.approx(
            row[f"absorption_{group}_s-1_cMpc-3"], rel=2e-14, abs=1e-200
        )
        node_total = math.fsum(
            math.fsum(float(x) for x in result.node_current[(group, c)])
            for c in owner.COMPONENTS
        )
        assert node_total == pytest.approx(
            row[f"absorption_{group}_s-1_cMpc-3"], rel=2e-14, abs=1e-200
        )

    for component, group in owner.UNSUPPORTED:
        assert result.owner_kappa[(group, component)] == 0.0
        assert result.owner_current[(group, component)] == 0.0
        assert np.count_nonzero(result.node_current[(group, component)]) == 0

    assert result.resolved_source_flags["EFFECTIVE_HI_SUBGRID"] == (0, 0, 0)


def test_state_conditioning_moves_explicit_owner_fractions_in_declared_direction():
    forcing = _load("forcing")
    owner = _load("owner_kernel")
    model = forcing.CanonicalForcing.from_stage_inputs(
        forcing_csv=R1B_R1 / "data/bdf_replay/canonical_time_resolved_forcing_nodes.csv",
        owner_csv=R2A / "data/time_resolved_owner_split.csv",
    )
    state = _state_dict()
    kernel = owner.DynamicOwnerKernel.from_stage_inputs(
        initial_state=state,
        atomic_moments_csv=R1B_R1 / "data/atomic_moments/verner_gray_and_limit_moments.csv",
        r1b_r1_stage=R1B_R1,
        r2a_stage=R2A,
    )
    t = 0.5 * model.duration_seconds(0)
    row = model.evaluate(0, t)
    raw_subgrid = {g: model.external_subgrid_raw(0, g, t) for g in forcing.GROUPS}
    base = kernel.evaluate(
        forcing_row=row,
        state=state,
        external_subgrid_raw=raw_subgrid,
        subgrid_lane="LOCAL_NEUTRAL_HAZARD_PRIMARY",
    )

    perturbed = {k: np.asarray(v).copy() for k, v in state.items()}
    transfer = 0.1 * perturbed["N_HII"]
    perturbed["N_HII"] -= transfer
    perturbed["N_HI"] += transfer
    changed = kernel.evaluate(
        forcing_row=row,
        state=perturbed,
        external_subgrid_raw=raw_subgrid,
        subgrid_lane="LOCAL_NEUTRAL_HAZARD_PRIMARY",
    )
    assert changed.owner_fraction[("G2b", "EXPLICIT_HI_ATOMIC")] > base.owner_fraction[("G2b", "EXPLICIT_HI_ATOMIC")]


def test_unknown_or_posthoc_subgrid_lane_is_rejected():
    owner = _load("owner_kernel")
    state = _state_dict()
    kernel = owner.DynamicOwnerKernel.from_stage_inputs(
        initial_state=state,
        atomic_moments_csv=R1B_R1 / "data/atomic_moments/verner_gray_and_limit_moments.csv",
        r1b_r1_stage=R1B_R1,
        r2a_stage=R2A,
    )
    with pytest.raises(KeyError):
        kernel.subgrid_measure(
            forcing_row={"z_mid": 5.95, "Gamma_HI_s-1": 2e-13},
            state=state,
            group="G1",
            lane="BEST_AFTER_RESULTS",
        )
