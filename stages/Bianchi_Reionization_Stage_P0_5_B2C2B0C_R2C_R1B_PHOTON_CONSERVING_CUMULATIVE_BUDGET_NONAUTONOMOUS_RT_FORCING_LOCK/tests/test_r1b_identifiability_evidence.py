from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

STAGE = Path(__file__).resolve().parents[1]


def _rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), np.finfo(float).tiny)


def test_temporal_null_witness_preserves_endpoints_integral_and_positivity() -> None:
    frame = pd.read_csv(STAGE / "data/temporal_null_witness.csv")
    base = float(np.trapezoid(frame.baseline_J, frame.time_s))
    plus = float(np.trapezoid(frame.plus_J, frame.time_s))
    minus = float(np.trapezoid(frame.minus_J, frame.time_s))
    assert frame.plus_J.min() > 0.0
    assert frame.minus_J.min() > 0.0
    assert frame.plus_J.iloc[0] == frame.baseline_J.iloc[0]
    assert frame.plus_J.iloc[-1] == frame.baseline_J.iloc[-1]
    assert frame.minus_J.iloc[0] == frame.baseline_J.iloc[0]
    assert frame.minus_J.iloc[-1] == frame.baseline_J.iloc[-1]
    assert _rel(base, plus) < 1.0e-12
    assert _rel(base, minus) < 1.0e-12
    assert np.max(np.abs(frame.plus_J - frame.minus_J)) > 0.0


def test_spatial_null_witness_preserves_pointwise_total_but_moves_node_counts() -> None:
    frame = pd.read_csv(STAGE / "data/spatial_partition_null_witness.csv")
    assert frame.node_a_redistributed_J.min() > 0.0
    assert frame.node_b_redistributed_J.min() > 0.0
    assert np.max(
        np.abs(frame.redistributed_pointwise_total_J - frame.baseline_pointwise_total_J)
        / np.maximum(np.abs(frame.baseline_pointwise_total_J), np.finfo(float).tiny)
    ) < 1.0e-12
    da = float(
        np.trapezoid(
            frame.node_a_redistributed_J - frame.node_a_baseline_J, frame.time_s
        )
    )
    db = float(
        np.trapezoid(
            frame.node_b_redistributed_J - frame.node_b_baseline_J, frame.time_s
        )
    )
    assert da != 0.0
    assert db != 0.0
    assert abs(da + db) < 1.0e45


def test_rank_formulas_and_durable_verdict() -> None:
    rank = pd.read_csv(STAGE / "data/constraint_rank_nullity.csv")
    for row in rank.itertuples(index=False):
        expected = (
            row.time_knot_count - 3
            if row.family == "SINGLE_NODE_ENDPOINTS_PLUS_ONE_INTERVAL_INTEGRAL"
            else (row.node_count - 1) * (row.time_knot_count - 2)
        )
        assert row.nullity == expected
    summary = json.loads((STAGE / "data/summary.json").read_text())
    assert summary["identifiability_verdict"] == (
        "UNDERIDENTIFIED_NODE_GROUP_FORCING_DYNAMIC_OPACITY_AND_THERMAL_HISTORY"
    )
    assert summary["temporal_positive_null_witness_pass"] is True
    assert summary["spatial_positive_partition_null_witness_pass"] is True


def test_thermal_auditor_respects_group_bounds_and_primary_g3_zero() -> None:
    frame = pd.read_csv(STAGE / "data/thermal_group_moment_audit.csv")
    assert frame.loc[frame.group.eq("G3"), "primary_source_exact_zero"].all()
    assert (frame.optically_thin_sigma_weighted_HI_excess_eV >= frame.possible_group_excess_min_eV).all()
    assert (frame.optically_thin_sigma_weighted_HI_excess_eV <= frame.possible_group_excess_max_eV).all()
    assert (frame.optically_thick_HI_excess_eV >= frame.possible_group_excess_min_eV).all()
    assert (frame.optically_thick_HI_excess_eV <= frame.possible_group_excess_max_eV).all()
    assert np.max(
        np.abs(
            frame.optically_thick_HI_excess_eV
            - frame.optically_thin_sigma_weighted_HI_excess_eV
        )
    ) > 0.0
