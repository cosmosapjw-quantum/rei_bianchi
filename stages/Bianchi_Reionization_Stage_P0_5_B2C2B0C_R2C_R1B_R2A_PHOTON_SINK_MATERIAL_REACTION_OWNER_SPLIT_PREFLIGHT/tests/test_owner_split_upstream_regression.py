from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).parents[1]


def test_interval_zero_low_groups_are_subgrid_dominated():
    d = pd.read_csv(ROOT / "inputs/upstream/reconciled_physical_component_absorption.csv")
    d = d[(d.interval_index == 0) & d.group.isin(["G1", "G2a", "G2b"])]
    total = d["absorption_rate_s-1_cMpc-3"].sum()
    resolved_hi = d.loc[d.component == "EXPLICIT_HI_ATOMIC", "absorption_rate_s-1_cMpc-3"].sum()
    subgrid = d.loc[d.component == "EFFECTIVE_HI_SUBGRID", "absorption_rate_s-1_cMpc-3"].sum()
    assert subgrid / total > 0.95
    assert total / resolved_hi > 100.0


def test_group_one_is_structurally_all_subgrid_at_all_midpoints():
    d = pd.read_csv(ROOT / "inputs/upstream/reconciled_physical_component_absorption.csv")
    g1 = d[d.group == "G1"]
    assert (g1.loc[g1.component == "EFFECTIVE_HI_SUBGRID", "absorption_rate_s-1_cMpc-3"] > 0).all()
    assert (g1.loc[g1.component != "EFFECTIVE_HI_SUBGRID", "absorption_rate_s-1_cMpc-3"] == 0).all()


def test_primary_g3_absorption_is_exact_zero():
    d = pd.read_csv(ROOT / "inputs/upstream/reconciled_group_total_absorption.csv")
    assert (d.loc[d.group == "G3", "total_absorption_rate_s-1_cMpc-3"] == 0).all()
