"""Targeted checks for the independent V7 source-free Radau reference."""
from __future__ import annotations

from radau_casea_reference import T_DOMAIN, run, table_parity


def test_literal_rate_table_parity() -> None:
    parity = table_parity()
    assert parity["points"] == 129
    assert parity["max_relative_error"] == 0.0


def test_short_casea_radau_reference_preserves_selected_ledger() -> None:
    result = run()
    final = result["final"]
    diagnostics = result["diagnostics"]
    assert T_DOMAIN[0] <= final["Tgas_K"] <= T_DOMAIN[1]
    assert diagnostics["minimum_fraction_or_w"] > 0.0
    assert diagnostics["energy_relative_residual"] < 2e-11
    assert diagnostics["hydrogen_nuclei_residual"] == 0.0
    assert diagnostics["helium_nuclei_residual"] == 0.0
    assert result["checkout_igm_rates_matches_declared_owner"]
    assert "not a direct source-on endpoint-accuracy comparison" in result["native_comparison_status"]
