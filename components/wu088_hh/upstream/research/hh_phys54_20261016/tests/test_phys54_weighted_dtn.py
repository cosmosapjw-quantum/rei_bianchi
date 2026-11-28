from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("phys54", HERE / "scripts/phys54_weighted_dtn.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(mod)


def test_screen_bound_is_positive_and_exterior_decreasing():
    assert mod.screened_multiplier_upper(27.0) > 0.0
    assert mod.screened_multiplier_upper(28.0) < mod.screened_multiplier_upper(27.0)


def test_conditional_form_reduction_has_exact_margin():
    statement = mod.conditional_statement(0.04, 0.01)
    assert statement["state"] == "CONDITIONAL_COERCIVE"
    assert abs(statement["margin"] - 0.03) < 1e-15
    assert mod.conditional_statement(0.01, 0.01)["state"] == "NO_COERCIVITY_FROM_THESE_CONSTANTS"


def test_cf_diagnostic_is_explicitly_noncertifying():
    data = mod.central_cf_diagnostic(21, 29)
    assert data["kind"] == "NONCERTIFYING_CENTRAL_CF_DIAGNOSTIC"
    assert data["min_minus_re_z_over_ell_plus_1"] > 0.0
    assert "screened_outgoing_perturbation_bound" in data["not_a_proof"]


def test_dependency_free_cf_matches_known_rust_reference_to_f64_roundoff():
    # CPython complex division can differ by a few ulps from rustc; this is a
    # diagnostic cross-check, not a replacement oracle.
    assert abs(mod.central_cf_real(21) + 0.18253880022977356) < 1e-15
